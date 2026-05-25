"""Menu principal del sistema en consola."""

from __future__ import annotations

import tkinter as tk
import time

from services.ventas_service import VentasService
from ui.peliculas_ui import PeliculasUI
from ui.reportes_ui import ReportesUI
from ui.salas_ui import SalasUI
from ui.ventas_ui import VentasUI


class MainWindow:
    def __init__(self) -> None:
        self._peliculas_ui = PeliculasUI()
        self._reportes_ui = ReportesUI()
        self._tk_root: tk.Tk | None = None
        self._ventas_service = VentasService()

    def show(self) -> None:
        while True:
            print("\n=== Sistema de Gestion de Cine ===")
            print("1. Peliculas")
            print("2. Salas y asientos")
            print("3. Venta de entradas")
            print("4. Reportes")
            print("0. Salir")

            opcion = input("Seleccione una opcion: ").strip()
            if opcion == "1":
                self._peliculas_ui.show()
            elif opcion == "2":
                self._abrir_salas()
            elif opcion == "3":
                self._abrir_ventas()
            elif opcion == "4":
                self._reportes_ui.show()
            elif opcion == "0":
                self._cerrar_tk()
                print("Saliendo del sistema.")
                break
            else:
                print("Opcion no valida.")

    def _obtener_root_tk(self) -> tk.Tk:
        if self._tk_root is None:
            self._tk_root = tk.Tk()
            self._tk_root.withdraw()
        return self._tk_root

    def _esperar_ventana(self, window: tk.Toplevel | None) -> None:
        if window is None:
            return
        try:
            while window.winfo_exists():
                self._obtener_root_tk().update()
                time.sleep(0.02)
        except tk.TclError:
            pass

    def _abrir_salas(self) -> None:
        try:
            ui = SalasUI(self._obtener_root_tk())
            ui.show()
            if ui.window is not None:
                ui.window.protocol("WM_DELETE_WINDOW", ui.window.destroy)
            self._esperar_ventana(ui.window)
        except tk.TclError as exc:
            print(f"No se pudo abrir el modulo grafico de salas: {exc}")

    def _abrir_ventas(self) -> None:
        try:
            ui = VentasUI(self._obtener_root_tk(), service=self._ventas_service)
            ui.show()
            if ui.window is not None:
                ui.window.protocol("WM_DELETE_WINDOW", ui.window.destroy)
            self._esperar_ventana(ui.window)
        except tk.TclError as exc:
            print(f"No se pudo abrir el modulo grafico de ventas: {exc}")

    def _cerrar_tk(self) -> None:
        if self._tk_root is None:
            return
        try:
            self._tk_root.destroy()
        except tk.TclError:
            pass
        self._tk_root = None
