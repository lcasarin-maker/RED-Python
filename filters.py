"""Filters module for RED-Python handling rule matching and file utilities."""

import fnmatch
import logging
import os
import re
import stat
import time

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants exposed to the UI
# ---------------------------------------------------------------------------

METHODS = [
    "wildcard",
    "contains",
    "startswith",
    "endswith",
    "exact",
    "exact_path",
    "regex_name",
    "regex_path",
]
TYPES = ["ignore_file", "ignore_dir", "never_empty"]

METHOD_LABELS = {
    "wildcard": "Wildcard (e.g. *.tmp)",
    "contains": "Contains",
    "startswith": "Starts with",
    "endswith": "Ends with",
    "exact": "Exact name",
    "exact_path": "Exact path",
    "regex_name": "Regex (name)",
    "regex_path": "Regex (full path)",
}
TYPE_LABELS = {
    "ignore_file": "Ignore file",
    "ignore_dir": "Ignore folder",
    "never_empty": "Never empty",
}


# ---------------------------------------------------------------------------
# Core rule matching - 7 methods
# ---------------------------------------------------------------------------


def match_rule(name: str, full_path: str, rule: dict) -> bool:
    """
    Return True if name / full_path satisfies the filter rule.
    rule keys: enabled, type, method, pattern
    """
    if not rule.get("enabled", True):
        return False
    pattern = rule.get("pattern", "").strip()
    method = rule.get("method", "wildcard")
    if not pattern:
        return False

    n_lo = name.lower()
    p_lo = pattern.lower()
    fp = full_path or name

    _matchers = {
        "wildcard": lambda n, p, f: fnmatch.fnmatch(n, p),
        "contains": lambda n, p, f: p in n,
        "startswith": lambda n, p, f: n.startswith(p),
        "endswith": lambda n, p, f: n.endswith(p),
        "exact": lambda n, p, f: n == p,
        "exact_path": lambda n, p, f: os.path.normcase(f) == os.path.normcase(pattern),
        "regex_name": lambda n, p, f: bool(re.search(pattern, name, re.IGNORECASE)),
        "regex_path": lambda n, p, f: bool(re.search(pattern, f, re.IGNORECASE)),
    }

    try:
        if method in _matchers:
            return _matchers[method](n_lo, p_lo, fp)
    except re.error:
        pass
    return False


def _active(filter_rules: list, rtype: str) -> list:
    return [
        r for r in filter_rules if r.get("type") == rtype and r.get("enabled", True)
    ]


def is_file_ignored(name: str, full_path: str, filter_rules: list) -> bool:
    return any(
        match_rule(name, full_path, r) for r in _active(filter_rules, "ignore_file")
    )


def is_dir_ignored(name: str, full_path: str, filter_rules: list) -> bool:
    return any(
        match_rule(name, full_path, r) for r in _active(filter_rules, "ignore_dir")
    )


def is_never_empty(name: str, full_path: str, filter_rules: list) -> bool:
    """Return True if this directory should never be marked as empty."""
    return any(
        match_rule(name, full_path, r) for r in _active(filter_rules, "never_empty")
    )


# ---------------------------------------------------------------------------
# Long-path helpers
# ---------------------------------------------------------------------------


def long_path(path: str) -> str:
    """Add the \\?\\ prefix for Windows paths longer than 260 chars."""
    if os.name == "nt" and not path.startswith("\\\\?\\"):
        path = "\\\\?\\" + os.path.abspath(path)
    return path


def strip_long_prefix(path: str) -> str:
    if path.startswith("\\\\?\\"):
        return path[4:]
    return path


# ---------------------------------------------------------------------------
# File / directory attribute helpers
# ---------------------------------------------------------------------------


def is_hidden(path: str) -> bool:
    if os.path.basename(path).startswith("."):
        return True
    if os.name == "nt":
        try:
            return bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
        except Exception as _e:
            import sys

            print(f"[DEBUG] Ignored Exception: {_e}", file=sys.stderr)
    return False


def is_system(path: str) -> bool:
    if os.name == "nt":
        try:
            return bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM)
        except Exception as _e:
            import sys

            print(f"[DEBUG] Ignored Exception: {_e}", file=sys.stderr)
    return False


def get_age_hours(path: str) -> float:
    try:
        return (time.time() - os.path.getmtime(path)) / 3600
    except Exception:
        logger.debug("Could not stat mtime for %s", path, exc_info=True)
        return float("inf")


def is_protected(path: str, protected_dirs: list) -> bool:
    norm = os.path.normcase(os.path.abspath(path))
    name = os.path.basename(norm)
    for protected in protected_dirs:
        p = protected.strip()
        if not p:
            continue
        pnorm = os.path.normcase(os.path.abspath(p))
        pname = os.path.basename(pnorm)
        if norm == pnorm or norm.startswith(pnorm + os.sep):
            return True
        if name in (pname, pname.lower()):
            return True
    return False


# ---------------------------------------------------------------------------
# Directory emptiness checks
# ---------------------------------------------------------------------------


def _is_file_empty(entry_path, settings) -> bool:
    if not settings.get("ignore_empty_files", True):
        return False
    try:
        return os.path.getsize(entry_path) == 0
    except Exception:
        logger.debug("Could not stat size for %s", entry_path, exc_info=True)
        return False

def _is_file_hidden(entry_path, settings) -> bool:
    if settings.get("scan_hidden", False):
        return False
    try:
        return is_hidden(entry_path) or is_system(entry_path)
    except Exception:
        logger.debug("Could not check hidden/system attrs for %s", entry_path, exc_info=True)
        return False

def _is_ignorable_file(entry, entry_path, settings) -> bool:
    try:
        if os.path.isdir(entry_path):
            return True  # we skip dirs in these checks
    except Exception:
        logger.debug("Could not check isdir for %s", entry_path, exc_info=True)
        return True

    if not settings.get("follow_symlinks", False) and os.path.islink(entry_path):
        return True

    if is_file_ignored(entry, entry_path, settings.get("filter_rules", [])):
        return True

    if _is_file_empty(entry_path, settings):
        return True

    if _is_file_hidden(entry_path, settings):
        return True

    return False


def has_only_ignorable_files(lpath: str, settings) -> bool:
    """
    Return True if the directory contains no real files -
    only files that are ignorable (by filter rules, zero-byte, or hidden/system).
    Subdirectories are NOT checked here; the caller handles them.
    """
    try:
        entries = os.listdir(lpath)
    except (PermissionError, OSError):
        return False

    for entry in entries:
        if not _is_ignorable_file(entry, os.path.join(lpath, entry), settings):
            return False
    return True


def collect_ignorable_files(lpath: str, settings) -> list:
    """Return full paths of ignorable files inside lpath (used before os.rmdir)."""
    result = []
    try:
        entries = os.listdir(lpath)
    except Exception:
        logger.debug("Could not list directory %s", lpath, exc_info=True)
        return result

    for entry in entries:
        entry_path = os.path.join(lpath, entry)
        try:
            if os.path.isdir(entry_path):
                continue
        except Exception:
            logger.debug("Could not check isdir for %s", entry_path, exc_info=True)
            continue

        if _is_ignorable_file(entry, entry_path, settings):
            result.append(entry_path)

    return result
