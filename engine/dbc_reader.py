"""DBC (CAN Database) file parser.

Parses standard DBC files and returns a structured dictionary of messages
and signals. Supports UTF-8 and GBK encodings.
"""

from typing import Any


def _find_str(source: str, startbit: int, endstr: str) -> tuple[str, int]:
    """Find endstr in source from startbit, return substring and end position."""
    source = str(source)
    endbit = startbit
    for i, ch in enumerate(source):
        if ch == endstr:
            endbit = i
            break
    return source[startbit:endbit], endbit


def read_dbc(filepath: str) -> dict[str, dict[str, Any]]:
    """Parse a DBC file.

    Returns:
        {
            "message_name": {
                "id": "hex_id",
                "msglen": "length",
                "txecu": "transmitter_ecu",
                "signal": {
                    "signal_name": {
                        "endbit": str, "siglen": str,
                        "byteorder": "0"|"1",  # 0=Motorola, 1=Intel
                        "factor": str, "offset": str,
                        "min": str, "max": str, "unit": str,
                        "rxecu": [str, ...]
                    }
                },
                "TxCycTime": str
            }
        }
    """
    db: dict[str, dict] = {}

    try:
        with open(filepath, encoding="UTF-8") as f:
            dbc_list = f.readlines()
    except (ValueError, UnicodeDecodeError):
        with open(filepath, encoding="GBK") as f:
            dbc_list = f.readlines()

    # Single-pass: build cycle time lookup
    tx_cycle_times: dict[str, str] = {}
    for line in dbc_list:
        if line.startswith('BA_ "GenMsgCycleTime" BO_ '):
            rest = line[26:]
            try:
                id_end = rest.index(" ")
                msg_id = rest[:id_end]
                cyc, _ = _find_str(rest[id_end + 1:], 0, ";")
                tx_cycle_times[msg_id] = cyc
            except (ValueError, IndexError):
                pass

    length = len(dbc_list)
    i = 0
    while i < length:
        line = dbc_list[i]

        if line.startswith("BO_"):
            readbit = 4
            msg_id, _ = _find_str(line[readbit:], 0, " ")
            readbit += len(msg_id) + 1
            msgname, _ = _find_str(line[readbit:], 0, ":")
            readbit += len(msgname) + 2
            msglen, _ = _find_str(line[readbit:], 0, " ")
            readbit += len(msglen) + 1
            txecu, _ = _find_str(line[readbit:], 0, "\n")

            db[msgname] = {
                "id": msg_id,
                "msglen": msglen,
                "txecu": txecu.strip(),
                "signal": {},
                "TxCycTime": tx_cycle_times.get(msg_id, ""),
            }

            i += 1
            while i < length and dbc_list[i].startswith(" SG_ "):
                line = dbc_list[i]
                readbit = 5
                signame, _ = _find_str(line[readbit:], 0, " ")
                readbit += len(signame)
                temp, _ = _find_str(line[readbit:], 0, ":")
                readbit += len(temp) + 2
                endbit, _ = _find_str(line[readbit:], 0, "|")
                readbit += len(endbit) + 1
                siglen, _ = _find_str(line[readbit:], 0, "@")
                readbit += len(siglen) + 1
                byteorder, _ = _find_str(line[readbit:], 0, "+")
                readbit += len(byteorder) + 3
                factor, _ = _find_str(line[readbit:], 0, ",")
                readbit += len(factor) + 1
                offset, _ = _find_str(line[readbit:], 0, ")")
                readbit += len(offset) + 3
                vmin, _ = _find_str(line[readbit:], 0, "|")
                readbit += len(vmin) + 1
                vmax, _ = _find_str(line[readbit:], 0, "]")
                readbit += len(vmax) + 3
                unit, _ = _find_str(line[readbit:], 0, '"')
                readbit += len(unit) + 3

                rxecu: list[str] = []
                while readbit < len(line):
                    temp, end = _find_str(line[readbit:], 0, ",")
                    if temp == "":
                        temp, _ = _find_str(line[readbit:], 0, "\n")
                        if temp.strip():
                            rxecu.append(temp.strip())
                        break
                    rxecu.append(temp.strip())
                    readbit += len(temp) + 1

                db[msgname]["signal"][signame] = {
                    "endbit": endbit,
                    "siglen": siglen,
                    "byteorder": byteorder,
                    "factor": factor,
                    "offset": offset,
                    "min": vmin,
                    "max": vmax,
                    "unit": unit,
                    "rxecu": rxecu,
                }
                i += 1
        else:
            i += 1

    return db
