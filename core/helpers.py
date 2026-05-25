"""
Helpers de persistencia y utilidades.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger("cine_management")


def load_json_file(path: str) -> Any:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json_file(path: str, payload: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_name(f"{file_path.name}.tmp")

    try:
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
        os.replace(temp_path, file_path)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def log_error(message: str) -> None:
    LOGGER.error(message)
