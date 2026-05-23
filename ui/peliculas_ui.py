"""
Interfaz del modulo de peliculas.

TODO: definir componentes y acciones del modulo.
"""

import tkinter as tk


class PeliculasUI:
    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent
        self.window: tk.Toplevel | None = None

    def show(self) -> None:
        if self.window is None or not self.window.winfo_exists():
            self.window = tk.Toplevel(self.parent)
            self.window.title("Peliculas")
            self.window.geometry("400x300")
            self.window.configure(bg="#f2f2f2")

            label = tk.Label(
                self.window,
                text="Modulo de Peliculas",
                bg="#f2f2f2",
                fg="#333333",
                font=("Arial", 12, "bold"),
            )
            label.pack(pady=20)

            # TODO: agregar formulario y tabla de peliculas
        else:
            self.window.focus()
