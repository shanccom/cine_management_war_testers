"""
Interfaz en consola del modulo de peliculas.

TODO: agregar confirmaciones antes de eliminar registros.
"""

from core.peliculas import PeliculaManager
from core.validaciones import (
    CLASIFICACIONES_VALIDAS,
    GENEROS_VALIDOS,
    validar_clasificacion,
    validar_duracion,
    validar_genero,
    validar_nombre,
    validar_sala,
)


class PeliculasUI:
    def __init__(self, manager: PeliculaManager | None = None) -> None:
        # Inicializa el gestor de peliculas.
        self.manager = manager or PeliculaManager()

    def show(self) -> None:
        # Muestra el menu del modulo en consola.
        while True:
            print("\n=== Modulo de Peliculas ===")
            print("1. Registrar pelicula")
            print("2. Editar pelicula")
            print("3. Eliminar pelicula")
            print("4. Listar peliculas")
            print("0. Volver")

            opcion = input("Seleccione una opcion: ").strip()
            if opcion == "1":
                self.registrar_pelicula()
            elif opcion == "2":
                self.editar_pelicula()
            elif opcion == "3":
                self.eliminar_pelicula()
            elif opcion == "4":
                self.listar_peliculas()
            elif opcion == "0":
                break
            else:
                print("Opcion no valida.")

    def registrar_pelicula(self) -> None:
        # Registra una pelicula nueva.
        pelicula = self._leer_pelicula()
        if self.manager.agregar_pelicula(pelicula):
            print("Pelicula registrada.")
        else:
            self._mostrar_errores("No se pudo registrar la pelicula.")

    def editar_pelicula(self) -> None:
        # Edita una pelicula existente.
        peliculas = self.manager.listar_peliculas()
        if not peliculas:
            print("No hay peliculas para editar.")
            return

        self._mostrar_peliculas(peliculas)
        indice = self._leer_indice()
        if indice is None:
            return
        if indice < 0 or indice >= len(peliculas):
            print("Indice fuera de rango.")
            return

        pelicula = self._leer_pelicula()
        if self.manager.editar_pelicula(indice, pelicula):
            print("Pelicula actualizada.")
        else:
            self._mostrar_errores("No se pudo editar la pelicula.")

    def eliminar_pelicula(self) -> None:
        # Elimina una pelicula existente.
        peliculas = self.manager.listar_peliculas()
        if not peliculas:
            print("No hay peliculas para eliminar.")
            return

        self._mostrar_peliculas(peliculas)
        indice = self._leer_indice()
        if indice is None:
            return
        if indice < 0 or indice >= len(peliculas):
            print("Indice fuera de rango.")
            return

        if self.manager.eliminar_pelicula(indice):
            print("Pelicula eliminada.")
        else:
            print("No se pudo eliminar la pelicula.")

    def listar_peliculas(self) -> None:
        # Lista las peliculas registradas.
        peliculas = self.manager.listar_peliculas()
        if not peliculas:
            print("No hay peliculas registradas.")
            return
        self._mostrar_peliculas(peliculas)

    def _leer_pelicula(self) -> dict:
        # Solicita los campos de la pelicula por consola.
        nombre = self._leer_con_validacion("Nombre: ", validar_nombre)
        genero = self._leer_con_validacion(
            f"Genero ({', '.join(GENEROS_VALIDOS)}): ",
            validar_genero,
        )
        duracion = self._leer_con_validacion(
            "Duracion (30-300): ",
            validar_duracion,
        )
        clasificacion = self._leer_con_validacion(
            f"Clasificacion ({', '.join(CLASIFICACIONES_VALIDAS)}): ",
            validar_clasificacion,
        )
        sala = self._leer_con_validacion(
            "Sala (1-20): ",
            validar_sala,
        )

        return {
            "nombre": nombre,
            "genero": genero,
            "duracion": duracion,
            "clasificacion": clasificacion,
            "sala": sala,
        }

    def _leer_con_validacion(self, prompt: str, validador) -> object:
        # Lee un valor y lo valida en el momento.
        while True:
            valor = input(prompt).strip()
            ok, mensaje, dato = validador(valor)
            if ok:
                return dato
            print(mensaje)

    def _mostrar_errores(self, encabezado: str) -> None:
        # Muestra errores del gestor si existen.
        print(encabezado)
        if self.manager.ultimo_error:
            for mensaje in self.manager.ultimo_error:
                print(f"- {mensaje}")

    def _leer_indice(self) -> int | None:
        # Lee el indice desde la consola con manejo simple de errores.
        valor = input("Indice: ").strip()
        try:
            return int(valor)
        except ValueError:
            print("Indice no valido.")
            return None

    def _mostrar_peliculas(self, peliculas: list[dict]) -> None:
        # Muestra las peliculas en formato de tabla simple.
        header = (
            f"{'ID':<4} {'Nombre':<20} {'Genero':<15} {'Duracion':<10} "
            f"{'Clasificacion':<15} {'Sala':<10}"
        )
        print("\nListado de peliculas")
        print(header)
        print("-" * len(header))

        for indice, pelicula in enumerate(peliculas):
            print(
                f"{indice:<4} "
                f"{pelicula.get('nombre', ''):<20} "
                f"{pelicula.get('genero', ''):<15} "
                f"{pelicula.get('duracion', ''):<10} "
                f"{pelicula.get('clasificacion', ''):<15} "
                f"{pelicula.get('sala', ''):<10}"
            )

        # TODO: mejorar el formato cuando los textos son largos
