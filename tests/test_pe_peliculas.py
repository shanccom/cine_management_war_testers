"""
Pruebas de Particion de Equivalencia para el modulo de peliculas.
"""
import pytest

from core.peliculas import PeliculaManager
from core.validaciones import (
    CLASIFICACIONES_VALIDAS,
    GENEROS_VALIDOS,
    validar_clasificacion,
    validar_duracion,
    validar_genero,
    validar_nombre,
    validar_pelicula,
    validar_sala,
)

def _pelicula_valida() -> dict:
    return {
        "nombre": "Matrix",
        "genero": GENEROS_VALIDOS[0],
        "duracion": "120",
        "clasificacion": CLASIFICACIONES_VALIDAS[0],
        "sala": "5",
    }

@pytest.mark.parametrize(
    "valor, esperado_ok",
    [
        ("", False),
        ("Matrix", True),
        ("A", False),
        ("A" * 51, False),
    ],
)
def test_pe_nombre_ok(valor, esperado_ok) -> None:
    # Arrange
    # Escenario: vacio, valido, muy corto, muy largo
    entrada = valor
    esperado = esperado_ok

    # Act
    ok, _, _ = validar_nombre(entrada)
    actual = ok

    # Assert
    assert actual is esperado


@pytest.mark.parametrize(
    "valor, esperado_ok",
    [
        (GENEROS_VALIDOS[0], True),
        ("Romance", False),
    ],
)
def test_pe_genero_ok(valor, esperado_ok) -> None:
    # Arrange
    # Escenario: genero valido e invalido
    entrada = valor
    esperado = esperado_ok

    # Act
    ok, _, _ = validar_genero(entrada)
    actual = ok

    # Assert
    assert actual is esperado


@pytest.mark.parametrize(
    "valor, esperado_ok",
    [
        ("120", True),
        ("29", False),
        ("301", False),
        ("texto", False),
    ],
)
def test_pe_duracion_ok(valor, esperado_ok) -> None:
    # Arrange
    # Escenario: dentro del rango, menor al limite, mayor al limite, texto
    entrada = valor
    esperado = esperado_ok

    # Act
    ok, _, _ = validar_duracion(entrada)
    actual = ok

    # Assert
    assert actual is esperado


@pytest.mark.parametrize(
    "valor, esperado_ok",
    [
        (CLASIFICACIONES_VALIDAS[0], True),
        ("R", False),
    ],
)
def test_pe_clasificacion_ok(valor, esperado_ok) -> None:
    # Arrange
    # Escenario: clasificacion valida e invalida
    entrada = valor
    esperado = esperado_ok

    # Act
    ok, _, _ = validar_clasificacion(entrada)
    actual = ok

    # Assert
    assert actual is esperado


@pytest.mark.parametrize(
    "valor, esperado_ok",
    [
        ("10", True),
        ("0", False),
        ("21", False),
        ("texto", False),
    ],
)
def test_pe_sala_ok(valor, esperado_ok) -> None:
    # Arrange
    # Escenario: sala valida, menor al rango, mayor al rango, texto
    entrada = valor
    esperado = esperado_ok

    # Act
    ok, _, _ = validar_sala(entrada)
    actual = ok

    # Assert
    assert actual is esperado


def test_pe_pelicula_valida_ok() -> None:
    # Arrange
    # Escenario: pelicula con todos los campos validos
    pelicula = _pelicula_valida()
    esperado = True

    # Act
    ok, _, _ = validar_pelicula(pelicula)
    actual = ok

    # Assert
    assert actual is esperado

def test_pe_pelicula_valida_errores() -> None:
    # Arrange
    # Escenario: pelicula valida no debe retornar errores
    pelicula = _pelicula_valida()
    esperado = []

    # Act
    _, errores, _ = validar_pelicula(pelicula)
    actual = errores

    # Assert
    assert actual == esperado


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("nombre", ""),
        ("duracion", "-5"),
        ("nombre", "A" * 120),
        ("nombre", "Alien!"),
        ("sala", ["texto"]),
    ],
)
def test_robustez_pelicula_invalida_ok(campo, valor) -> None:
    # Arrange
    # Escenario: datos extremos o tipos incorrectos
    pelicula = _pelicula_valida()
    pelicula[campo] = valor
    esperado = False

    # Act
    ok, _, _ = validar_pelicula(pelicula)
    actual = ok

    # Assert
    assert actual is esperado


def test_robustez_datos_no_diccionario_ok() -> None:
    # Arrange
    # Escenario: estructura de datos invalida
    pelicula = ["no", "dict"]
    esperado = False

    # Act
    ok, _, _ = validar_pelicula(pelicula)
    actual = ok

    # Assert
    assert actual is esperado

def test_robustez_constructor_ruta_archivo_invalida() -> None:
    # Arrange
    # Escenario: tipo incorrecto en la ruta del archivo
    ruta_invalida = 123

    # Act / Assert
    with pytest.raises(TypeError):
        PeliculaManager(ruta_archivo=ruta_invalida)