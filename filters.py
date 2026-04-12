import os
import re
import stat
import time
import fnmatch

# ---------------------------------------------------------------------------
# Constants exposed to UI
# ---------------------------------------------------------------------------

METHODS = [
    'wildcard', 'contains', 'startswith', 'endswith',
    'exact', 'exact_path', 'regex_name', 'regex_path',
]
TYPES = ['ignore_file', 'ignore_dir', 'never_empty']

METHOD_LABELS = {
    'wildcard':   'Wildcard  (ej: *.tmp)',
    'contains':   'Contiene',
    'startswith': 'Empieza por',
    'endswith':   'Termina en',
    'exact':      'Nombre exacto',
    'exact_path': 'Ruta exacta',
    'regex_name': 'Regex (nombre)',
    'regex_path': 'Regex (ruta completa)',
}
TYPE_LABELS = {
    'ignore_file': 'Ignorar archivo',
    'ignore_dir':  'Ignorar carpeta',
    'never_empty': 'Nunca vacío',
}


# ---------------------------------------------------------------------------
# Core rule matching — 7 methods
# ---------------------------------------------------------------------------

def match_rule(name: str, full_path: str, rule: dict) -> bool:
    """
    Return True if name / full_path satisfies the filter rule.
    rule keys: enabled, type, method, pattern
    """
    if not rule.get('enabled', True):
        return False
    pattern = rule.get('pattern', '').strip()
    method  = rule.get('method', 'wildcard')
    if not pattern:
        return False

    n_lo = name.lower()
    p_lo = pattern.lower()
    fp   = full_path or name

    if method == 'wildcard':
        return fnmatch.fnmatch(n_lo, p_lo)
    if method == 'contains':
        return p_lo in n_lo
    if method == 'startswith':
        return n_lo.startswith(p_lo)
    if method == 'endswith':
        return n_lo.endswith(p_lo)
    if method == 'exact':
        return n_lo == p_lo
    if method == 'exact_path':
        return os.path.normcase(fp) == os.path.normcase(pattern)
    if method == 'regex_name':
        try:
            return bool(re.search(pattern, name, re.IGNORECASE))
        except re.error:
            return False
    if method == 'regex_path':
        try:
            return bool(re.search(pattern, fp, re.IGNORECASE))
        except re.error:
            return False
    return False


def _active(filter_rules: list, rtype: str) -> list:
    return [r for r in filter_rules
            if r.get('type') == rtype and r.get('enabled', True)]


def is_file_ignored(name: str, full_path: str, filter_rules: list) -> bool:
    return any(match_rule(name, full_path, r) for r in _active(filter_rules, 'ignore_file'))


def is_dir_ignored(name: str, full_path: str, filter_rules: list) -> bool:
    return any(match_rule(name, full_path, r) for r in _active(filter_rules, 'ignore_dir'))


def is_never_empty(name: str, full_path: str, filter_rules: list) -> bool:
    """Return True if this directory should never be marked as empty."""
    return any(match_rule(name, full_path, r) for r in _active(filter_rules, 'never_empty'))


# ---------------------------------------------------------------------------
# Long-path helpers
# ---------------------------------------------------------------------------

def long_path(path: str) -> str:
    """Add \\?\\ prefix for Windows paths > 260 chars."""
    if os.name == 'nt' and not path.startswith('\\\\?\\'):
        path = '\\\\?\\' + os.path.abspath(path)
    return path


def strip_long_prefix(path: str) -> str:
    if path.startswith('\\\\?\\'):
        return path[4:]
    return path


# ---------------------------------------------------------------------------
# File / directory attribute helpers
# ---------------------------------------------------------------------------

def is_hidden(path: str) -> bool:
    if os.path.basename(path).startswith('.'):
        return True
    if os.name == 'nt':
        try:
            return bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
        except Exception:
            pass
    return False


def is_system(path: str) -> bool:
    if os.name == 'nt':
        try:
            return bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM)
        except Exception:
            pass
    return False


def get_age_hours(path: str) -> float:
    try:
        return (time.time() - os.path.getmtime(path)) / 3600
    except Exception:
        return float('inf')


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

def has_only_ignorable_files(lpath: str, settings) -> bool:
    """
    Return True if the directory contains no real files —
    only files that are ignorable (by filter rules, 0-byte, or hidden/system).
    Subdirectories are NOT checked here; the caller handles them.
    """
    try:
        entries = os.listdir(lpath)
    except (PermissionError, OSError):
        return False

    filter_rules = settings.get('filter_rules', [])

    for entry in entries:
        entry_path = os.path.join(lpath, entry)

        try:
            if os.path.isdir(entry_path):
                continue
        except Exception:
            continue

        if not settings.get('follow_symlinks', False) and os.path.islink(entry_path):
            continue

        if is_file_ignored(entry, entry_path, filter_rules):
            continue

        if settings.get('ignore_empty_files', True):
            try:
                if os.path.getsize(entry_path) == 0:
                    continue
            except Exception:
                pass

        if not settings.get('scan_hidden', False):
            try:
                if is_hidden(entry_path) or is_system(entry_path):
                    continue
            except Exception:
                pass

        return False  # Real file found

    return True


def collect_ignorable_files(lpath: str, settings) -> list:
    """Return full paths of ignorable files inside lpath (used before os.rmdir)."""
    result = []
    try:
        entries = os.listdir(lpath)
    except Exception:
        return result

    filter_rules = settings.get('filter_rules', [])

    for entry in entries:
        entry_path = os.path.join(lpath, entry)
        try:
            if os.path.isdir(entry_path):
                continue
        except Exception:
            continue

        ignorable = False
        if is_file_ignored(entry, entry_path, filter_rules):
            ignorable = True
        elif settings.get('ignore_empty_files', True):
            try:
                ignorable = os.path.getsize(entry_path) == 0
            except Exception:
                pass
        if not ignorable and not settings.get('scan_hidden', False):
            try:
                ignorable = is_hidden(entry_path) or is_system(entry_path)
            except Exception:
                pass

        if ignorable:
            result.append(entry_path)

    return result
