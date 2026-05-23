"""
Interfaz del modulo de salas.
"""

import json
import os
import tkinter as tk
from tkinter import messagebox

from core.salas import Sala

class SalasUI:
    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent
        self.window: tk.Toplevel | None = None
        self.json_path = os.path.join("data", "salas.json")

    def show(self) -> None:
        if self.window is None or not self.window.winfo_exists():
            self.window = tk.Toplevel(self.parent)
            self.window.title("Salas")
            self.window.geometry("400x350")
            self.window.configure(bg="#f2f2f2")

            label = tk.Label(
                self.window,
                text="Modulo de Salas",
                bg="#f2f2f2",
                fg="#333333",
                font=("Arial", 12, "bold"),
            )
            label.pack(pady=10)

            frame_form = tk.Frame(self.window, bg="#f2f2f2")
            frame_form.pack(pady=10)

            tk.Label(frame_form, text="Numero de Sala:", bg="#f2f2f2").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.entry_numero = tk.Entry(frame_form, width=20)
            self.entry_numero.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(frame_form, text="Capacidad:", bg="#f2f2f2").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            self.entry_capacidad = tk.Entry(frame_form, width=20)
            self.entry_capacidad.grid(row=1, column=1, padx=5, pady=5)

            btn_guardar = tk.Button(
                self.window,
                text="Guardar Sala",
                command=self.guardar_sala,
                bg="#4CAF50",
                fg="white",
                font=("Arial", 10, "bold"),
            )
            btn_guardar.pack(pady=15)
        else:
            self.window.focus()

    def guardar_sala(self) -> None:
        """Lee datos de formulario, valida y guarda en JSON."""
        numero_str = self.entry_numero.get()
        capacidad_str = self.entry_capacidad.get()

        try:
            numero = int(numero_str)
            capacidad = int(capacidad_str)
        except ValueError:
            messagebox.showerror(
                "Error de Formato",
                "El numero y la capacidad deben ser numeros enteros validos.",
            )
            return

        try:
            sala_id = f"S{numero}"
            nueva_sala = Sala(sala_id=sala_id, numero=numero, capacidad=capacidad)
        except (ValueError, TypeError) as e:
            messagebox.showerror("Error de Validacion", str(e))
            return

        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                data = {"items": []}

            for item in data.get("items", []):
                if item.get("numero") == nueva_sala.numero:
                    messagebox.showerror(
                        "Error",
                        f"La sala {nueva_sala.numero} ya existe en el sistema.",
                    )
                    return

            data["items"].append(nueva_sala.to_dict())

            with open(self.json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            messagebox.showinfo("Exito", f"Sala {numero} registrada correctamente.")
            self.entry_numero.delete(0, tk.END)
            self.entry_capacidad.delete(0, tk.END)
        except (OSError, json.JSONDecodeError) as e:
            messagebox.showerror(
                "Error de Sistema",
                f"No se pudo acceder al archivo de datos: {e}",
            )
        except Exception as e:
            messagebox.showerror(
                "Error de Sistema",
                f"No se pudo guardar la informacion: {e}",
            )