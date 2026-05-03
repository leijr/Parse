# ParseTool

Automotive ECU data analysis desktop application. Parse oscilloscope snapshots from MDF/MF4 log files, verify CAN bus CRC integrity, and match DBC signals against interface sheets.

Built with Python and tkinter. Dark/light theme support.

## Features

- **Snapshot** — Read OSC snapshot data from MDF/MF4 files, decode CAN signals (uint8/uint16/real32), export to Excel, and visualize waveforms in a popup plot window.
- **CRC Check** — Validate CAN and CANFD log data integrity with CRC-8 (Profile 1) and CRC-16 (Profile 5) algorithms.
- **CAN Matcher** — Parse DBC files and match CAN_IN / CAN_OUT signals against external Excel interface definitions.

## Project structure

```
Parse/
├── parsetool.py              # Application entry point
├── engine/
│   ├── snapshot_engine.py    # MDF OSC data parser and plotter
│   ├── crc_engine.py         # CRC-8 / CRC-16 checksum engine
│   ├── can_matcher.py        # CAN signal matching and DBC→Excel
│   ├── dbc_reader.py         # DBC file parser
│   └── config.py             # Project config loader
├── pages/
│   ├── home_page.py          # Home screen with feature cards
│   ├── snapshot_page.py      # Snapshot parsing controls
│   ├── crc_page.py           # CRC check controls
│   └── can_page.py           # CAN matcher controls
├── widgets/
│   ├── sidebar.py            # Navigation sidebar
│   └── log_panel.py          # Scrollable log output
├── config/
│   ├── nidec.json            # Nidec project signal definitions
│   ├── lv.json               # GAC LV project
│   ├── hv.json               # GAC HV project
│   └── xof.json              # GAC XOF project
└── theme/
    └── theme.py              # Catppuccin color scheme and fonts
```

## Supported projects

| Project | Config | Signals |
|---------|--------|---------|
| A02 Nidec | `config/nidec.json` | 40 OSC signals |
| GAC LV | `config/lv.json` | 24 OSC signals |
| GAC HV | `config/hv.json` | 22 OSC signals |
| GAC XOF | `config/xof.json` | 59 OSC signals |

Add or modify a project by editing the corresponding JSON config file — no code changes needed.

## Requirements

- Python 3.9+
- tkinter (included with most Python distributions)
- [asammdf](https://github.com/danielhrisca/asammdf)
- pandas
- matplotlib
- numpy
- openpyxl

```bash
pip install asammdf pandas matplotlib numpy openpyxl
```

## Usage

```bash
python parsetool.py
```

### Snapshot

1. Select a project type (Nidec / LV / HV / XOF)
2. Optionally check "Parse bigdata signals"
3. Click "Select MDF/MF4 File" and pick a log file
4. Click "Start Parse" — results are exported to Excel; plots open in a separate window

### CRC Check

1. Select protocol (CAN / CANFD) and CRC algorithm (CRC-8 / CRC-16)
2. Load a CSV log file
3. Results show passed/failed status per message

### CAN Matcher

1. Select a DBC file and an Excel interface file
2. Choose the target ECU
3. Run matching to produce aligned CAN_IN / CAN_OUT sheets

## Config file format

Each `config/*.json` defines signal layout and plot groups:

```json
{
  "data_len": 744,
  "byte_num_per_frame": 8,
  "uint8_number": 5,
  "uint16_number": 3,
  "uint32_number": 12,
  "uint8_frame_num": 13,
  "uint16_frame_num": 25,
  "real32_frame_num": 50,
  "len_other": 4,
  "len_all": 24,
  "len_uint": 20,
  "signals": [
    {"index": 0, "name": "debug5_sthandletoturnoff",
     "frame_num": 13, "byte_size": 1, "offset": 0, "extra": 1}
  ],
  "plot_groups": [
    {"indices": [5], "ylabel": "转子位置"}
  ]
}
```

- `frame_num` — CAN frames this signal spans per cycle
- `byte_size` — bytes per data point (1=uint8, 2=uint16, 4=real32)
- `offset` — calibration offset (raw = raw + offset)
- `extra` — calibration scale (final = offset + raw × extra) for nidec; secondary offset for others
- `plot_groups` — which signal indices to plot together in each subplot
