"""Core module for RED-Python handling scanning and cleaning of directories."""
import os
import stat
import threading
import time
import logging
from datetime import datetime
from dataclasses import dataclass

from filters import (
    long_path,
    strip_long_prefix,
    is_protected,
    is_dir_ignored,
    is_never_empty,
    has_only_ignorable_files,
    collect_ignorable_files,
    get_age_hours,
)

_islink = os.path.islink

# S9: Logging Mandatorio - configure logger for RED-Python
logger = logging.getLogger("red_python")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


@dataclass
class ScanResult:
    path: str
    status: str = "empty"  # empty | protected | error
    depth: int = 0
    selected: bool = True
    freed_bytes: int = 0


class Scanner:
    """
    Scans one or more root directories for empty / effectively-empty folders.
    Runs in a daemon thread; communicates via callbacks.

    Algorithm (bottom-up, from limpiador.py — improved):
      Walk topdown=False. A directory is "would-be-empty" when:
        1. All its files are ignorable (filter rules / 0-byte / hidden).
        2. All its subdirectories are already in the would_be_empty set.
        3. It does NOT match a 'never_empty' rule.
      This correctly propagates emptiness up chains of nested dirs.
    """

    def __init__(
        self, settings, on_found=None, on_log=None, on_done=None, on_progress=None
    ):
        self.settings = settings
        self.on_found = on_found or (lambda r: None)
        self.on_log = on_log or (lambda m: None)
        self.on_done = on_done or (lambda n: None)
        self.on_progress = on_progress or (lambda p: None)
        self._stop = threading.Event()
        self._thread = None

    def scan(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, args=(paths,), daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    # ------------------------------------------------------------------
    def _run(self, paths):
        total = 0
        for root in paths:
            if self._stop.is_set():
                break
            total += self._scan_root(root)
        self.on_log(
            f"[{_ts()}] Escaneo finalizado — {total} carpetas vacías encontradas."
        )
        self.on_done(total)

    def _scan_root(self, root):
        root = os.path.abspath(root)
        lroot = long_path(root)
        would_be_empty = set()  # normcase paths confirmed empty
        count = 0

        filter_rules = self.settings.get("filter_rules", [])
        max_depth = self.settings.get("max_depth", 0)
        min_age = self.settings.get("min_age_hours", 0)
        follow = self.settings.get("follow_symlinks", False)

        self.on_log(f"[{_ts()}] Iniciando escaneo: {root}")

        try:
            for lraiz, carpetas, _ in os.walk(lroot, topdown=False, followlinks=follow):
                if self._stop.is_set():
                    break

                raiz = strip_long_prefix(lraiz)

                # Skip the root itself
                if os.path.normcase(raiz) == os.path.normcase(root):
                    continue

                self.on_progress(raiz)

                # Depth
                try:
                    depth = len(os.path.relpath(raiz, root).split(os.sep))
                except ValueError:
                    depth = 0
                if max_depth > 0 and depth > max_depth:
                    continue

                # Symlink guard
                if not follow and _islink(raiz):
                    continue

                # All subdirs must be in would_be_empty for this dir to qualify
                if not all(
                    os.path.normcase(os.path.join(raiz, c)) in would_be_empty
                    for c in carpetas
                ):
                    continue

                # Files check
                if not has_only_ignorable_files(lraiz, self.settings):
                    continue

                # Age filter
                if min_age > 0 and get_age_hours(lraiz) < min_age:
                    continue

                dirname = os.path.basename(raiz)

                # ignore_dir rule → skip entirely (don't mark would_be_empty either,
                # so its parent won't see it as removable)
                if is_dir_ignored(dirname, raiz, filter_rules):
                    continue

                # Protected?
                if is_protected(raiz, self.settings.get("protected_dirs", [])):
                    would_be_empty.add(os.path.normcase(raiz))
                    result = ScanResult(raiz, "protected", depth)
                    result.selected = False
                    self.on_found(result)
                    self.on_log(f"[{_ts()}] Protegida: {raiz}")
                    continue

                # never_empty rule → don't mark as empty, but children already processed
                if is_never_empty(dirname, raiz, filter_rules):
                    self.on_log(f"[{_ts()}] Nunca-vacía (regla): {raiz}")
                    continue

                # ✓ Empty!
                would_be_empty.add(os.path.normcase(raiz))
                result = ScanResult(raiz, "empty", depth)
                self.on_found(result)
                self.on_log(f"[{_ts()}] Vacía: {raiz}")
                count += 1

        except Exception as e:
            self.on_log(f"[{_ts()}] ERROR en escaneo: {e}")

        return count


# ---------------------------------------------------------------------------


class Cleaner:
    """
    Deletes (or simulates deletion of) ScanResult objects.
    Runs in a daemon thread; communicates via callbacks.
    """

    def __init__(
        self, settings, on_deleted=None, on_log=None, on_done=None, on_error=None
    ):
        self.settings = settings
        self.on_deleted = on_deleted or (lambda r: None)
        self.on_log = on_log or (lambda m: None)
        self.on_done = on_done or (lambda n, b: None)
        self.on_error = on_error or (lambda r, e: None)
        self._stop = threading.Event()
        self._thread = None

    def delete(self, results):
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, args=(results,), daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    # ------------------------------------------------------------------
    def _run(self, results):
        mode = self.settings.get("delete_mode", "simulate")
        pause_ms = self.settings.get("pause_ms", 0)
        max_warn = self.settings.get("max_warnings", 10)

        to_delete = [r for r in results if r.selected and r.status == "empty"]
        to_delete.sort(key=lambda r: r.depth, reverse=True)  # deepest first

        self.on_log(
            f"[{_ts()}] Iniciando eliminación ({mode.upper()}) — "
            f"{len(to_delete)} carpetas."
        )

        count = errors = 0
        total_bytes = 0

        for result in to_delete:
            if self._stop.is_set():
                break
            freed = self._delete_one(result, mode)
            if freed is None:
                errors += 1
                if errors >= max_warn:
                    self.on_log(
                        f"[{_ts()}] Demasiados errores ({max_warn}), deteniendo."
                    )
                    break
            else:
                count += 1
                total_bytes += freed
                self.on_deleted(result)

            if pause_ms > 0:
                time.sleep(pause_ms / 1000)

        mb = total_bytes / (1024 * 1024)
        self.on_log(
            f"[{_ts()}] Proceso completado — "
            f"{count} carpetas, {errors} errores, {mb:.2f} MB liberados."
        )
        self.on_done(count, total_bytes)

    def _delete_one(self, result, mode):
        path = result.path
        lpath = long_path(path)
        freed = 0

        if mode != "simulate":
            freed = self._purge_ignorable_files(lpath)

        if mode == "simulate":
            self.on_log(f"[{_ts()}] [SIMULACIÓN] Se eliminaría: {path}")
            return 0

        if mode == "recycle":
            try:
                import send2trash

                send2trash.send2trash(path)
                self.on_log(f"[{_ts()}] Papelera: {path}")
                return freed
            except Exception as e:
                self.on_log(f"[{_ts()}] ERROR (papelera): {path} — {e}")
                self.on_error(result, e)
                return None

        # permanent
        try:
            try:
                os.chmod(lpath, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
            except Exception as _e:
                import sys; print(f'[DEBUG] Ignored Exception: {_e}', file=sys.stderr)
            os.rmdir(lpath)
            self.on_log(f"[{_ts()}] Eliminada: {path}")
            return freed
        except PermissionError as e:
            self.on_log(f"[{_ts()}] PERMISO DENEGADO: {path}")
            self.on_error(result, e)
            return None
        except Exception as e:
            self.on_log(f"[{_ts()}] ERROR: {path} — {e}")
            self.on_error(result, e)
            return None

    def _purge_ignorable_files(self, lpath) -> int:
        freed = 0
        for fpath in collect_ignorable_files(lpath, self.settings):
            lfpath = long_path(fpath)
            try:
                freed += os.path.getsize(lfpath)
            except Exception as _e:
                import sys; print(f'[DEBUG] Ignored Exception: {_e}', file=sys.stderr)
            try:
                # Force write permissions to allow deletion of read-only junk
                os.chmod(lfpath, stat.S_IWRITE)
                os.remove(lfpath)
            except Exception as _e:
                import sys; print(f'[DEBUG] Ignored Exception: {_e}', file=sys.stderr)
        return freed
