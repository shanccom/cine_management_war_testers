"""
Pruebas de Particion de Equivalencia (PE) para el modulo de salas.
"""

import unittest
from core.salas import Sala

class TestPESalas(unittest.TestCase):
    
    def setUp(self) -> None:
        # Se ejecuta antes de cada test.
        # Preparamos una sala valida para poder probar la logica de asientos.
        self.sala_prueba = Sala(sala_id="S1", numero=1, capacidad=50)

    # --- CLASES INVALIDAS DE CREACION DE SALA ---

    def test_pe_capacidad_negativa(self) -> None:
        """
        Clase Invalida: Cualquier capacidad negativa (ej: -15).
        Resultado Esperado: Rechazo con ValueError.
        """
        with self.assertRaises(ValueError) as context:
            Sala(sala_id="S2", numero=2, capacidad=-15)
        self.assertIn("entre 1 y 300", str(context.exception))

    def test_pe_numero_sala_negativo(self) -> None:
        """
        Clase Invalida: Cualquier numero de sala negativo (ej: -5).
        Resultado Esperado: Rechazo con ValueError.
        """
        with self.assertRaises(ValueError) as context:
            Sala(sala_id="S-5", numero=-5, capacidad=100)
        self.assertIn("no puede ser negativo", str(context.exception))

    def test_pe_inyeccion_tipos_invalidos(self) -> None:
        """
        Clase Invalida: Ingresar letras o texto donde van numeros enteros.
        Resultado Esperado: Rechazo con TypeError.
        """
        with self.assertRaises(TypeError):
            # Simulamos que el rival logra saltar la interfaz y manda un string
            Sala(sala_id="S3", numero="Tres", capacidad=50)

    # --- CLASES INVALIDAS DE RESERVA DE ASIENTOS ---

    def test_pe_asiento_vacio(self) -> None:
        """
        Clase Invalida: Codigo de asiento compuesto solo por espacios o vacio.
        Resultado Esperado: Rechazo con ValueError.
        """
        with self.assertRaises(ValueError) as context:
            self.sala_prueba.reservar_asiento("    ")
        self.assertIn("no puede estar vacio", str(context.exception))

    def test_pe_asiento_tipo_invalido(self) -> None:
        """
        Clase Invalida: Enviar un numero entero o booleano como asiento en lugar de texto.
        Resultado Esperado: Rechazo con TypeError.
        """
        with self.assertRaises(TypeError) as context:
            self.sala_prueba.reservar_asiento(123)
        self.assertIn("debe ser un texto", str(context.exception))

    def test_pe_asiento_duplicado(self) -> None:
        """
        Clase Invalida: Intentar reservar un asiento que ya pertenece a la lista de ocupados.
        Resultado Esperado: Rechazo con ValueError.
        """
        # Primera reserva (Valida)
        self.sala_prueba.reservar_asiento("A1")
        
        # Segunda reserva del mismo asiento (Invalida)
        with self.assertRaises(ValueError) as context:
            self.sala_prueba.reservar_asiento("A1")
        self.assertIn("ya se encuentra reservado", str(context.exception))


if __name__ == "__main__":
    unittest.main()