"""Snapshot data parsing page."""

import os
import tkinter as tk
from tkinter import ttk, filedialog
import threading

from theme import Colors, Fonts
from engine import SnapShotEngine, list_projects


class SnapshotPage(ttk.Frame):
    """Page for parsing and visualizing snapshot (OSC) data."""

    def __init__(self, parent, log=None, set_status=None, **kw):
        super().__init__(parent, **kw)
        self._log = log
        self._set_status = set_status or (lambda s: None)
        self._filepath = ""
        self._project_var = tk.StringVar(value="nidec")
        self._bigdata_var = tk.BooleanVar(value=False)
        self._signal_var = tk.StringVar(value="")
        self._plot_win = None  # current plot popup window
        self._build()

    def _build(self):
        # Full-width control panel (no embedded plot area)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self, style="Card.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        ttk.Label(left, text="Project Configuration", font=Fonts.SUBHEAD,
                  background=Colors.SURFACE).pack(anchor="w", padx=16,
                  pady=(16, 12))

        projects = list_projects()
        proj_frame = tk.Frame(left, bg=Colors.SURFACE)
        proj_frame.pack(fill="x", padx=16, pady=(0, 12))
        for key, desc in projects.items():
            rb = ttk.Radiobutton(
                proj_frame, text=f"{key.upper()} — {desc}",
                variable=self._project_var, value=key,
            )
            rb.pack(anchor="w", pady=2)

        bigdata_frame = tk.Frame(left, bg=Colors.SURFACE)
        bigdata_frame.pack(fill="x", padx=16, pady=(0, 12))
        ttk.Checkbutton(
            bigdata_frame, text="Parse bigdata signals",
            variable=self._bigdata_var,
        ).pack(anchor="w")

        ttk.Separator(left, orient="horizontal").pack(fill="x", padx=16, pady=8)

        ttk.Label(left, text="Signal Pattern", font=Fonts.SUBHEAD,
                  background=Colors.SURFACE).pack(anchor="w", padx=16, pady=(8, 4))
        hint = tk.Label(left, text="Use * as wildcard, e.g. *OSC*",
                        bg=Colors.SURFACE, fg=Colors.TEXT_DIM, font=Fonts.SMALL)
        hint.pack(anchor="w", padx=16)
        entry = ttk.Entry(left, textvariable=self._signal_var, width=30)
        entry.pack(fill="x", padx=16, pady=(4, 12))
        entry.insert(0, "")

        ttk.Separator(left, orient="horizontal").pack(fill="x", padx=16, pady=8)

        ttk.Label(left, text="Data File", font=Fonts.SUBHEAD,
                  background=Colors.SURFACE).pack(anchor="w", padx=16, pady=(8, 4))
        self._file_label = tk.Label(left, text="No file selected",
                                    bg=Colors.SURFACE, fg=Colors.TEXT_DIM,
                                    font=Fonts.SMALL, wraplength=500,
                                    justify="left")
        self._file_label.pack(anchor="w", padx=16)

        btn_frame = tk.Frame(left, bg=Colors.SURFACE)
        btn_frame.pack(fill="x", padx=16, pady=(8, 16))
        ttk.Button(btn_frame, text="Select MDF/MF4 File",
                   command=self._select_file, style="Accent.TButton",
                   ).pack(side="left", padx=(0, 8))
        self._start_btn = ttk.Button(btn_frame, text="Start Parse",
                                     command=self._start_parse)
        self._start_btn.pack(side="left")

        self._progress = ttk.Progressbar(left, mode="indeterminate")
        self._progress.pack(fill="x", padx=16, pady=(0, 16))

    def _select_file(self):
        path = filedialog.askopenfilename(
            title="Select snapshot data file",
            filetypes=[("Data files", "*.mdf *.dat *.mf4"), ("All files", "*.*")],
        )
        if path:
            self._filepath = path
            self._file_label.configure(text=os.path.basename(path))
            self._log.info(f"Selected file: {path}")

    def _start_parse(self):
        if not self._filepath:
            self._log.warn("Please select a data file first")
            return
        pattern = self._signal_var.get().strip()
        if not pattern:
            pattern = "*"
        if "*" not in pattern:
            pattern = f"*{pattern}*"

        self._start_btn.configure(state="disabled")
        self._progress.start()
        self._set_status("Parsing snapshot data...")

        engine = SnapShotEngine(
            self._filepath,
            self._project_var.get(),
            self._bigdata_var.get(),
            pattern,
            log_callback=lambda msg, level="INFO": getattr(
                self._log, level.lower(), self._log.info)(msg),
        )

        def task():
            result = engine.run()
            if result == "OK":
                self._log.success("OSC data parsing completed")
                big_result = engine.run_bigdata()
                if big_result == "OK":
                    self._log.success("Bigdata parsing completed")
                elif big_result == "NG":
                    self._log.error("Bigdata parsing failed")
            else:
                self._log.error("OSC data parsing failed")

            self.after(0, lambda: self._show_plot(engine))
            self.after(0, self._done)

        threading.Thread(target=task, daemon=True).start()

    def _show_plot(self, engine):
        # Close previous plot window if open
        if self._plot_win and self._plot_win.winfo_exists():
            self._plot_win.destroy()
        self._plot_win = None

        try:
            win = tk.Toplevel(self)
            win.title(f"Snapshot Plot — {engine.basename}")
            win.geometry("1100x780")
            win.minsize(700, 500)
            win.configure(bg=Colors.BG_CRUST)

            # Dark backdrop
            top_bar = tk.Frame(win, bg=Colors.BG_CRUST, bd=0, height=32)
            top_bar.pack(fill="x", side="top")
            top_bar.pack_propagate(False)
            tk.Label(top_bar, text=f"  {engine.basename}",
                     bg=Colors.BG_CRUST, fg=Colors.TEXT_DIM,
                     font=Fonts.SMALL).pack(side="left")
            close_btn = tk.Label(top_bar, text="✕", bg=Colors.BG_CRUST,
                                fg=Colors.TEXT_DIM, font=Fonts.SMALL,
                                padx=14, pady=4, cursor="hand2")
            close_btn.pack(side="right")
            close_btn.bind("<Button-1>", lambda e: win.destroy())
            close_btn.bind("<Enter>",
                           lambda e, b=close_btn: b.configure(bg=Colors.SURFACE1, fg=Colors.TEXT))
            close_btn.bind("<Leave>",
                           lambda e, b=close_btn: b.configure(bg=Colors.BG_CRUST, fg=Colors.TEXT_DIM))
            top_bar.bind("<ButtonPress-1>", lambda e: self._start_drag(win, e))
            top_bar.bind("<B1-Motion>", lambda e: self._on_drag(win, e))

            plot_frame = tk.Frame(win, bg="#1e1e2e")
            plot_frame.pack(fill="both", expand=True)

            canvas = engine.plot(master=plot_frame)
            if canvas:
                canvas.get_tk_widget().pack(fill="both", expand=True)

            win.protocol("WM_DELETE_WINDOW", self._on_plot_close)
            self._plot_win = win
        except Exception as e:
            self._log.error(f"Plot error: {e}")

    def _start_drag(self, win, event):
        win._drag_x = event.x
        win._drag_y = event.y

    def _on_drag(self, win, event):
        x = win.winfo_x() + (event.x - win._drag_x)
        y = win.winfo_y() + (event.y - win._drag_y)
        win.geometry(f"+{x}+{y}")

    def _on_plot_close(self):
        if self._plot_win:
            self._plot_win.destroy()
        self._plot_win = None

    def _done(self):
        self._progress.stop()
        self._start_btn.configure(state="normal")
        self._set_status("Ready")
