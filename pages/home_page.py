import tkinter as tk
from tkinter import ttk
from theme import Colors, Fonts


class HomePage(ttk.Frame):
    """Creative home page with feature cards."""

    CARDS = [
        ("◉", "Snapshot", "Parse oscilloscope snapshots\n"
         "from MDF/MF4 log files.\n"
         "Decode signals, export to\n"
         "Excel, and plot waveforms."),
        ("☑", "CRC Check", "Verify CRC/Checksum integrity\n"
         "of CAN bus log data.\n"
         "Supports CAN and CANFD\n"
         "with CRC-8 and CRC-16."),
        ("↔", "CAN Matcher", "Match CAN signals between\n"
         "DBC definitions and interface\n"
         "Excel sheets. Export matched\n"
         "results."),
    ]

    def __init__(self, parent, on_navigate=None, **kw):
        super().__init__(parent, **kw)
        self.on_navigate = on_navigate
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=30)
        self.rowconfigure(1, weight=70)

        header = tk.Frame(self, bg=Colors.BG, bd=0)
        header.grid(row=0, column=0, sticky="ew", pady=(60, 0))
        header.columnconfigure(0, weight=1)

        tk.Label(
            header, text="ParseTool", bg=Colors.BG, fg=Colors.TEXT,
            font=Fonts.TITLE,
        ).grid(row=0, column=0, pady=(0, 4))

        tk.Label(
            header, text="Automotive Data Analysis Suite",
            bg=Colors.BG, fg=Colors.TEXT_DIM, font=Fonts.BODY,
        ).grid(row=1, column=0)

        cards_frame = tk.Frame(self, bg=Colors.BG, bd=0)
        cards_frame.grid(row=1, column=0, sticky="n", pady=(48, 0))
        cards_frame.columnconfigure((0, 1, 2), weight=1, uniform="card")

        for idx, (icon, title, desc) in enumerate(self.CARDS):
            card = self._make_card(cards_frame, icon, title, desc, idx)
            card.grid(row=0, column=idx, padx=16, pady=10, sticky="n", ipadx=20, ipady=20)

    def _make_card(self, parent, icon, title, desc, idx):
        card = tk.Frame(parent, bg=Colors.SURFACE, bd=0, highlightthickness=0,
                        cursor="hand2")

        tk.Label(card, text=icon, bg=Colors.SURFACE, fg=Colors.ACCENT,
                 font=("Apple Color Emoji", 36)).pack(pady=(28, 8))

        tk.Label(card, text=title, bg=Colors.SURFACE, fg=Colors.TEXT,
                 font=Fonts.SUBHEAD).pack(pady=(0, 12))

        tk.Label(card, text=desc, bg=Colors.SURFACE, fg=Colors.TEXT_DIM,
                 font=Fonts.SMALL, justify="center").pack(pady=(0, 24))

        pages = ["snapshot", "crc", "can"]
        for w in card.winfo_children() + [card]:
            w.bind("<Button-1>", lambda e, p=pages[idx]: self._navigate(p))
            w.bind("<Enter>", lambda e, c=card: c.configure(bg=Colors.HOVER))
            w.bind("<Leave>", lambda e, c=card: c.configure(bg=Colors.SURFACE))

        return card

    def _navigate(self, page_key):
        if self.on_navigate:
            self.on_navigate(page_key)
