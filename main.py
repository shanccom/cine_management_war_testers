"""
Sistema de Gestion de Cine

TODO: Punto de entrada principal. Agregar configuracion y carga inicial.
"""

import tkinter as tk

from ui.main_window import MainWindow


def main() -> None:
    # TODO: agregar parametros de inicio y configuracion global
    root = tk.Tk()
    root.title("Sistema de Gestion de Cine")
    root.geometry("600x400")
    root.configure(bg="#f2f2f2")

    MainWindow(root)

    # TODO: conectar carga de datos desde JSON
    root.mainloop()


if __name__ == "__main__":
    main()
