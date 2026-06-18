"""RED-Python application main module."""
import os
import csv
import copy
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

from config import (
    Settings,
    DEFAULT_FILTER_RULES,
    DEFAULT_PROTECTED_DIRS,
    DEFAULT_SETTINGS,
)
from core import Scanner, Cleaner, ScanResult
from filters import METHODS, TYPES, METHOD_LABELS, TYPE_LABELS


def _ts():
    return datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Rule add/edit dialog
# ---------------------------------------------------------------------------


class RuleDialog(tk.Toplevel):
    """Small dialog to add or edit a single filter rule."""

    def __init__(self, parent, rule=None):
        super().__init__(parent)
        self.title("Add rule" if rule is None else "Edit rule")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.result = None

        rule = rule or {
            "enabled": True,
            "type": "ignore_file",
            "method": "exact",
            "pattern": "",
        }

        f = ttk.Frame(self, padding=12)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="Type:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self._type = tk.StringVar(value=rule["type"])
        ttk.Combobox(
            f, textvariable=self._type, state="readonly", width=20, values=TYPES
        ).grid(row=0, column=1, sticky=tk.W, padx=8)

        ttk.Label(f, text="Method:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self._method = tk.StringVar(value=rule["method"])
        ttk.Combobox(
            f, textvariable=self._method, state="readonly", width=28, values=METHODS
        ).grid(row=1, column=1, sticky=tk.W, padx=8)

        ttk.Label(f, text="Pattern:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self._pattern = tk.StringVar(value=rule["pattern"])
        ttk.Entry(f, textvariable=self._pattern, width=32).grid(
            row=2, column=1, sticky=tk.W, padx=8
        )

        self._enabled = tk.BooleanVar(value=rule.get("enabled", True))
        ttk.Checkbutton(f, text="Enabled", variable=self._enabled).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=4
        )

        bf = ttk.Frame(f)
        bf.grid(row=4, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(bf, text="OK", command=self._ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=4)

        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self.destroy())
        self.wait_window()

    def _ok(self):
        pattern = self._pattern.get().strip()
        if not pattern:
            messagebox.showwarning(
                "Empty field", "The pattern cannot be empty.", parent=self
            )
            return
        self.result = {
            "enabled": self._enabled.get(),
            "type": self._type.get(),
            "method": self._method.get(),
            "pattern": pattern,
        }
        self.destroy()


# ---------------------------------------------------------------------------
# Settings dialog
# ---------------------------------------------------------------------------


class SettingsDialog(tk.Toplevel):

    def __init__(self, parent, settings: Settings):
        super().__init__(parent)
        self.title("Settings - RED-Python")
        self.geometry("700x560")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.settings = settings
        self._rules: list = []  # working copy of filter_rules

        self._build()
        self._load()

    # ------------------------------------------------------------------
    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # ── Tab 1: Filter Rules ───────────────────────────────────────
        t1 = ttk.Frame(nb)
        nb.add(t1, text="Filter rules")

        info = (
            'Types: "Ignore file" treats the file as nonexistent. '
            '"Ignore folder" skips that folder and its children. '
            '"Never empty" prevents the folder from being marked empty '
            "(but still processes its subfolders)."
        )
        ttk.Label(
            t1, text=info, wraplength=660, justify=tk.LEFT, foreground="#555"
        ).pack(anchor=tk.W, padx=6, pady=(6, 2))

        # Treeview
        cols = ("enabled", "type", "method", "pattern")
        tf = ttk.Frame(t1)
        tf.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)

        sy = ttk.Scrollbar(tf, orient=tk.VERTICAL)
        self._rtree = ttk.Treeview(
            tf,
            columns=cols,
            show="headings",
            yscrollcommand=sy.set,
            selectmode="browse",
            height=12,
        )
        sy.config(command=self._rtree.yview)

        self._rtree.heading("enabled", text="Enabled")
        self._rtree.heading("type", text="Type")
        self._rtree.heading("method", text="Method")
        self._rtree.heading("pattern", text="Pattern")
        self._rtree.column("enabled", width=60, minwidth=50, anchor=tk.CENTER)
        self._rtree.column("type", width=130, minwidth=100)
        self._rtree.column("method", width=150, minwidth=110)
        self._rtree.column("pattern", width=260, minwidth=120)

        # Color tags
        self._rtree.tag_configure("on", foreground="#1a1a1a")
        self._rtree.tag_configure("off", foreground="#aaaaaa")

        sy.pack(side=tk.RIGHT, fill=tk.Y)
        self._rtree.pack(fill=tk.BOTH, expand=True)
        self._rtree.bind("<Double-1>", self._on_row_double_click)

        # Buttons row
        bf = ttk.Frame(t1)
        bf.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(bf, text="+ Add", command=self._rule_add).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(bf, text="✎ Edit", command=self._rule_edit).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(bf, text="× Delete", command=self._rule_delete).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(bf, text="✓ / ✗ Toggle", command=self._rule_toggle).pack(
            side=tk.LEFT, padx=8
        )
        ttk.Button(bf, text="↑", width=3, command=lambda: self._rule_move(-1)).pack(
            side=tk.LEFT, padx=1
        )
        ttk.Button(bf, text="↓", width=3, command=lambda: self._rule_move(1)).pack(
            side=tk.LEFT, padx=1
        )
        ttk.Button(bf, text="Restore defaults", command=self._rules_restore).pack(
            side=tk.RIGHT, padx=2
        )

        # ── Tab 2: Protection ─────────────────────────────────────────
        t2 = ttk.Frame(nb)
        nb.add(t2, text="Protection")
        ttk.Label(
            t2, text="Protected folders (one per line - never deleted):"
        ).pack(anchor=tk.W, padx=6, pady=(6, 0))
        self._protected = tk.Text(t2, font=("Consolas", 9))
        sb2 = ttk.Scrollbar(t2, command=self._protected.yview)
        self._protected.config(yscrollcommand=sb2.set)
        sb2.pack(side=tk.RIGHT, fill=tk.Y)
        self._protected.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)

        # ── Tab 3: Advanced ───────────────────────────────────────────
        t3 = ttk.Frame(nb)
        nb.add(t3, text="Advanced")

        g = ttk.Frame(t3)
        g.pack(fill=tk.X, padx=12, pady=10)

        def spin(label, var, lo, hi, r):
            ttk.Label(g, text=label).grid(row=r, column=0, sticky=tk.W, pady=4)
            ttk.Spinbox(g, from_=lo, to=hi, textvariable=var, width=9).grid(
                row=r, column=1, sticky=tk.W, padx=8
            )

        self._max_depth = tk.IntVar()
        self._min_age = tk.IntVar()
        self._pause_ms = tk.IntVar()
        self._max_warn = tk.IntVar()
        spin("Maximum depth (0 = unlimited):", self._max_depth, 0, 200, 0)
        spin("Minimum age in hours (0 = no filter):", self._min_age, 0, 87600, 1)
        spin("Pause between deletions (ms):", self._pause_ms, 0, 10000, 2)
        spin("Max errors before stopping:", self._max_warn, 1, 500, 3)

        self._empty_files = tk.BooleanVar()
        self._scan_hidden = tk.BooleanVar()
        self._follow_sym = tk.BooleanVar()
        self._play_sound = tk.BooleanVar()
        ttk.Checkbutton(
            g,
            text="Treat 0-byte files as empty",
            variable=self._empty_files,
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=4)
        ttk.Checkbutton(
            g,
            text="Scan hidden and system folders",
            variable=self._scan_hidden,
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=4)
        ttk.Checkbutton(
            g,
            text="Follow symbolic links (watch for loops)",
            variable=self._follow_sym,
        ).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=4)
        ttk.Checkbutton(
            g,
            text="Play a sound when long tasks finish",
            variable=self._play_sound,
        ).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=4)

        # Windows Integration
        if os.name == "nt":
            ttk.Separator(g, orient=tk.HORIZONTAL).grid(
                row=7, column=0, columnspan=2, sticky=tk.EW, pady=10
            )
            ttk.Label(g, text="Windows integration:", font=("", 9, "bold")).grid(
                row=8, column=0, sticky=tk.W, pady=4
            )

            self._shell_frame = ttk.Frame(g)
            self._shell_frame.grid(row=9, column=0, columnspan=2, sticky=tk.W)

            self._btn_reg = ttk.Button(
                self._shell_frame,
                text="Add to context menu",
                command=self._reg_shell,
            )
            self._btn_reg.pack(side=tk.LEFT, padx=2)

            self._btn_unreg = ttk.Button(
                self._shell_frame,
                text="Remove from context menu",
                command=self._unreg_shell,
            )
            self._btn_unreg.pack(side=tk.LEFT, padx=2)

            self._update_shell_buttons()

    def _update_shell_buttons(self):
        import shell_integration

        registered = shell_integration.is_registered()
        if registered:
            self._btn_reg.config(state=tk.DISABLED)
            self._btn_unreg.config(state=tk.NORMAL)
        else:
            self._btn_reg.config(state=tk.NORMAL)
            self._btn_unreg.config(state=tk.DISABLED)

    def _reg_shell(self):
        import shell_integration

        ok, msg = shell_integration.register_context_menu()
        if ok:
            messagebox.showinfo("Success", msg, parent=self)
        else:
            messagebox.showerror("Error", f"Could not register: {msg}", parent=self)
        self._update_shell_buttons()

    def _unreg_shell(self):
        import shell_integration

        ok, msg = shell_integration.unregister_context_menu()
        if ok:
            messagebox.showinfo("Success", msg, parent=self)
        else:
            messagebox.showerror("Error", f"Could not remove: {msg}", parent=self)
        self._update_shell_buttons()

        # ── Bottom buttons ────────────────────────────────────────────
        bb = ttk.Frame(self)
        bb.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(bb, text="Cancel", command=self.destroy).pack(
            side=tk.RIGHT, padx=4
        )
        ttk.Button(bb, text="Save", command=self._save).pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Load / save
    # ------------------------------------------------------------------

    def _load(self):
        self._rules = [dict(r) for r in self.settings.get("filter_rules", [])]
        self._refresh_tree()

        self._protected.delete("1.0", tk.END)
        self._protected.insert(
            "1.0", "\n".join(self.settings.get("protected_dirs", []))
        )

        self._max_depth.set(self.settings.get("max_depth", 0))
        self._min_age.set(self.settings.get("min_age_hours", 0))
        self._pause_ms.set(self.settings.get("pause_ms", 0))
        self._max_warn.set(self.settings.get("max_warnings", 10))
        self._empty_files.set(self.settings.get("ignore_empty_files", True))
        self._scan_hidden.set(self.settings.get("scan_hidden", False))
        self._follow_sym.set(self.settings.get("follow_symlinks", False))

    def _save(self):
        self.settings["filter_rules"] = self._rules
        self.settings["protected_dirs"] = [
            l.strip()
            for l in self._protected.get("1.0", tk.END).splitlines()
            if l.strip()
        ]
        self.settings["max_depth"] = self._max_depth.get()
        self.settings["min_age_hours"] = self._min_age.get()
        self.settings["pause_ms"] = self._pause_ms.get()
        self.settings["max_warnings"] = self._max_warn.get()
        self.settings["ignore_empty_files"] = self._empty_files.get()
        self.settings["scan_hidden"] = self._scan_hidden.get()
        self.settings["follow_symlinks"] = self._follow_sym.get()
        self.settings.save()
        self.destroy()

    # ------------------------------------------------------------------
    # Rule tree helpers
    # ------------------------------------------------------------------

    def _refresh_tree(self):
        for item in self._rtree.get_children():
            self._rtree.delete(item)
        for i, r in enumerate(self._rules):
            tag = "on" if r.get("enabled", True) else "off"
            self._rtree.insert(
                "",
                tk.END,
                iid=str(i),
                values=(
                    "✓" if r.get("enabled", True) else "✗",
                    TYPE_LABELS.get(r.get("type", ""), r.get("type", "")),
                    METHOD_LABELS.get(r.get("method", ""), r.get("method", "")),
                    r.get("pattern", ""),
                ),
                tags=(tag,),
            )

    def _selected_index(self):
        sel = self._rtree.selection()
        return int(sel[0]) if sel else None

    def _rule_add(self):
        dlg = RuleDialog(self)
        if dlg.result:
            self._rules.append(dlg.result)
            self._refresh_tree()
            self._rtree.selection_set(str(len(self._rules) - 1))

    def _rule_edit(self):
        idx = self._selected_index()
        if idx is None:
            return
        dlg = RuleDialog(self, dict(self._rules[idx]))
        if dlg.result:
            self._rules[idx] = dlg.result
            self._refresh_tree()
            self._rtree.selection_set(str(idx))

    def _rule_delete(self):
        idx = self._selected_index()
        if idx is None:
            return
        self._rules.pop(idx)
        self._refresh_tree()

    def _rule_toggle(self):
        idx = self._selected_index()
        if idx is None:
            return
        self._rules[idx]["enabled"] = not self._rules[idx].get("enabled", True)
        self._refresh_tree()
        self._rtree.selection_set(str(idx))

    def _on_row_double_click(self, event):
        col = self._rtree.identify_column(event.x)
        if col == "#1":  # enabled column → toggle
            self._rule_toggle()
        else:  # other columns → edit
            self._rule_edit()

    def _rule_move(self, direction):
        idx = self._selected_index()
        if idx is None:
            return
        new_idx = idx + direction
        if 0 <= new_idx < len(self._rules):
            self._rules[idx], self._rules[new_idx] = (
                self._rules[new_idx],
                self._rules[idx],
            )
            self._refresh_tree()
            self._rtree.selection_set(str(new_idx))

    def _rules_restore(self):
        if messagebox.askyesno(
            "Restore",
            "Restore filter rules to their default values?",
            parent=self,
        ):
            self._rules = [dict(r) for r in DEFAULT_FILTER_RULES]
            self._refresh_tree()


# ---------------------------------------------------------------------------
# Main application window
# ---------------------------------------------------------------------------


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RED-Python — Remove Empty Directories")
        self.geometry("1000x700")
        self.minsize(720, 500)

        self.settings = Settings().load()
        self.results: list[ScanResult] = []
        self.scanner = None
        self.cleaner = None
        self._scanning = False
        self._deleting = False

        self._apply_style()
        self._build()

    # ------------------------------------------------------------------
    def _apply_style(self):
        s = ttk.Style(self)
        for theme in ("vista", "winnative", "clam", "alt", "default"):
            try:
                s.theme_use(theme)
                break
            except Exception as _e:
                import sys; print(f'[DEBUG] Ignored Exception: {_e}', file=sys.stderr); continue

    # ------------------------------------------------------------------
    def _build(self):
        # ── Toolbar ────────────────────────────────────────────────────
        tb = ttk.Frame(self)
        tb.pack(fill=tk.X, padx=6, pady=4)

        ttk.Label(tb, text="Paths:").pack(side=tk.LEFT)
        self._path_entry = ttk.Entry(tb, width=52)
        self._path_entry.pack(side=tk.LEFT, padx=(4, 2))
        self._path_entry.bind("<Return>", lambda e: self._add_path())

        ttk.Button(tb, text="Browse", command=self._browse).pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text="+ Add", command=self._add_path).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(tb, text="− Remove", command=self._remove_path).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Separator(tb, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Label(tb, text="Mode:").pack(side=tk.LEFT)
        self._mode = tk.StringVar(value=self.settings.get("delete_mode", "recycle"))
        ttk.Combobox(
            tb,
            textvariable=self._mode,
            width=11,
            state="readonly",
            values=["simulate", "recycle", "permanent"],
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(tb, text="⚙ Config", command=self._open_settings).pack(side=tk.RIGHT)

        # ── Main split ─────────────────────────────────────────────────
        pw_h = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pw_h.pack(fill=tk.BOTH, expand=True, padx=6)

        # Left: path list
        lf = ttk.LabelFrame(pw_h, text="Paths to scan")
        pw_h.add(lf, weight=1)
        self._path_list = tk.Listbox(lf, selectmode=tk.EXTENDED, font=("Consolas", 9))
        sb_l = ttk.Scrollbar(lf, command=self._path_list.yview)
        self._path_list.config(yscrollcommand=sb_l.set)
        sb_l.pack(side=tk.RIGHT, fill=tk.Y)
        self._path_list.pack(fill=tk.BOTH, expand=True)
        for p in self.settings.get("recent_paths", []):
            self._path_list.insert(tk.END, p)

        # Right: results + log
        pw_v = ttk.PanedWindow(pw_h, orient=tk.VERTICAL)
        pw_h.add(pw_v, weight=4)

        # Results tree
        rf = ttk.LabelFrame(pw_v, text="Results")
        pw_v.add(rf, weight=3)

        sy = ttk.Scrollbar(rf, orient=tk.VERTICAL)
        sx = ttk.Scrollbar(rf, orient=tk.HORIZONTAL)
        self._tree = ttk.Treeview(
            rf,
            columns=("status", "depth"),
            yscrollcommand=sy.set,
            xscrollcommand=sx.set,
            selectmode="extended",
        )
        self._tree.heading("#0", text="Ruta", anchor=tk.W)
        self._tree.heading("status", text="Estado", anchor=tk.W)
        self._tree.heading("depth", text="Nivel", anchor=tk.CENTER)
        self._tree.column("#0", width=680, minwidth=200)
        self._tree.column("status", width=110, minwidth=80)
        self._tree.column("depth", width=60, minwidth=40)

        self._tree.tag_configure("empty", foreground="#c0392b")
        self._tree.tag_configure("protected", foreground="#2980b9")
        self._tree.tag_configure("error", foreground="#e67e22")
        self._tree.tag_configure(
            "deleted", foreground="#95a5a6", font=("TkDefaultFont", 9, "overstrike")
        )

        sy.config(command=self._tree.yview)
        sx.config(command=self._tree.xview)
        sy.pack(side=tk.RIGHT, fill=tk.Y)
        sx.pack(side=tk.BOTTOM, fill=tk.X)
        self._tree.pack(fill=tk.BOTH, expand=True)

        self._ctx = tk.Menu(self, tearoff=0)
        self._ctx.add_command(label="Select all", command=self._sel_all)
        self._ctx.add_command(label="Deselect all", command=self._desel_all)
        self._ctx.add_separator()
        self._ctx.add_command(label="Open in Explorer", command=self._open_explorer)
        self._tree.bind("<Button-3>", self._show_ctx)

        # Log
        lf2 = ttk.LabelFrame(pw_v, text="Log")
        pw_v.add(lf2, weight=1)
        sl = ttk.Scrollbar(lf2)
        self._log = tk.Text(
            lf2,
            height=7,
            font=("Consolas", 8),
            state=tk.DISABLED,
            yscrollcommand=sl.set,
            wrap=tk.NONE,
        )
        sl.config(command=self._log.yview)
        sl.pack(side=tk.RIGHT, fill=tk.Y)
        self._log.pack(fill=tk.BOTH, expand=True)

        # ── Progress ───────────────────────────────────────────────────
        pf = ttk.Frame(self)
        pf.pack(fill=tk.X, padx=6)
        self._progress = ttk.Progressbar(pf, mode="indeterminate")
        self._progress.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self._progress_label = ttk.Label(pf, text="", width=42, anchor=tk.W)
        self._progress_label.pack(side=tk.LEFT, padx=4)

        # ── Bottom bar ─────────────────────────────────────────────────
        bf = ttk.Frame(self)
        bf.pack(fill=tk.X, padx=6, pady=4)

        self._status = tk.StringVar(value="Ready.")
        ttk.Label(bf, textvariable=self._status, relief=tk.SUNKEN, anchor=tk.W).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6)
        )

        self._btn_stop = ttk.Button(bf, text="Stop", command=self._stop, state=tk.DISABLED)
        self._btn_stop.pack(side=tk.RIGHT, padx=2)
        self._btn_delete = ttk.Button(
            bf, text="Delete selected", command=self._delete, state=tk.DISABLED
        )
        self._btn_delete.pack(side=tk.RIGHT, padx=2)
        self._btn_scan = ttk.Button(bf, text="Scan", command=self._scan)
        self._btn_scan.pack(side=tk.RIGHT, padx=2)
        ttk.Button(bf, text="Export…", command=self._export).pack(
            side=tk.RIGHT, padx=2
        )
        ttk.Button(bf, text="Deselect", command=self._desel_all).pack(
            side=tk.RIGHT, padx=2
        )
        ttk.Button(bf, text="Select all", command=self._sel_all).pack(
            side=tk.RIGHT, padx=2
        )

    # ------------------------------------------------------------------
    # Path list
    # ------------------------------------------------------------------

    def _browse(self):
        path = filedialog.askdirectory(title="Select folder")
        if path:
            self._path_entry.delete(0, tk.END)
            self._path_entry.insert(0, path)
            self._add_path()

    def _add_path(self):
        raw = self._path_entry.get().strip().strip('"')
        if not raw:
            return
        if not os.path.isdir(raw):
            messagebox.showerror("Error", f"Invalid path:\n{raw}")
            return
        if raw not in self._path_list.get(0, tk.END):
            self._path_list.insert(tk.END, raw)
        self._path_entry.delete(0, tk.END)

    def _remove_path(self):
        for i in reversed(self._path_list.curselection()):
            self._path_list.delete(i)

    def _get_paths(self):
        return list(self._path_list.get(0, tk.END))

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _open_settings(self):
        SettingsDialog(self, self.settings)

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------

    def _scan(self):
        paths = self._get_paths()
        if not paths:
            messagebox.showwarning(
                "No paths", "Add at least one folder before scanning."
            )
            return
        self.results.clear()
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._clear_log()
        self.settings["delete_mode"] = self._mode.get()
        self._lock_ui(scanning=True)
        self._progress.start(10)
        for p in paths:
            self.settings.add_recent_path(p)

        self.scanner = Scanner(
            settings=self.settings,
            on_found=self._on_found,
            on_log=self._append_log,
            on_done=self._on_scan_done,
            on_progress=self._on_progress,
        )
        self.scanner.scan(paths)

    def _on_found(self, result: ScanResult):
        self.results.append(result)

        def _do():
            labels = {"empty": "Empty", "protected": "Protected", "error": "Error"}

            # Get size and date
            size_str = "0 B"
            date_str = "-"
            try:
                import os
                from filters import long_path, collect_ignorable_files

                lpath = long_path(result.path)
                mtime = os.path.getmtime(lpath)
                date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

                # Calculate "potential savings" from ignorable files
                total_bytes = 0
                for fpath in collect_ignorable_files(lpath, self.settings):
                    try:
                        total_bytes += os.path.getsize(long_path(fpath))
                    except Exception as _e:
                        import sys; print(f'[DEBUG] Ignored Exception: {_e}', file=sys.stderr)

                if total_bytes > 0:
                    if total_bytes < 1024:
                        size_str = f"{total_bytes} B"
                    elif total_bytes < 1024 * 1024:
                        size_str = f"{total_bytes/1024:.1f} KB"
                    else:
                        size_str = f"{total_bytes/(1024*1024):.1f} MB"
            except Exception as _e:
                import sys; print(f'[DEBUG] Ignored Exception: {_e}', file=sys.stderr)

            self._tree.insert(
                "",
                tk.END,
                iid=result.path,
                text=result.path,
                values=(
                    labels.get(result.status, result.status),
                    size_str,
                    date_str,
                    result.depth,
                ),
                tags=(result.status,),
            )

        self.after(0, _do)

    def _on_progress(self, path):
        short = os.path.basename(path) or path
        self.after(0, lambda: self._progress_label.config(text=short[:46]))

    def _on_scan_done(self, count):
        def _do():
            self._progress.stop()
            self._progress_label.config(text="")
            self._unlock_ui()
            empty = sum(1 for r in self.results if r.status == "empty")
            if empty > 0:
                self._btn_delete.config(state=tk.NORMAL)
            self._status.set(f"Scan complete - {empty} empty folders found.")

        self.after(0, _do)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def _delete(self):
        selected_ids = set(self._tree.selection())
        if selected_ids:
            to_process = [
                r
                for r in self.results
                if r.status == "empty" and r.path in selected_ids
            ]
        else:
            to_process = [r for r in self.results if r.status == "empty"]

        if not to_process:
            messagebox.showinfo(
                "No selection", "There are no empty folders to delete."
            )
            return

        mode = self._mode.get()
        self.settings["delete_mode"] = mode

        if mode == "permanent":
            if not messagebox.askyesno(
                "Confirm permanent deletion",
                f"Delete {len(to_process)} folders PERMANENTLY?\n\n"
                "This action CANNOT be undone.",
                icon="warning",
            ):
                return
        elif mode == "recycle":
            if not messagebox.askyesno(
                "Confirm",
                f"Send {len(to_process)} folders to the Recycle Bin?",
            ):
                return

        self._lock_ui(scanning=False)
        self._progress.start(10)

        self.cleaner = Cleaner(
            settings=self.settings,
            on_deleted=self._on_deleted,
            on_log=self._append_log,
            on_done=self._on_delete_done,
            on_error=self._on_delete_error,
        )
        self.cleaner.delete(to_process)

    def _on_deleted(self, result: ScanResult):
        def _do():
            try:
                vals = self._tree.item(result.path, "values")
                self._tree.item(
                    result.path,
                    tags=("deleted",),
                    values=("Deleted", vals[1] if vals else ""),
                )
            except Exception as _e:
                import sys; print(f'[DEBUG] Ignored Exception: {_e}', file=sys.stderr)

        self.after(0, _do)

    def _on_delete_error(self, result, exc):
        def _do():
            try:
                self._tree.item(result.path, tags=("error",))
            except Exception as _e:
                import sys; print(f'[DEBUG] Ignored Exception: {_e}', file=sys.stderr)

        self.after(0, _do)

    def _on_delete_done(self, count, total_bytes):
        def _do():
            self._progress.stop()
            self._progress_label.config(text="")
            self._unlock_ui()
            mb = total_bytes / (1024 * 1024)
            mode = self._mode.get()
            if mode == "simulate":
                msg = f"Simulation complete.\n\n{count} folders would be deleted."
            else:
                msg = (
                    f"Deletion complete.\n\n"
                    f"{count} folders processed\n{mb:.2f} MB freed"
                )
            self._status.set(f"{count} folders processed - {mb:.2f} MB freed.")
            self._play_done_sound()
            messagebox.showinfo("Process complete", msg)

        self.after(0, _do)

    # ------------------------------------------------------------------
    # Stop
    # ------------------------------------------------------------------

    def _stop(self):
        if self._scanning and self.scanner:
            self.scanner.stop()
        if self._deleting and self.cleaner:
            self.cleaner.stop()
        self._append_log(f"[{_ts()}] Operation stopped by the user.")
        self.after(0, self._unlock_ui)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _export(self):
        if not self.results:
            messagebox.showinfo("No data", "Run a scan first.")
            return
        path = filedialog.asksaveasfilename(
            title="Export results",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Texto", "*.txt"), ("Todos", "*.*")],
        )
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["Path", "Status", "Level"])
                    for r in self.results:
                        w.writerow([r.path, r.status, r.depth])
            else:
                with open(path, "w", encoding="utf-8") as f:
                    for r in self.results:
                        f.write(f"{r.status}\t{r.path}\n")
            self._status.set(f"Exported: {path}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))

    # ------------------------------------------------------------------
    # Tree helpers
    # ------------------------------------------------------------------

    def _sel_all(self):
        self._tree.selection_set(self._tree.get_children())

    def _desel_all(self):
        self._tree.selection_remove(self._tree.get_children())

    def _show_ctx(self, event):
        item = self._tree.identify_row(event.y)
        if item:
            self._tree.selection_add(item)
        self._ctx.post(event.x_root, event.y_root)

    def _open_explorer(self):
        sel = self._tree.selection()
        if not sel:
            return
        path = sel[0]
        target = path if os.path.exists(path) else os.path.dirname(path)
        if os.path.exists(target):
            os.startfile(target)

    # ------------------------------------------------------------------
    # Log
    # ------------------------------------------------------------------

    def _append_log(self, msg):
        def _do():
            self._log.config(state=tk.NORMAL)
            self._log.insert(tk.END, msg + "\n")
            self._log.see(tk.END)
            self._log.config(state=tk.DISABLED)

        self.after(0, _do)

    def _clear_log(self):
        self._log.config(state=tk.NORMAL)
        self._log.delete("1.0", tk.END)
        self._log.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # UI lock/unlock
    # ------------------------------------------------------------------

    def _lock_ui(self, scanning):
        self._scanning = scanning
        self._deleting = not scanning
        self._btn_scan.config(state=tk.DISABLED)
        self._btn_delete.config(state=tk.DISABLED)
        self._btn_stop.config(state=tk.NORMAL)
        self._status.set("Scanning…" if scanning else "Deleting…")

    def _unlock_ui(self):
        self._scanning = False
        self._deleting = False
        self._btn_scan.config(state=tk.NORMAL)
        self._btn_stop.config(state=tk.DISABLED)
        self._progress.stop()
