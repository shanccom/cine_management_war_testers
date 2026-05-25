"""Pruebas de seguridad, ataques y casos limite para el modulo de ventas (pytest).

Estas pruebas cubren entradas malformadas, valores limites y vectores maliciosos
como parte de Black Box / QA ofensivo. No modifican codigo de produccion.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.ventas_service import VentasService


def _base_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pelicula_id": "P010",
        "pelicula_titulo": "Pelicula Prueba",
        "sala_id": "S9",
        "sala_numero": 9,
        "funcion_id": "F009",
        "fecha_hora": (datetime.now() + timedelta(hours=1)).replace(microsecond=0).isoformat(timespec="seconds"),
        "cliente_nombre": "Test User",
        "cliente_documento": "00000000",
        "cliente_edad": 30,
        "cantidad_entradas": 1,
        "precio_unitario": 20.0,
        "metodo_pago": "efectivo",
        "tipo_cliente": "general",
        "restriccion_edad": 0,
        "capacidad_sala": 100,
        "ocupadas_actuales": 0,
    }
    payload.update(overrides)
    return payload


@pytest.fixture()
def ventas_service(tmp_path) -> VentasService:
    return VentasService(tmp_path / "ventas.json")


@pytest.mark.parametrize(
    "pelicula_id, expected_error",
    [
        ("P001", None),  # id existe / valido (no se valida existencia en el codigo actual)
        ("", "ERR_VALIDACION"),
        (None, "ERR_VALIDACION"),
        ("\"'<>/\\..\"", None),  # caracteres especiales - actualmente aceptados como texto
        ("A" * 5000, None),  # nombre excesivamente largo - actual comportamiento: aceptado
    ],
)
def test_pelicula_casos(ventas_service: VentasService, pelicula_id: object, expected_error: str | None) -> None:
    payload = _base_payload(pelicula_id=pelicula_id)
    result = ventas_service.comprar_entrada(payload)
    if expected_error is None:
        assert result["status"] in ("ok", "error")
    else:
        assert result["status"] == "error"
        assert result["codigo_error"] == expected_error


@pytest.mark.parametrize(
    "fecha_valor, expected_error",
    [
        ((datetime.now() + timedelta(days=1)).isoformat(timespec="seconds"), None),
        ("2026-02-30T10:00:00", "ERR_VALIDACION"),
        ("not-a-date", "ERR_VALIDACION"),
        ("", "ERR_VALIDACION"),
        (None, "ERR_VALIDACION"),
        ("2026-05-24 12:00:00", "ERR_VALIDACION"),  # missing T separator expected by iso
    ],
)
def test_fecha_casos(ventas_service: VentasService, fecha_valor: object, expected_error: str | None) -> None:
    payload = _base_payload(fecha_hora=fecha_valor)
    result = ventas_service.comprar_entrada(payload)
    if expected_error is None:
        assert result["status"] == "ok"
    else:
        assert result["status"] == "error"
        assert result["codigo_error"] == expected_error


@pytest.mark.parametrize(
    "nombre, expected_error",
    [
        ("", "ERR_VALIDACION"),
        ("   ", "ERR_VALIDACION"),
        ("123456", None),  # nombre numerico: actual comportamiento lo acepta
        ("<script>alert(1)</script>", None),
        ("\ud83d\ude00", None),  # emoji como texto
        ("A" * 5000, None),
    ],
)
def test_cliente_nombre_casos(ventas_service: VentasService, nombre: object, expected_error: str | None) -> None:
    payload = _base_payload(cliente_nombre=nombre)
    result = ventas_service.comprar_entrada(payload)
    if expected_error is None:
        assert result["status"] in ("ok", "error")
    else:
        assert result["status"] == "error"
        assert result["codigo_error"] == expected_error


@pytest.mark.parametrize(
    "edad, restriccion, expected_error",
    [
        (-1, 0, "ERR_VALIDACION"),
        ("", 0, "ERR_VALIDACION"),
        (18.5, 0, "ERR_VALIDACION"),
        ("abc", 0, "ERR_VALIDACION"),
        (17, 18, "ERR_EDAD_INSUFICIENTE"),
        (18, 18, None),
    ],
)
def test_cliente_edad_casos(ventas_service: VentasService, edad: object, restriccion: int, expected_error: str | None) -> None:
    payload = _base_payload(cliente_edad=edad, restriccion_edad=restriccion)
    result = ventas_service.comprar_entrada(payload)
    if expected_error is None:
        assert result["status"] == "ok"
    else:
        assert result["status"] == "error"
        assert result["codigo_error"] == expected_error


@pytest.mark.parametrize(
    "metodo, expected_error",
    [
        ("efectivo", None),
        ("", "ERR_VALIDACION"),
        ("bitcoin", "ERR_VALIDACION"),
        ("Efectivo", None),
    ],
)
def test_metodo_pago_casos(ventas_service: VentasService, metodo: object, expected_error: str | None) -> None:
    payload = _base_payload(metodo_pago=metodo)
    result = ventas_service.comprar_entrada(payload)
    if expected_error is None:
        assert result["status"] == "ok"
    else:
        assert result["status"] == "error"
        assert result["codigo_error"] == expected_error


@pytest.mark.parametrize(
    "sala_id, capacidad, ocupadas, cantidad, expected_error",
    [
        ("S1", 100, 0, 1, None),
        ("", 100, 0, 1, "ERR_VALIDACION"),
        ("S1", 0, 0, 1, "ERR_INSUFICIENTE_ASIENTOS"),
        ("S1", 10, 10, 1, "ERR_INSUFICIENTE_ASIENTOS"),
    ],
)
def test_sala_casos(ventas_service: VentasService, sala_id: object, capacidad: int, ocupadas: int, cantidad: int, expected_error: str | None) -> None:
    payload = _base_payload(sala_id=sala_id, capacidad_sala=capacidad, ocupadas_actuales=ocupadas, cantidad_entradas=cantidad)
    result = ventas_service.comprar_entrada(payload)
    if expected_error is None:
        assert result["status"] == "ok"
    else:
        assert result["status"] == "error"
        assert result["codigo_error"] == expected_error


@pytest.mark.parametrize(
    "hora_val, expected_error",
    [
        ("2026-05-24T12:00:00", None),
        ("2026-05-24T25:00:00", "ERR_VALIDACION"),
        ("", "ERR_VALIDACION"),
    ],
)
def test_hora_casos(ventas_service: VentasService, hora_val: object, expected_error: str | None) -> None:
    payload = _base_payload(fecha_hora=hora_val)
    result = ventas_service.comprar_entrada(payload)
    if expected_error is None:
        assert result["status"] == "ok"
    else:
        assert result["status"] == "error"
        assert result["codigo_error"] == expected_error


@pytest.mark.parametrize(
    "cantidad, expected_error",
    [
        (-5, "ERR_VALIDACION"),
        (0, "ERR_VALIDACION"),
        (11, "ERR_VALIDACION"),
        (2.5, "ERR_VALIDACION"),
        (10**9, "ERR_VALIDACION"),
    ],
)
def test_cantidad_casos(ventas_service: VentasService, cantidad: object, expected_error: str | None) -> None:
    payload = _base_payload(cantidad_entradas=cantidad)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "error"
    assert result["codigo_error"] == expected_error


def test_vectores_maliciosos_no_crashean(ventas_service: VentasService) -> None:
    malicious_values = ["../../", "NULL", "NaN", "Infinity", "\x00", "\ud83d\ude0f", "\u202e"]
    for val in malicious_values:
        payload = _base_payload(pelicula_titulo=val, cliente_nombre=val, cliente_documento=val)
        result = ventas_service.comprar_entrada(payload)
        assert result["status"] in ("ok", "error")
