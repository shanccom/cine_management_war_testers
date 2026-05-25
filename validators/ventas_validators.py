"""
Validadores del modulo de ventas.
"""

from __future__ import annotations

from datetime import datetime
from numbers import Real
from typing import Any

from config.constants import MAX_POR_COMPRA, METODOS_PAGO_PERMITIDOS, MIN_POR_COMPRA


def _raise_type_error(field_name: str, expected: str) -> None:
    raise TypeError(f"{field_name} debe ser {expected}")


def validar_texto_no_vacio(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        _raise_type_error(field_name, "una cadena de texto")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} no puede estar vacio")
    return normalized


def validar_entero(value: Any, field_name: str, *, minimo: int | None = None, maximo: int | None = None) -> int:
    if isinstance(value, bool):
        _raise_type_error(field_name, "un entero")
    if isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValueError(f"{field_name} no puede estar vacio")
        try:
            value = int(value)
        except ValueError as exc:
            raise TypeError(f"{field_name} debe ser un entero") from exc
    if not isinstance(value, int):
        _raise_type_error(field_name, "un entero")
    if minimo is not None and value < minimo:
        raise ValueError(f"{field_name} debe ser mayor o igual que {minimo}")
    if maximo is not None and value > maximo:
        raise ValueError(f"{field_name} debe ser menor o igual que {maximo}")
    return value


def validar_decimal(value: Any, field_name: str, *, minimo: float | None = None) -> float:
    if isinstance(value, bool):
        _raise_type_error(field_name, "un numero decimal")
    if isinstance(value, str):
        value = value.strip().replace(",", ".")
        if not value:
            raise ValueError(f"{field_name} no puede estar vacio")
        try:
            value = float(value)
        except ValueError as exc:
            raise TypeError(f"{field_name} debe ser un numero decimal") from exc
    if not isinstance(value, Real):
        _raise_type_error(field_name, "un numero decimal")
    value = float(value)
    if minimo is not None and value < minimo:
        raise ValueError(f"{field_name} debe ser mayor o igual que {minimo}")
    return round(value, 2)


def validar_metodo_pago(value: Any) -> str:
    metodo = validar_texto_no_vacio(value, "metodo_pago").lower()
    if metodo not in METODOS_PAGO_PERMITIDOS:
        raise ValueError(
            f"metodo_pago invalido. Valores permitidos: {', '.join(METODOS_PAGO_PERMITIDOS)}"
        )
    return metodo


def validar_fecha_hora(value: Any) -> str:
    texto = validar_texto_no_vacio(value, "fecha_hora")
    # Enforce strict ISO format with 'T' separator to avoid ambiguous formats
    if "T" not in texto:
        raise ValueError("fecha_hora debe seguir el formato ISO 8601 con separador 'T'")
    try:
        datetime.fromisoformat(texto)
    except ValueError as exc:
        raise ValueError("fecha_hora debe seguir el formato ISO 8601") from exc
    return texto


def validar_payload_venta(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TypeError("payload debe ser un diccionario")

    validated = {
        "pelicula_id": validar_texto_no_vacio(payload.get("pelicula_id"), "pelicula_id"),
        "pelicula_titulo": validar_texto_no_vacio(payload.get("pelicula_titulo", payload.get("titulo", "")), "pelicula_titulo"),
        "sala_id": validar_texto_no_vacio(payload.get("sala_id"), "sala_id"),
        "sala_numero": validar_entero(payload.get("sala_numero", 0), "sala_numero", minimo=0),
        "funcion_id": validar_texto_no_vacio(payload.get("funcion_id"), "funcion_id"),
        "fecha_hora": validar_fecha_hora(payload.get("fecha_hora")),
        "cliente_nombre": validar_texto_no_vacio(payload.get("cliente_nombre"), "cliente_nombre"),
        "cliente_documento": validar_texto_no_vacio(payload.get("cliente_documento"), "cliente_documento"),
        "cliente_edad": validar_entero(payload.get("cliente_edad"), "cliente_edad", minimo=0),
        "cantidad_entradas": validar_entero(payload.get("cantidad_entradas"), "cantidad_entradas", minimo=MIN_POR_COMPRA, maximo=MAX_POR_COMPRA),
        "precio_unitario": validar_decimal(payload.get("precio_unitario"), "precio_unitario", minimo=0.0),
        "metodo_pago": validar_metodo_pago(payload.get("metodo_pago")),
        "tipo_cliente": validar_texto_no_vacio(payload.get("tipo_cliente", "general"), "tipo_cliente"),
        "restriccion_edad": validar_entero(payload.get("restriccion_edad", 0), "restriccion_edad", minimo=0),
        "capacidad_sala": validar_entero(payload.get("capacidad_sala", 0), "capacidad_sala", minimo=0),
        "ocupadas_actuales": validar_entero(payload.get("ocupadas_actuales", 0), "ocupadas_actuales", minimo=0),
    }

    validated["tipo_cliente"] = validated["tipo_cliente"].lower()
    return validated
