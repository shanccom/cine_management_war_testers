"""Pruebas de Analisis de Valores Limite para ventas con pytest."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.ventas_service import VentasService


def _base_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pelicula_id": "P003",
        "pelicula_titulo": "Deadpool y Wolverine",
        "sala_id": "S2",
        "sala_numero": 2,
        "funcion_id": "F002",
        "fecha_hora": (datetime.now() + timedelta(hours=3)).replace(microsecond=0).isoformat(timespec="seconds"),
        "cliente_nombre": "Maria Gomez",
        "cliente_documento": "87654321",
        "cliente_edad": 25,
        "cantidad_entradas": 1,
        "precio_unitario": 35.0,
        "metodo_pago": "efectivo",
        "tipo_cliente": "general",
        "restriccion_edad": 18,
        "capacidad_sala": 100,
        "ocupadas_actuales": 20,
    }
    payload.update(overrides)
    return payload


@pytest.fixture()
def ventas_service(tmp_path) -> VentasService:
    return VentasService(tmp_path / "ventas.json")


@pytest.mark.parametrize(
    "cantidad_entradas, expected_status, expected_error",
    [
        (0, "error", "ERR_VALIDACION"),
        (1, "ok", None),
        (10, "ok", None),
        (11, "error", "ERR_VALIDACION"),
    ],
)
def test_limites_cantidad(
    ventas_service: VentasService,
    cantidad_entradas: int,
    expected_status: str,
    expected_error: str | None,
) -> None:
    payload = _base_payload(cantidad_entradas=cantidad_entradas)

    result = ventas_service.comprar_entrada(payload)

    assert result["status"] == expected_status
    if expected_error is not None:
        assert result["codigo_error"] == expected_error
    else:
        assert result["venta_id"].startswith("V-")


@pytest.mark.parametrize(
    "cliente_edad, expected_error",
    [
        (17, "ERR_EDAD_INSUFICIENTE"),
        (18, None),
    ],
)
def test_limite_edad_para_clasificacion_18(
    ventas_service: VentasService,
    cliente_edad: int,
    expected_error: str | None,
) -> None:
    payload = _base_payload(cliente_edad=cliente_edad)

    result = ventas_service.comprar_entrada(payload)

    if expected_error is None:
        assert result["status"] == "ok"
        assert result["total"] == pytest.approx(35.0)
    else:
        assert result["status"] == "error"
        assert result["codigo_error"] == expected_error


def test_monto_en_soles_en_ticket(ventas_service: VentasService) -> None:
    payload = _base_payload(precio_unitario=42.5, cantidad_entradas=2)

    result = ventas_service.comprar_entrada(payload)

    assert result["status"] == "ok"
    assert "S/." in result["ticket_texto"]
    assert result["total"] == pytest.approx(85.0)
