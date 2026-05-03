"""CRC checksum verification page."""

import os
import tkinter as tk
from tkinter import ttk, filedialog
import threading

from theme import Colors, Fonts
from engine import read_dbc, CRCValidator, CAN, CANFD


class CRCPage(ttk.Frame):
    """Page for CRC/Checksum verification of CAN bus data."""

    def __init__(self, parent, log=None, set_status=None, **kw):
        super().__init__(parent, **kw)
        self._log = log
        self._set_status = set_status or (lambda s: None)
        self._dbc_result = {}
        self._asc_path = ""
        self._can_type_var = tk.IntVar(value=CAN)

        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2), weight=0)

        # ── Row 0: DBC selection ──────────────────────────────────────
        dbc_frame = ttk.Frame(self, style="Card.TFrame")
        dbc_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        dbc_frame.columnconfigure(1, weight=1)

        ttk.Label(dbc_frame, text="DBC File",
                  font=Fonts.SUBHEAD, background=Colors.SURFACE).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        self._dbc_label = tk.Label(dbc_frame, text="No DBC loaded",
                                   bg=Colors.SURFACE, fg=Colors.TEXT_DIM,
                                   font=Fonts.SMALL, anchor="w")
        self._dbc_label.grid(row=1, column=0, columnspan=2, sticky="ew",
                             padx=16)
        ttk.Button(dbc_frame, text="Load DBC",
                   command=self._load_dbc).grid(
            row=0, column=1, sticky="e", padx=16, pady=(12, 4))

        # ── Row 1: Signal picker ──────────────────────────────────────
        picker_frame = ttk.Frame(self, style="Card.TFrame")
        picker_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        picker_frame.columnconfigure((0, 1, 2), weight=1)

        # CAN ID dropdown
        ttk.Label(picker_frame, text="CAN Message",
                  font=Fonts.SMALL, background=Colors.SURFACE).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 2))
        self._msg_var = tk.StringVar()
        self._msg_combo = ttk.Combobox(picker_frame, textvariable=self._msg_var,
                                       state="readonly")
        self._msg_combo.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
        self._msg_combo.bind("<<ComboboxSelected>>", self._on_msg_select)

        # Available signals
        ttk.Label(picker_frame, text="Available Signals",
                  font=Fonts.SMALL, background=Colors.SURFACE).grid(
            row=0, column=1, sticky="w", padx=8, pady=(12, 2))
        self._avail_list = tk.Listbox(picker_frame,
                                      bg=Colors.SURFACE1, fg=Colors.TEXT,
                                      font=Fonts.BODY, selectbackground=Colors.ACCENT,
                                      selectforeground=Colors.BG_CRUST,
                                      exportselection=False, relief="flat",
                                      highlightthickness=0)
        self._avail_list.grid(row=1, column=1, sticky="nsew", padx=8, pady=(0, 8))

        # Selected signals
        ttk.Label(picker_frame, text="Selected for CRC Check",
                  font=Fonts.SMALL, background=Colors.SURFACE).grid(
            row=0, column=2, sticky="w", padx=8, pady=(12, 2))
        self._sel_list = tk.Listbox(picker_frame,
                                    bg=Colors.SURFACE1, fg=Colors.TEXT,
                                    font=Fonts.BODY, selectbackground=Colors.ACCENT,
                                    selectforeground=Colors.BG_CRUST,
                                    exportselection=False, relief="flat",
                                    highlightthickness=0)
        self._sel_list.grid(row=1, column=2, sticky="nsew", padx=(8, 16), pady=(0, 8))

        # Add/Remove buttons
        btn_col = tk.Frame(picker_frame, bg=Colors.SURFACE)
        btn_col.grid(row=1, column=1, sticky="e", padx=(0, 12), pady=(0, 40))
        ttk.Button(btn_col, text="Add →", command=self._add_signal).pack(side="left", padx=2)
        ttk.Button(btn_col, text="← Remove", command=self._remove_signal).pack(side="left", padx=2)

        self.rowconfigure(1, weight=1)
        picker_frame.rowconfigure(1, weight=1)

        # ── Row 2: ASC file + CAN type + Start ────────────────────────
        run_frame = ttk.Frame(self, style="Card.TFrame")
        run_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(8, 16))
        run_frame.columnconfigure(1, weight=1)

        ttk.Label(run_frame, text="ASC Log File",
                  font=Fonts.SUBHEAD, background=Colors.SURFACE).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        self._asc_label = tk.Label(run_frame, text="No ASC loaded",
                                   bg=Colors.SURFACE, fg=Colors.TEXT_DIM,
                                   font=Fonts.SMALL, anchor="w")
        self._asc_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16)
        ttk.Button(run_frame, text="Load ASC",
                   command=self._load_asc).grid(
            row=0, column=1, sticky="e", padx=16, pady=(12, 4))

        # CAN type radio
        type_frame = tk.Frame(run_frame, bg=Colors.SURFACE)
        type_frame.grid(row=2, column=0, columnspan=2, sticky="w",
                        padx=16, pady=(8, 4))
        ttk.Radiobutton(type_frame, text="CAN (CRC-8 Profile 1)",
                        variable=self._can_type_var, value=CAN).pack(
            side="left", padx=(0, 16))
        ttk.Radiobutton(type_frame, text="CANFD (CRC-16 Profile 5)",
                        variable=self._can_type_var, value=CANFD).pack(
            side="left")

        # Start
        self._start_btn = ttk.Button(run_frame, text="Start CRC Check",
                                     command=self._start_crc,
                                     style="Accent.TButton")
        self._start_btn.grid(row=3, column=0, columnspan=2,
                             sticky="e", padx=16, pady=(8, 12))

        self._progress = ttk.Progressbar(run_frame, mode="indeterminate")
        self._progress.grid(row=3, column=0, sticky="ew", padx=16, pady=(8, 12))
        self._progress.grid_remove()

    def _load_dbc(self):
        path = filedialog.askopenfilename(
            title="Select DBC file",
            filetypes=[("DBC files", "*.dbc"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self._dbc_result = read_dbc(path)
            self._dbc_label.configure(text=os.path.basename(path))
            self._msg_combo["values"] = list(self._dbc_result.keys())
            self._avail_list.delete(0, "end")
            self._sel_list.delete(0, "end")
            self._log.success(f"DBC loaded: {len(self._dbc_result)} messages")
        except Exception as e:
            self._log.error(f"DBC parse error: {e}")

    def _on_msg_select(self, event=None):
        msg_name = self._msg_var.get()
        self._avail_list.delete(0, "end")
        if msg_name in self._dbc_result:
            for sig in self._dbc_result[msg_name]["signal"]:
                self._avail_list.insert("end", sig)

    def _add_signal(self):
        sel = self._avail_list.curselection()
        if sel:
            item = self._avail_list.get(sel[0])
            full = f"{self._msg_var.get()}.{item}"
            existing = list(self._sel_list.get(0, "end"))
            if full not in existing:
                self._sel_list.insert("end", full)

    def _remove_signal(self):
        sel = self._sel_list.curselection()
        if sel:
            self._sel_list.delete(sel[0])

    def _load_asc(self):
        path = filedialog.askopenfilename(
            title="Select ASC log file",
            filetypes=[("ASC files", "*.asc"), ("All files", "*.*")],
        )
        if path:
            self._asc_path = path
            self._asc_label.configure(text=os.path.basename(path))
            self._log.info(f"ASC file selected: {path}")

    def _start_crc(self):
        if not self._asc_path:
            self._log.warn("Please select an ASC file first")
            return
        items = list(self._sel_list.get(0, "end"))
        if not items:
            self._log.warn("Please add at least one signal to check")
            return

        can_type = self._can_type_var.get()

        # Validate signals
        can_ids = []
        for item in items:
            msg_name, sig_name = item.split(".")
            msg = self._dbc_result.get(msg_name, {})
            sig = msg.get("signal", {}).get(sig_name, {})
            msglen = int(msg.get("msglen", 0))
            siglen = int(sig.get("siglen", 0))
            endbit = int(sig.get("endbit", 0))
            byteorder = sig.get("byteorder", "0")

            valid = False
            if can_type == CANFD:
                if byteorder == "0" and endbit == 7 and siglen == 16 and msglen == 64:
                    valid = True
                elif byteorder != "0" and endbit == 0 and siglen == 16 and msglen == 64:
                    valid = True
            else:
                if byteorder == "0" and endbit == 63 and siglen == 8 and msglen == 8:
                    valid = True
                elif byteorder != "0" and endbit == 56 and siglen == 8 and msglen == 8:
                    valid = True

            if not valid:
                self._log.warn(f"{item} may not be a CRC/Checksum signal")
            can_ids.append(msg.get("id", ""))

        can_ids = list(set(can_ids))
        self._start_btn.configure(state="disabled")
        self._progress.grid()
        self._progress.start()
        self._set_status("Running CRC check...")

        def task():
            validator = CRCValidator(can_ids, self._asc_path, can_type)
            results = validator.run()
            self.after(0, lambda: self._show_results(results))
            self.after(0, self._done)

        threading.Thread(target=task, daemon=True).start()

    def _show_results(self, results):
        for r in results:
            if "FAILED" in r:
                self._log.error(r)
            elif "passed" in r.lower():
                self._log.success(r)
            else:
                self._log.warn(r)

    def _done(self):
        self._progress.stop()
        self._progress.grid_remove()
        self._start_btn.configure(state="normal")
        self._set_status("Ready")
