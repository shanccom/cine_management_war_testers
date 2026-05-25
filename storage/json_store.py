"""
Persistencia JSON del sistema.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from config.constants import SCHEMA_VERSION_VENTAS
from core.helpers import load_json_file, save_json_file


class JsonStore:
    def __init__(self, path: str | Path, default_payload: dict[str, Any] | None = None) -> None:
        self.path = Path(path)
        self.default_payload = default_payload or {"items": [], "_schema_version": SCHEMA_VERSION_VENTAS}

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return deepcopy(self.default_payload)

        data = load_json_file(str(self.path))
        if not isinstance(data, dict):
            return deepcopy(self.default_payload)

        if "items" not in data or not isinstance(data["items"], list):
            data["items"] = []
        if "_schema_version" not in data:
            data["_schema_version"] = self.default_payload.get("_schema_version", SCHEMA_VERSION_VENTAS)
        return data

    def save(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise TypeError("payload debe ser un diccionario")
        if "items" in payload and not isinstance(payload["items"], list):
            raise TypeError("payload['items'] debe ser una lista")
        save_json_file(str(self.path), payload)

    def append_item(self, item: Any, collection_key: str = "items") -> dict[str, Any]:
        payload = self.load()
        if collection_key not in payload or not isinstance(payload[collection_key], list):
            payload[collection_key] = []
        payload[collection_key].append(item)
        self.save(payload)
        return payload


class VentasStore(JsonStore):
    def __init__(self, path: str | Path) -> None:
        super().__init__(path, default_payload={"items": [], "_schema_version": SCHEMA_VERSION_VENTAS})
