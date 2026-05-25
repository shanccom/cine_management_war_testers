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
        "cliente_nombre": "Maria",
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


@pytest.mark.parametrize(
    "edad",
    [
        5,
        6,
        17,
        18,
        25,
        99,
        110,
    ],
)
def test_cliente_edad_valida_avl(ventas_service: VentasService, edad: int) -> None:
    payload = _base_payload(cliente_edad=edad, restriccion_edad=0)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "ok", f"Edad valida rechazada: {edad!r} -> {result}"


@pytest.mark.parametrize(
    "edad",
    [
        0,
        1,
        2,
        3,
        4,
    ],
)
def test_cliente_menor_de_cinco_no_paga_avl(ventas_service: VentasService, edad: int) -> None:
    payload = _base_payload(cliente_edad=edad, restriccion_edad=0)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "ok"
    assert result["total"] == pytest.approx(0.0)
    assert "S/. 0.00" in result["ticket_texto"]


@pytest.mark.parametrize(
    "edad",
    [
        -1,
        -5,
        "-1",
        "+1",
        " 20 ",
        "abc",
        "18a",
        "18.5",
        "",
        None,
        True,
        [],
        {},
        float("nan"),
        float("inf"),
        18.5,
        111,
        9999,
        "1e2",
        "--10",
        "🙂",
    ],
)
def test_cliente_edad_invalida_avl(ventas_service: VentasService, edad: object) -> None:
    payload = _base_payload(cliente_edad=edad)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "error"
    assert result["codigo_error"] == "ERR_VALIDACION"


def test_monto_en_soles_en_ticket(ventas_service: VentasService) -> None:
    payload = _base_payload(precio_unitario=42.5, cantidad_entradas=2)

    result = ventas_service.comprar_entrada(payload)

    assert result["status"] == "ok"
    assert "S/." in result["ticket_texto"]
    assert result["total"] == pytest.approx(85.0)


# --- Pruebas AVL adicionales para cliente_nombre
def test_cliente_nombre_too_short_and_too_long_avl(ventas_service: VentasService) -> None:
    payload_short = _base_payload(cliente_nombre="A")
    res_short = ventas_service.comprar_entrada(payload_short)
    assert res_short["status"] == "error"
    assert res_short["codigo_error"] == "ERR_VALIDACION"

    payload_long = _base_payload(cliente_nombre="A" * 10000)
    res_long = ventas_service.comprar_entrada(payload_long)
    assert res_long["status"] == "error"
    assert res_long["codigo_error"] == "ERR_VALIDACION"


@pytest.mark.parametrize(
    "nombre",
    [
        "AB",
        "Carlos",
        "María",
        "José",
        "Zoë",
        "Renée",
        "李小龍",
        "André",
    ],
)
def test_cliente_nombre_valido_solo_letras_avl(ventas_service: VentasService, nombre: str) -> None:
    payload = _base_payload(cliente_nombre=nombre)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "ok", f"Nombre valido rechazado: {nombre!r} -> {result}"


@pytest.mark.parametrize(
    "nombre",
    [
        "Juan Perez",
        "María-José",
        "O'Connor",
        "Ana María",
        "Alaa el-Din",
        "123ABC",
        "ABC123",
        "<script>",
        "DROP TABLE",
        "\x00",
        "\t",
        "\n",
        "😀",
        "   Juan",
        "Juan   ",
    ],
)
def test_cliente_nombre_invalido_solo_letras_avl(ventas_service: VentasService, nombre: object) -> None:
    payload = _base_payload(cliente_nombre=nombre)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "error"
    assert result["codigo_error"] == "ERR_VALIDACION"


@pytest.mark.parametrize(
    "documento, expected_status, expected_fragment",
    [
        ("1234567", "error", "8 digitos"),
        ("12345678", "ok", None),
        ("123456789", "ok", None),
        ("1234567890", "error", "8 digitos"),
        ("00000000", "ok", None),
        ("000000000", "ok", None),
    ],
)
def test_limites_documento_dni_carnet_avl(
    ventas_service: VentasService,
    documento: str,
    expected_status: str,
    expected_fragment: str | None,
) -> None:
    payload = _base_payload(cliente_documento=documento)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == expected_status
    if expected_status == "error":
        assert result["codigo_error"] == "ERR_VALIDACION"
        assert expected_fragment is not None
        assert expected_fragment in result["mensaje"].lower()


@pytest.mark.parametrize(
    "documento",
    [
        "12A45678",
        "12-45678",
        "1234 678",
        "1234567a",
        "1234567.",
        "<script>",
        "../../123",
        " 12345678 ",
        True,
        None,
        ["12345678"],
        {"doc": "12345678"},
    ],
)
def test_documento_solo_numeros_y_sin_simbolos_avl(ventas_service: VentasService, documento: object) -> None:
    payload = _base_payload(cliente_documento=documento)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "error"
    assert result["codigo_error"] == "ERR_VALIDACION"
    assert any(
        fragment in result["mensaje"].lower()
        for fragment in ("numeros", "cadena", "nulo", "espacios")
    )
