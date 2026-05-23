from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]


def asset_path(name: str) -> Path:
    return project_root() / "assets" / name
