import tkinter as tk
from tkinter import ttk


class Colors:
    """Theme-aware color palette. Swapped by apply_theme()."""

    BG         = "#1e1e2e"
    BG_DEEP    = "#181825"
    BG_CRUST   = "#11111b"
    SURFACE    = "#252536"
    SURFACE1   = "#313244"
    SURFACE2   = "#45475a"
    OVERLAY    = "#585b70"

    TEXT       = "#cdd6f4"
    TEXT_DIM   = "#a6adc8"
    TEXT_MUTED = "#6c7086"

    ACCENT     = "#89b4fa"
    ACCENT_DIM = "#74a0e0"
    SUCCESS    = "#a6e3a1"
    WARNING    = "#f9e2af"
    ERROR      = "#f38ba8"

    BORDER     = "#313244"
    HOVER      = "#363650"


# Light palette kept separately for the swap
_LIGHT = {
    "BG":         "#eff1f5",
    "BG_DEEP":    "#e6e9ef",
    "BG_CRUST":   "#dce0e8",
    "SURFACE":    "#ccd0da",
    "SURFACE1":   "#bcc0cc",
    "SURFACE2":   "#acb0be",
    "OVERLAY":    "#9ca0b0",
    "TEXT":       "#4c4f69",
    "TEXT_DIM":   "#5c5f77",
    "TEXT_MUTED": "#8c8fa1",
    "ACCENT":     "#1e66f5",
    "ACCENT_DIM": "#4c8af5",
    "SUCCESS":    "#40a02b",
    "WARNING":    "#df8e1d",
    "ERROR":      "#d20f39",
    "BORDER":     "#ccd0da",
    "HOVER":      "#dce0e8",
}

_DARK = {
    "BG":         "#1e1e2e",
    "BG_DEEP":    "#181825",
    "BG_CRUST":   "#11111b",
    "SURFACE":    "#252536",
    "SURFACE1":   "#313244",
    "SURFACE2":   "#45475a",
    "OVERLAY":    "#585b70",
    "TEXT":       "#cdd6f4",
    "TEXT_DIM":   "#a6adc8",
    "TEXT_MUTED": "#6c7086",
    "ACCENT":     "#89b4fa",
    "ACCENT_DIM": "#74a0e0",
    "SUCCESS":    "#a6e3a1",
    "WARNING":    "#f9e2af",
    "ERROR":      "#f38ba8",
    "BORDER":     "#313244",
    "HOVER":      "#363650",
}


class Fonts:
    HEADING   = ("Helvetica", 22, "bold")
    SUBHEAD   = ("Helvetica", 14, "bold")
    BODY      = ("Helvetica", 12)
    SMALL     = ("Helvetica", 10)
    MONO      = ("Menlo", 11)
    TITLE     = ("Helvetica", 28, "bold")
    SIDEBAR   = ("Helvetica", 13)
    STATUS    = ("Helvetica", 10)


def apply_theme(root: tk.Tk, dark: bool = True):
    """Apply the theme and return a toggle callback."""
    _swap_colors(dark)
    _apply_ttk_style(root)

    def toggle():
        nonlocal dark
        dark = not dark
        _swap_colors(dark)
        _apply_ttk_style(root)
        _update_tk_widgets(root)
        return dark

    return toggle


def _swap_colors(dark: bool):
    src = _DARK if dark else _LIGHT
    for k, v in src.items():
        setattr(Colors, k, v)


def _apply_ttk_style(root: tk.Tk):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=Colors.BG, foreground=Colors.TEXT, font=Fonts.BODY)

    style.configure("TFrame", background=Colors.BG)
    style.configure("TLabel", background=Colors.BG, foreground=Colors.TEXT, font=Fonts.BODY)
    style.configure("TButton",
                    background=Colors.SURFACE1,
                    foreground=Colors.TEXT,
                    borderwidth=0,
                    focusthickness=0,
                    padding=(12, 6),
                    font=Fonts.BODY,
                    relief="flat")
    style.map("TButton",
              background=[("active", Colors.ACCENT), ("pressed", Colors.ACCENT_DIM)],
              foreground=[("active", Colors.BG_CRUST)])

    style.configure("Accent.TButton",
                    background=Colors.ACCENT,
                    foreground=Colors.BG_CRUST,
                    font=Fonts.SUBHEAD,
                    padding=(18, 10))
    style.map("Accent.TButton",
              background=[("active", Colors.ACCENT_DIM), ("pressed", Colors.SURFACE2)])

    style.configure("TEntry",
                    fieldbackground=Colors.SURFACE,
                    foreground=Colors.TEXT,
                    borderwidth=1,
                    relief="solid",
                    padding=8,
                    font=Fonts.BODY)
    style.map("TEntry",
              fieldbackground=[("focus", Colors.SURFACE1)])

    style.configure("TCombobox",
                    fieldbackground=Colors.SURFACE,
                    background=Colors.SURFACE1,
                    foreground=Colors.TEXT,
                    arrowcolor=Colors.TEXT,
                    borderwidth=1,
                    relief="solid",
                    padding=6)
    style.map("TCombobox",
              fieldbackground=[("readonly", Colors.SURFACE)],
              foreground=[("readonly", Colors.TEXT)])

    root.option_add("*TCombobox*Listbox.background", Colors.SURFACE)
    root.option_add("*TCombobox*Listbox.foreground", Colors.TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", Colors.ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", Colors.BG_CRUST)
    root.option_add("*TCombobox*Listbox.font", Fonts.BODY)

    style.configure("TRadiobutton",
                    background=Colors.BG,
                    foreground=Colors.TEXT,
                    font=Fonts.BODY)
    style.map("TRadiobutton",
              background=[("active", Colors.BG)],
              foreground=[("selected", Colors.ACCENT)])

    style.configure("TNotebook", background=Colors.BG, borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=Colors.SURFACE,
                    foreground=Colors.TEXT_DIM,
                    padding=(16, 8),
                    font=Fonts.BODY,
                    borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", Colors.ACCENT)],
              foreground=[("selected", Colors.BG_CRUST)],
              expand=[("selected", [0, 0, 0, 0])])

    style.configure("TProgressbar",
                    background=Colors.ACCENT,
                    troughcolor=Colors.SURFACE,
                    borderwidth=0,
                    thickness=8)

    style.configure("TSeparator", background=Colors.BORDER)

    style.configure("Card.TFrame",
                    background=Colors.SURFACE,
                    relief="flat",
                    borderwidth=1)

    style.configure("Sidebar.TFrame", background=Colors.BG_DEEP)

    style.configure("TScale", background=Colors.BG, troughcolor=Colors.SURFACE1)
    style.configure("TCheckbutton",
                    background=Colors.BG,
                    foreground=Colors.TEXT,
                    font=Fonts.BODY)
    style.map("TCheckbutton",
              background=[("active", Colors.BG)],
              foreground=[("selected", Colors.ACCENT)])


def _update_tk_widgets(widget: tk.Widget):
    """Walk the widget tree and refresh bg/fg for raw tk widgets."""
    _refresh_one(widget)
    for child in widget.winfo_children():
        _update_tk_widgets(child)


def _refresh_one(w: tk.Widget):
    """Swap a single tk widget's colors if they match a known theme color."""
    cls = w.winfo_class()

    bg_map = {
        "Frame":       ("BG_DEEP", "BG"),
        "Label":       ("BG",),
        "Canvas":      ("BG_DEEP",),
        "Text":        ("BG_CRUST",),
        "Listbox":     ("SURFACE1",),
        "Toplevel":    ("BG",),
    }
    if cls in bg_map:
        key = bg_map[cls][0]
        try:
            w.configure(bg=getattr(Colors, key))
        except tk.TclError:
            pass

    if cls == "Listbox":
        try:
            w.configure(fg=Colors.TEXT, selectbackground=Colors.ACCENT,
                        selectforeground=Colors.BG_CRUST)
        except tk.TclError:
            pass

    if cls == "Text":
        try:
            w.configure(fg=Colors.TEXT, insertbackground=Colors.TEXT)
        except tk.TclError:
            pass

    if cls == "Label":
        try:
            cur_fg = w.cget("fg")
            # Only update if it looks like a theme colour (not black/white defaults)
            if cur_fg not in ("black", "white", "systemTextColor"):
                w.configure(fg=Colors.TEXT)
        except tk.TclError:
            pass
