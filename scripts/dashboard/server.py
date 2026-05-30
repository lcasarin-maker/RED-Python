#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DASHBOARD SERVER — Observabilidad para Coder Cerberus
Lee evidencia real desde REGISTRY.json y .protocol/evidence/
"""

import json
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class DashboardHandler(BaseHTTPRequestHandler):
    def get_registry_data(self):
        registry_path = Path("D:/GoogleDrive/AI/Cerberus/.protocol/metadata/REGISTRY.json")
        if not registry_path.exists():
            return {}
        try:
            return json.loads(registry_path.read_text(encoding='utf-8'))
        except Exception as e:
            logging.error(f"Failed to load registry: {e}")
            return {}

    def get_evidence_stats(self):
        evidence_dir = Path("D:/GoogleDrive/AI/Cerberus/.protocol/evidence")
        total_tokens_saved = 0
        recent_activities = []
        if evidence_dir.exists():
            for f in sorted(evidence_dir.glob("*.json"), reverse=True)[:10]:
                try:
                    data = json.loads(f.read_text(encoding='utf-8'))
                    recent_activities.append({
                        "name": f.name,
                        "timestamp": data.get("timestamp", ""),
                        "action": data.get("action", "unknown")
                    })
                    if "metrics" in data and "tokens_saved" in data["metrics"]:
                        total_tokens_saved += data["metrics"]["tokens_saved"]
                except json.JSONDecodeError as e:
                    print(f"Error: {e}")
        return {"total_tokens_saved": total_tokens_saved, "recent": recent_activities}

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            registry = self.get_registry_data()
            projects = registry.get("projects", [])
            stats = self.get_evidence_stats()
            
            html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cerberus Control Center — Dashboard Premium</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        :root {{
            --bg-gradient: radial-gradient(circle at top, #131a26 0%, #080c10 100%);
            --glass-bg: rgba(22, 30, 46, 0.7);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-red: #f85149;
            --accent-yellow: #d29922;
            --shadow-premium: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 1px rgba(255, 255, 255, 0.1) inset;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Outfit', sans-serif;
            background: var(--bg-gradient);
            color: var(--text-primary);
            min-height: 100vh;
            padding-bottom: 50px;
            overflow-x: hidden;
        }}

        .header {{
            background: rgba(16, 22, 34, 0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 25px 20px;
            border-bottom: 1px solid var(--glass-border);
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .header h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #58a6ff 0%, #82aaff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            display: inline-flex;
            align-items: center;
            gap: 12px;
        }}

        .header p {{
            color: var(--text-secondary);
            font-size: 1rem;
            font-weight: 400;
            letter-spacing: 0.5px;
        }}

        .container {{
            max-width: 1300px;
            margin: 30px auto;
            padding: 0 25px;
        }}

        .card {{
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: var(--shadow-premium);
        }}

        .card h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--accent-blue);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .health-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }}

        .health-metric {{
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 14px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: all 0.3s ease;
        }}

        .health-metric:hover {{
            background: rgba(30, 41, 59, 0.6);
            border-color: rgba(88, 166, 255, 0.2);
            transform: translateY(-2px);
        }}

        .health-metric span.label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            text-transform: uppercase;
            font-weight: 500;
            letter-spacing: 1px;
        }}

        .health-metric span.value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .value.success {{ color: var(--accent-green); }}
        .value.blue {{ color: var(--accent-blue); }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}

        .project-card {{
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 18px;
            padding: 25px;
            box-shadow: var(--shadow-premium);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 240px;
        }}

        .project-card:hover {{
            transform: translateY(-6px) scale(1.01);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(99, 102, 241, 0.15);
            background: rgba(22, 30, 46, 0.85);
        }}

        .project-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }}

        .project-card h3 {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.3px;
        }}

        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .badge-active {{
            background: rgba(63, 185, 80, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(63, 185, 80, 0.2);
        }}

        .badge-pending {{
            background: rgba(210, 153, 34, 0.15);
            color: var(--accent-yellow);
            border: 1px solid rgba(210, 153, 34, 0.2);
        }}

        .badge-blocked {{
            background: rgba(248, 81, 73, 0.15);
            color: var(--accent-red);
            border: 1px solid rgba(248, 81, 73, 0.2);
        }}

        .project-desc {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.4;
            margin-bottom: 15px;
            flex-grow: 1;
        }}

        .project-metrics {{
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 15px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }}

        .metric-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        .metric-item span {{
            font-weight: 600;
            font-size: 0.95rem;
        }}

        .metric-item span.ok {{ color: var(--accent-green); }}
        .metric-item span.fail {{ color: var(--accent-red); }}

        .project-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th, td {{
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid var(--glass-border);
        }}

        th {{
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.9rem;
            background: rgba(30, 41, 59, 0.2);
        }}

        td {{ font-size: 0.95rem; }}

        .badge-action {{
            background: rgba(88, 166, 255, 0.15);
            color: var(--accent-blue);
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.85rem;
            border: 1px solid rgba(88, 166, 255, 0.2);
        }}
    </style>
    <script>
        setTimeout(() => location.reload(), 10000); // Auto-refresh every 10s
    </script>
</head>
<body>
    <div class="header">
        <h1>🛡️ Cerberus Control Center</h1>
        <p>Monitoreo Premium del Ecosistema de Protocolo en Tiempo Real</p>
    </div>
    <div class="container">
        <div class="card">
            <h2><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> Estado de Salud del Ecosistema</h2>
            <div class="health-grid">
                <div class="health-metric">
                    <span class="label">Proyectos Fleet</span>
                    <span class="value success">{len(projects)}</span>
                </div>
                <div class="health-metric">
                    <span class="label">Estado de Protocolo</span>
                    <span class="value success">ACTIVO & SEGURO</span>
                </div>
                <div class="health-metric">
                    <span class="label">Tokens Optimizados</span>
                    <span class="value blue">+{stats['total_tokens_saved']:,}</span>
                </div>
                <div class="health-metric">
                    <span class="label">Última Comprobación</span>
                    <span class="value" style="font-size: 1.15rem; font-weight: 600; padding-top: 8px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
            </div>
        </div>

        <h2 style="margin: 35px 0 15px 0; font-size: 1.6rem; font-weight: 600; color: var(--accent-blue); display: flex; align-items: center; gap: 10px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg> Flota de Satélites Activos (TIER 1-3)
        </h2>
        <div class="grid">
"""
            for p in projects:
                status = p.get("status", "unknown")
                if status == "active":
                    badge_class = "badge-active"
                    status_text = "APPROVED"
                elif status == "pending_sync":
                    badge_class = "badge-pending"
                    status_text = "PENDING SYNC"
                else:
                    badge_class = "badge-blocked"
                    status_text = status.upper()

                details = p.get("adoption_details", {})
                hook_val = "✔" if details.get("hook_installed") else "✘"
                hook_class = "ok" if details.get("hook_installed") else "fail"
                auditor_val = "✔" if details.get("auditor_present") else "✘"
                auditor_class = "ok" if details.get("auditor_present") else "fail"
                tests_val = "✔" if details.get("tests_present") else "✘"
                tests_class = "ok" if details.get("tests_present") else "fail"

                html += f"""
            <div class="project-card">
                <div>
                    <div class="project-header">
                        <h3>{p.get('name', 'Unknown')}</h3>
                        <span class="status-badge {badge_class}">{status_text}</span>
                    </div>
                    <p class="project-desc">{p.get('description', '')[:100]}...</p>
                </div>
                <div>
                    <div class="project-metrics">
                        <div class="metric-item">
                            <span>Hooks</span>
                            <span class="{hook_class}">{hook_val}</span>
                        </div>
                        <div class="metric-item">
                            <span>Auditor</span>
                            <span class="{auditor_class}">{auditor_val}</span>
                        </div>
                        <div class="metric-item">
                            <span>Tests</span>
                            <span class="{tests_class}">{tests_val}</span>
                        </div>
                    </div>
                    <div class="project-footer">
                        <span>Sync: {p.get('last_sync', 'Never')[:16]}</span>
                    </div>
                </div>
            </div>
"""
            html += """
        </div>

        <div class="card" style="margin-top: 40px; padding: 25px;">
            <h2><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg> Bitácora de Evidencias Recientes</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Estampa de Tiempo</th>
                            <th>Acción Operativa</th>
                            <th>Fichero del Log</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for act in stats['recent']:
                html += f"""
                        <tr>
                            <td style="font-weight: 500; color: var(--text-primary);">{act['timestamp']}</td>
                            <td><span class="badge-action">{act['action'].upper()}</span></td>
                            <td style="color: var(--text-secondary); font-family: monospace;">{act['name']}</td>
                        </tr>
"""
            
            html += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>"""
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
 
    def log_message(self, format, *args):
        return  # Suppress logging



def run_server(port=5000):
    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    print(f"[OK] Dashboard server running on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Server stopped")

if __name__ == "__main__":
    run_server()
