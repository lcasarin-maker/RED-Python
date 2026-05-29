"""
TEST: test_regla_6_token_tracking.py
Parte de la suite de validacion de Protocolo Agentes.
"""

import os
import unittest
import sqlite3
import tempfile
from pathlib import Path
from scripts.token_tracker import TokenTracker

class TestRegla6TokenTracking(unittest.TestCase):
    def setUp(self):
        # Usar una base de datos de test temporal (no hardcodeada)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "test_tokens.db")
        self.tracker = TokenTracker(db_path=self.db_path)

    def tearDown(self):
        self.tracker.close()
        self.temp_dir.cleanup()

    def test_log_event_and_cost_calculation(self):
        """Verifica que un evento se guarda y el costo se calcula correctamente."""
        self.tracker.log_completion(
            agent_id="test_agent",
            session_id="session_1",
            model="claude-haiku",
            tokens_estimated=1000,
            tokens_actual=1200,
            note="Test event"
        )
        
        # Verificar en DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT tokens_actual, cost_actual FROM token_events WHERE session_id='session_1'")
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        tokens, cost = row
        self.assertEqual(tokens, 1200)
        # 1200 * 0.00008 = 0.096
        self.assertAlmostEqual(cost, 0.096, places=4)

    def test_variance_alert(self):
        """Verifica que se genera una alerta si la varianza supera el 20%."""
        # Caso: Varianza del 50% (1000 vs 1500)
        self.tracker.log_completion(
            agent_id="test_agent",
            session_id="session_alert",
            model="claude-sonnet",
            tokens_estimated=1000,
            tokens_actual=1500
        )
        
        alerts = self.tracker.get_alerts()
        self.assertTrue(len(alerts) > 0)
        self.assertEqual(alerts[0][2], "token_variance")
        self.assertIn("Variance 50%", alerts[0][3])

    def test_summary_generation(self):
        """Verifica que el resumen agrega datos correctamente."""
        self.tracker.log_completion("agent_a", "s1", "claude-haiku", 100, 100)
        self.tracker.log_completion("agent_a", "s2", "claude-haiku", 100, 200)
        
        summary = self.tracker.get_summary()
        self.assertEqual(len(summary), 1)
        agent_id, sessions, avg_tokens, total_cost, variance = summary[0]
        self.assertEqual(agent_id, "agent_a")
        self.assertEqual(sessions, 2)
        self.assertEqual(avg_tokens, 150) # (100+200)/2

if __name__ == "__main__":
    unittest.main()
