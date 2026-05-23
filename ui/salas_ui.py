"""
Interfaz del modulo de salas.

TODO: definir componentes y acciones del modulo.
"""

import tkinter as tk


class SalasUI:
    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent
        self.window: tk.Toplevel | None = None

    def show(self) -> None:
        if self.window is None or not self.window.winfo_exists():
            self.window = tk.Toplevel(self.parent)
            self.window.title("Salas")
            self.window.geometry("400x300")
            self.window.configure(bg="#f2f2f2")

            label = tk.Label(
                self.window,
                text="Modulo de Salas",
                bg="#f2f2f2",
                fg="#333333",
                font=("Arial", 12, "bold"),
            )
            label.pack(pady=20)

            # TODO: agregar formulario y tabla de salas
        else:
            self.window.focus()
