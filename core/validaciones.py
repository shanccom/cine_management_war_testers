"""
Funciones de validacion.
"""

from __future__ import annotations

from typing import Any

from validators.ventas_validators import validar_payload_venta


def validar_pelicula(data: dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
    return all(key in data for key in ("pelicula_id", "titulo", "duracion", "clasificacion"))


def validar_sala(data: dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
    return all(key in data for key in ("sala_id", "numero", "capacidad"))


def validar_venta(data: dict[str, Any]) -> bool:
    try:
        validar_payload_venta(data)
    except (TypeError, ValueError):
        return False
    return True
