#!/usr/bin/env python3
"""Reminder de revision humana — lee review_queue.json y muestra notificacion Windows.
Diseñado para ejecutarse via Task Scheduler (ver setup_reminder_task.py).
"""
import subprocess
import sys
from pathlib import Path

# Importar review_queue desde el mismo directorio
sys.path.insert(0, str(Path(__file__).parent))
from manage_review_queue import list_pending


def _show_windows_toast(title: str, message: str) -> None:
    ps = f"""
Add-Type -AssemblyName System.Windows.Forms
$icon = [System.Windows.Forms.NotifyIcon]::new()
$icon.Icon = [System.Drawing.SystemIcons]::Warning
$icon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Warning
$icon.BalloonTipTitle = '{title}'
$icon.BalloonTipText = '{message}'
$icon.Visible = $true
$icon.ShowBalloonTip(8000)
Start-Sleep -Milliseconds 8500
$icon.Visible = $false
$icon.Dispose()
"""
    subprocess.run(
        ["powershell", "-NonInteractive", "-Command", ps],
        capture_output=True,
        timeout=15,
    )


def _append_historial(pending: list) -> None:
    historial = Path(__file__).parents[1] / "HISTORIAL.md"
    if not historial.exists():
        return
    from datetime import date

    lines = [f"\n## REVIEW REMINDER — {date.today().isoformat()}"]
    lines.append(f"Commits pendientes de verificacion humana ({len(pending)}):")
    for p in pending:
        files_str = ", ".join(p["files"][:3])
        suffix = f" +{len(p['files'])-3} mas" if len(p["files"]) > 3 else ""
        lines.append(f"- `{p['commit']}` ({p['timestamp'][:10]}) — {files_str}{suffix}")
    lines.append(
        "Para marcar verificado: `python scripts/manage_review_queue.py --ack <hash>`"
    )
    with open(historial, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    pending = list_pending()
    if not pending:
        print("[Reminder] Sin commits pendientes. Todo verificado.")
        return
    n = len(pending)
    msg = (
        f"Tienes {n} commit{'s' if n > 1 else ''} sin verificar en tests/ o scripts/. "
        "Ejecuta run_security_audit_12d.py y confirma que al menos 1 test falla sin el feature."
    )
    print(f"[Reminder] {msg}")
    _show_windows_toast("CoderCerberus — Revision Pendiente", msg)
    _append_historial(pending)


if __name__ == "__main__":
    main()
