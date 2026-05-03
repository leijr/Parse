"""CAN signal matching page."""

import os
import tkinter as tk
from tkinter import ttk, filedialog
import threading

import pandas as pd
from theme import Colors, Fonts
from engine import read_dbc, dbc_to_excel, match_can_in, match_can_out


class CANPage(ttk.Frame):
    """Page for CAN signal matching and DBC conversion."""

    def __init__(self, parent, log=None, set_status=None, **kw):
        super().__init__(parent, **kw)
        self._log = log
        self._set_status = set_status or (lambda s: None)
        self._dbc_result = {}
        self._dbc_path = ""
        self._canin_path = ""
        self._canout_path = ""

        self._canin_sheets: list[str] = []
        self._canout_sheets: list[str] = []

        self._ecu_var = tk.StringVar()
        self._canin_sheet_var = tk.StringVar()
        self._canout_sheet_var = tk.StringVar()

        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2, 3), weight=0)

        # ── DBC Section ───────────────────────────────────────────────
        dbc_frame = ttk.Frame(self, style="Card.TFrame")
        dbc_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        dbc_frame.columnconfigure(1, weight=1)

        ttk.Label(dbc_frame, text="DBC File",
                  font=Fonts.SUBHEAD, background=Colors.SURFACE).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        self._dbc_label = tk.Label(dbc_frame, text="No DBC loaded",
                                   bg=Colors.SURFACE, fg=Colors.TEXT_DIM,
                                   font=Fonts.SMALL, anchor="w")
        self._dbc_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16)

        btn_row = tk.Frame(dbc_frame, bg=Colors.SURFACE)
        btn_row.grid(row=0, column=1, sticky="e", padx=16, pady=(12, 4))
        ttk.Button(btn_row, text="Load DBC", command=self._load_dbc).pack(side="right")

        # ECU selector
        ttk.Label(dbc_frame, text="Target ECU",
                  font=Fonts.SMALL, background=Colors.SURFACE).grid(
            row=2, column=0, sticky="w", padx=16, pady=(8, 2))
        self._ecu_combo = ttk.Combobox(dbc_frame, textvariable=self._ecu_var,
                                       state="readonly")
        self._ecu_combo.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 12))

        # ── CAN IN Section ────────────────────────────────────────────
        cin_frame = ttk.Frame(self, style="Card.TFrame")
        cin_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        cin_frame.columnconfigure(1, weight=1)

        ttk.Label(cin_frame, text="CAN IN Interface (optional)",
                  font=Fonts.SUBHEAD, background=Colors.SURFACE).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        self._canin_label = tk.Label(cin_frame, text="No file selected",
                                     bg=Colors.SURFACE, fg=Colors.TEXT_DIM,
                                     font=Fonts.SMALL, anchor="w")
        self._canin_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16)
        ttk.Button(cin_frame, text="Load Excel", command=self._load_canin).grid(
            row=0, column=1, sticky="e", padx=16, pady=(12, 4))

        ttk.Label(cin_frame, text="Sheet",
                  font=Fonts.SMALL, background=Colors.SURFACE).grid(
            row=2, column=0, sticky="w", padx=16, pady=(8, 2))
        self._canin_combo = ttk.Combobox(cin_frame,
                                         textvariable=self._canin_sheet_var,
                                         state="readonly")
        self._canin_combo.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 12))

        # ── CAN OUT Section ───────────────────────────────────────────
        cout_frame = ttk.Frame(self, style="Card.TFrame")
        cout_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=8)
        cout_frame.columnconfigure(1, weight=1)

        ttk.Label(cout_frame, text="CAN OUT Interface (optional)",
                  font=Fonts.SUBHEAD, background=Colors.SURFACE).grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        self._canout_label = tk.Label(cout_frame, text="No file selected",
                                      bg=Colors.SURFACE, fg=Colors.TEXT_DIM,
                                      font=Fonts.SMALL, anchor="w")
        self._canout_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16)
        ttk.Button(cout_frame, text="Load Excel", command=self._load_canout).grid(
            row=0, column=1, sticky="e", padx=16, pady=(12, 4))

        ttk.Label(cout_frame, text="Sheet",
                  font=Fonts.SMALL, background=Colors.SURFACE).grid(
            row=2, column=0, sticky="w", padx=16, pady=(8, 2))
        self._canout_combo = ttk.Combobox(cout_frame,
                                          textvariable=self._canout_sheet_var,
                                          state="readonly")
        self._canout_combo.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 12))

        # ── Start Button ──────────────────────────────────────────────
        run_frame = ttk.Frame(self, style="Card.TFrame")
        run_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(8, 16))
        self._start_btn = ttk.Button(run_frame, text="Start Match",
                                     command=self._start_match,
                                     style="Accent.TButton")
        self._start_btn.pack(side="right", padx=16, pady=12)

        self._progress = ttk.Progressbar(run_frame, mode="indeterminate")
        self._progress.pack(side="right", fill="x", expand=True, padx=16, pady=12)
        self._progress.pack_forget()

    def _load_dbc(self):
        path = filedialog.askopenfilename(
            title="Select DBC file",
            filetypes=[("DBC files", "*.dbc"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self._dbc_result = read_dbc(path)
            self._dbc_path = path
            self._dbc_label.configure(text=os.path.basename(path))

            ecu_list = list(set(
                m["txecu"] for m in self._dbc_result.values()
            ))
            self._ecu_combo["values"] = sorted(ecu_list)
            if ecu_list:
                self._ecu_var.set(ecu_list[0])

            self._log.success(f"DBC loaded: {len(self._dbc_result)} msgs, "
                              f"{len(ecu_list)} ECUs")
        except Exception as e:
            self._log.error(f"DBC parse error: {e}")

    def _load_canin(self):
        path = filedialog.askopenfilename(
            title="Select CAN IN interface Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if path:
            self._canin_path = path
            self._canin_label.configure(text=os.path.basename(path))
            try:
                self._canin_sheets = pd.ExcelFile(path).sheet_names
                self._canin_combo["values"] = self._canin_sheets
                if self._canin_sheets:
                    self._canin_sheet_var.set(self._canin_sheets[0])
            except Exception as e:
                self._log.error(f"Error reading sheets: {e}")

    def _load_canout(self):
        path = filedialog.askopenfilename(
            title="Select CAN OUT interface Excel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if path:
            self._canout_path = path
            self._canout_label.configure(text=os.path.basename(path))
            try:
                self._canout_sheets = pd.ExcelFile(path).sheet_names
                self._canout_combo["values"] = self._canout_sheets
                if self._canout_sheets:
                    self._canout_sheet_var.set(self._canout_sheets[0])
            except Exception as e:
                self._log.error(f"Error reading sheets: {e}")

    def _start_match(self):
        if not self._dbc_path:
            self._log.warn("Please load a DBC file first")
            return
        ecu = self._ecu_var.get()
        if not ecu:
            self._log.warn("Please select an ECU")
            return

        self._start_btn.configure(state="disabled")
        self._progress.pack(side="right", fill="x", expand=True, padx=16, pady=12)
        self._progress.start()
        self._set_status("Matching CAN signals...")

        def task():
            cwd = os.getcwd()
            dbc_save = os.path.join(cwd, "DBC_SAVE.xlsx")

            dbc_to_excel(self._dbc_path, dbc_save, ecu)
            msgs = [f"DBC parsed → {dbc_save}"]

            if self._canin_path:
                try:
                    canin_save = os.path.join(cwd, "CANIN_SAVE.xlsx")
                    match_can_in(self._canin_path, dbc_save,
                                 self._canin_sheet_var.get(), canin_save)
                    msgs.append(f"CAN IN matched → {canin_save}")
                except Exception as e:
                    msgs.append(f"CAN IN error: {e}")

            if self._canout_path:
                try:
                    canout_save = os.path.join(cwd, "CANOUT_SAVE.xlsx")
                    match_can_out(self._canout_path, dbc_save,
                                  self._canout_sheet_var.get(), canout_save)
                    msgs.append(f"CAN OUT matched → {canout_save}")
                except Exception as e:
                    msgs.append(f"CAN OUT error: {e}")

            self.after(0, lambda: [self._log.success(m) for m in msgs])
            self.after(0, self._done)

        threading.Thread(target=task, daemon=True).start()

    def _done(self):
        self._progress.stop()
        self._progress.pack_forget()
        self._start_btn.configure(state="normal")
        self._set_status("Ready")
