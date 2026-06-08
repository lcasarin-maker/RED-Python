#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEADLOCK RESOLVER — Detect and alert on blocked agents
Implementa FASE 6: Detecta patrones de deadlock y genera alertas automáticas
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from scripts.core_utils import setup_windows_utf8, setup_alerts_db

setup_windows_utf8()


class DeadlockResolver:
    """Detecta agentes bloqueados y genera alertas en la base de datos."""

    def __init__(
        self, db_path=".secrets/protocolo/protocol_state.db", threshold_minutes=10
    ):
        """Inicializa con la ruta de la DB y el umbral de tiempo."""
        self.db_path = Path(db_path)
        self.threshold = threshold_minutes * 60

    def analyze_agent_state(self, agent_id: str) -> bool:
        """Analiza estado del agente para detectar deadlock."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, status FROM agent_heartbeats
            WHERE agent_id = ?
            ORDER BY timestamp DESC LIMIT 10
        """,
            (agent_id,),
        )
        heartbeats = cursor.fetchall()
        conn.close()

        if not heartbeats:
            return False
        statuses = [hb[1] for hb in heartbeats]
        if len(set(statuses)) == 1 and statuses[0] == "blocked":
            return True

        try:
            latest_time = datetime.fromisoformat(heartbeats[0][0])
            time_since = (datetime.now() - latest_time).total_seconds()
            if time_since > self.threshold:
                return True
        except Exception as e:
            import logging

            logging.warning(
                "deadlock_resolver: no se pudo parsear timestamp de %s: %s", agent_id, e
            )
        return False

    def insert_alert(self, agent_id: str, message: str, recommendation: str) -> None:
        """Inserta una alerta con recomendación en la base de datos."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        setup_alerts_db(cursor)
        cursor.execute(
            """
            INSERT INTO alerts (severity, type, message, agent_id)
            VALUES (?, ?, ?, ?)
        """,
            (
                "warn",
                "deadlock_detected",
                f"{message} | RECOMMENDATION: {recommendation}",
                agent_id,
            ),
        )
        conn.commit()
        conn.close()

    def check_all_agents(self) -> int:
        """Verifica la salud de todos los agentes registrados."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT agent_id FROM agent_heartbeats ORDER BY agent_id"
        )
        agents = cursor.fetchall()
        conn.close()

        alerts_generated = 0
        for (agent_id,) in agents:
            if self.analyze_agent_state(agent_id):
                self.insert_alert(
                    agent_id, f"Agent {agent_id} deadlocked", "Run /compact"
                )
                alerts_generated += 1
        return alerts_generated


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deadlock resolver")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--threshold", type=int, default=10)
    args = parser.parse_args()
    resolver = DeadlockResolver(threshold_minutes=args.threshold)
    if args.check:
        alerts = resolver.check_all_agents()
        print(f"Alerts: {alerts}")
