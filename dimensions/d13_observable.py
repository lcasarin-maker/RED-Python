#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D13 Observable Behavior (Sprint 28.5): canal HOOK — observabilidad del agente,
no pass/fail del repo. Consolida los 4 scripts d13_* (token meter, decision logger,
divergence detector, D13Report) en un módulo (S19, copiado sin puente). El gate la
SALTA; su rol en el Stop hook es OBSERVAR la sesión (uso de tokens), no bloquear.

tiktoken es opcional: si falta, count_tokens degrada a 0 (no crashea el hook)."""
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dimensions.context import AuditContext

try:
    import tiktoken
except ImportError:
    tiktoken = None

logger = logging.getLogger("dimensions.d13")


def count_tokens(file_path: str) -> int:
    """Tokens cl100k_base de un archivo. 0 si no existe o si tiktoken no está."""
    if tiktoken is None:
        logger.debug("tiktoken ausente: count_tokens degrada a 0")
        return 0
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return 0
    return len(tiktoken.get_encoding("cl100k_base").encode(content))


def estimate_cost(tokens: int, rate_per_1k: float = 0.002) -> float:
    return (tokens / 1000) * rate_per_1k


class DecisionLogger:
    """Registra decisiones del agente en JSONL (observabilidad de comportamiento)."""

    def __init__(self, log_dir: str = "~/.cerberus/decision_logs"):
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"decisions_{now}.jsonl"

    def log_decision(
        self,
        agent: str,
        decision: str,
        reasoning: str,
        action: str,
        result: str,
        metadata: dict = None,
    ) -> str:
        decision_id = str(uuid.uuid4())
        record = {
            "decision_id": decision_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "decision": decision,
            "reasoning": reasoning,
            "action": action,
            "result": result,
            "metadata": metadata or {},
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return decision_id


class DivergenceDetector:
    """Detecta divergencia de una acción vs las reglas PUEDE/NO PUEDE de AGENT.md."""

    def __init__(self, agent_md_path: str = "AGENT.md"):
        self.agent_md = Path(agent_md_path)
        self.can_do, self.cannot_do = set(), set()
        self._parse_agent_md()

    def _parse_agent_md(self):
        if not self.agent_md.exists():
            return
        content = self.agent_md.read_text(encoding="utf-8")
        for match in re.finditer(r"PUEDE:\s*([^\n]+)", content):
            self.can_do.add(match.group(1).strip().lower())
        for match in re.finditer(r"NO PUEDE:\s*([^\n]+)", content):
            self.cannot_do.add(match.group(1).strip().lower())

    def check(self, action: str, context: str = None) -> dict:
        low = action.lower()
        if low in self.cannot_do:
            return {
                "action": action,
                "allowed": False,
                "severity": "CRITICAL",
                "reason": f"'{action}' en NO PUEDE",
                "context": context,
            }
        if low in self.can_do:
            return {
                "action": action,
                "allowed": True,
                "severity": "OK",
                "reason": f"'{action}' en PUEDE",
                "context": context,
            }
        return {
            "action": action,
            "allowed": False,
            "severity": "WARNING",
            "reason": f"'{action}' no explícito",
            "context": context,
        }


class D13Report:
    """Orchestrator/dashboard: costo de tokens de los manifiestos + decisiones."""

    def __init__(self, max_decisions: int = 100):
        self.max_decisions = max_decisions
        self.decision_logger = DecisionLogger()
        self.divergence_detector = DivergenceDetector()
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def _load_token_data(self) -> dict:
        root = Path(".").resolve()
        files = {
            "SPEC.md": root / "SPEC.md",
            "AGENT.md": root / "AGENT.md",
            "PLAN.md": root / "PLAN.md",
        }
        data, total = {}, 0
        for label, path in files.items():
            tokens = count_tokens(str(path))
            total += tokens
            data[label] = {
                "tokens": tokens,
                "cost_usd": round(estimate_cost(tokens), 6),
            }
        data["TOTAL"] = {"tokens": total, "cost_usd": round(estimate_cost(total), 6)}
        return data

    def _load_recent_decisions(self) -> list:
        decisions = []
        if self.decision_logger.log_file.exists():
            with open(self.decision_logger.log_file, "r", encoding="utf-8") as f:
                decisions = [json.loads(line) for line in f]
        return decisions[-self.max_decisions :]

    def generate_json(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "tokens": self._load_token_data(),
            "recent_decisions": self._load_recent_decisions(),
            "divergence_rules": {
                "can_do": list(self.divergence_detector.can_do),
                "cannot_do": list(self.divergence_detector.cannot_do),
            },
        }

    def generate_html(self) -> str:
        data = self.generate_json()
        total = data["tokens"].get("TOTAL", {})
        return (
            "<html><head><title>D13 Observable Behavior</title></head><body>"
            f"<h1>D13 Observable Behavior</h1><p>timestamp: {data['timestamp']}</p>"
            f"<p>tokens TOTAL: {total.get('tokens', 0)} (${total.get('cost_usd', 0)})</p>"
            f"<p>decisiones recientes: {len(data['recent_decisions'])}</p></body></html>"
        )


class D13Observable:
    """Dimensión D13 (canal hook): observabilidad del comportamiento del agente."""

    id = "d13"
    name = "OBSERVABLE BEHAVIOR"
    channel = "hook"

    def audit(self, ctx: AuditContext) -> list:
        """Canal hook: no audita el repo. El gate la salta."""
        return []

    def observe_session(self, transcript_path: str) -> dict:
        """Suma el uso de tokens de los mensajes assistant del transcript (observa
        la sesión en el Stop hook). Cuenta SOLO desde el último /compact (línea con
        isCompactSummary:true) para evitar falsos positivos cuando el JSONL acumula
        historial previo."""
        try:
            with open(transcript_path, encoding="utf-8") as fh:
                lines = fh.readlines()
        except OSError as exc:
            logger.warning(
                "observe_session: transcript ilegible %s: %s", transcript_path, exc
            )
            return {"assistant_messages": 0, "output_tokens": 0}
        # Buscar el último marcador de compact (isCompactSummary:true) y partir desde ahí.
        # Esta versión de Claude Code NO emite type=="summary"; el marcador real es una
        # línea type=="user" con isCompactSummary:true. Sin esto se medía la sesión entera.
        last_summary_idx = -1
        for idx, line in enumerate(lines):
            obj = _parse_line(line)
            if obj is not None and obj.get("isCompactSummary"):
                last_summary_idx = idx
        session_lines = lines[last_summary_idx + 1 :]
        msgs, out_tokens = 0, 0
        for line in session_lines:
            obj = _parse_line(line)
            if obj is None or obj.get("type") != "assistant":
                continue
            msgs += 1
            out_tokens += (
                obj.get("message", {}).get("usage", {}).get("output_tokens", 0) or 0
            )
        return {"assistant_messages": msgs, "output_tokens": out_tokens}


def _parse_line(line: str):
    """Parsea una línea JSONL; None si vacía o no-JSON (registrado, no silencioso)."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        logger.debug("línea de transcript no-JSON, saltada")
        return None
