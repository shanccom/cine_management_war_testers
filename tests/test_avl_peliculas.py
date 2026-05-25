"""
Pruebas de Analisis de Valores Limite para el modulo de peliculas.
"""
import pytest

from core.validaciones import validar_duracion, validar_sala

@pytest.mark.parametrize(
    "valor, esperado_ok",
    [
        ("29", False),
        ("30", True),
        ("31", True),
    ],
)
def test_avl_duracion_frontera_inferior(valor, esperado_ok) -> None:
    # Arrange
    # Escenario: frontera inferior con invalido y valido
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
        ("299", True),
        ("300", True),
        ("301", False),
    ],
)
def test_avl_duracion_frontera_superior(valor, esperado_ok) -> None:
    # Arrange
    # Escenario: frontera superior con valido e invalido
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
        ("0", False),
        ("1", True),
        ("2", True),
    ],
)
def test_avl_sala_frontera_inferior(valor, esperado_ok) -> None:
    # Arrange
    # Escenario: frontera inferior con invalido y valido
    entrada = valor
    esperado = esperado_ok

    # Act
    ok, _, _ = validar_sala(entrada)
    actual = ok

    # Assert
    assert actual is esperado


@pytest.mark.parametrize(
    "valor, esperado_ok",
    [
        ("19", True),
        ("20", True),
        ("21", False),
    ],
)
def test_avl_sala_frontera_superior(valor, esperado_ok) -> None:
    # Arrange
    # Escenario: frontera superior con valido e invalido
    entrada = valor
    esperado = esperado_ok

    # Act
    ok, _, _ = validar_sala(entrada)
    actual = ok

    # Assert
    assert actual is esperado
