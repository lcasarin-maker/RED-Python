#!/usr/bin/env python3
"""Configura Task Scheduler de Windows para ejecutar review_reminder.py diariamente.
Ejecutar UNA SOLA VEZ: python scripts/setup_reminder_task.py
Requiere Python en PATH. No requiere privilegios de administrador.
"""
import subprocess
import sys
from pathlib import Path

TASK_NAME = "CoderCerberusReviewReminder"
PYTHON = sys.executable
SCRIPT = str(Path(__file__).parent / "review_reminder.py")
START_TIME = "09:00"  # 9am diario


def task_exists() -> bool:
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME],
        capture_output=True, text=True
    )
    return result.returncode == 0


def create_task() -> None:
    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{PYTHON}" "{SCRIPT}"',
        "/SC", "DAILY",
        "/ST", START_TIME,
        "/F",  # sobrescribir si ya existe
        "/RL", "LIMITED",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[Setup] Tarea '{TASK_NAME}' creada — se ejecutara diariamente a las {START_TIME}.")
    else:
        print(f"[Setup] Error creando tarea: {result.stderr.strip()}")
        print("[Setup] Alternativa: ejecutar manualmente 'python scripts/review_reminder.py'")


def delete_task() -> None:
    subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"], check=True)
    print(f"[Setup] Tarea '{TASK_NAME}' eliminada.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "--create"
    if action == "--delete":
        delete_task()
    elif action == "--status":
        status = "EXISTE" if task_exists() else "NO EXISTE"
        print(f"[Setup] Tarea '{TASK_NAME}': {status}")
    else:
        if task_exists():
            print(f"[Setup] Tarea '{TASK_NAME}' ya existe. Usa --delete para eliminar.")
        else:
            create_task()
