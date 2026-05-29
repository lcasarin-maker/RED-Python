#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTONOMOUS ORCHESTRATOR — Background daemon que ejecuta TODO automáticamente
Corre 24/7 sin intervención usuario, orquesta todos los scripts
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path
from subprocess import run
import logging

logging.basicConfig(
    filename=Path.home() / '.secrets' / 'protocolo' / 'orchestrator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = Path.home() / '.secrets' / 'protocolo' / 'protocol_state.db'
SCRIPTS_DIR = Path(__file__).parent


class AutonomousOrchestrator:
    def __init__(self):
        self.running = True
        self.last_runs = {}
        logger.info('[ORCHESTRATOR] Iniciando daemon')

    def execute_task(self, task_name, script_path, args=None):
        """Execute a task and log result"""
        try:
            cmd = ['python', str(script_path)]
            if args:
                cmd.extend(args)

            result = run(cmd, capture_output=True, text=True, timeout=60)
            logger.info(f'[TASK] {task_name}: exit_code={result.returncode}')

            return {
                'task': task_name,
                'timestamp': datetime.now().isoformat(),
                'exit_code': result.returncode,
                'success': result.returncode == 0
            }
        except Exception as e:
            logger.error(f'[TASK] {task_name}: {str(e)}')
            return {'task': task_name, 'error': str(e), 'success': False}

    def should_run(self, task_name, interval_seconds):
        """Check if enough time has passed since last run"""
        last = self.last_runs.get(task_name, 0)
        now = time.time()

        if now - last >= interval_seconds:
            self.last_runs[task_name] = now
            return True

        return False

    def run_heartbeat_check(self):
        """Every 30 seconds: Check agent heartbeats"""
        if self.should_run('heartbeat_check', 30):
            self.execute_task(
                'heartbeat_check',
                SCRIPTS_DIR / 'heartbeat_monitor.py',
                ['--daemon']
            )

    def run_health_check(self):
        """Every 5 minutes: Project health dashboard"""
        if self.should_run('health_check', 300):
            self.execute_task(
                'health_check',
                SCRIPTS_DIR / 'auto_maestro.py'
            )

    def run_deadlock_check(self):
        """Every 5 minutes: Detect deadlocked agents"""
        if self.should_run('deadlock_check', 300):
            self.execute_task(
                'deadlock_check',
                SCRIPTS_DIR / 'deadlock_resolver.py'
            )

    def run_archive_sessions(self):
        """Every 1 hour: Archive old sessions (>30 days)"""
        if self.should_run('archive_sessions', 3600):
            self.execute_task(
                'archive_sessions',
                SCRIPTS_DIR / 'compress_historial.py',
                ['--days', '30']
            )

    def run_cache_rebuild(self):
        """Every 6 hours: Rebuild protocol rules cache"""
        if self.should_run('cache_rebuild', 21600):
            self.execute_task(
                'cache_rebuild',
                SCRIPTS_DIR / 'cache_protocol_rules.py',
                ['--build']
            )

    def run_encoding_fix(self):
        """Every 30 minutes: Auto-fix encoding issues"""
        if self.should_run('encoding_fix', 1800):
            # Scan for encoding issues in key files
            self.execute_task(
                'encoding_fix',
                SCRIPTS_DIR / 'fix_encoding.py',
                ['--auto-scan']
            )

    def start_dashboard(self):
        """Start dashboard server if not running"""
        if self.should_run('dashboard_start', 86400):  # Check once per day
            self.execute_task(
                'dashboard_start',
                SCRIPTS_DIR / 'dashboard_server.py',
                ['--daemon']
            )

    def log_orchestrator_status(self):
        """Log status to DB every minute"""
        if self.should_run('log_status', 60):
            try:
                db = sqlite3.connect(str(DB_PATH))
                cursor = db.cursor()

                # Log orchestrator heartbeat
                cursor.execute(
                    "INSERT INTO orchestrator_status (timestamp, running, tasks_completed) VALUES (?, ?, ?)",
                    (datetime.now().isoformat(), 1, len(self.last_runs))
                )
                db.commit()
                db.close()
            except Exception as e:
                logger.error(f'[LOGGING] {str(e)}')

    def run_loop(self):
        """Main orchestration loop"""
        logger.info('[ORCHESTRATOR] Iniciando loop de orquestación')

        while self.running:
            try:
                # Run tasks on their intervals
                self.run_heartbeat_check()
                self.run_health_check()
                self.run_deadlock_check()
                self.run_archive_sessions()
                self.run_cache_rebuild()
                self.run_encoding_fix()
                self.start_dashboard()
                self.log_orchestrator_status()

                # Sleep 10 seconds before next loop iteration
                time.sleep(10)

            except KeyboardInterrupt:
                logger.info('[ORCHESTRATOR] Shutting down (SIGINT)')
                self.running = False
            except Exception as e:
                logger.error(f'[ORCHESTRATOR] Error in loop: {str(e)}')
                time.sleep(10)

    def _stop(self):
        """Graceful shutdown"""
        self.running = False
        logger.info('[ORCHESTRATOR] Stopped')


def main():
    import sys

    if '--daemon' in sys.argv:
        # Run as background daemon
        orchestrator = AutonomousOrchestrator()

        # Create tables if not exist
        try:
            db = sqlite3.connect(str(DB_PATH))
            cursor = db.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orchestrator_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    running INTEGER,
                    tasks_completed INTEGER
                )
            ''')
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f'[INIT] {str(e)}')

        orchestrator.run_loop()

    elif '--status' in sys.argv:
        # Check status
        try:
            db = sqlite3.connect(str(DB_PATH))
            cursor = db.cursor()
            cursor.execute("SELECT * FROM orchestrator_status ORDER BY timestamp DESC LIMIT 5")
            rows = cursor.fetchall()
            db.close()

            if rows:
                print("[ORCHESTRATOR STATUS]")
                for row in rows:
                    print(f"  {row[1]}: running={row[2]}, tasks={row[3]}")
            else:
                print("[ORCHESTRATOR] No status yet")
        except Exception as e:
            print(f"[ORCHESTRATOR] Error: {str(e)}")

    else:
        print("Usage: autonomous_orchestrator.py [--daemon|--status]")


if __name__ == '__main__':
    main()
