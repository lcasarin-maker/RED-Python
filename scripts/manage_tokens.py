#!/usr/bin/env python3
"""
manage_tokens.py v2.0 — CoderCerberus Token & Context Management
Módulo único con 4 clases de gestión de tokens y contexto:
  OutputCompressor  — compresión quirúrgica de output verboso
  ContextStore      — almacenamiento externo de contexto (LangChain pattern)
  ContextExtractor  — extracción RAG de STATUS.md
  TokenOptimizer    — 4 tácticas de ahorro: compact, cache, extract, report

CLI: python scripts/manage_tokens.py --compact [--quiet]
"""

import json
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

try:
    from scripts.core_utils import setup_windows_utf8, TOKEN_BUDGET as _TOKEN_BUDGET, get_historical_path, get_status_md_path
    setup_windows_utf8()
except ImportError as e:
    import sys as _sys
    _sys.stderr.write(f"[WARN] token_manager: core_utils no disponible ({e}) — UTF-8 no configurado\n")
    _TOKEN_BUDGET = 150_000  # fallback: session token budget (see core_utils.TOKEN_BUDGET)


# ── 1. OutputCompressor (ex rtk_auto_compress.RTKAutoCompress) ──────────────

class OutputCompressor:
    """Compresión quirúrgica de output verboso — trunca líneas largas."""
    VERBOSITY_THRESHOLD = 500
    LINE_LIMIT = 120

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // 4

    @staticmethod
    def should_compress(output: str) -> bool:
        return len(output) > OutputCompressor.VERBOSITY_THRESHOLD

    @staticmethod
    def process_output(output: str, command_type: str = "git") -> tuple:
        """Trunca líneas largas si output supera el umbral. Retorna (text, used)."""
        if not OutputCompressor.should_compress(output):
            return output, False
        lines = [
            line[:OutputCompressor.LINE_LIMIT - 3] + "..." if len(line) > OutputCompressor.LINE_LIMIT else line
            for line in output.split('\n')
        ]
        compressed = '\n'.join(lines)
        before = OutputCompressor.estimate_tokens(output)
        after = OutputCompressor.estimate_tokens(compressed)
        if before > after:
            savings = (before - after) / before * 100
            print(f"\n[OK] Auto-compressed: {before} -> {after} tokens ({savings:.0f}% saved)",
                  file=sys.stderr)
            return compressed, True
        return output, False


# ── 2. ContextExtractor ──────────────────────────────────────────────────────

class ContextExtractor:
    """Extrae secciones relevantes de STATUS.md con scoring RAG. Decide si COMPACT."""

    PROJECTS = ['RED-Python', 'Declutter', 'Agente_Inmobiliario', 'Aequitas_OS']
    TECH_TERMS = ['heartbeat', 'merge', 'token', 'cache', 'compact', 'dashboard',
                  'encoding', 'validation', 'git', 'hook', 'test', 'script', 'db',
                  'api', 'daemon', 'alert', 'monitor', 'remediate', 'historial']
    TOKEN_BUDGET = _TOKEN_BUDGET

    def extract_keywords(self, task: str) -> set:
        import re
        kws = {p for p in self.PROJECTS if p.lower() in task.lower()}
        kws |= {t for t in self.TECH_TERMS if t in task.lower()}
        kws |= set(re.findall(r'(\w+\.py|\w+\.md|\w+\.json)', task))
        return kws

    def parse_status_md(self, content: str) -> dict:
        """Parsea STATUS.md en secciones CAMPO numeradas. API pública."""
        import re
        campos, current, lines = {}, None, []
        for line in content.split('\n'):
            # GF-1: case-insensitive match — STATUS.md uses "## Campo 1:" (mixed case)
            if re.match(r'^## campo\s+\d+', line, re.IGNORECASE):
                if current:
                    campos[current] = '\n'.join(lines).strip()
                m = re.search(r'campo\s+(\d+)', line, re.IGNORECASE)
                current = m.group(1) if m else None
                lines = [line]
            elif current:
                lines.append(line)
        if current:
            campos[current] = '\n'.join(lines).strip()
        return campos

    def score_campo_relevance(self, num: str, content: str, kws: set) -> float:
        """Puntúa relevancia de un CAMPO (0.0–1.0) respecto a keywords de tarea. API pública."""
        score = {'1': 0.3, '3': 0.2, '6': 0.4}.get(num, 0.0)
        if num == '4' and any(k in kws for k in ['error', 'bug', 'block']):
            score += 0.3
        score += (sum(1 for k in kws if k.lower() in content.lower()) / (len(kws) + 1)) * 0.5
        return min(score, 1.0)

    def extract_relevant_context(self, task: str, status_path) -> tuple:
        """Retorna (extracted_text, tokens_saved, report_dict)."""
        try:
            content = Path(status_path).read_text(encoding='utf-8')
        except OSError as e:
            return "", 0, {"error": str(e)}
        kws = self.extract_keywords(task)
        campos = self.parse_status_md(content)
        scored = sorted(
            [(n, c, self.score_campo_relevance(n, c, kws)) for n, c in campos.items()],
            key=lambda x: x[2], reverse=True
        )
        relevant = [s for s in scored if s[2] > 0.1][:4]
        extracted = '\n\n'.join(c for _, c, _ in relevant)
        orig_tok = int(len(content.split()) * 1.3)
        extr_tok = int(len(extracted.split()) * 1.3)
        return extracted, orig_tok - extr_tok, {
            'keywords_found': list(kws), 'campos': [n for n, _, _ in relevant],
            'original_tokens': orig_tok, 'extracted_tokens': extr_tok,
            'savings_percent': round((orig_tok - extr_tok) / max(orig_tok, 1) * 100, 1)
        }

# ── 3. TokenOptimizer ────────────────────────────────────────────────────────

def _split_sessions(lines: list) -> list:
    """Split HISTORIAL.md lines into session blocks delimited by ## SESIÓN/SESSION headers."""
    sessions: list[str] = []
    current: list[str] = []
    for line in lines:
        if line.startswith(("## SESIÓN", "## SESSION")):
            if current:
                sessions.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        sessions.append("\n".join(current))
    return sessions


class TokenOptimizer:
    """4 tácticas de ahorro de tokens. Usa ContextExtractor internamente."""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.db_path = Path.home() / ".secrets" / "protocolo" / "protocol_state.db"
        self.extractor = ContextExtractor()
        self._ensure_token_optimizations_table()  # GF-5

    def _ensure_token_optimizations_table(self) -> None:
        """Create token_optimizations table if the DB file exists (GF-5 / P7.0).
        Without this, _log() silently fails with 'no such table' on every call.
        """
        if not self.db_path.exists():
            return
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS token_optimizations "
                    "(id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, "
                    "action TEXT, tokens_saved INTEGER, method TEXT)"
                )
        except Exception as e:
            print(f"[WARN] token_optimizations init: {e}")

    def _log(self, action: str, tokens_saved: int, method: str) -> bool:
        if not self.db_path.exists():
            return False
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute(
                    "INSERT INTO token_optimizations (timestamp,action,tokens_saved,method) VALUES (?,?,?,?)",
                    (datetime.now().isoformat(), action, tokens_saved, method)
                )
            return True
        except Exception as e:
            print(f"[WARN] log failed: {e}")
            return False

    def check_and_compact(self) -> dict:
        """Táctica 1: compactar HISTORIAL con compresión ReMe si >45 sesiones."""
        hp = get_historical_path(self.project_dir)
        if not hp.exists():
            return None
        try:
            content = hp.read_text(encoding='utf-8')
            lines = content.splitlines()
            count = sum(1 for l in lines if l.startswith("## SESIÓN") or l.startswith("## SESSION"))
            if count > 45:
                print(f"[ACTION] COMPACT triggered: {count} sessions via ReMe Semantic Engine")
                
                # 1. Save standard forensic backup
                backup_path = self.project_dir / "docs" / "archive" / "reports"
                backup_path.mkdir(parents=True, exist_ok=True)
                backup = backup_path / f"HISTORIAL_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                backup.write_text(content, encoding='utf-8')
                
                # 2. Run ReMe Memory Compression
                from scripts.compress_memory_context import compress_memory_block
                compressed = compress_memory_block(content)
                
                # 3. Save ReMe structured JSON archive
                json_archive = backup_path / "historial_reme_compressed.json"
                json_archive.write_text(json.dumps(compressed, indent=2, ensure_ascii=False), encoding='utf-8')
                
                # 4. Extract recent sessions (keep the most recent 10 sessions)
                sessions = _split_sessions(lines)
                
                # Keep most recent 10 sessions
                recent_sessions = sessions[:10] if len(sessions) > 10 else sessions
                recent_text = "\n\n".join(recent_sessions)
                
                # Create ReMe high-density markdown summary header
                summary_lines = compressed.get("fact_summaries", [])
                compacted_summaries = summary_lines[10:] if len(summary_lines) > 10 else summary_lines
                
                reme_header = (
                    "# HISTORIAL DE SESIONES (COMPACTADO - ReMe v1.1)\n\n"
                    "> [!NOTE]\n"
                    "> Las sesiones antiguas han sido compactadas semánticamente para optimizar tokens de contexto.\n"
                    f"> El registro completo se encuentra archivado en [historial_reme_compressed.json](file:///{json_archive.absolute().as_posix()}).\n\n"
                    "## 📚 ARCHIVE SUMMARY (ReMe Semantic Compression)\n"
                    f"- Total sesiones compactadas: {len(compacted_summaries)} / {count}\n"
                    "- " + "\n- ".join(compacted_summaries) + "\n\n"
                    "---\n\n"
                )
                
                hp.write_text(reme_header + recent_text, encoding='utf-8')
                
                self._log("COMPACT", count * 200, "compress_historial_reme")
                return {"action": "COMPACT", "sessions": count}
        except Exception as e:
            print(f"[ERROR] compact failed: {e}")
        return None

    def rebuild_cache(self) -> dict:
        """Táctica 2: regenerar el caché REAL de mandatos (fuente canónica única).

        Delega en cache_protocol_rules.build_cache, que parsea los mandatos S/B
        desde PROTOCOL_SYSTEM/BEHAVIOR.md hacia .claude/cache/protocol_rules.json
        (el caché que consume run_security_audit_12d). Reemplaza el contador roto de "REGLA #"
        sobre AGENT.md (que devolvía 0) y elimina el caché impostor huérfano.
        """
        try:
            from scripts.cache_protocol_rules import build_cache, _DEFAULT_CACHE_FILE
            cache_file = self.project_dir / _DEFAULT_CACHE_FILE
            if not build_cache(self.project_dir, cache_file):
                return None
            data = json.loads(cache_file.read_text(encoding='utf-8'))
            count = data.get("total_mandates", 0)
            self._log("REBUILD_CACHE", count, "cache_protocol_rules")
            return {"action": "CACHE", "rules": count}
        except Exception as e:
            print(f"[WARN] cache rebuild failed: {e}")
        return None

    def smart_context_extraction(self) -> dict:
        """Táctica 3: extracción inteligente de STATUS.md (usa ContextExtractor)."""
        sp = get_status_md_path(self.project_dir)
        if not sp.exists():
            return None
        try:
            _, savings, report = self.extractor.extract_relevant_context("general", sp)
            if report.get('original_tokens', 0) > 1500:
                print(f"[ACTION] Smart extraction: {report['original_tokens']} → {report['extracted_tokens']} tokens")
                self._log("SMART_EXTRACTION", savings, "smart_context_extractor")
                return {"action": "SMART_EXTRACTION", **report}
        except Exception as e:
            print(f"[WARN] smart extraction failed: {e}")
        return None

    def generate_report(self) -> None:
        """Táctica 4: reporte de optimizaciones desde sqlite."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                rows = conn.execute(
                    "SELECT action, COUNT(*), SUM(tokens_saved) FROM token_optimizations GROUP BY action"
                ).fetchall()
            print("\n[REPORT] Optimizations Performed")
            total = sum(r[2] or 0 for r in rows)
            for action, count, saved in rows:
                print(f"  {action}: {count}x (saved ~{saved:,} tokens)")
            print(f"\n[TOTAL] Estimated tokens saved: {total:,}")
        except Exception as e:
            print(f"[WARN] Report generation failed: {e}")

    def run_all(self) -> dict:
        """Ejecuta todas las tácticas y genera reporte."""
        print(f"\n[START] Token Optimizer at {datetime.now().isoformat()}")
        results = {}
        for tactic in [self.check_and_compact, self.rebuild_cache,
                       self.smart_context_extraction]:
            try:
                r = tactic()
                if r:
                    results[r["action"]] = r
            except Exception as e:
                print(f"[WARN] Tactic failed: {e}")
        self.generate_report()
        print("\n[OK] Token Optimizer completed")
        print(f"Optimizations applied: {len(results)}")
        return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="CoderCerberus Token Manager CLI")
    parser.add_argument("--compact", action="store_true", help="Run compact + cache tactics")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-critical output")
    args = parser.parse_args()
    opt = TokenOptimizer()
    if args.compact:
        opt.check_and_compact()
        opt.rebuild_cache()
        opt.generate_report()
    else:
        opt.run_all()
