"""
Modelo base de ventas.

TODO: agregar metodos de negocio y validaciones.
"""


class Venta:
    def __init__(
        self,
        venta_id: str = "",
        pelicula_id: str = "",
        sala_id: str = "",
        cantidad: int = 0,
        total: float = 0.0,
    ) -> None:
        # TODO: validar datos de entrada
        self.venta_id = venta_id
        self.pelicula_id = pelicula_id
        self.sala_id = sala_id
        self.cantidad = cantidad
        self.total = total

    def to_dict(self) -> dict:
        # TODO: agregar campos adicionales cuando se requiera
        return {
            "venta_id": self.venta_id,
            "pelicula_id": self.pelicula_id,
            "sala_id": self.sala_id,
            "cantidad": self.cantidad,
            "total": self.total,
        }

    @staticmethod
    def from_dict(data: dict) -> "Venta":
        # TODO: validar estructura de datos
        return Venta(
            venta_id=data.get("venta_id", ""),
            pelicula_id=data.get("pelicula_id", ""),
            sala_id=data.get("sala_id", ""),
            cantidad=data.get("cantidad", 0),
            total=data.get("total", 0.0),
        )
