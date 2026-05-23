"""
Modelo base de peliculas.

TODO: agregar metodos de negocio y validaciones.
"""


class Pelicula:
    def __init__(
        self,
        pelicula_id: str = "",
        titulo: str = "",
        duracion: int = 0,
        clasificacion: str = "",
    ) -> None:
        # TODO: validar datos de entrada
        self.pelicula_id = pelicula_id
        self.titulo = titulo
        self.duracion = duracion
        self.clasificacion = clasificacion

    def to_dict(self) -> dict:
        # TODO: agregar campos adicionales cuando se requiera
        return {
            "pelicula_id": self.pelicula_id,
            "titulo": self.titulo,
            "duracion": self.duracion,
            "clasificacion": self.clasificacion,
        }

    @staticmethod
    def from_dict(data: dict) -> "Pelicula":
        # TODO: validar estructura de datos
        return Pelicula(
            pelicula_id=data.get("pelicula_id", ""),
            titulo=data.get("titulo", ""),
            duracion=data.get("duracion", 0),
            clasificacion=data.get("clasificacion", ""),
        )
