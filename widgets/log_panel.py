import tkinter as tk
from tkinter import ttk
import time
from theme import Colors, Fonts


class LogPanel(ttk.Frame):
    """Color-coded scrolling log panel."""

    LEVEL_COLORS = {
        "INFO":    Colors.TEXT,
        "SUCCESS": Colors.SUCCESS,
        "WARN":    Colors.WARNING,
        "ERROR":   Colors.ERROR,
    }

    def __init__(self, parent, max_lines=2000, **kw):
        super().__init__(parent, **kw)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.text = tk.Text(
            self,
            bg=Colors.BG_CRUST,
            fg=Colors.TEXT,
            insertbackground=Colors.TEXT,
            font=Fonts.MONO,
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=10,
            wrap="word",
            state="disabled",
            maxundo=0,
        )
        self.text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)

        self.text.tag_configure("INFO", foreground=Colors.TEXT)
        self.text.tag_configure("SUCCESS", foreground=Colors.SUCCESS)
        self.text.tag_configure("WARN", foreground=Colors.WARNING)
        self.text.tag_configure("ERROR", foreground=Colors.ERROR)
        self.text.tag_configure("timestamp", foreground=Colors.TEXT_MUTED,
                                font=Fonts.SMALL)
        self._max_lines = max_lines

    def _write(self, level: str, msg: str):
        ts = time.strftime("%H:%M:%S")
        self.text.configure(state="normal")
        self.text.insert("end", f"[{ts}] ", "timestamp")
        self.text.insert("end", f"[{level}] ", level)
        self.text.insert("end", f"{msg}\n")
        self.text.see("end")
        self._trim()
        self.text.configure(state="disabled")

    def info(self, msg: str):
        self._write("INFO", msg)

    def success(self, msg: str):
        self._write("SUCCESS", msg)

    def warn(self, msg: str):
        self._write("WARN", msg)

    def error(self, msg: str):
        self._write("ERROR", msg)

    def clear(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def _trim(self):
        lines = int(self.text.index("end-1c").split(".")[0])
        if lines > self._max_lines:
            self.text.delete("1.0", f"{lines - self._max_lines}.0")
