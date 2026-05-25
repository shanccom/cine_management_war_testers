"""
Pruebas de Analisis de Valores Limite para salas.
"""

import unittest

# Importamos la clase que acabamos de blindar
from core.salas import Sala

class TestAVLSalas(unittest.TestCase):
    
    def test_limite_inferior_invalido(self) -> None:
        """
        Prueba con capacidad = 0.
        Debe rebotar y lanzar un ValueError.
        """
        with self.assertRaises(ValueError) as context:
            Sala(sala_id="S01", numero=1, capacidad=0)
            
        self.assertEqual(str(context.exception), "La capacidad de la sala debe estar entre 1 y 300")

    def test_limite_inferior_valido(self) -> None:
        """
        Prueba con capacidad = 1 (Minimo permitido).
        Debe crearse correctamente sin lanzar errores.
        """
        sala = Sala(sala_id="S02", numero=2, capacidad=1)
        self.assertEqual(sala.capacidad, 1)

    def test_limite_superior_valido(self) -> None:
        """
        Prueba con capacidad = 300 (Maximo permitido).
        Debe crearse correctamente sin lanzar errores.
        """
        sala = Sala(sala_id="S03", numero=3, capacidad=300)
        self.assertEqual(sala.capacidad, 300)

    def test_limite_superior_invalido(self) -> None:
        """
        Prueba con capacidad = 301.
        Debe rebotar y lanzar un ValueError.
        """
        with self.assertRaises(ValueError) as context:
            Sala(sala_id="S04", numero=4, capacidad=301)
            
        self.assertEqual(str(context.exception), "La capacidad de la sala debe estar entre 1 y 300")


if __name__ == "__main__":
    unittest.main()