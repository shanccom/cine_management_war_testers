"""Pruebas estrictas y ofensivas para el campo `cliente_nombre`.

Estas pruebas implementan Particion de Equivalencia (PE), Analisis de Valores Limite (AVL)
y vectores maliciosos (injecciones, rutas, caracteres no imprimibles, tipos invalidos).
Diseñadas por QA ofensivo para detectar debilidades y forzar cambios en produccion.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from services.ventas_service import VentasService


def _base_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pelicula_id": "PX",
        "pelicula_titulo": "Prueba",
        "sala_id": "S1",
        "sala_numero": 1,
        "funcion_id": "F1",
        "fecha_hora": (datetime.now() + timedelta(hours=1)).replace(microsecond=0).isoformat(timespec="seconds"),
        "cliente_nombre": "Nombre Valido",
        "cliente_documento": "11111111",
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
    "nombre",
    [
        # Validos: nombres normales, con espacios, guiones y apóstrofes
        "Juan Perez",
        "María-José O'Connor",
        "Óscar Núñez",
        "Anne Marie",
        "李小龍",
        "N'Golo Kanté",
        "Alaa el-Din",
        "José Luis",
        "Renée",
        "A" * 2,  # limite inferior aceptable (2)
        "A" * 100,  # long razonable alta
        "Zoë",
        "Émilie",
    ],
)
def test_cliente_nombre_valido(ventas_service: VentasService, nombre: str) -> None:
    payload = _base_payload(cliente_nombre=nombre)
    result = ventas_service.comprar_entrada(payload)
    assert result["status"] == "ok", f"Nombre valido rechazado: {nombre!r} -> {result}"


@pytest.mark.parametrize(
    "nombre",
    [
        "",  # vacio
        "   ",  # espacios solo
        "\t",  # tab
        "\n",  # salto de linea
        None,
        12345,  # tipo incorrecto: int
        12.34,  # float
        True,  # booleano
        [],  # lista
        {},  # dict
        float("nan"),
        float("inf"),
        "A",  # demasiado corto (<2)
        "A" * 10000,  # overflow longitud extrema
        "1234567890",  # solo numeros
        "DROP TABLE usuarios;",  # SQL injection
        "<script>alert(1)</script>",  # XSS
        "SELECT * FROM usuarios;",
        "../../etc/passwd",
        "\\x00",  # null byte
        "\u202e\u202e\u202e",  # unicode control
        "\ud83d\ude00",  # emoji
        "\x1f\x8b\x08",  # secuencia binaria / control
        "    Nombre  Con  Doble   Espacio   ",  # doble espacio interno (deseable: normalizar)
        "   InicioEspacio",
        "FinEspacio   ",
        "' OR '1'='1' --",  # SQL tautologia
    ],
)
def test_cliente_nombre_invalidos(ventas_service: VentasService, nombre: object) -> None:
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
def test_cliente_nombre_inyecciones_y_rutas(ventas_service: VentasService, raw: str) -> None:
    payload = _base_payload(cliente_nombre=raw)
    result = ventas_service.comprar_entrada(payload)
    # En seguridad preferimos que sean rechazadas; exigir error de validacion
    assert result["status"] == "error"
    assert result["codigo_error"] == "ERR_VALIDACION"


def test_cliente_nombre_no_crashea_con_copias_masivas(ventas_service: VentasService) -> None:
    huge = "Nombre" * 10000
    payload = _base_payload(cliente_nombre=huge)
    result = ventas_service.comprar_entrada(payload)
    # No debe crashear; preferible rechazo por validacion o manejo, no excepcion
    assert result["status"] in ("error", "ok")
