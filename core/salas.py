"""
Modelo base de salas.
"""

class Sala:
    def __init__(
        self,
        sala_id: str = "",
        numero: int = 0,
        capacidad: int = 0,
    ) -> None:
        if type(numero) is not int:
            raise TypeError("El numero de sala debe ser un numero entero")

        if type(capacidad) is not int:
            raise TypeError("La capacidad debe ser un numero entero")

        if numero < 0:
            raise ValueError("El numero de sala no puede ser negativo")

        if capacidad < 1 or capacidad > 300:
            raise ValueError("La capacidad de la sala debe estar entre 1 y 300")

        self.sala_id = str(sala_id)
        self.numero = numero
        self.capacidad = capacidad

    def to_dict(self) -> dict:
        return {
            "sala_id": self.sala_id,
            "numero": self.numero,
            "capacidad": self.capacidad,
        }

    @staticmethod
    def from_dict(data: dict) -> "Sala":
        return Sala(
            sala_id=data.get("sala_id", ""),
            numero=data.get("numero", 0),
            capacidad=data.get("capacidad", 0),
        )