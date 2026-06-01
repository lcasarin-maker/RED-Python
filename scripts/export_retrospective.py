#!/usr/bin/env python3
"""
export_retrospective.py v1.0 — FASE 8: Auto-export retrospectivas
Exports the latest HISTORIAL.md session to JSON and/or protocol_state.db.
DB path: env var CERBERUS_DB_PATH or .secrets/protocolo/protocol_state.db.
"""

import argparse
import json
import logging
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.core_utils import setup_windows_utf8

setup_windows_utf8()
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
_logger = logging.getLogger("auto_export_retrospective")

_DEFAULT_DB = ".secrets/protocolo/protocol_state.db"


class AutoExportRetrospective:
    """Auto-exports sessions from HISTORIAL.md to JSON and/or SQLite DB."""

    def __init__(self, db_path: str | None = None, historial_path: Path | None = None):
        raw_db = db_path or os.getenv("CERBERUS_DB_PATH", _DEFAULT_DB)
        self.db_path = Path(raw_db)
        self.historial_path = historial_path or Path("HISTORIAL.md")

    def setup_db(self) -> None:
        """Create retrospectives table if it does not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS retrospectives (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    learning_1 TEXT,
                    violation TEXT,
                    next_agent_knows TEXT,
                    protocol_gaps TEXT,
                    token_efficiency FLOAT,
                    export_status TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def extract_latest_session(self) -> dict | None:
        """Extract the most recent session block from HISTORIAL.md."""
        if not self.historial_path.exists():
            _logger.warning("extract_latest_session: %s not found", self.historial_path)
            return None
        content = self.historial_path.read_text(encoding="utf-8", errors="ignore")
        sessions = re.findall(r'## Ses[ií][oó]n.*?(?=## Ses[ií][oó]n|$)', content, re.DOTALL | re.IGNORECASE)
        if not sessions:
            return None
        return self._parse_session(sessions[-1])

    def _extract_retrospective_json(self, text: str) -> dict | None:
        """Extract and parse the first JSON object from retrospective text. Returns None on failure."""
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            return None
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError as e:
            _logger.debug("_extract_retrospective_json: JSON decode failed: %s", e)
            return None

    def _parse_session(self, session_text: str) -> dict:
        """Parse session text into a structured dict."""
        session: dict = {
            "session_id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "learning": None,
            "violation": None,
            "next_agent_knows": None,
            "protocol_gaps": None,
            "token_efficiency": None,
        }

        if re.search(r'RETROSPECT(?:IVE|IVA)', session_text, re.IGNORECASE):
            retro_match = re.search(
                r'(?:RETROSPECTIVE|RETROSPECTIVA).*?(?:```json)?(.*?)(?:```)?(?=^##|\Z)',
                session_text, re.DOTALL | re.MULTILINE | re.IGNORECASE,
            )
            if retro_match:
                data = self._extract_retrospective_json(retro_match.group(1))
                if data:
                    session.update({
                        "learning": data.get("learning", ""),
                        "violation": data.get("violation", ""),
                        "next_agent_knows": data.get("next_agent_knows", ""),
                        "protocol_gaps": data.get("protocol_gaps", ""),
                        "token_efficiency": data.get("token_efficiency", 0),
                    })
        return session

    def export_to_json(self, session: dict, output_dir: Path) -> str:
        """Export session dict to a timestamped JSON file."""
        output_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"session_{session['session_id'][:8]}_{ts}.json"
        filename.write_text(json.dumps(session, indent=2, ensure_ascii=False), encoding="utf-8")
        _logger.info("export_to_json: wrote %s", filename)
        self._prune_exports(output_dir)
        return str(filename)

    @staticmethod
    def _prune_exports(output_dir: Path, keep: int = 50) -> None:
        """Bounded retention: keep only the most recent N session exports so
        exports/ cannot grow without limit (and flood Drive sync)."""
        exports = sorted(output_dir.glob("session_*.json"))
        for stale in exports[:-keep]:
            try:
                stale.unlink()
            except OSError as e:
                _logger.warning("export prune failed for %s: %s", stale.name, e)

    def export_to_db(self, session: dict) -> None:
        """Insert session into retrospectives table."""
        self.setup_db()
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(
                """INSERT INTO retrospectives
                   (id, session_id, learning_1, violation, next_agent_knows,
                    protocol_gaps, token_efficiency, export_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid4()),
                    session["session_id"],
                    session.get("learning"),
                    session.get("violation"),
                    session.get("next_agent_knows"),
                    session.get("protocol_gaps"),
                    session.get("token_efficiency"),
                    "exported",
                ),
            )
            conn.commit()
            _logger.info("export_to_db: inserted session %s", session["session_id"][:8])
        finally:
            conn.close()

    def auto_export(
        self,
        export_json: bool = True,
        export_db: bool = True,
        output_dir: Path | None = None,
    ) -> dict:
        """Auto-export the latest session to configured targets.

        Returns a results dict with keys: session_id, exports (list).
        Returns {"status": "no_session_found"} when HISTORIAL.md has no sessions.
        """
        session = self.extract_latest_session()
        if not session:
            return {"status": "no_session_found"}

        out_dir = output_dir or Path("exports")
        results: dict = {"session_id": session["session_id"], "exports": []}

        if export_json:
            try:
                path = self.export_to_json(session, out_dir)
                results["exports"].append({"type": "json", "path": path})
            except Exception as e:
                _logger.error("auto_export: JSON export failed: %s", e)
                results["exports"].append({"type": "json", "error": str(e)})

        if export_db:
            try:
                self.export_to_db(session)
                results["exports"].append({"type": "db", "table": "retrospectives"})
            except Exception as e:
                _logger.error("auto_export: DB export failed: %s", e)
                results["exports"].append({"type": "db", "error": str(e)})

        return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-export session retrospectives")
    parser.add_argument("--auto", action="store_true", help="Export latest session")
    parser.add_argument("--json-only", action="store_true", help="Export to JSON only")
    parser.add_argument("--db-only", action="store_true", help="Export to DB only")
    parser.add_argument("--output-dir", type=Path, default=Path("exports"))
    args = parser.parse_args()

    exporter = AutoExportRetrospective()
    if args.auto:
        result = exporter.auto_export(
            export_json=not args.db_only,
            export_db=not args.json_only,
            output_dir=args.output_dir,
        )
        if result.get("status") == "no_session_found":
            _logger.warning("No session found in HISTORIAL.md")
            return 0
        exports = result.get("exports", [])
        ok = [e for e in exports if "error" not in e]
        err = [e for e in exports if "error" in e]
        _logger.info("auto_export: session %s exported to %d target(s)",
                     result.get("session_id", "?")[:8], len(ok))
        for e in err:
            _logger.error("[%s] %s", e["type"], e["error"])
        return 0

    _logger.info("Use --auto to export latest session")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
