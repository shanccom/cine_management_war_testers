"""
Pruebas de Analisis de Valores Limite para salas usando pytest.
"""

import pytest
from core.salas import Sala

def test_limite_inferior_invalido() -> None:
    """
    Prueba con capacidad = 0.
    Debe rebotar y lanzar un ValueError.
    """
    with pytest.raises(ValueError) as context:
        Sala(sala_id="S01", numero=1, capacidad=0)
        
    assert str(context.value) == "La capacidad de la sala debe estar entre 1 y 300"

def test_limite_inferior_valido() -> None:
    """
    Prueba con capacidad = 1 (Minimo permitido).
    Debe crearse correctamente sin lanzar errores.
    ```"""
    sala = Sala(sala_id="S02", numero=2, capacidad=1)
    assert sala.capacidad == 1

def test_limite_superior_valido() -> None:
    """
    Prueba con capacidad = 300 (Maximo permitido).
    Debe crearse correctamente sin lanzar errores.
    """
    sala = Sala(sala_id="S03", numero=3, capacidad=300)
    assert sala.capacidad == 300

def test_limite_superior_invalido() -> None:
    """
    Prueba con capacidad = 301.
    Debe rebotar y lanzar un ValueError.
    """
    with pytest.raises(ValueError) as context:
        Sala(sala_id="S04", numero=4, capacidad=301)
        
    assert str(context.value) == "La capacidad de la sala debe estar entre 1 y 300"