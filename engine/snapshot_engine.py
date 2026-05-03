"""Snapshot data parser — core logic from SnapshotTools_V42.
Config loaded from per-project JSON files.
"""

import os
import datetime
import numpy as np
import pandas as pd
import struct
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.font_manager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from asammdf import MDF

from .config import load_project_config

MAX_CYCLES = 20
POINTS_PER_CYCLE = 100

# ── Bigdata signal names ──
BIGDATA_SIGNALS = [
    'DCU_FaultData_RC', 'DCU_stPWMEna', 'DCU_stMode', 'DCU_uLowVolt',
    'DCU_FaultData_1Bit_1', 'DCU_FaultData_1Bit_2', 'DCU_FaultData_1Bit_3',
    'DCU_FaultData_1Bit_4', 'DCU_FaultData_4Bit_1', 'DCU_stASCProt',
    'DCU_agRotorPosn', 'DCU_stFaultFlag100us', 'DCU_PWMFreq', 'DCU_uDcVolt',
    'DCU_iCurdFinalRef', 'DCU_iCurqFinalRef', 'DCU_iCurdFb', 'DCU_iCurqFb',
    'DCU_iPhaCurU', 'DCU_iPhaCurV', 'DCU_iPhaCurW',
    'DCU_uVoltdFinalRef', 'DCU_uVoltqFinalRef', 'DCU_iDcCur',
    'DCU_ResFaultFlag', 'DCU_stTsc',
    'DCU_IGBTSt_UT', 'DCU_IGBTSt_UB', 'DCU_IGBTSt_VT', 'DCU_IGBTSt_VB',
    'DCU_IGBTSt_WT', 'DCU_IGBTSt_WB',
    'DCU_FaultData_12Bit_1', 'DCU_FaultData_16Bit_1',
]

_PROJECT_MAP = {"nidec": "gac_nidec", "lv": "gac_lv",
                "hv": "gac_hv", "xof": "gac_xof"}


class SnapShotEngine:
    """Snapshot OSC data parser, Excel exporter and plotter."""

    def __init__(self, filepath, project, bigdata, signal_pattern, log_callback=None):
        self.filepath = filepath
        self.basename = os.path.splitext(os.path.basename(filepath))[0]
        self._log_cb = log_callback or (lambda msg, level=None: None)
        self._do_bigdata = bigdata

        pt = _PROJECT_MAP.get(project, "gac_nidec")
        self._pt = pt                   # internal project key ("gac_nidec" etc.)
        self._signal_tpl = "DCU_OSC_Signal*"

        # ── Load project config ──
        raw = load_project_config(project)
        para_keys = {"data_len", "byte_num_per_frame",
                     "uint8_number", "uint16_number", "uint32_number",
                     "uint8_frame_num", "uint16_frame_num", "real32_frame_num",
                     "len_other", "len_all", "len_uint"}
        self.basic_para = {pt: {k: raw[k] for k in para_keys if k in raw}}

        # Build signal table: [index, data[], name, frame_num, byte_size, offset, extra]
        signals = []
        for s in sorted(raw["signals"], key=lambda s: s["index"]):
            signals.append([s["index"], [], s["name"], s["frame_num"],
                            s["byte_size"], s["offset"], s["extra"]])
        self.signals = {pt: signals}

        # Build plot groups
        self.plot_groups = {
            pt: [[g["indices"], g["ylabel"]] for g in raw["plot_groups"]]
        }

        # ── Runtime state ──
        self.filename = None
        self.cycle_num = 0
        self.bigdata = {k: [] for k in BIGDATA_SIGNALS}

        self.lost_frame = []
        self.zero_indices = []
        self.osc_frames = []            # hex string per CAN frame
        self.osc_rolling = []           # rolling counter (nidec only)

    # ═══════════════════════════════════════════════════════════════════
    # helpers
    # ═══════════════════════════════════════════════════════════════════

    def _log(self, msg, level="INFO"):
        try:
            self._log_cb(msg, level)
        except Exception:
            print(f"[{level}] {msg}")

    @staticmethod
    def _timestamp():
        return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")

    # ═══════════════════════════════════════════════════════════════════
    # Public API
    # ═══════════════════════════════════════════════════════════════════

    def run(self):
        """Parse OSC data → decode → export Excel. Returns 'OK' or 'NG'."""
        try:
            self.filename = os.path.splitext(os.path.basename(self.filepath))[0]
            self._log(f"Parsing OSC data for {self._pt}...", "INFO")

            if self._read_osc_frames() != 'OK':
                self._log("Failed to read OSC data from MDF", "ERROR")
                return "NG"
            self._log(f"Read {len(self.osc_frames)} OSC frames", "INFO")

            self._fill_lost_frames()
            self._log(f"After fill: {len(self.osc_frames)} frames, "
                      f"lost: {len(self.zero_indices)}", "INFO")

            self._decode_all_signals()
            self._log(f"Decoded {self.cycle_num} cycles", "INFO")

            self._export_osc_excel()
            self._log("OSC Excel exported", "SUCCESS")
            return "OK"
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._log(f"Snapshot error: {e}", "ERROR")
            return "NG"

    def run_bigdata(self):
        """Parse bigdata signals → export Excel. Returns 'OK'/'NG'/'SKIP'."""
        if not self._do_bigdata:
            return "SKIP"
        try:
            if self._read_bigdata() != 'OK':
                self._log("Failed to read bigdata from MDF", "ERROR")
                return "NG"
            self._export_bigdata_excel()
            self._log("Bigdata Excel exported", "SUCCESS")
            return "OK"
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._log(f"Bigdata error: {e}", "ERROR")
            return "NG"

    def plot(self, master=None):
        """Generate plots. If master is given, embed in tkinter and return canvas."""
        return self._draw_plots(master=master)

    # ═══════════════════════════════════════════════════════════════════
    # OSC read
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _hex_from_sample(raw) -> str:
        """Convert a single MDF sample to a 2-char hex string."""
        s = hex(raw)
        if len(s) == 3:
            return '0' + s[-1:]
        if len(s) == 4:
            return s[-2:]
        return '00'

    def _read_osc_frames(self):
        """Read MDF OSC channels and build self.osc_frames (list of hex strings)."""
        pt = self._pt
        is_nidec = (pt == 'gac_nidec')
        ch_start, ch_end = (2, 34) if is_nidec else (1, 9)

        try:
            mdf = MDF(self.filepath)

            ch1_name = self._signal_tpl.replace("*", "1", 1)
            ch1_samples = mdf.get(ch1_name).samples.tolist()
            n_samples = len(ch1_samples)

            if is_nidec:
                self.osc_rolling = ch1_samples

            channel_samples = []
            for ch in range(ch_start, ch_end):
                ch_name = self._signal_tpl.replace("*", str(ch), 1)
                try:
                    channel_samples.append(mdf.get(ch_name).samples)
                except Exception:
                    channel_samples.append(None)

            for i in range(n_samples):
                parts = []
                for samples in channel_samples:
                    parts.append(self._hex_from_sample(samples[i]))
                self.osc_frames.append(''.join(parts))

            mdf.close()
            return 'OK'
        except Exception:
            return 'NG'

    # ═══════════════════════════════════════════════════════════════════
    # Fill lost frames
    # ═══════════════════════════════════════════════════════════════════

    def _fill_lost_frames(self):
        pt = self._pt
        self.zero_indices = []

        if pt == 'gac_nidec':
            self._fill_nidec()
        else:
            self._fill_standard()

    def _fill_nidec(self):
        dlen = self.basic_para[self._pt]["data_len"]
        rolling = self.osc_rolling
        zero_entry = '0' * len(self.osc_frames[0]) if self.osc_frames else '00'

        para_count = 1 + sum(1 for i in range(len(rolling) - 1)
                             if int(rolling[i + 1]) < int(rolling[i]))

        for para in range(para_count):
            base = dlen * para
            for i in range(base, dlen * (para + 1)):
                expected = i % dlen
                try:
                    if int(rolling[i]) != expected:
                        rolling.insert(i, expected)
                        self.osc_frames.insert(i, zero_entry)
                        self.zero_indices.append(i)
                except IndexError:
                    rolling.append(expected)
                    self.osc_frames.append(zero_entry)
                    self.zero_indices.append(i)

    def _fill_standard(self):
        dlen = self.basic_para[self._pt]["data_len"]
        total = len(self.osc_frames)
        if total < dlen:
            pad = dlen - total
        else:
            pad = (dlen - total % dlen) % dlen
        zero_entry = '0' * (len(self.osc_frames[0]) if self.osc_frames else 16)
        for _ in range(pad):
            self.osc_frames.append(zero_entry)

    # ═══════════════════════════════════════════════════════════════════
    # OSC decode
    # ═══════════════════════════════════════════════════════════════════

    def _decode_all_signals(self):
        pt = self._pt
        dlen = self.basic_para[pt]["data_len"]
        n_uint = self.basic_para[pt]["len_uint"]
        n_other = self.basic_para[pt]["len_other"]

        self.cycle_num = min(len(self.osc_frames) // dlen, MAX_CYCLES)

        for cycle in range(self.cycle_num):
            cursor = cycle * dlen  # running frame pointer

            # Main signals (uint8 / uint16 / real32)
            for si in range(n_uint):
                sig = self.signals[pt][si]
                self._extract_signal(cursor, 0, POINTS_PER_CYCLE,
                                     sig[4], si)
                cursor += sig[3]

            # "Other" signals
            for oi in range(n_other):
                si = n_uint + oi
                sig = self.signals[pt][si]
                self._extract_signal(cursor + sig[6], sig[5],
                                     sig[3], sig[4], si)
                target = (cycle + 1) * POINTS_PER_CYCLE
                while len(sig[1]) < target:
                    sig[1].append(' ')

            if pt == 'gac_nidec':
                target = (cycle + 1) * POINTS_PER_CYCLE
                while len(self.lost_frame) < target:
                    self.lost_frame.append(' ')

        # ── Post-decode calibration ──
        if pt == 'gac_nidec':
            for si in range(n_uint):
                sig = self.signals[pt][si]
                sig[1] = [sig[5] + v * sig[6] for v in sig[1]]
        else:
            for si in range(n_uint):
                sig = self.signals[pt][si]
                if sig[4] == 4:          # real32
                    sig[1] = [self._real32_to_dec(int(v)) for v in sig[1]]

    def _extract_signal(self, frame_start, byte_start,
                         n_values, byte_size, sig_index):
        """Read `n_values` of `byte_size` bytes each from osc_frames, starting
        at fram e index `frame_start`, byte offset `byte_start`.
        Appends decoded values to self.signals[pt][sig_index][1]."""
        pt = self._pt
        bpf = self.basic_para[pt]["byte_num_per_frame"]
        total_bytes = n_values * byte_size

        end_pos = frame_start * bpf + byte_start + total_bytes
        end_frame = end_pos // bpf
        end_byte = end_pos % bpf

        buf = ''
        for fi in range(frame_start, end_frame + 1):
            if pt == 'gac_nidec' and fi in self.zero_indices:
                self.lost_frame.append(self.signals[pt][sig_index][2])

            b_start = byte_start if fi == frame_start else 0
            b_end = end_byte if fi == end_frame else bpf
            h_start = b_start * 2
            h_end = (b_end + 1) * 2          # slice end (exclusive)
            buf += self.osc_frames[fi][h_start:h_end]

        self._decode_hex_values(buf, byte_size, n_values, sig_index)

    def _decode_hex_values(self, hex_buf, byte_size, count, sig_index):
        """Decode `count` big-endian integers of `byte_size` bytes from hex_buf."""
        pt = self._pt
        dst = self.signals[pt][sig_index][1]
        for j in range(count):
            chars = ''
            for k in range(byte_size, 0, -1):      # MSB first
                off = 2 * (byte_size * j + k - 1)
                chars += hex_buf[off:off + 2]
            dst.append(int(chars, 16))

    @staticmethod
    def _real32_to_dec(v: int) -> float:
        """IEEE 754 single-precision decode (MSB-first)."""
        raw = struct.pack(">I", v)
        return struct.unpack(">f", raw)[0]

    # ═══════════════════════════════════════════════════════════════════
    # Bigdata
    # ═══════════════════════════════════════════════════════════════════

    def _read_bigdata(self):
        try:
            mdf = MDF(self.filepath)
            for name in BIGDATA_SIGNALS:
                self.bigdata[name] = mdf.get(name).samples.tolist()

            rc = self.bigdata[BIGDATA_SIGNALS[0]]
            para_idx = []
            for i, v in enumerate(rc):
                para_idx.append('第{}段数据'.format(
                    len(para_idx) + 1) if v == 1 else ' ')
            self.bigdata['段落符号'] = para_idx
            mdf.close()
            return 'OK'
        except Exception:
            return 'NG'

    # ═══════════════════════════════════════════════════════════════════
    # Excel export
    # ═══════════════════════════════════════════════════════════════════

    def _export_osc_excel(self):
        pt = self._pt
        export = {}
        for i in range(self.basic_para[pt]["len_all"]):
            export[self.signals[pt][i][2]] = self.signals[pt][i][1]
        if pt == 'gac_nidec':
            export['lost_frame_Signal_Name'] = self.lost_frame

        path = os.path.join(os.getcwd(),
                            f"{self.filename}_SnapshotData_{pt}_{self._timestamp()}.xlsx")
        pd.DataFrame(export).to_excel(path, index=False)

    def _export_bigdata_excel(self):
        path = os.path.join(os.getcwd(),
                            f"{self.filename}_Bigdata_{self._timestamp()}.xlsx")
        pd.DataFrame(self.bigdata).to_excel(path, index=False)

    # ═══════════════════════════════════════════════════════════════════
    # Plot
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _setup_cn_font():
        """Set matplotlib to use an available Chinese-capable font."""
        candidates = ['PingFang HK', 'STHeiti', 'Heiti TC', 'Lantinghei SC',
                      'MicroSoft YaHei', 'SimHei', 'Noto Sans CJK SC']
        available = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
        family = next((f for f in candidates if f in available), 'sans-serif')
        matplotlib.rc('font', family=family, size=10)

    def _draw_plots(self, master=None):
        pt = self._pt
        groups = self.plot_groups[pt]
        self._setup_cn_font()
        date_str = datetime.datetime.now().strftime("%Y_%m_%d")

        if master:
            return self._embedded_plot(master, groups, date_str)
        else:
            return self._standalone_plots(groups, date_str)

    def _embedded_plot(self, master, groups, date_str):
        pt = self._pt
        fig = plt.figure(figsize=(14, 10))
        fig.patch.set_facecolor("#1e1e2e")
        fig.suptitle(f' "{self.filename}" _SnapshotData_{date_str}',
                     fontsize=12, color="#cdd6f4", fontweight="bold")
        colors = plt.cm.tab10.colors

        for gi, group in enumerate(groups):
            ax = fig.add_subplot(4, 2, gi + 1)
            ax.set_facecolor("#252536")
            for ki, si in enumerate(group[0]):
                if si >= len(self.signals[pt]):
                    continue
                ys = self.signals[pt][si][1]
                ax.plot(range(len(ys)), ys, linewidth=1.0,
                        color=colors[ki % len(colors)],
                        label=self.signals[pt][si][2][:30], alpha=0.85)
            ax.set_ylabel(group[1], fontsize=8, color="#a6adc8")
            ax.legend(fontsize=6, loc="upper right",
                      facecolor="#313244", edgecolor="#45475a",
                      labelcolor="#cdd6f4")
            ax.grid(True, alpha=0.2, color="#45475a")
            ax.tick_params(colors="#a6adc8", labelsize=7)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.draw()
        return canvas

    def _standalone_plots(self, groups, date_str):
        pt = self._pt
        for cycle in range(self.cycle_num):
            fig = plt.figure(figsize=(12, 6.5))
            fig.suptitle(f' "{self.filename}" _SnapshotData_{date_str}'
                         f'-第{cycle + 1}组快照数据--共{self.cycle_num}组快照数据',
                         fontsize=14, x=0.5, y=0.95)
            for gi, group in enumerate(groups):
                ax = fig.add_subplot(4, 2, gi + 1)
                for si in group[0]:
                    sig = self.signals[pt][si]
                    start, end = cycle * 100, (cycle + 1) * 100
                    ls = '-.' if (pt == 'gac_nidec'
                                  and sig[2] in self.lost_frame[start:end]) else '-'
                    ax.plot(sig[1][start:end], label=sig[2], linestyle=ls)
                ax.set_ylabel(group[1])
                ax.legend(loc='upper left')
                ax.grid()
        plt.show(block=False)
        return None
