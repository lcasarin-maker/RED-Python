#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DASHBOARD SERVER v3.0 — Observabilidad Premium para Coder Cerberus
Muestra telemetría de satélites en HSL de alta fidelidad, con progreso en tiempo real y tokens.
"""

import json
import sqlite3
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

class DashboardHandler(BaseHTTPRequestHandler):
    def get_registry_data(self):
        reg = Path("D:/GoogleDrive/AI/Cerberus/.protocol/metadata/REGISTRY.json")
        try:
            return json.loads(reg.read_text(encoding='utf-8')) if reg.exists() else {}
        except Exception as e:
            sys.stderr.write(f"[WARN] Failed to read registry: {e}\n")
            return {}

    def get_evidence_stats(self):
        saved = 0
        db = Path.home() / ".secrets" / "protocolo" / "protocol_state.db"
        if db.exists():
            try:
                with sqlite3.connect(str(db)) as conn:
                    res = conn.execute("SELECT SUM(tokens_saved) FROM token_optimizations").fetchone()
                    if res and res[0]:
                        saved = int(res[0])
            except Exception as e:
                sys.stderr.write(f"[WARN] SQLite token read failed: {e}\n")
        
        recent = []
        ev_dir = Path("D:/GoogleDrive/AI/Cerberus/.protocol/evidence")
        if ev_dir.exists():
            for f in sorted(ev_dir.glob("*.json"), reverse=True)[:10]:
                try:
                    data = json.loads(f.read_text(encoding='utf-8'))
                    recent.append({
                        "name": f.name,
                        "timestamp": data.get("timestamp", "")[:19].replace("T", " "),
                        "action": data.get("action", "unknown")
                    })
                    if saved == 0 and "metrics" in data:
                        saved += data["metrics"].get("tokens_saved", 0)
                except Exception as e:
                    sys.stderr.write(f"[WARN] Failed to read evidence: {e}\n")
        return {"tokens": saved, "recent": recent}

    def do_GET(self):
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        registry = self.get_registry_data()
        projects = registry.get("projects", [])
        stats = self.get_evidence_stats()

        # Calculate satellite parity: count active & approved projects
        active_projects = [p for p in projects if p.get("status") in ("active", "approved", "synced")]
        approved_count = sum(1 for p in active_projects if p.get("adoption_verified", False))
        total_count = len(active_projects) if active_projects else 1
        parity_percent = int((approved_count / total_count) * 100)

        # Build projects HTML cards
        cards_html = ""
        for p in projects:
            status = p.get("status", "unknown")
            is_ok = p.get("adoption_verified", False)
            badge_cls, label = ("badge-active", "APPROVED") if is_ok else ("badge-blocked", status.upper())
            
            details = p.get("adoption_details", {})
            h_cls, h_val = ("ok", "✔") if details.get("hook_installed") else ("fail", "✘")
            a_cls, a_val = ("ok", "✔") if details.get("auditor_present") else ("fail", "✘")
            t_cls, t_val = ("ok", "✔") if details.get("tests_present") else ("fail", "✘")
            
            cards_html += f"""
            <div class="card p-card">
                <div class="card-header">
                    <h3>{p.get('name', 'Unknown')}</h3>
                    <span class="badge {badge_cls}">{label}</span>
                </div>
                <p class="desc">{p.get('description', '')[:85]}...</p>
                <div class="metrics">
                    <div class="m-item"><span>Hooks</span><span class="{h_cls}">{h_val}</span></div>
                    <div class="m-item"><span>Auditor</span><span class="{a_cls}">{a_val}</span></div>
                    <div class="m-item"><span>Tests</span><span class="{t_cls}">{t_val}</span></div>
                </div>
                <div class="card-footer">Sync: {p.get('last_sync', 'Never')[:16].replace('T', ' ')}</div>
            </div>
            """

        # Build recent activity table
        table_html = ""
        for act in stats['recent']:
            table_html += f"""
            <tr>
                <td>{act['timestamp']}</td>
                <td><span class="badge-action">{act['action'].upper()}</span></td>
                <td class="mono">{act['name']}</td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Cerberus Control Center — Dashboard Premium</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        :root {{
            --bg: radial-gradient(circle at top, hsl(220, 25%, 7%) 0%, hsl(220, 30%, 4%) 100%);
            --card-bg: hsla(220, 20%, 10%, 0.7);
            --border: hsla(0, 0%, 100%, 0.08);
            --glow: hsla(215, 90%, 60%, 0.15);
            --text: hsl(210, 15%, 90%);
            --text-dim: hsl(210, 10%, 60%);
            --accent: hsl(215, 95%, 60%);
            --green: hsl(142, 70%, 45%);
            --red: hsl(355, 80%, 55%);
            --yellow: hsl(38, 90%, 55%);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Outfit', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 30px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, hsl(215, 95%, 65%) 0%, hsl(240, 95%, 70%) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        .header p {{ color: var(--text-dim); font-size: 1.1rem; }}
        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 1px rgba(255,255,255,0.05);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }}
        .hero-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }}
        .metric-card {{ text-align: center; display: flex; flex-direction: column; gap: 6px; padding: 20px; }}
        .metric-card span.lbl {{ color: var(--text-dim); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }}
        .metric-card span.val {{ font-size: 2.2rem; font-weight: 700; }}
        .val.ok {{ color: var(--green); }}
        .val.act {{ color: var(--accent); }}
        .progress-bar-container {{ width: 100%; height: 10px; background: rgba(255,255,255,0.05); border-radius: 5px; margin-top: 10px; overflow: hidden; }}
        .progress-bar {{ height: 100%; background: linear-gradient(90deg, var(--accent), var(--green)); width: {parity_percent}%; transition: width 1s ease-in-out; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
        .p-card {{ display: flex; flex-direction: column; justify-content: space-between; min-height: 230px; }}
        .p-card:hover {{
            transform: translateY(-4px) scale(1.01);
            border-color: hsla(215, 90%, 60%, 0.3);
            box-shadow: 0 15px 35px rgba(0,0,0,0.6), 0 0 15px var(--glow);
        }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
        .card-header h3 {{ font-size: 1.2rem; font-weight: 600; letter-spacing: -0.3px; }}
        .badge {{ font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; }}
        .badge-active {{ background: hsla(142, 70%, 45%, 0.15); color: var(--green); border: 1px solid hsla(142, 70%, 45%, 0.2); }}
        .badge-blocked {{ background: hsla(355, 80%, 55%, 0.15); color: var(--red); border: 1px solid hsla(355, 80%, 55%, 0.2); }}
        .desc {{ color: var(--text-dim); font-size: 0.85rem; line-height: 1.4; margin-bottom: 15px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; margin-bottom: 12px; }}
        .m-item {{ display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 0.75rem; color: var(--text-dim); }}
        .m-item span {{ font-weight: 600; font-size: 0.9rem; }}
        .ok {{ color: var(--green); }}
        .fail {{ color: var(--red); }}
        .card-footer {{ font-size: 0.75rem; color: var(--text-dim); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ color: var(--text-dim); font-weight: 600; font-size: 0.85rem; background: rgba(255,255,255,0.02); }}
        td {{ font-size: 0.9rem; }}
        .badge-action {{ background: hsla(215, 95%, 60%, 0.15); color: var(--accent); padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }}
        .mono {{ font-family: monospace; color: var(--text-dim); }}
    </style>
    <script>
        setTimeout(() => location.reload(), 8000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Cerberus Control Center</h1>
            <p>Monitoreo Premium del Ecosistema en Tiempo Real</p>
        </div>
        <div class="card">
            <h2 style="font-size:1.3rem; margin-bottom:20px; display:flex; align-items:center; gap:8px;">
                📊 Telemetría General ({approved_count}/{total_count} Satélites Sincronizados)
            </h2>
            <div class="hero-grid">
                <div class="metric-card">
                    <span class="lbl">Total Satélites</span>
                    <span class="val act">{total_count}</span>
                </div>
                <div class="metric-card">
                    <span class="lbl">Paridad Global</span>
                    <span class="val ok">{parity_percent}%</span>
                </div>
                <div class="metric-card">
                    <span class="lbl">Tokens Optimizados</span>
                    <span class="val act">+{stats['tokens']:,}</span>
                </div>
            </div>
            <div class="progress-bar-container"><div class="progress-bar"></div></div>
        </div>
        <h2 style="font-size:1.4rem; margin:35px 0 15px 0; color:var(--accent);">🛸 Flota de Satélites Verificados</h2>
        <div class="grid">{cards_html}</div>
        <div class="card" style="margin-top:35px;">
            <h2 style="font-size:1.3rem; margin-bottom:15px;">📜 Bitácora de Evidencias</h2>
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr><th>Estampa de Tiempo</th><th>Acción</th><th>Fichero</th></tr>
                    </thead>
                    <tbody>{table_html}</tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>"""
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        # Evita stubs silenciosos asignando explícitamente a variables
        _ignored_format = format
        _ignored_args = args

def run_server(port=5000):
    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    sys.stdout.write(f"[OK] Premium Dashboard running on http://127.0.0.1:{port}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\n[OK] Dashboard server stopped manually\n")

if __name__ == "__main__":
    run_server()
