#!/usr/bin/env python3
"""ParseTool — Automotive Data Analysis Suite
A modern tkinter-based desktop application for automotive ECU data analysis.
"""

import tkinter as tk
from tkinter import ttk

from theme import Colors, Fonts, apply_theme
from widgets import Sidebar, LogPanel
from pages import HomePage


class ParseTool(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("ParseTool")
        self.geometry("1060x720")
        self.minsize(860, 560)
        self.configure(bg=Colors.BG)

        self._toggle_theme = apply_theme(self, dark=True)

        self._dark = True
        self._current_page_key = "home"
        self._build_chrome()
        self._build_layout()
        self.log.info("ParseTool v2.0 started — ready.")

    # ── Chrome ────────────────────────────────────────────────────────
    def _build_chrome(self):
        self.title_bar = tk.Frame(self, bg=Colors.BG_CRUST, bd=0, height=36)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        self.title_bar._theme_slot = "BG_CRUST"

        tk.Label(self.title_bar, text="  ParseTool", bg=Colors.BG_CRUST,
                 fg=Colors.TEXT_DIM, font=Fonts.SMALL).pack(side="left")

        win_btns = tk.Frame(self.title_bar, bg=Colors.BG_CRUST, bd=0)
        win_btns.pack(side="right")
        win_btns._theme_slot = "BG_CRUST"

        # Theme toggle
        self._theme_btn = tk.Label(
            win_btns, text="☀", bg=Colors.BG_CRUST, fg=Colors.WARNING,
            font=Fonts.SMALL, padx=12, pady=5, cursor="hand2",
        )
        self._theme_btn.pack(side="right")
        self._theme_btn.bind("<Button-1>", lambda e: self._on_theme_toggle())
        self._theme_btn.bind("<Enter>", lambda e: self._theme_btn.configure(bg=Colors.SURFACE1))
        self._theme_btn.bind("<Leave>", lambda e: self._theme_btn.configure(bg=Colors.BG_CRUST))

        for symbol, cmd in [("—", self.iconify), ("□", self._toggle_maximize),
                            ("✕", self.destroy)]:
            btn = tk.Label(win_btns, text=symbol, bg=Colors.BG_CRUST,
                           fg=Colors.TEXT_DIM, font=Fonts.SMALL,
                           padx=14, pady=5, cursor="hand2")
            btn.pack(side="right")
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=Colors.SURFACE1))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=Colors.BG_CRUST))

        self.title_bar.bind("<ButtonPress-1>", self._start_move)
        self.title_bar.bind("<ButtonRelease-1>", self._stop_move)
        self.title_bar.bind("<B1-Motion>", self._on_move)

        self.status_bar = tk.Frame(self, bg=Colors.BG_DEEP, bd=0, height=28)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)
        self.status_bar._theme_slot = "BG_DEEP"
        self.status_label = tk.Label(self.status_bar, text=" Ready",
                                     bg=Colors.BG_DEEP, fg=Colors.TEXT_MUTED,
                                     font=Fonts.STATUS, anchor="w", padx=12)
        self.status_label.pack(fill="x")
        self.status_label._theme_slot = "BG_DEEP"

    # ── Layout ────────────────────────────────────────────────────────
    def _build_layout(self):
        self._body = tk.Frame(self, bg=Colors.BG, bd=0)
        self._body.pack(fill="both", expand=True)

        right = tk.Frame(self._body, bg=Colors.BG, bd=0)

        self.content = tk.Frame(right, bg=Colors.BG, bd=0)
        self.content.pack(fill="both", expand=True)

        sep = ttk.Separator(right, orient="horizontal")
        sep.pack(fill="x", padx=4, pady=0)

        self.log = LogPanel(right, height=140)
        self.log.pack(fill="x", side="bottom", padx=12, pady=12)

        self.sidebar = Sidebar(self._body, on_navigate=self.navigate_to, width=180)
        self.sidebar.pack(side="left", fill="y")

        self._sep = tk.Frame(self._body, bg=Colors.BORDER, width=1)
        self._sep.pack(side="left", fill="y")

        right.pack(side="left", fill="both", expand=True)

    # ── Navigation ────────────────────────────────────────────────────
    def navigate_to(self, page_key: str):
        self._current_page_key = page_key
        self._clear_content()
        if page_key == "home":
            page = HomePage(self.content, on_navigate=self.navigate_to)
            self.status_label.configure(text=" Ready")
        elif page_key == "snapshot":
            from pages import SnapshotPage
            page = SnapshotPage(self.content, log=self.log, set_status=self._set_status)
            self.status_label.configure(text=" Snapshot Mode")
        elif page_key == "crc":
            from pages import CRCPage
            page = CRCPage(self.content, log=self.log, set_status=self._set_status)
            self.status_label.configure(text=" CRC Check Mode")
        elif page_key == "can":
            from pages import CANPage
            page = CANPage(self.content, log=self.log, set_status=self._set_status)
            self.status_label.configure(text=" CAN Matcher Mode")
        page.pack(fill="both", expand=True)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _set_status(self, text: str):
        self.status_label.configure(text=f" {text}")

    # ── Theme toggle ──────────────────────────────────────────────────
    def _on_theme_toggle(self):
        self._dark = self._toggle_theme()
        self.configure(bg=Colors.BG)
        self._theme_btn.configure(
            text="☀" if self._dark else "🌙",
            bg=Colors.BG_CRUST,
            fg=Colors.WARNING if self._dark else Colors.ACCENT,
        )
        self.title_bar.configure(bg=Colors.BG_CRUST)
        self.status_bar.configure(bg=Colors.BG_DEEP)
        self.status_label.configure(bg=Colors.BG_DEEP, fg=Colors.TEXT_MUTED)
        self._sep.configure(bg=Colors.BORDER)
        # Rebuild sidebar with new theme, keeping current page selection
        self.sidebar.destroy()
        self.sidebar = Sidebar(self._body, on_navigate=self.navigate_to,
                               active_key=self._current_page_key, width=180)
        self.sidebar.pack(side="left", fill="y", before=self._sep)
        # Rebuild current page with new theme
        self.navigate_to(self._current_page_key)

    # ── Window management ─────────────────────────────────────────────
    def _start_move(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _stop_move(self, event):
        self._drag_x = None
        self._drag_y = None

    def _on_move(self, event):
        x = self.winfo_x() + (event.x - self._drag_x)
        y = self.winfo_y() + (event.y - self._drag_y)
        self.geometry(f"+{x}+{y}")

    def _toggle_maximize(self):
        if self.attributes("-fullscreen"):
            self.attributes("-fullscreen", False)
            self.geometry("1060x720")
        else:
            self.attributes("-fullscreen", True)


if __name__ == "__main__":
    app = ParseTool()
    app.mainloop()
