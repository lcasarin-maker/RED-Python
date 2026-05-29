#!/usr/bin/env python3
"""
sync_binding.py v1.0 — CoderCerberus Protocol Synchronizer

Detecta cambios en archivos core del protocolo y notifica a Claude.
Mantiene checksum de versión para sincronización automática.

Usage:
  python scripts/sync_binding.py --check      # Detectar cambios
  python scripts/sync_binding.py --update     # Actualizar checksum
  python scripts/sync_binding.py --diff       # Mostrar diff detallado
"""

import json
import hashlib
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, Tuple

# Fix Windows UTF-8 encoding — siempre activo (subprocesos heredan PYTEST_CURRENT_TEST)
import os

# Bootstrap sys.path so scripts.core_utils is importable regardless of invocation method
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from scripts.core_utils import setup_windows_utf8
    setup_windows_utf8()
except ImportError:
    logging.debug("sync_binding: core_utils not on path; UTF-8 setup skipped (standalone mode)")

class ProtocolSyncManager:
    """Maneja sincronización bidireccional entre protocolo y agente."""

    PROTOCOL_FILES = {
        "AGENT.md",
        "PROTOCOL_SYSTEM.md",
        "PROTOCOL_BEHAVIOR.md",
        "SPEC.md",
        # .agent_state.json excluido: contiene los checksums mismos → circular dependency
    }

    def __init__(self, root_dir: Path = None):
        self.root = root_dir or Path.cwd()
        self.state_file = self.root / ".agent_state.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Cargar estado actual del agente."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, ValueError):
                return {"protocol_checksums": {}, "version": "0.02"}
        return {"protocol_checksums": {}, "version": "0.02"}

    def _save_state(self) -> None:
        """Guardar estado actualizado."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _compute_file_hash(self, filepath: Path) -> str:
        """Computar SHA256 de archivo."""
        if not filepath.exists():
            return "NOTFOUND"
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception as e:
            logging.warning("sync_binding: no se pudo leer %s: %s", filepath, e)
            return "UNREADABLE"

    def _get_current_hashes(self) -> Dict[str, str]:
        """Obtener checksums actuales de archivos core."""
        hashes = {}
        for fname in self.PROTOCOL_FILES:
            fpath = self.root / fname
            hashes[fname] = self._compute_file_hash(fpath)
        return hashes

    def check_changes(self) -> Tuple[bool, Set[str]]:
        """
        Detectar si hay cambios en protocolo.

        Returns:
            (has_changes: bool, changed_files: set)
        """
        current = self._get_current_hashes()
        stored = self.state.get("protocol_checksums", {})

        changed = set()
        for fname, current_hash in current.items():
            stored_hash = stored.get(fname, "NOTFOUND")
            if current_hash != stored_hash:
                changed.add(fname)

        return len(changed) > 0, changed

    def report_changes(self, changed_files: Set[str]) -> str:
        """Generar reporte legible de cambios."""
        if not changed_files:
            return "✅ Protocolo sin cambios (checksums coinciden)"

        report = ["⚠️  CAMBIOS DETECTADOS EN PROTOCOLO:\n"]
        for fname in sorted(changed_files):
            fpath = self.root / fname
            if fpath.exists():
                with open(fpath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                report.append(f"  📝 {fname} ({len(lines)} líneas)")
            else:
                report.append(f"  ❌ {fname} (NO ENCONTRADO)")

        report.append("\n🔄 ACCIÓN REQUERIDA:")
        report.append("  → Humano: Revisar cambios con: python scripts/sync_binding.py --diff")
        report.append("  → Humano: Aprobar e integrar: python scripts/sync_binding.py --sync")
        report.append("  → El --sync actualiza cerebro central y propaga a todos los proyectos.")

        return "\n".join(report)

    def update_checksums(self) -> None:
        """Actualizar checksums después de cambios validados.

        Escribe dos veces: la segunda corrige el hash de .agent_state.json
        que cambia al ser escrito en la primera pasada (anti-circular dependency).
        """
        current = self._get_current_hashes()
        self.state["protocol_checksums"] = current
        self.state["last_sync"] = datetime.now().isoformat()
        self._save_state()
        # .agent_state.json cambió al escribirse — recomputar su hash final
        self.state["protocol_checksums"][".agent_state.json"] = self._compute_file_hash(self.state_file)
        self._save_state()
        print("✅ Checksums actualizados en .agent_state.json")

    def show_diff(self) -> None:
        """Mostrar diff detallado de cambios (resumen)."""
        current = self._get_current_hashes()
        stored = self.state.get("protocol_checksums", {})

        print("📊 DIFF DE PROTOCOLO:\n")
        for fname in sorted(self.PROTOCOL_FILES):
            current_hash = current.get(fname, "NOTFOUND")
            stored_hash = stored.get(fname, "NOTFOUND")

            status = "✅ SIN CAMBIOS" if current_hash == stored_hash else "⚠️  MODIFICADO"
            print(f"{status:20} | {fname:30} | {current_hash}")

        print("\n💡 Para detalles línea-por-línea:")
        print("   git diff AGENT.md PROTOCOL_SYSTEM.md PROTOCOL_BEHAVIOR.md")

    def sync_and_propagate(self) -> int:
        """
        Integra cambios detectados al cerebro central y propaga a proyectos satélite.

        Flujo:
        1. Muestra qué archivos cambiaron (antes → después)
        2. Actualiza protocol_checksums en .agent_state.json
        3. Escribe entrada en HISTORIAL.md
        4. Llama a global_sync_safe.py --apply para propagar a todos los proyectos
        """
        import subprocess

        has_changes, changed = self.check_changes()

        # Paso 1: Mostrar diff
        self.show_diff()

        if not has_changes:
            print("\n✅ Sin cambios pendientes. Nada que sincronizar.")
            return 0

        # Paso 2: Actualizar checksums
        self.update_checksums()
        print(f"\n✅ Checksums actualizados ({len(changed)} archivo(s) integrados al cerebro).")

        # Paso 3: Registrar en HISTORIAL.md
        historial_path = self.root / "HISTORIAL.md"
        timestamp = datetime.now().isoformat(timespec="seconds")
        entry = (
            f"\n---\n"
            f"## SYNC [{timestamp}]\n"
            f"**Archivos integrados:** {', '.join(sorted(changed))}\n"
            f"**Acción:** sync_binding.py --sync — checksums actualizados, propagación iniciada.\n"
        )
        with open(historial_path, 'a', encoding='utf-8') as f:
            f.write(entry)
        print(f"✅ Entrada registrada en HISTORIAL.md")

        # Paso 4: Propagar a proyectos satélite
        print("\n🌍 Propagando a proyectos satélite...")
        sync_script = self.root / "scripts" / "global_sync_safe.py"
        if sync_script.exists():
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.root) + os.pathsep + env.get("PYTHONPATH", "")
            result = subprocess.run(
                [sys.executable, str(sync_script), "--apply"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore", env=env
            )
            if result.returncode == 0:
                print("✅ Propagación completada exitosamente.")
            else:
                print(f"⚠️  Propagación completada con advertencias:\n{result.stderr[:500]}")
        else:
            print("⚠️  global_sync_safe.py no encontrado. Propagación omitida.")

        print("\n🎯 SYNC COMPLETO — Alerta eliminada. Próximo --check retornará ✅.")
        return 0


def _sync_check(manager: "ProtocolSyncManager") -> int:
    has_changes, changed = manager.check_changes()
    print(manager.report_changes(changed))
    return 1 if has_changes else 0


def main():
    """CLI entrypoint."""
    manager = ProtocolSyncManager()
    cmd = sys.argv[1] if len(sys.argv) >= 2 else "--check"

    if cmd == "--check":
        return _sync_check(manager)

    dispatch = {
        "--update": lambda: (manager.update_checksums(), 0)[1],
        "--diff":   lambda: (manager.show_diff(), 0)[1],
        "--sync":   manager.sync_and_propagate,
    }
    if cmd in dispatch:
        return dispatch[cmd]()
    if cmd in ("--help", "-h"):
        print("Usage: sync_binding.py [--check|--update|--diff|--sync]")
        print("  --check   Detect protocol drift (exit 1 if drift, 0 if clean)")
        print("  --update  Update checksums in .agent_state.json")
        print("  --diff    Show line-by-line diff of changed protocol files")
        print("  --sync    Full sync: update checksums + propagate to satellites")
        return 0
    print("Usage: sync_binding.py [--check|--update|--diff|--sync]")
    return 1


if __name__ == "__main__":
    sys.exit(main())
