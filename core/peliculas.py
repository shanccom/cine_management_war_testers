"""
Modelo base de peliculas y gestor de almacenamiento.

TODO: agregar reglas de negocio cuando se definan.
"""

from __future__ import annotations

import json
from pathlib import Path


class Pelicula:
    # Modelo simple para una pelicula.
    def __init__(
        self,
        nombre: str = "",
        genero: str = "",
        duracion: str = "",
        clasificacion: str = "",
        sala: str = "",
    ) -> None:
        # TODO: agregar validaciones basicas de campos
        self.nombre = nombre
        self.genero = genero
        self.duracion = duracion
        self.clasificacion = clasificacion
        self.sala = sala

    def to_dict(self) -> dict:
        # Convierte el modelo en un diccionario para JSON.
        return {
            "nombre": self.nombre,
            "genero": self.genero,
            "duracion": self.duracion,
            "clasificacion": self.clasificacion,
            "sala": self.sala,
        }

    @staticmethod
    def from_dict(data: dict) -> "Pelicula":
        # Crea una pelicula desde un diccionario.
        return Pelicula(
            nombre=data.get("nombre", ""),
            genero=data.get("genero", ""),
            duracion=data.get("duracion", ""),
            clasificacion=data.get("clasificacion", ""),
            sala=data.get("sala", ""),
        )


class PeliculaManager:
    # Maneja la persistencia JSON del modulo de peliculas.
    def __init__(self, ruta_archivo: str | None = None) -> None:
        # Define la ruta de almacenamiento.
        base_dir = Path(__file__).resolve().parent.parent
        self.ruta_archivo = (
            Path(ruta_archivo)
            if ruta_archivo
            else base_dir / "data" / "peliculas.json"
        )
        self._asegurar_archivo()

    def _asegurar_archivo(self) -> None:
        # Crea el archivo JSON si no existe.
        try:
            if not self.ruta_archivo.exists():
                self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
                with self.ruta_archivo.open("w", encoding="utf-8") as archivo:
                    json.dump({"items": []}, archivo, indent=2, ensure_ascii=False)
        except OSError:
            # TODO: agregar registro de errores en archivo o consola
            pass

    def cargar_peliculas(self) -> list[dict]:
        # Carga la lista de peliculas desde el JSON.
        self._asegurar_archivo()
        try:
            with self.ruta_archivo.open("r", encoding="utf-8") as archivo:
                data = json.load(archivo)
            items = data.get("items", [])
            if not isinstance(items, list):
                # TODO: validar estructura de datos del JSON
                return []
            return items
        except (OSError, json.JSONDecodeError):
            # TODO: informar error de lectura
            return []

    def guardar_peliculas(self, peliculas: list[dict]) -> bool:
        # Guarda la lista de peliculas en el JSON.
        try:
            with self.ruta_archivo.open("w", encoding="utf-8") as archivo:
                json.dump(
                    {"items": peliculas},
                    archivo,
                    indent=2,
                    ensure_ascii=False,
                )
            return True
        except OSError:
            # TODO: informar error de escritura
            return False

    def listar_peliculas(self) -> list[dict]:
        # Retorna la lista actual de peliculas.
        return self.cargar_peliculas()

    def agregar_pelicula(self, pelicula: dict) -> bool:
        # Agrega una pelicula al almacenamiento.
        peliculas = self.cargar_peliculas()
        peliculas.append(pelicula)
        return self.guardar_peliculas(peliculas)

    def editar_pelicula(self, indice: int, pelicula: dict) -> bool:
        # Edita una pelicula segun su indice.
        peliculas = self.cargar_peliculas()
        if indice < 0 or indice >= len(peliculas):
            # TODO: mejorar manejo de indices invalidos
            return False
        peliculas[indice] = pelicula
        return self.guardar_peliculas(peliculas)

    def eliminar_pelicula(self, indice: int) -> bool:
        # Elimina una pelicula segun su indice.
        peliculas = self.cargar_peliculas()
        if indice < 0 or indice >= len(peliculas):
            # TODO: mejorar manejo de indices invalidos
            return False
        peliculas.pop(indice)
        return self.guardar_peliculas(peliculas)
