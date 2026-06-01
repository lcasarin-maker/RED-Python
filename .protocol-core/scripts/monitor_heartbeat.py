#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HEARTBEAT MONITOR: Detecta si agentes están activos o bloqueados
- Escribe heartbeat events en BD
- Detecta timeout >5 min = ALERTA CRITICAL
- Analiza HISTORIAL.md para detectar deadlock
"""

import logging
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class HeartbeatMonitor:
    def __init__(self, heartbeat_dir=None):
        self.alerts = []
        self.projects = {
            # Core projects (active)
            "Protocolo Agentes": r"D:\GoogleDrive\AI\Protocolo Agentes",
            "Aequitas_OS": r"D:\GoogleDrive\AI\Aequitas_OS",
            "Agente_Inmobiliario": r"D:\GoogleDrive\AI\Agente_Inmobiliario",
            "Quenza": r"D:\GoogleDrive\AI\Quenza",
            "Declutter": r"D:\GoogleDrive\AI\Declutter",
            "RED-Python": r"D:\GoogleDrive\AI\RED-Python",

            # Active but with limited scope
            "Calculadora de sueldos": r"D:\GoogleDrive\AI\Calculadora de sueldos",
            "Amparo Pensiones": r"D:\GoogleDrive\AI\Amparo Pensiones",

            # Info/Data projects (monitoring but low priority)
            "Blog_Ciudadano_X": r"D:\GoogleDrive\AI\Blog_Ciudadano_X",
            "Imagen_Corporativa_Aequitas": r"D:\GoogleDrive\AI\Imagen_Corporativa_Aequitas",
            "Maletin Homeopatia": r"D:\GoogleDrive\AI\Maletin Homeopatia",
            "Sistemas_Estocasticos_Ruleta": r"D:\GoogleDrive\AI\Sistemas_Estocasticos_Ruleta",
        }
        # Allow custom heartbeat directory for testing; default to protocol location
        if heartbeat_dir is None:
            self.heartbeat_dir = Path(r"D:\GoogleDrive\AI\.secrets\protocolo\heartbeats")
        else:
            self.heartbeat_dir = Path(heartbeat_dir)
        self.heartbeat_dir.mkdir(parents=True, exist_ok=True)

    def ping_project(self, project_name, project_path):
        """Registra un heartbeat para un proyecto."""
        heartbeat_file = self.heartbeat_dir / f"{project_name}_heartbeat.json"
        
        # Leer último heartbeat si existe
        last_heartbeat = None
        if heartbeat_file.exists():
            try:
                with open(heartbeat_file, 'r', encoding='utf-8') as f:
                    last_heartbeat = json.load(f)
            except Exception as e:
                logging.error(f"Error reading {heartbeat_file}: {e}")

        # Verificar si hay cambios en HISTORIAL.md
        historial_path = Path(project_path) / "HISTORIAL.md"
        historial_modified = None
        if historial_path.exists():
            historial_modified = historial_path.stat().st_mtime

        # Nuevo heartbeat
        now = datetime.now().isoformat()
        heartbeat = {
            "timestamp": now,
            "project": project_name,
            "status": "alive",
            "historial_modified": historial_modified,
            "historial_last_seen": last_heartbeat.get("historial_modified") if last_heartbeat else None,
        }

        # Detectar deadlock: sin cambios en >10 min
        if last_heartbeat and historial_modified:
            last_time = last_heartbeat.get("timestamp")
            if last_time:
                last_dt = datetime.fromisoformat(last_time)
                now_dt = datetime.fromisoformat(now)
                delta = (now_dt - last_dt).total_seconds() / 60  # minutos
                
                if delta > 10 and historial_modified == last_heartbeat.get("historial_modified"):
                    heartbeat["status"] = "blocked"
                    self.alerts.append({
                        "project": project_name,
                        "type": "DEADLOCK",
                        "severity": "HIGH",
                        "message": f"Sin cambios en {int(delta)} min — posible bloqueo",
                        "timestamp": now,
                    })

        # Guardar heartbeat
        with open(heartbeat_file, 'w', encoding='utf-8') as f:
            json.dump(heartbeat, f, indent=2, ensure_ascii=False)

        status = f"[OK] {heartbeat['status'].upper()}"
        print(f"  {status} {project_name}")

        return heartbeat

    def run(self):
        """Escanea todos los proyectos."""
        print("=" * 70)
        print("[BEAT] HEARTBEAT MONITOR — Verificando salud de agentes")
        print("=" * 70)

        for project_name, project_path in self.projects.items():
            if Path(project_path).exists():
                try:
                    self.ping_project(project_name, project_path)
                except Exception as e:
                    print(f"  [FAIL] {project_name} - Error processing: {e}")
            else:
                print(f"  [FAIL] {project_name} (path no existe)")

        # Guardar alertas
        if self.alerts:
            alerts_file = self.heartbeat_dir / "alerts.json"
            with open(alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, indent=2, ensure_ascii=False)
            print(f"\n[WARN]  {len(self.alerts)} ALERTAS DETECTADAS:")
            for alert in self.alerts:
                print(f"   • [{alert['severity']}] {alert['project']}: {alert['message']}")
        else:
            print("\n[OK] Todos los proyectos: HEALTHY")

        return 0 if not self.alerts else 1


def main():
    parser = argparse.ArgumentParser(description="Run the Cerberus heartbeat monitor.")
    parser.parse_args()
    monitor = HeartbeatMonitor()
    sys.exit(monitor.run())

if __name__ == "__main__":
    main()
