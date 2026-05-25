"""
Pruebas de Particion de Equivalencia (PE) para el modulo de salas usando pytest.
"""

import pytest
from core.salas import Sala

@pytest.fixture
def sala_prueba() -> Sala:
    """Fixture que prepara una sala valida para las pruebas de asientos."""
    return Sala(sala_id="S1", numero=1, capacidad=50)


# --- CLASES INVALIDAS DE CREACION DE SALA ---

def test_pe_capacidad_negativa() -> None:
    """
    Clase Invalida: Cualquier capacidad negativa (ej: -15).
    Resultado Esperado: Rechazo con ValueError.
    """
    with pytest.raises(ValueError) as context:
        Sala(sala_id="S2", numero=2, capacidad=-15)
    assert "entre 1 y 300" in str(context.value)

def test_pe_numero_sala_negativo() -> None:
    """
    Clase Invalida: Cualquier numero de sala negativo (ej: -5).
    Resultado Esperado: Rechazo con ValueError.
    """
    with pytest.raises(ValueError) as context:
        Sala(sala_id="S-5", numero=-5, capacidad=100)
    assert "no puede ser negativo" in str(context.value)

def test_pe_inyeccion_tipos_invalidos() -> None:
    """
    Clase Invalida: Ingresar letras o texto donde van numeros enteros.
    Resultado Esperado: Rechazo con TypeError.
    """
    with pytest.raises(TypeError):
        Sala(sala_id="S3", numero="Tres", capacidad=50)


# --- CLASES INVALIDAS DE RESERVA DE ASIENTOS ---

def test_pe_asiento_vacio(sala_prueba: Sala) -> None:
    """
    Clase Invalida: Codigo de asiento compuesto solo por espacios o vacio.
    Resultado Esperado: Rechazo con ValueError.
    """
    with pytest.raises(ValueError) as context:
        sala_prueba.reservar_asiento("    ")
    assert "no puede estar vacio" in str(context.value)

def test_pe_asiento_tipo_invalido(sala_prueba: Sala) -> None:
    """
    Clase Invalida: Enviar un numero entero o booleano como asiento en lugar de texto.
    Resultado Esperado: Rechazo con TypeError.
    """
    with pytest.raises(TypeError) as context:
        sala_prueba.reservar_asiento(123)
    assert "debe ser un texto" in str(context.value)

def test_pe_asiento_duplicado(sala_prueba: Sala) -> None:
    """
    Clase Invalida: Intentar reservar un asiento que ya pertenece a la lista de ocupados.
    Resultado Esperado: Rechazo con ValueError.
    """
    # Primera reserva (Valida)
    sala_prueba.reservar_asiento("A1")
    
    # Segunda reserva del mismo asiento (Invalida)
    with pytest.raises(ValueError) as context:
        sala_prueba.reservar_asiento("A1")
    assert "ya se encuentra reservado" in str(context.value)

def test_pe_asiento_fuera_de_capacidad_logica() -> None:
    """
    Clase Invalida: Un asiento con formato correcto pero numero incoherente (ej: Z99 en capacidad 2).
    Resultado Esperado: Rechazo con ValueError por inconsistencia semantica.
    """
    # Creamos la sala de pruebas local aqui adentro
    sala_pequena = Sala(sala_id="S5", numero=5, capacidad=2)
    
    with pytest.raises(ValueError) as context:
        sala_pequena.reservar_asiento("Z99")
    assert "no puede exceder la capacidad maxima" in str(context.value)