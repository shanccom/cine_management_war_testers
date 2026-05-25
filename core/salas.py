"""
Modelo base de salas y gestion de asientos con validacion Regex.
"""

import re

class Sala:
    def __init__(
        self,
        sala_id: str = "",
        numero: int = 0,
        capacidad: int = 0,
        asientos_ocupados: list = None,
    ) -> None:
        
        # 1. Validaciones de Tipo de Entrada
        if type(numero) is not int:
            raise TypeError("El numero de sala debe ser un numero entero")

        if type(capacidad) is not int:
            raise TypeError("La capacidad debe ser un numero entero")

        # 2. Validaciones de Valores Limite (AVL)
        if numero < 0:
            raise ValueError("El numero de sala no puede ser negativo")

        if capacidad < 1 or capacidad > 300:
            raise ValueError("La capacidad de la sala debe estar entre 1 y 300")

        # Asignacion de propiedades basicas
        self.sala_id = str(sala_id)
        self.numero = numero
        self.capacidad = capacidad

        # 3. Inicializacion y validacion de la lista de asientos
        if asientos_ocupados is None:
            self.asientos_ocupados = []
        else:
            if type(asientos_ocupados) is not list:
                raise TypeError("Los asientos ocupados deben estructurarse en una lista")
            self.asientos_ocupados = list(asientos_ocupados)

    def reservar_asiento(self, asiento_id: str) -> bool:
        """
        Reserva un asiento especifico en la sala.
        Valida el tipo, formato Regex, disponibilidad y duplicados.
        """
        if type(asiento_id) is not str:
            raise TypeError("El identificador del asiento debe ser un texto")
            
        asiento_limpio = asiento_id.strip().upper()
        if not asiento_limpio:
            raise ValueError("El codigo de asiento no puede estar vacio")

        # 4. Validacion de Formato Estricto (Regex)
        # ^[A-Z]    -> Debe empezar con una letra mayuscula de la A a la Z.
        # \d{1,2}$  -> Debe terminar obligatoriamente con 1 o 2 digitos numericos (ej: A1, B12).
        patron_asiento = r"^[A-Z]\d{1,2}$"
        if not re.match(patron_asiento, asiento_limpio):
            raise ValueError("El formato del asiento debe ser una letra seguida de uno o dos numeros (ej: A1, B12)")

        if len(self.asientos_ocupados) >= self.capacidad:
            raise ValueError("No se pueden reservar mas asientos, la sala esta llena")

        if asiento_limpio in self.asientos_ocupados:
            raise ValueError(f"El asiento {asiento_limpio} ya se encuentra reservado")

        self.asientos_ocupados.append(asiento_limpio)
        return True

    def to_dict(self) -> dict:
        return {
            "sala_id": self.sala_id,
            "numero": self.numero,
            "capacidad": self.capacidad,
            "asientos_ocupados": self.asientos_ocupados,
        }

    @staticmethod
    def from_dict(data: dict) -> "Sala":
        return Sala(
            sala_id=data.get("sala_id", ""),
            numero=data.get("numero", 0),
            capacidad=data.get("capacidad", 0),
            asientos_ocupados=data.get("asientos_ocupados", []),
        )