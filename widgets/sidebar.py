import tkinter as tk
from tkinter import ttk
from theme import Colors, Fonts


class Sidebar(ttk.Frame):
    """Creative sidebar with icon navigation and hover animations."""

    NAV_ITEMS = [
        ("⌂",  "Home",     "home"),
        ("◉",  "Snapshot", "snapshot"),
        ("☑",  "CRC",      "crc"),
        ("↔",  "CAN",      "can"),
    ]

    def __init__(self, parent, on_navigate=None, active_key="home", **kw):
        super().__init__(parent, style="Sidebar.TFrame", **kw)
        self.on_navigate = on_navigate
        self._active_idx = 0
        self._buttons = []

        target_idx = 0
        for i, (_, _, key) in enumerate(self.NAV_ITEMS):
            if key == active_key:
                target_idx = i
                break

        self._build(initial_idx=target_idx, initial_key=active_key)
        self.pack_propagate(False)

    def _build(self, initial_idx=0, initial_key="home"):
        header = tk.Frame(self, bg=Colors.BG_DEEP, bd=0)
        header.pack(fill="x", pady=(24, 32), padx=10)

        logo = tk.Label(
            header, text="P", bg=Colors.ACCENT, fg=Colors.BG_CRUST,
            font=("Helvetica", 26, "bold"), width=2, height=1,
        )
        logo.pack()

        title = tk.Label(
            header, text="ParseTool", bg=Colors.BG_DEEP, fg=Colors.TEXT,
            font=Fonts.SUBHEAD,
        )
        title.pack(pady=(8, 0))

        ver = tk.Label(
            header, text="v2.0", bg=Colors.BG_DEEP, fg=Colors.TEXT_MUTED,
            font=Fonts.SMALL,
        )
        ver.pack()

        tk.Frame(self, bg=Colors.BORDER, height=1).pack(fill="x", padx=20, pady=(0, 16))

        btn_frame = tk.Frame(self, bg=Colors.BG_DEEP, bd=0)
        btn_frame.pack(fill="both", expand=True, padx=10)

        for idx, (icon, label, key) in enumerate(self.NAV_ITEMS):
            btn = self._make_nav_btn(btn_frame, icon, label, idx)
            btn.pack(fill="x", pady=2)
            self._buttons.append(btn)

        self._select(initial_idx, initial_key)

    def _make_nav_btn(self, parent, icon, label, idx):
        frame = tk.Frame(parent, bg=Colors.BG_DEEP, bd=0, cursor="hand2")

        canvas = tk.Canvas(frame, bg=Colors.BG_DEEP, bd=0, highlightthickness=0,
                           width=4, height=30)
        canvas.pack(side="left", padx=(2, 6))
        self._setup_indicator_canvas(canvas, idx)

        icon_lbl = tk.Label(frame, text=icon, bg=Colors.BG_DEEP, fg=Colors.TEXT_DIM,
                            font=("Apple Color Emoji", 16))
        icon_lbl.pack(side="left", padx=(4, 4))

        text_lbl = tk.Label(frame, text=label, bg=Colors.BG_DEEP, fg=Colors.TEXT_DIM,
                            font=Fonts.SIDEBAR, anchor="w", width=8)
        text_lbl.pack(side="left")

        for w in (frame, canvas, icon_lbl, text_lbl):
            w.bind("<Button-1>", lambda e, f=frame, i=idx: self._on_frame_click(f, i))
            w.bind("<Enter>", lambda e, f=frame, c=canvas, il=icon_lbl, tl=text_lbl:
                   self._on_hover_enter(f, c, il, tl))
            w.bind("<Leave>", lambda e, f=frame, c=canvas, il=icon_lbl, tl=text_lbl, i=idx:
                   self._on_hover_leave(f, c, il, tl, i))

        frame.icon = icon_lbl
        frame.text = text_lbl
        frame.canvas = canvas
        frame.idx = idx
        return frame

    def _setup_indicator_canvas(self, canvas, idx):
        canvas.indicator = canvas.create_rectangle(0, 5, 4, 25, fill=Colors.BG_DEEP,
                                                    outline="", tags="indicator")

    def _on_frame_click(self, frame, idx):
        self._select(idx, self.NAV_ITEMS[idx][2])

    def _on_hover_enter(self, frame, canvas, icon_lbl, text_lbl):
        if frame.idx != self._active_idx:
            frame.configure(bg=Colors.HOVER)
            canvas.configure(bg=Colors.HOVER)
            icon_lbl.configure(bg=Colors.HOVER)
            text_lbl.configure(bg=Colors.HOVER)

    def _on_hover_leave(self, frame, canvas, icon_lbl, text_lbl, idx):
        if idx != self._active_idx:
            frame.configure(bg=Colors.BG_DEEP)
            canvas.configure(bg=Colors.BG_DEEP)
            icon_lbl.configure(bg=Colors.BG_DEEP)
            text_lbl.configure(bg=Colors.BG_DEEP)

    def _select(self, idx, key):
        self._active_idx = idx
        for i, btn in enumerate(self._buttons):
            active = (i == idx)
            bg = Colors.ACCENT if active else Colors.BG_DEEP
            fg = Colors.BG_CRUST if active else Colors.TEXT_DIM
            btn.configure(bg=bg)
            btn.icon.configure(bg=bg, fg=fg)
            btn.text.configure(bg=bg, fg=fg)
            btn.canvas.itemconfig(btn.canvas.indicator,
                                  fill=Colors.BG_CRUST if active else Colors.BG_DEEP)
            btn.canvas.configure(bg=bg)

        if self.on_navigate:
            self.on_navigate(key)
