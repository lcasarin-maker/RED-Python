#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOKEN TRACKER — Auto-logging de tokens reales vs estimated
Rastrea el uso de tokens y genera alertas por varianza excesiva.
"""

import json
import sys
import sqlite3
from pathlib import Path

import logging
from scripts.core_utils import setup_windows_utf8, setup_common_db, setup_alerts_db, setup_token_events_db

_logger = logging.getLogger("token_tracker")

setup_windows_utf8()

MODEL_COSTS_PER_TOKEN = {
    "claude-haiku": 0.00008,
    "claude-sonnet": 0.003,
    "claude-opus": 0.015,
}


def _coerce_int(value):
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _cost_per_token(model: str) -> float:
    model_name = (model or "").lower()
    return next((rate for key, rate in MODEL_COSTS_PER_TOKEN.items() if key in model_name), 0.00008)


def _sum_ints(*values) -> int | None:
    total = 0
    seen = False
    for value in values:
        coerced = _coerce_int(value)
        if coerced is None:
            continue
        total += coerced
        seen = True
    return total if seen else None


def _first_present(*values):
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _first_int(*values) -> int | None:
    for value in values:
        coerced = _coerce_int(value)
        if coerced is not None:
            return coerced
    return None

class TokenTracker:
    """Rastrea el consumo de tokens de agentes para analisis de eficiencia."""

    def __init__(self, db_path: str = ".secrets/protocolo/tokens.db"):
        """
        Inicializa la conexion a la DB y asegura el esquema.
        
        Inputs: db_path (str): Ruta al archivo de base de datos.
        Outputs: None
        Contract: Establece la conexion sqlite3 y crea tablas si no existen.
        """
        try:
            self.db_path = Path(db_path)
            if str(db_path) == ":memory:":
                self.conn = sqlite3.connect(":memory:")
                self.cursor = self.conn.cursor()
            else:
                self.conn, self.cursor = setup_common_db(self.db_path)
            self.setup_db()
        except Exception as e:
            print(f"❌ Error inicializando tracker: {e}")
            sys.exit(1)

    def setup_db(self) -> None:
        """Crea el esquema de la base de datos si no existe."""
        setup_token_events_db(self.cursor)
        setup_alerts_db(self.cursor)
        self.conn.commit()

    def log_completion(self, agent_id: str, session_id: str, model: str, tokens_estimated: int, tokens_actual: int, note: str = "") -> None:
        """
        Registra un evento de consumo de tokens y verifica varianza.
        
        Inputs:
            agent_id (str): ID del agente.
            session_id (str): ID de la sesion.
            model (str): Nombre del modelo usado.
            tokens_estimated (int): Tokens estimados al inicio.
            tokens_actual (int): Tokens consumidos realmente.
            note (str): Notas adicionales.
        Outputs: None
        Contract: Inserta el registro en token_events y genera alerta si la varianza > 20%.
        """
        try:
            cost_per_token = _cost_per_token(model)
            cost_actual = tokens_actual * cost_per_token

            self.cursor.execute("""
                INSERT INTO token_events (agent_id, session_id, model, tokens_estimated, tokens_actual, cost_actual, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (agent_id, session_id, model, tokens_estimated, tokens_actual, cost_actual, note))
            self.conn.commit()

            if tokens_estimated > 0:
                variance = abs(tokens_actual - tokens_estimated) / tokens_estimated
                if variance > 0.2:
                    severity = 'warn' if tokens_actual > tokens_estimated else 'info'
                    self.cursor.execute("INSERT INTO alerts (severity, type, message, agent_id) VALUES (?, ?, ?, ?)",
                        (severity, 'token_variance', f'Variance {variance*100:.0f}%', agent_id))
                    self.conn.commit()
        except Exception as e:
            print(f"❌ Error registrando tokens: {e}")

    def _parse_transcript_entry(self, payload: dict) -> dict | None:
        """Normalize a transcript JSON object into a cost event."""
        if not isinstance(payload, dict):
            return None

        model_value = _first_present(
            payload.get("model"),
            payload.get("llm_model"),
            payload.get("provider_model"),
            payload.get("engine"),
        )
        agent_value = _first_present(
            payload.get("agent_id"),
            payload.get("agent"),
            payload.get("actor"),
            payload.get("user"),
        )
        session_value = _first_present(
            payload.get("session_id"),
            payload.get("conversation_id"),
            payload.get("run_id"),
            payload.get("id"),
        )
        note_value = _first_present(payload.get("note"), payload.get("message"), payload.get("event"))
        model = str(model_value if model_value is not None else "unknown")
        agent_id = str(agent_value if agent_value is not None else "transcript")
        session_id = str(session_value if session_value is not None else "transcript")
        note = str(note_value if note_value is not None else "")
        usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}

        tokens_estimated = _first_int(payload.get("tokens_estimated"), payload.get("estimated_tokens"))
        tokens_actual = _first_int(payload.get("tokens_actual"), payload.get("actual_tokens"))

        if tokens_actual is None:
            tokens_actual = _first_int(
                usage.get("total_tokens"),
                payload.get("total_tokens"),
                payload.get("usage_total_tokens"),
            )
        if tokens_actual is None:
            tokens_actual = _sum_ints(
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
                payload.get("prompt_tokens"),
                payload.get("completion_tokens"),
                payload.get("input_tokens"),
                payload.get("output_tokens"),
            )

        if tokens_estimated is None:
            tokens_estimated = _sum_ints(
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
                payload.get("prompt_tokens"),
                payload.get("completion_tokens"),
            )
        if tokens_estimated is None:
            tokens_estimated = tokens_actual

        if tokens_actual is None:
            return None

        cost_per_token = _cost_per_token(model)
        cost_actual = payload.get("cost_actual")
        if cost_actual is None:
            cost_actual = round(tokens_actual * cost_per_token, 6)
        else:
            cost_actual = float(cost_actual)

        return {
            "agent_id": agent_id,
            "session_id": session_id,
            "model": model,
            "tokens_estimated": int(tokens_estimated or 0),
            "tokens_actual": int(tokens_actual),
            "cost_actual": float(cost_actual),
            "note": note,
        }

    def analyze_transcript(self, transcript_path: str | Path = "transcript.jsonl") -> dict:
        """Parse a JSONL transcript and return a cost summary."""
        path = Path(transcript_path)
        result = {
            "path": str(path),
            "exists": path.exists(),
            "entries": [],
            "entry_count": 0,
            "sessions": 0,
            "tokens_estimated": 0,
            "tokens_actual": 0,
            "total_cost": 0.0,
            "models": {},
        }
        if not path.exists():
            return result

        seen_sessions = set()
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception as e:
            _logger.warning("analyze_transcript failed reading %s: %s", path, e)
            return result

        for line_no, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line:
                continue
            payload = self._parse_transcript_json_line(line, path, line_no)
            if payload is None:
                continue

            entry = self._parse_transcript_entry(payload)
            if not entry:
                continue

            result["entries"].append(entry)
            result["entry_count"] += 1
            result["tokens_estimated"] += entry["tokens_estimated"]
            result["tokens_actual"] += entry["tokens_actual"]
            result["total_cost"] += entry["cost_actual"]
            seen_sessions.add(entry["session_id"])
            model_key = entry["model"]
            model_bucket = result["models"].setdefault(
                model_key,
                {"entries": 0, "tokens_actual": 0, "total_cost": 0.0},
            )
            model_bucket["entries"] += 1
            model_bucket["tokens_actual"] += entry["tokens_actual"]
            model_bucket["total_cost"] += entry["cost_actual"]

        result["sessions"] = len(seen_sessions)
        result["total_cost"] = round(result["total_cost"], 6)
        for model_key in result["models"]:
            result["models"][model_key]["total_cost"] = round(result["models"][model_key]["total_cost"], 6)
        return result

    def _parse_transcript_json_line(self, line: str, path: Path, line_no: int) -> dict | None:
        """Parse one JSONL line and surface malformed input explicitly."""
        try:
            return json.loads(line)
        except json.JSONDecodeError as exc:
            _logger.warning("ignoring malformed transcript line %s in %s: %s", line_no, path, exc)
            return None

    def format_transcript_cost_report(self, transcript_path: str | Path = "transcript.jsonl") -> str:
        """Return a human-readable cost report for a transcript."""
        summary = self.analyze_transcript(transcript_path)
        if not summary["exists"]:
            return f"cost: transcript not found at {summary['path']}"

        lines = [
            f"cost: transcript={summary['path']}",
            f"entries={summary['entry_count']} sessions={summary['sessions']}",
            f"tokens_estimated={summary['tokens_estimated']} tokens_actual={summary['tokens_actual']}",
            f"total_cost_usd={summary['total_cost']:.6f}",
        ]
        if summary["models"]:
            lines.append("by_model:")
            for model_name in sorted(summary["models"]):
                bucket = summary["models"][model_name]
                lines.append(
                    f"  - {model_name}: entries={bucket['entries']} tokens_actual={bucket['tokens_actual']} cost_usd={bucket['total_cost']:.6f}"
                )
        return "\n".join(lines)

    def get_summary(self, days: int = 7) -> list:
        """
        Retorna un resumen del uso de tokens en los últimos N días.
        
        Args:
            days (int): Número de días a analizar.
        Returns:
            list: Filas con estadísticas por agente.
        """
        try:
            # SQLite does not allow parametrizing the interval string, so we format it directly.
            query = f"""
                SELECT agent_id,
                       COUNT(*) AS sessions,
                       AVG(tokens_actual) AS avg_tokens,
                       SUM(cost_actual) AS total_cost,
                       ROUND(100.0 * (AVG(tokens_actual) - AVG(tokens_estimated)) / AVG(tokens_estimated), 1) AS variance
                FROM token_events
                WHERE datetime(timestamp) > datetime('now', '-{days} days')
                GROUP BY agent_id
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception:
            return []

    def get_alerts(self, limit: int = 50) -> list:
        """Retorna las alertas más recientes."""
        try:
            self.cursor.execute("SELECT id, timestamp, type, message, severity, agent_id FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            _logger.warning("get_alerts failed: %s", e)
            return []

    def close(self) -> None:
        """Cierra la conexion a la base de datos de forma segura."""
        try:
            self.conn.close()
        except Exception as e:
            _logger.warning("token_tracker: error al cerrar DB: %s", e)

if __name__ == "__main__":
    try:
        tracker = TokenTracker()
        print("Tracker inicializado.")
        tracker.close()
    except Exception as e:
        print(f"❌ Error en ejecucion directa: {e}")
        sys.exit(1)
