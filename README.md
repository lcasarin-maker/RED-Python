# RED-Python — Remove Empty Directories

A cross-platform Python tool for finding and removing empty (or effectively empty) directories.  
Combines the best of [hxseven/Remove-Empty-Directories](https://github.com/hxseven/Remove-Empty-Directories) (C#/Windows), the simplicity of a bottom-up Python approach, and additional features gathered from the broader ecosystem (Czkawka, VoidFinder, emptydir, etc.).

---

## Features

| Feature | Description |
|---|---|
| **Smart detection** | Finds folders that *would* become empty after cleanup — not just physically empty ones |
| **GUI + CLI** | Full tkinter GUI for desktop use; CLI mode for scripting and automation |
| **Simulation mode** | Preview exactly what would be deleted before touching anything |
| **Recycle Bin** | Safely moves folders to the Recycle Bin instead of permanent deletion |
| **Permanent delete** | Direct removal with confirmation dialog |
| **Multi-path scan** | Add multiple root directories to scan in a single pass |
| **Recent paths** | History of the last 10 used paths |
| **Ignore patterns** | Wildcard (`*.tmp`) and regex (`/pattern/`) for files and folder names |
| **Safe defaults** | Pre-configured to ignore `desktop.ini`, `Thumbs.db`, `.DS_Store`, `__pycache__`, `.venv`, etc. |
| **Protected dirs** | System32, SysWOW64, $RECYCLE.BIN and others are never touched |
| **Max depth** | Limit scan depth to avoid going too deep |
| **Age filter** | Skip directories modified less than N hours ago |
| **0-byte files** | Treat empty files as non-existent (configurable) |
| **Symlink detection** | Avoids infinite loops caused by symbolic links |
| **Permission handling** | Separates permission errors from other errors; continues gracefully |
| **Detailed log** | Timestamped log with all operations |
| **Export results** | Save scan results to CSV or TXT |
| **Post-action report** | Shows total folders processed and MB freed |
| **Persistent settings** | Configuration saved to `~/.red_python/settings.json` |
| **Long path support** | Handles Windows paths longer than 260 characters (`\\?\` prefix) |

---

## Requirements

- Python 3.10+
- [`send2trash`](https://pypi.org/project/Send2Trash/) (for Recycle Bin support)

```bash
pip install -r requirements.txt
```

---

## Usage

### GUI

```bash
python red.py
```

### CLI

```bash
# Simulate (dry-run) — show what would be deleted
python red.py --scan "C:\Users\Me\Projects" --dry-run

# Send to Recycle Bin (default)
python red.py --scan "D:\Backup" "E:\Archive"

# Permanent delete with depth limit
python red.py --scan "C:\Temp" --permanent --max-depth 3

# Export results to CSV
python red.py --scan "C:\Data" --dry-run --export results.csv

# All options
python red.py --help
```

#### CLI Options

| Option | Description |
|---|---|
| `--scan PATH [PATH...]` | Root directories to scan (required) |
| `--dry-run` | Simulate — list what would be deleted |
| `--permanent` | Delete permanently (default: Recycle Bin) |
| `--max-depth N` | Max recursion depth (0 = unlimited) |
| `--min-age N` | Only delete dirs older than N hours |
| `--no-empty-files` | Do NOT treat 0-byte files as empty |
| `--scan-hidden` | Include hidden and system folders |
| `--follow-symlinks` | Follow symbolic links |
| `--export FILE` | Save results to FILE (.csv or .txt) |
| `--quiet` | Only show summary output |

---

## Build executable (Windows)

```bash
pip install pyinstaller
pyinstaller red.spec
```

Output: `dist/RED-Python.exe` — a standalone Windows executable, no Python required.

---

## How it works

RED-Python uses a **bottom-up walk** (`os.walk(topdown=False)`) and tracks a set of "would-be-empty" directories:

1. A directory is considered **effectively empty** if:
   - All files in it match an ignore pattern, are 0-byte (if configured), or are hidden/system files
   - All subdirectories are already in the `would_be_empty` set

2. This correctly handles **nested chains**: a folder containing only empty subfolders is also detected as empty.

3. Before permanent deletion, any remaining ignorable files (e.g. `Thumbs.db`) inside the directory are removed first so `os.rmdir` can succeed.

---

## Configuration

Settings are stored at `~/.red_python/settings.json` and editable via the GUI (⚙ Config button).

Default ignored files:
```
desktop.ini, Thumbs.db, .DS_Store, ._*, .gitkeep,
__pycache__, .venv, .ipynb_checkpoints, .jekyll-cache
```

Default protected directories (never deleted):
```
C:\Windows\System32, C:\Windows\SysWOW64, C:\Windows\WinSxS,
$RECYCLE.BIN, System Volume Information
```

---

## Inspired by

- [hxseven/Remove-Empty-Directories](https://github.com/hxseven/Remove-Empty-Directories) — original RED (C#)
- [alexwlchan/emptydir](https://github.com/alexwlchan/emptydir) — opinionated safe defaults
- [qarmin/czkawka](https://github.com/qarmin/czkawka) — multi-purpose disk cleaner
- [sztaroszta/VoidFinder](https://github.com/sztaroszta/VoidFinder) — Python/tkinter approach

---

## License

MIT
