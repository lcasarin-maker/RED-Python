#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOKEN TRACKER — Auto-logging de tokens reales vs estimated
Rastrea el uso de tokens y genera alertas por varianza excesiva.
"""

import sys
from pathlib import Path

import logging
from scripts.core_utils import setup_windows_utf8, setup_common_db, setup_alerts_db, setup_token_events_db

_logger = logging.getLogger("token_tracker")

setup_windows_utf8()

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
            cost_map = {"claude-haiku": 0.00008, "claude-sonnet": 0.003, "claude-opus": 0.015}
            cost_per_token = next((v for k, v in cost_map.items() if k in model.lower()), 0.00008)
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
