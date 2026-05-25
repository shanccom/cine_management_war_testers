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
        "cliente_nombre": "Juan",
        "cliente_documento": "12345678",
        "tipo_documento": "dni",
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
def test_cliente_edad_valida_pe(ventas_service: VentasService, edad: int) -> None:
    payload = _base_payload(cliente_edad=edad)
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
def test_cliente_menor_de_cinco_pe(ventas_service: VentasService, edad: int) -> None:
    payload = _base_payload(cliente_edad=edad)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "error"
    assert result["codigo_error"] == "ERR_VALIDACION"
    assert "mayor o igual que 5" in result["mensaje"].lower()


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
def test_cliente_edad_invalida_pe(ventas_service: VentasService, edad: object) -> None:
    payload = _base_payload(cliente_edad=edad)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "error", f"Edad invalida aceptada: {edad!r} -> {result}"
    assert result["codigo_error"] == "ERR_VALIDACION"


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


# --- Casos adicionales para cliente_nombre (PE y vectores maliciosos)
@pytest.mark.parametrize(
    "nombre",
    [
        "Juan",
        "María",
        "李小龍",
        "Renée",
        "Zoë",
        "Émilie",
        "Ángel",
        "André",
    ],
)
def test_cliente_nombre_valido_pe(ventas_service: VentasService, nombre: str) -> None:
    payload = _base_payload(cliente_nombre=nombre)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "ok", f"Nombre valido rechazado: {nombre!r} -> {result}"


@pytest.mark.parametrize(
    "nombre",
    [
        "",
        "   ",
        "\t",
        "\n",
        None,
        12345,
        12.34,
        True,
        [],
        {},
        float("nan"),
        float("inf"),
        "A",
        "A" * 10000,
        "1234567890",
        "Juan Perez",
        "María-José",
        "O'Connor",
        "Ana María",
        "Alaa el-Din",
        "DROP TABLE usuarios;",
        "<script>alert(1)</script>",
        "SELECT * FROM usuarios;",
        "../../etc/passwd",
        "\\x00",
        "\u202e\u202e\u202e",
        "\ud83d\ude00",
        "\x1f\x8b\x08",
        "' OR '1'='1' --",
    ],
)
def test_cliente_nombre_invalidos_pe(ventas_service: VentasService, nombre: object) -> None:
    payload = _base_payload(cliente_nombre=nombre)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "error", f"Nombre invalido aceptado: {nombre!r} -> {result}"
    assert result["codigo_error"] == "ERR_VALIDACION"


@pytest.mark.parametrize(
    "raw",
    [
        "<img src=x onerror=alert(1)>",
        "\"; DROP TABLE ventas; --",
        "../../..\\..\\windows\\system32",
        "\x00\x01\x02",
    ],
)
def test_cliente_nombre_inyecciones_pe(ventas_service: VentasService, raw: str) -> None:
    payload = _base_payload(cliente_nombre=raw)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "error"
    assert result["codigo_error"] == "ERR_VALIDACION"


def test_cliente_nombre_no_crashea_pe(ventas_service: VentasService) -> None:
    huge = "Nombre" * 10000
    payload = _base_payload(cliente_nombre=huge)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] in ("error", "ok")


@pytest.mark.parametrize(
    "documento, tipo_documento, expected_status, expected_fragment",
    [
        ("12345678", "dni", "ok", None),
        ("123456789", "carnet", "ok", None),
        ("00000000", "dni", "ok", None),
        ("000000000", "carnet", "ok", None),
        ("123456789", "dni", "error", "8 digitos"),
        ("12345678", "carnet", "error", "9 digitos"),
        (" 12345678 ", "dni", "error", "espacios"),
        ("1234567", "dni", "error", "8 digitos"),
        ("1234567890", "dni", "error", "8 digitos"),
        ("12A45678", "dni", "error", "solo numeros"),
        ("12-45678", "dni", "error", "solo numeros"),
        ("", "dni", "error", "vac"),
        (None, "dni", "error", "nulo"),
        (True, "dni", "error", "cadena"),
        (["12345678"], "dni", "error", "cadena"),
        ({"doc": "12345678"}, "dni", "error", "cadena"),
    ],
)
def test_cliente_documento_pe(
    ventas_service: VentasService,
    documento: object,
    tipo_documento: str,
    expected_status: str,
    expected_fragment: str | None,
) -> None:
    payload = _base_payload(cliente_documento=documento, tipo_documento=tipo_documento)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == expected_status
    if expected_status == "error":
        assert result["codigo_error"] == "ERR_VALIDACION"
        assert expected_fragment is not None
        assert expected_fragment in result["mensaje"].lower()

