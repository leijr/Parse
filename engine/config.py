"""Project configuration loader.

Loads per-project signal definitions and parameters from JSON files.
"""

import json
import os
from typing import Any

_CFG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")

_META = {
    "nidec": "A02 Nidec Project",
    "lv":    "GAC LV Project",
    "hv":    "GAC HV Project",
    "xof":   "GAC XOF Project",
}

_cache: dict[str, dict] = {}


def list_projects() -> dict[str, str]:
    return dict(_META)


def load_project_config(project: str) -> dict[str, Any]:
    if project in _cache:
        return _cache[project]
    path = os.path.join(_CFG_DIR, f"{project}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    _cache[project] = data
    return data
