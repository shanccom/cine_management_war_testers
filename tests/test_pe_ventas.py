"""Pruebas de Particion de Equivalencia para ventas con pytest."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.ventas_service import VentasService


def _base_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pelicula_id": "P002",
        "pelicula_titulo": "Intensamente 2",
        "sala_id": "S1",
        "sala_numero": 1,
        "funcion_id": "F001",
        "fecha_hora": (datetime.now() + timedelta(hours=2)).replace(microsecond=0).isoformat(timespec="seconds"),
        "cliente_nombre": "Juan Perez",
        "cliente_documento": "12345678",
        "cliente_edad": 20,
        "cantidad_entradas": 2,
        "precio_unitario": 24.0,
        "metodo_pago": "efectivo",
        "tipo_cliente": "general",
        "restriccion_edad": 0,
        "capacidad_sala": 100,
        "ocupadas_actuales": 20,
    }
    payload.update(overrides)
    return payload


@pytest.fixture()
def ventas_service(tmp_path) -> VentasService:
    return VentasService(tmp_path / "ventas.json")


@pytest.mark.parametrize(
    "cantidad_entradas, metodo_pago, cliente_edad, restriccion_edad, expected_status",
    [
        (1, "efectivo", 20, 0, "ok"),
    ],
)
def test_clases_validas(
    ventas_service: VentasService,
    cantidad_entradas: int,
    metodo_pago: str,
    cliente_edad: int,
    restriccion_edad: int,
    expected_status: str,
) -> None:
    payload = _base_payload(
        cantidad_entradas=cantidad_entradas,
        metodo_pago=metodo_pago,
        cliente_edad=cliente_edad,
        restriccion_edad=restriccion_edad,
    )

    result = ventas_service.comprar_entrada(payload)

    assert result["status"] == expected_status
    assert result["venta_id"].startswith("V-")
    assert "TICKET DE VENTA" in result["ticket_texto"]
    assert "S/." in result["ticket_texto"]


@pytest.mark.parametrize(
    "override_payload, codigo_error",
    [
        ({"cantidad_entradas": -1}, "ERR_VALIDACION"),
        ({"metodo_pago": ""}, "ERR_VALIDACION"),
        ({"cliente_edad": "no-numero"}, "ERR_VALIDACION"),
        ({"restriccion_edad": 18, "cliente_edad": 17}, "ERR_EDAD_INSUFICIENTE"),
    ],
)
def test_clases_invalidas(
    ventas_service: VentasService,
    override_payload: dict[str, object],
    codigo_error: str,
) -> None:
    payload = _base_payload(**override_payload)

    result = ventas_service.comprar_entrada(payload)

    assert result["status"] == "error"
    assert result["codigo_error"] == codigo_error


def test_metodo_pago_solo_efectivo(ventas_service: VentasService) -> None:
    payload = _base_payload(metodo_pago="tarjeta")

    result = ventas_service.comprar_entrada(payload)

    assert result["status"] == "error"
    assert result["codigo_error"] == "ERR_VALIDACION"
    assert "efectivo" in result["mensaje"].lower()


def test_ticket_se_recupera_despues_de_compra(ventas_service: VentasService) -> None:
    payload = _base_payload()
    compra = ventas_service.comprar_entrada(payload)

    ticket = ventas_service.mostrar_ticket(compra["venta_id"])

    assert ticket["status"] == "ok"
    assert compra["venta_id"] in ticket["ticket_texto"]
