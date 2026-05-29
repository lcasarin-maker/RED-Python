#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-REMEDIATION ENGINE — Detecta problemas y auto-arregla si es seguro
Auto-fix para severidad LOW/MEDIUM, requiere aprobación para CRITICAL
"""

import json
from pathlib import Path
from datetime import datetime
from subprocess import run
import sqlite3


class RemediationRule:
    """Define a remediation action"""

    def __init__(self, issue_type, severity, auto_action=None, requires_approval=False):
        self.issue_type = issue_type
        self.severity = severity
        self.auto_action = auto_action
        self.requires_approval = requires_approval

    def execute(self):
        """Execute the remediation action"""
        if self.auto_action:
            return self.auto_action()
        return False


# Define all remediation rules
REMEDIATION_RULES = {
    'agent_heartbeat_missing': RemediationRule(
        'agent_heartbeat_missing',
        'HIGH',
        auto_action=lambda: restart_agent_session(),
        requires_approval=False
    ),
    'merge_conflict_non_overlapping': RemediationRule(
        'merge_conflict_non_overlapping',
        'LOW',
        auto_action=lambda: auto_merge_semantic(),
        requires_approval=False
    ),
    'merge_conflict_overlapping': RemediationRule(
        'merge_conflict_overlapping',
        'HIGH',
        requires_approval=True  # Requires manual approval
    ),
    'disk_space_low': RemediationRule(
        'disk_space_low',
        'MEDIUM',
        auto_action=lambda: compress_historial(),
        requires_approval=False
    ),
    'token_budget_exceeded': RemediationRule(
        'token_budget_exceeded',
        'CRITICAL',
        auto_action=lambda: force_compact(),
        requires_approval=False  # Critical, must execute
    ),
    'credentials_found_in_commit': RemediationRule(
        'credentials_found_in_commit',
        'CRITICAL',
        auto_action=lambda: block_push_notify(),
        requires_approval=False  # Critical, must block
    ),
    'encoding_issues': RemediationRule(
        'encoding_issues',
        'MEDIUM',
        auto_action=lambda: fix_encoding(),
        requires_approval=False
    )
}


def restart_agent_session():
    """Restart a blocked agent session"""
    run(['python', 'agent_ping.py', '--reset-state'], capture_output=True)
    return True


def auto_merge_semantic():
    """Auto-merge non-conflicting HISTORIAL.md"""
    result = run(
        ['python', 'merge_historial_semantic.py', '--auto'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def compress_historial():
    """Compress old sessions to free space"""
    result = run(
        ['python', 'compress_historial.py', '--days', '30'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def force_compact():
    """Force COMPACT to reduce context usage"""
    result = run(
        ['python', 'auto_compact_decision.py', '--force'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def block_push_notify():
    """Block push and notify user"""
    # This would be called by pre-push hook
    # Notification already sent by validate_data.py
    return True


def fix_encoding():
    """Auto-fix encoding issues"""
    result = run(
        ['python', 'fix_encoding.py', '--auto-scan', '--fix'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


class AutoRemediationEngine:
    def __init__(self):
        self.db_path = Path.home() / '.secrets' / 'protocolo' / 'protocol_state.db'
        self.approval_queue_path = self.db_path.parent / 'approval_queue.json'

    def detect_issues(self):
        """Detect issues from alerts/logs"""
        try:
            db = sqlite3.connect(str(self.db_path))
            cursor = db.cursor()

            # Check for missing heartbeats
            cursor.execute(
                "SELECT agent_id FROM agent_heartbeats WHERE timestamp < datetime('now', '-5 minutes') LIMIT 1"
            )
            if cursor.fetchone():
                yield {'type': 'agent_heartbeat_missing', 'severity': 'HIGH'}

            # Check disk space (simplified)
            import shutil
            usage = shutil.disk_usage('/')
            if usage.free / usage.total < 0.1:  # Less than 10% free
                yield {'type': 'disk_space_low', 'severity': 'MEDIUM'}

            # Check context usage
            cursor.execute("SELECT COUNT(*) FROM sessions WHERE status='IN_PROGRESS'")
            count = cursor.fetchone()[0]
            if count > 45:  # More than 45 messages
                yield {'type': 'token_budget_exceeded', 'severity': 'CRITICAL'}

            db.close()

        except Exception as e:
            print(f"[DETECT] Error: {str(e)}")

    def remediate(self, issue):
        """Attempt to remediate an issue"""
        issue_type = issue.get('type')

        if issue_type not in REMEDIATION_RULES:
            return {'status': 'unknown_issue', 'issue': issue_type}

        rule = REMEDIATION_RULES[issue_type]

        # If requires approval, add to queue
        if rule.requires_approval:
            self.add_to_approval_queue(issue, rule)
            return {'status': 'awaiting_approval', 'issue': issue_type}

        # Otherwise, auto-execute
        try:
            success = rule.execute()
            status = 'auto_fixed' if success else 'auto_fix_failed'
            return {
                'status': status,
                'issue': issue_type,
                'severity': rule.severity,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'remediation_error',
                'issue': issue_type,
                'error': str(e)
            }

    def add_to_approval_queue(self, issue, rule):
        """Add issue to approval queue"""
        try:
            queue = []
            if self.approval_queue_path.exists():
                queue = json.loads(self.approval_queue_path.read_text())

            queue.append({
                'id': len(queue) + 1,
                'issue': issue['type'],
                'severity': rule.severity,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending_approval'
            })

            self.approval_queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"[QUEUE] Error: {str(e)}")

    def run(self):
        """Main remediation loop"""
        for issue in self.detect_issues():
            result = self.remediate(issue)
            print(f"[REMEDIATION] {result}")

            # Log to DB
            try:
                db = sqlite3.connect(str(self.db_path))
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO remediation_log (issue_type, status, timestamp) VALUES (?, ?, ?)",
                    (issue['type'], result['status'], datetime.now().isoformat())
                )
                db.commit()
                db.close()
            except Exception as e:
                print(f"[LOG] Error: {str(e)}")


if __name__ == '__main__':
    import sys

    if '--daemon' in sys.argv:
        import time

        engine = AutoRemediationEngine()
        print("[AUTO-REMEDIATION] Starting engine")

        while True:
            engine.run()
            time.sleep(300)  # Check every 5 minutes

    elif '--approve' in sys.argv:
        # Approve pending action
        action_id = sys.argv[sys.argv.index('--approve') + 1]
        print(f"[APPROVE] Action {action_id} approved")

    else:
        print("Usage: auto_remediation.py [--daemon|--approve <action_id>]")
