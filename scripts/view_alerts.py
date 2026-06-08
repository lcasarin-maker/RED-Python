#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALERTS VIEWER — FASE 6: CLI para visualizar alertas centralizadas
Implementa REGLA #6: Token & alert tracking con filtrado por severidad y agente.

Usa la tabla `alerts` compartida con token_tracker y deadlock_resolver.
DB path: env var CERBERUS_DB_PATH o .secrets/protocolo/protocol_state.db (fallback).
"""

import os
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
logger = logging.getLogger("alerts_viewer")

# Environment variable takes precedence; fallback to relative path if not set
_DEFAULT_DB = os.getenv("CERBERUS_DB_PATH", ".secrets/protocolo/protocol_state.db")


class AlertsViewer:
    """Consulta y muestra alertas desde la tabla centralizada de alerts."""

    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: Ruta a la DB. Si None, usa CERBERUS_DB_PATH o el default.
        """
        raw = db_path or os.getenv("CERBERUS_DB_PATH", _DEFAULT_DB)
        self.db_path = Path(raw)

    def get_alerts(
        self, limit: int = 10, severity: str = None, agent_id: str = None
    ) -> list:
        """
        Retorna alertas filtradas por severidad y/o agente.

        Args:
            limit: Máximo de filas a retornar (default 10).
            severity: Filtro opcional — 'info', 'warn', 'error'.
            agent_id: Filtro opcional por agente.

        Returns:
            Lista de tuplas (timestamp, severity, type, message, agent_id).
        """
        if not self.db_path.exists():
            logger.warning("DB no encontrada: %s", self.db_path)
            return []

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            query = "SELECT timestamp, severity, type, message, agent_id FROM alerts WHERE 1=1"
            params: list = []

            if severity:
                query += " AND severity = ?"
                params.append(severity)
            if agent_id:
                query += " AND agent_id = ?"
                params.append(agent_id)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            alerts = cursor.fetchall()
            conn.close()
            return alerts
        except Exception as e:
            logger.error("get_alerts falló: %s", e)
            return []

    def display_alerts(self, alerts: list) -> None:
        """Imprime alertas en formato tabla."""
        if not alerts:
            print("No alerts found")
            return

        print(f"\nALERTS ({len(alerts)} total)\n")
        header = (
            f"{'Timestamp':<20} {'Severity':<8} {'Type':<20} {'Agent':<12} {'Message'}"
        )
        print(header)
        print("-" * len(header))

        _icons = {"info": "[I]", "warn": "[W]", "error": "[E]"}
        for ts, sev, atype, message, agent in alerts:
            try:
                ts_fmt = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M")
            except Exception:
                ts_fmt = (ts or "")[:19]

            icon = _icons.get(sev, "[?]")
            msg = (message or "")[:60]
            print(f"{ts_fmt:<20} {icon} {sev:<6} {atype:<20} {(agent or ''):<12} {msg}")

        print()

    def summary(self) -> dict:
        """Retorna conteo de alertas por severidad."""
        if not self.db_path.exists():
            return {}
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT severity, COUNT(*) FROM alerts GROUP BY severity")
            rows = cursor.fetchall()
            conn.close()
            return dict(rows)
        except Exception as e:
            logger.error("summary falló: %s", e)
            return {}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="REGLA #6: Alert viewer — CoderCerberus"
    )
    parser.add_argument("--recent", type=int, default=10, help="Últimas N alertas")
    parser.add_argument(
        "--severity",
        type=str,
        choices=["info", "warn", "error"],
        help="Filtrar por severidad",
    )
    parser.add_argument("--agent", type=str, help="Filtrar por agente")
    parser.add_argument(
        "--summary", action="store_true", help="Mostrar conteo por severidad"
    )

    args = parser.parse_args()
    viewer = AlertsViewer()

    if args.summary:
        counts = viewer.summary()
        for sev, count in sorted(counts.items()):
            print(f"  {sev}: {count}")
    else:
        alerts = viewer.get_alerts(
            limit=args.recent, severity=args.severity, agent_id=args.agent
        )
        viewer.display_alerts(alerts)
