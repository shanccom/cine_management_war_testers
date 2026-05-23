"""
Modelo base de salas.

TODO: agregar metodos de negocio y validaciones.
"""


class Sala:
    def __init__(
        self,
        sala_id: str = "",
        numero: int = 0,
        capacidad: int = 0,
    ) -> None:
        # TODO: validar datos de entrada
        self.sala_id = sala_id
        self.numero = numero
        self.capacidad = capacidad

    def to_dict(self) -> dict:
        # TODO: agregar campos adicionales cuando se requiera
        return {
            "sala_id": self.sala_id,
            "numero": self.numero,
            "capacidad": self.capacidad,
        }

    @staticmethod
    def from_dict(data: dict) -> "Sala":
        # TODO: validar estructura de datos
        return Sala(
            sala_id=data.get("sala_id", ""),
            numero=data.get("numero", 0),
            capacidad=data.get("capacidad", 0),
        )
