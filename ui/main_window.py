"""
Menu principal del sistema en consola.

TODO: agregar opciones para otros modulos.
"""

from ui.peliculas_ui import PeliculasUI


class MainWindow:
    def __init__(self) -> None:
        # Inicializa el menu principal en consola.
        self._peliculas_ui = PeliculasUI()

    def show(self) -> None:
        # Muestra el menu principal.
        while True:
            print("\n=== Sistema de Gestion de Cine ===")
            print("1. Peliculas")
            print("0. Salir")

            opcion = input("Seleccione una opcion: ").strip()
            if opcion == "1":
                self._peliculas_ui.show()
            elif opcion == "0":
                print("Saliendo del sistema.")
                break
            else:
                print("Opcion no valida.")
