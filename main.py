"""Punto de entrada e inicializacion del Sistema de Gestion de Cine."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

from config.constants import (
    BASE_DIR,
    DATA_DIR,
    PELICULAS_DATA_FILE,
    SALAS_DATA_FILE,
    SCHEMA_VERSION_VENTAS,
    VENTAS_DATA_FILE,
)
from core.helpers import save_json_file
from ui.main_window import MainWindow


DEFAULT_PELICULAS: list[dict[str, Any]] = [
    {
        "pelicula_id": "P001",
        "id": "P001",
        "titulo": "Oppenheimer",
        "nombre": "Oppenheimer",
        "genero": "Drama",
        "duracion": 180,
        "clasificacion": "+14",
        "sala": 1,
        "precio_unitario": 32.00,
        "restriccion_edad": 15,
    },
    {
        "pelicula_id": "P002",
        "id": "P002",
        "titulo": "Intensamente 2",
        "nombre": "Intensamente",
        "genero": "Comedia",
        "duracion": 96,
        "clasificacion": "ATP",
        "sala": 1,
        "precio_unitario": 24.00,
        "restriccion_edad": 0,
    },
    {
        "pelicula_id": "P003",
        "id": "P003",
        "titulo": "Deadpool y Wolverine",
        "nombre": "Deadpool Wolverine",
        "genero": "Accion",
        "duracion": 128,
        "clasificacion": "+18",
        "sala": 2,
        "precio_unitario": 35.00,
        "restriccion_edad": 18,
    },
]

DEFAULT_SALAS: list[dict[str, Any]] = [
    {
        "sala_id": "S1",
        "id": "S1",
        "numero": 1,
        "capacidad": 120,
        "funcion_id": "F-1",
        "asientos_ocupados": [],
        "asientos_ocupados_por_pelicula": {},
        "ocupadas_actuales": 0,
        "ocupadas": 0,
        "ocupacion": 0,
        "occupied": 0,
    }
]


def _load_payload(path: Path, default_payload: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return deepcopy(default_payload)

    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return deepcopy(default_payload)

    if not isinstance(payload, dict):
        return deepcopy(default_payload)

    if not isinstance(payload.get("items"), list):
        payload["items"] = []
    return payload


def _as_int(value: Any, fallback: int = 0) -> int:
    if isinstance(value, bool):
        return fallback
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return fallback


def _as_float(value: Any, fallback: float = 0.0) -> float:
    if isinstance(value, bool):
        return fallback
    try:
        return float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return fallback


def _as_seat_list(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_items = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        raw_items = value
    else:
        raw_items = []

    seats: list[str] = []
    for item in raw_items:
        seat = str(item).strip().upper()
        if seat and seat not in seats:
            seats.append(seat)
    return seats


def _normalizar_pelicula(item: dict[str, Any], index: int) -> dict[str, Any]:
    pelicula = dict(item)
    pelicula_id = str(pelicula.get("pelicula_id") or pelicula.get("id") or f"P{index + 1:03d}").strip()
    titulo = str(pelicula.get("titulo") or pelicula.get("nombre") or f"Pelicula {index + 1}").strip()

    pelicula["pelicula_id"] = pelicula_id
    pelicula["id"] = str(pelicula.get("id") or pelicula_id).strip()
    pelicula["titulo"] = titulo
    pelicula["nombre"] = str(pelicula.get("nombre") or titulo).strip()
    pelicula["genero"] = str(pelicula.get("genero") or "Drama").strip()
    pelicula["duracion"] = _as_int(pelicula.get("duracion"), 90)
    pelicula["clasificacion"] = str(pelicula.get("clasificacion") or "ATP").strip()
    pelicula["sala"] = _as_int(pelicula.get("sala"), 1)
    pelicula["precio_unitario"] = _as_float(pelicula.get("precio_unitario", pelicula.get("precio")), 25.0)
    pelicula["restriccion_edad"] = _as_int(pelicula.get("restriccion_edad"), 0)
    return pelicula


def _normalizar_sala(item: dict[str, Any], index: int) -> dict[str, Any]:
    sala = dict(item)
    numero = _as_int(sala.get("numero", sala.get("sala_numero")), index + 1)
    capacidad = _as_int(sala.get("capacidad", sala.get("capacity")), 120)
    capacidad = max(1, min(capacidad, 300))
    sala_id = str(sala.get("sala_id") or sala.get("id") or f"S{numero}").strip()

    ocupacion_por_pelicula: dict[str, list[str]] = {}
    raw_map = sala.get("asientos_ocupados_por_pelicula", {})
    if isinstance(raw_map, dict):
        for pelicula_id, seats in raw_map.items():
            key = str(pelicula_id).strip()
            if key:
                ocupacion_por_pelicula[key] = _as_seat_list(seats)

    asientos = _as_seat_list(sala.get("asientos_ocupados"))
    for seats in ocupacion_por_pelicula.values():
        for seat in seats:
            if seat not in asientos:
                asientos.append(seat)

    ocupadas = len(asientos)
    sala.update(
        {
            "sala_id": sala_id,
            "id": str(sala.get("id") or sala_id).strip(),
            "numero": numero,
            "capacidad": capacidad,
            "funcion_id": str(sala.get("funcion_id") or f"F-{numero}").strip(),
            "asientos_ocupados": asientos,
            "asientos_ocupados_por_pelicula": ocupacion_por_pelicula,
            "ocupadas_actuales": ocupadas,
            "ocupadas": ocupadas,
            "ocupacion": ocupadas,
            "occupied": ocupadas,
        }
    )
    return sala


def inicializar_datos() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    peliculas_payload = _load_payload(PELICULAS_DATA_FILE, {"items": DEFAULT_PELICULAS})
    if not peliculas_payload["items"]:
        peliculas_payload["items"] = deepcopy(DEFAULT_PELICULAS)
    peliculas_payload["items"] = [
        _normalizar_pelicula(item, index)
        for index, item in enumerate(peliculas_payload["items"])
        if isinstance(item, dict)
    ]
    save_json_file(str(PELICULAS_DATA_FILE), peliculas_payload)

    salas_payload = _load_payload(SALAS_DATA_FILE, {"items": DEFAULT_SALAS})
    if not salas_payload["items"]:
        salas_payload["items"] = deepcopy(DEFAULT_SALAS)
    salas_payload["items"] = [
        _normalizar_sala(item, index)
        for index, item in enumerate(salas_payload["items"])
        if isinstance(item, dict)
    ]
    save_json_file(str(SALAS_DATA_FILE), salas_payload)

    ventas_payload = _load_payload(
        VENTAS_DATA_FILE,
        {"items": [], "_schema_version": SCHEMA_VERSION_VENTAS},
    )
    ventas_payload.setdefault("_schema_version", SCHEMA_VERSION_VENTAS)
    save_json_file(str(VENTAS_DATA_FILE), ventas_payload)


def main() -> None:
    os.chdir(BASE_DIR)
    inicializar_datos()
    MainWindow().show()


if __name__ == "__main__":
    main()
