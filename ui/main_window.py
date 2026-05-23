"""
Ventana principal del sistema.

TODO: definir acciones reales y navegacion completa.
"""

import tkinter as tk
from tkinter import messagebox

from ui.peliculas_ui import PeliculasUI
from ui.salas_ui import SalasUI
from ui.ventas_ui import VentasUI
from ui.reportes_ui import ReportesUI


class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._build_menu()
        self._build_layout()

        # TODO: inicializar controladores o servicios
        self._peliculas_ui = PeliculasUI(self.root)
        self._salas_ui = SalasUI(self.root)
        self._ventas_ui = VentasUI(self.root)
        self._reportes_ui = ReportesUI(self.root)

    def _build_menu(self) -> None:
        # TODO: agregar opciones de menu adicionales
        menubar = tk.Menu(self.root)
        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        ayuda_menu = tk.Menu(menubar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self._show_about)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        self.root.config(menu=menubar)

    def _build_layout(self) -> None:
        container = tk.Frame(self.root, bg="#f2f2f2", padx=20, pady=20)
        container.pack(expand=True, fill="both")

        title = tk.Label(
            container,
            text="Sistema de Gestion de Cine",
            bg="#f2f2f2",
            fg="#333333",
            font=("Arial", 16, "bold"),
        )
        title.pack(pady=(0, 20))

        button_frame = tk.Frame(container, bg="#f2f2f2")
        button_frame.pack()

        buttons = [
            ("Peliculas", self._open_peliculas),
            ("Salas", self._open_salas),
            ("Ventas", self._open_ventas),
            ("Reportes", self._open_reportes),
        ]

        for text, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                width=20,
                pady=8,
                command=command,
                bg="#e0e0e0",
                fg="#333333",
                relief="flat",
            )
            btn.pack(pady=6)

        # TODO: agregar pie de pagina o estado

    def _open_peliculas(self) -> None:
        # TODO: conectar con flujo real de peliculas
        self._peliculas_ui.show()

    def _open_salas(self) -> None:
        # TODO: conectar con flujo real de salas
        self._salas_ui.show()

    def _open_ventas(self) -> None:
        # TODO: conectar con flujo real de ventas
        self._ventas_ui.show()

    def _open_reportes(self) -> None:
        # TODO: conectar con flujo real de reportes
        self._reportes_ui.show()

    def _show_about(self) -> None:
        # TODO: reemplazar por ventana dedicada
        messagebox.showinfo(
            "Acerca de",
            "Sistema de Gestion de Cine - Base para Guerra de Testers",
        )
