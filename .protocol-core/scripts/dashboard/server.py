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
<html>
<head>
    <title>Coder Cerberus V0.1 — Control Center</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #0d1117; color: #c9d1d9; }}
        .header {{ background: #161b22; padding: 20px; border-bottom: 1px solid #30363d; text-align: center; }}
        .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
        h1, h2 {{ color: #58a6ff; font-weight: 400; }}
        .card {{ background: #161b22; padding: 20px; margin: 15px 0; border-radius: 6px; border: 1px solid #30363d; }}
        .status-green {{ color: #3fb950; font-weight: bold; }}
        .status-yellow {{ color: #d29922; font-weight: bold; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; }}
        .project-card {{ border-left: 4px solid #238636; padding: 15px; background: #21262d; border-radius: 4px; }}
        .metric {{ margin: 10px 0; font-size: 1.1em; }}
        .metric strong {{ color: #8b949e; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #30363d; }}
        th {{ color: #8b949e; font-weight: normal; }}
    </style>
    <script>
        setTimeout(() => location.reload(), 10000); // Auto-refresh every 10s
    </script>
</head>
<body>
    <div class="header">
        <h1>🛡️ Cerberus Control Center</h1>
        <p>Real-time AI Protocol Ecosystem Monitoring</p>
    </div>
    <div class="container">
        <div class="card">
            <h2>Ecosystem Health</h2>
            <div class="grid">
                <div class="metric"><strong>Monitored Projects:</strong> <span class="status-green">{len(projects)}</span></div>
                <div class="metric"><strong>Protocol Status:</strong> <span class="status-green">ACTIVE & ENFORCED</span></div>
                <div class="metric"><strong>Total Tokens Optimized:</strong> <span class="status-green">+{stats['total_tokens_saved']:,}</span></div>
                <div class="metric"><strong>Last Check:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
        </div>

        <h2>Project Fleet (TIER 1-3)</h2>
        <div class="grid">
"""
            for p in projects:
                status_color = "#3fb950" if p.get("status") == "active" else "#d29922"
                html += f"""
            <div class="project-card" style="border-color: {status_color};">
                <h3 style="margin-top:0; color: #c9d1d9;">{p.get('name', 'Unknown')}</h3>
                <p><span style="color:{status_color}">●</span> {p.get('status', 'unknown').upper()}</p>
                <p style="font-size: 0.9em; color: #8b949e;">{p.get('description', '')[:60]}...</p>
                <p style="font-size: 0.8em; color: #8b949e;">Last Sync: {p.get('last_sync', 'Never')}</p>
            </div>
"""
            html += """
        </div>

        <div class="card" style="margin-top: 30px;">
            <h2>Recent Evidence Logs</h2>
            <table>
                <tr><th>Timestamp</th><th>Action</th><th>File</th></tr>
"""
            for act in stats['recent']:
                html += f"<tr><td>{act['timestamp']}</td><td><span class='status-green'>{act['action']}</span></td><td style='color: #8b949e;'>{act['name']}</td></tr>\n"
            
            html += """
            </table>
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
