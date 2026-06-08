#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cerberus Remediation Engine
- Runs deterministic fixes (formatting, sync_binding, hygiene cleanup).
- Queues non-deterministic failures (broken tests, missing specs/agents) in remediation_queue.json.
- Delivers desktop notifications using Wscript.Shell via PowerShell.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Paths
CORE_DIR = Path(__file__).resolve().parents[1]
QUEUE_PATH = CORE_DIR / ".protocol" / "remediation_queue.json"

def send_desktop_notification(title, message, timeout=5):
    """Sends a non-blocking Windows desktop notification using Wscript.Shell via PowerShell."""
    try:
        msg_clean = message.replace('"', "'").replace("\n", " ")
        title_clean = title.replace('"', "'")
        
        cmd = f'$wsh = New-Object -ComObject Wscript.Shell; $wsh.Popup("{msg_clean}", {timeout}, "{title_clean}", 64)'
        
        subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            timeout=timeout + 2
        )
    except Exception as e:
        logging.error(f"Failed to send desktop notification: {e}")

def load_remediation_queue():
    """Loads the current remediation queue from disk."""
    if not QUEUE_PATH.exists():
        return []
    try:
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error reading remediation queue: {e}")
        return []

def save_remediation_queue(queue):
    """Saves the remediation queue to disk."""
    try:
        QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving remediation queue: {e}")

def queue_issue(project_name, project_path, check_name, symptom):
    """Queues a non-deterministic issue for LLM agent resolution."""
    queue = load_remediation_queue()
    
    for item in queue:
        if (item.get("project_name") == project_name and 
            item.get("check_name") == check_name and 
            item.get("file_path") == str(project_path)):
            item["timestamp"] = datetime.now().isoformat()
            item["symptom"] = symptom
            save_remediation_queue(queue)
            return

    new_item = {
        "project_name": project_name,
        "file_path": str(project_path),
        "check_name": check_name,
        "symptom": symptom,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    queue.append(new_item)
    save_remediation_queue(queue)
    logging.info(f"Queued issue: {project_name} -> {check_name}")

def _fix_formatting(path, project_name):
    """Runs ruff format and check fixes on target path."""
    logging.info(f"Auto-fixing formatting/lint on {project_name}...")
    try:
        subprocess.run(["ruff", "check", "--fix", "."], cwd=path, capture_output=True, timeout=10)
        subprocess.run(["ruff", "format", "."], cwd=path, capture_output=True, timeout=10)
        logging.info(f"Successfully fixed formatting on {project_name}.")
        return True
    except Exception as e:
        logging.error(f"Failed to run formatting fixes on {project_name}: {e}")
        return False

def _fix_git_clean(path, project_name):
    """Runs hygiene cleanups on target path."""
    logging.info(f"Running hygiene cleanup on {project_name}...")
    try:
        cli_script = path / "scripts" / "protocol_cli.py"
        if cli_script.exists():
            subprocess.run([sys.executable, str(cli_script), "hygiene", "--fix"], cwd=path, capture_output=True, timeout=15)
        else:
            for p in path.rglob("__pycache__"):
                for f in p.glob("*"):
                    f.unlink()
                p.rmdir()
        logging.info(f"Successfully cleaned workspace for {project_name}.")
        return True
    except Exception as e:
        logging.error(f"Failed to clean hygiene on {project_name}: {e}")
        return False

def _fix_sync_drift(path, project_name):
    """Resynchronizes bindings on target path."""
    logging.info(f"Running sync_binding on {project_name}...")
    try:
        sync_script = path / "scripts" / "sync_binding.py"
        if sync_script.exists():
            subprocess.run([sys.executable, str(sync_script), "--sync"], cwd=path, capture_output=True, timeout=15)
            logging.info(f"Successfully resynced bindings on {project_name}.")
            return True
    except Exception as e:
        logging.error(f"Failed to resync bindings on {project_name}: {e}")
    return False

def auto_fix_project(project_name, project_path, failed_checks):
    """
    Attempts to fix deterministic failures for a given project.
    Returns: (fixed_checks, remaining_checks)
    """
    path = Path(project_path)
    if not path.exists():
        return [], failed_checks

    fixed = []
    remaining = []

    for check in failed_checks:
        if check in ["clean_code", "formatting"] and _fix_formatting(path, project_name):
            fixed.append(check)
            continue
        if check == "git_clean" and _fix_git_clean(path, project_name):
            fixed.append(check)
            continue
        if check in ["sync_drift", "drift"] and _fix_sync_drift(path, project_name):
            fixed.append(check)
            continue
            
        remaining.append(check)

    return fixed, remaining
