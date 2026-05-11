import os
import sys
import json
from pathlib import Path

_win = os.environ.get('SystemRoot', 'C:\\Windows')

DEFAULT_PROTECTED_DIRS = [
    os.path.join(_win, 'System32'),
    os.path.join(_win, 'SysWOW64'),
    os.path.join(_win, 'WinSxS'),
    '$RECYCLE.BIN',
    'System Volume Information',
]

# Unified filter rules — each rule is a dict:
#   enabled : bool
#   type    : 'ignore_file' | 'ignore_dir' | 'never_empty'
#   method  : 'wildcard' | 'contains' | 'startswith' | 'endswith' |
#             'exact' | 'exact_path' | 'regex_name' | 'regex_path'
#   pattern : str
DEFAULT_FILTER_RULES = [
    {'enabled': True,  'type': 'ignore_file', 'method': 'exact',    'pattern': 'desktop.ini'},
    {'enabled': True,  'type': 'ignore_file', 'method': 'exact',    'pattern': 'Thumbs.db'},
    {'enabled': True,  'type': 'ignore_file', 'method': 'exact',    'pattern': 'thumbs.db'},
    {'enabled': True,  'type': 'ignore_file', 'method': 'exact',    'pattern': '.DS_Store'},
    {'enabled': True,  'type': 'ignore_file', 'method': 'wildcard', 'pattern': '._*'},
    {'enabled': True,  'type': 'ignore_file', 'method': 'exact',    'pattern': '.gitkeep'},
    {'enabled': True,  'type': 'ignore_dir',  'method': 'exact',    'pattern': '__pycache__'},
    {'enabled': True,  'type': 'ignore_dir',  'method': 'exact',    'pattern': '.venv'},
    {'enabled': True,  'type': 'ignore_dir',  'method': 'exact',    'pattern': '.ipynb_checkpoints'},
    {'enabled': True,  'type': 'ignore_dir',  'method': 'exact',    'pattern': '.jekyll-cache'},
]

DEFAULT_SETTINGS = {
    'filter_rules':       DEFAULT_FILTER_RULES,
    'protected_dirs':     DEFAULT_PROTECTED_DIRS,
    'max_depth':          0,
    'min_age_hours':      0,
    'ignore_empty_files': True,
    'scan_hidden':        False,
    'follow_symlinks':    False,
    'delete_mode':        'recycle',
    'pause_ms':           0,
    'max_warnings':       10,
    'recent_paths':       [],
    'play_sound':         True,
}

CONFIG_FILENAME = 'settings.json'
DEFAULT_CONFIG_PATH = Path.home() / '.red_python' / CONFIG_FILENAME

def get_config_path():
    # Portable mode: if settings.json exists in the current directory (or executable dir), use it.
    local_path = Path(os.getcwd()) / CONFIG_FILENAME
    # Also check the directory of the script/executable
    script_dir_path = Path(os.path.dirname(os.path.abspath(sys.argv[0]))) / CONFIG_FILENAME
    
    if local_path.exists():
        return local_path
    if script_dir_path.exists():
        return script_dir_path
    return DEFAULT_CONFIG_PATH

class Settings:
    def __init__(self):
        self.config_path = get_config_path()
        self.data = {}
        for k, v in DEFAULT_SETTINGS.items():
            if isinstance(v, list):
                self.data[k] = [dict(i) if isinstance(i, dict) else i for i in v]
            else:
                self.data[k] = v

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                self.data.update(saved)
            except Exception:
                pass
        return self

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_recent_path(self, path: str):
        recent = self.data.get('recent_paths', [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.data['recent_paths'] = recent[:10]
        self.save()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)
