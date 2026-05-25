"""
Interfaz del modulo de salas y control de asientos.
"""

import json
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from core.salas import Sala

class SalasUI:
    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent
        self.window: tk.Toplevel | None = None
        self.json_path = os.path.join("data", "salas.json")

    def show(self) -> None:
        if self.window is None or not self.window.winfo_exists():
            self.window = tk.Toplevel(self.parent)
            self.window.title("Gestion de Salas")
            self.window.geometry("650x550")
            self.window.configure(bg="#f2f2f2")

            label = tk.Label(
                self.window,
                text="Modulo de Salas y Asientos",
                bg="#f2f2f2",
                fg="#333333",
                font=("Arial", 14, "bold"),
            )
            label.pack(pady=10)

            # --- FORMULARIO DE REGISTRO DE SALA ---
            frame_sala = tk.LabelFrame(self.window, text="Registrar Nueva Sala", bg="#f2f2f2", font=("Arial", 10, "bold"))
            frame_sala.pack(pady=10, fill="x", padx=15)

            tk.Label(frame_sala, text="Numero de Sala:", bg="#f2f2f2").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.entry_numero = tk.Entry(frame_sala, width=15)
            self.entry_numero.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(frame_sala, text="Capacidad (1-300):", bg="#f2f2f2").grid(row=0, column=2, padx=5, pady=5, sticky="e")
            self.entry_capacidad = tk.Entry(frame_sala, width=15)
            self.entry_capacidad.grid(row=0, column=3, padx=5, pady=5)

            btn_guardar = tk.Button(
                frame_sala,
                text="Guardar Sala",
                command=self.guardar_sala,
                bg="#4CAF50",
                fg="white",
                font=("Arial", 9, "bold"),
            )
            btn_guardar.grid(row=0, column=4, padx=10, pady=5)

            # --- TABLA DE VISUALIZACION (TREEVIEW) ---
            frame_tabla = tk.LabelFrame(self.window, text="Salas Registradas y Disponibilidad", bg="#f2f2f2", font=("Arial", 10, "bold"))
            frame_tabla.pack(pady=10, fill="both", expand=True, padx=15)

            # Columnas de la tabla
            columnas = ("id", "numero", "capacidad", "libres", "ocupados")
            self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)
            
            self.tabla.heading("id", text="ID Sala")
            self.tabla.heading("numero", text="Numero")
            self.tabla.heading("capacidad", text="Capacidad")
            self.tabla.heading("libres", text="Asientos Libres")
            self.tabla.heading("ocupados", text="Total Ocupados")

            self.tabla.column("id", width=80, anchor="center")
            self.tabla.column("numero", width=80, anchor="center")
            self.tabla.column("capacidad", width=100, anchor="center")
            self.tabla.column("libres", width=110, anchor="center")
            self.tabla.column("ocupados", width=110, anchor="center")

            self.tabla.pack(pady=5, fill="both", expand=True, padx=5)

            # --- FORMULARIO DE RESERVA DE ASIENTOS ---
            frame_reserva = tk.LabelFrame(self.window, text="Reservar Asiento en Sala Seleccionada", bg="#f2f2f2", font=("Arial", 10, "bold"))
            frame_reserva.pack(pady=10, fill="x", padx=15)

            tk.Label(frame_reserva, text="Codigo de Asiento (ej: A1):", bg="#f2f2f2").grid(row=0, column=0, padx=5, pady=10, sticky="e")
            self.entry_asiento = tk.Entry(frame_reserva, width=20)
            self.entry_asiento.grid(row=0, column=1, padx=5, pady=10)

            btn_reservar = tk.Button(
                frame_reserva,
                text="Reservar Asiento",
                command=self.reservar_asiento_ui,
                bg="#008CBA",
                fg="white",
                font=("Arial", 9, "bold"),
            )
            btn_reservar.grid(row=0, column=2, padx=15, pady=10)

            # Cargar los datos iniciales en la tabla
            self.actualizar_tabla()
        else:
            self.window.focus()

    def actualizar_tabla(self) -> None:
            """Limpia la tabla y vuelve a cargar los datos desde el archivo JSON con tolerancia a fallos."""
            # Limpiar registros existentes en la UI
            for row in self.tabla.get_children():
                self.tabla.delete(row)

            try:
                if os.path.exists(self.json_path):
                    with open(self.json_path, "r", encoding="utf-8") as file:
                        data = json.load(file)
                else:
                    data = {"items": []}

                for item in data.get("items", []):
                    try:
                        # Si el JSON fue alterado externamente con datos absurdos,
                        # el constructor del Core lanzara TypeError o ValueError aqui.
                        sala = Sala.from_dict(item)
                        asientos_libres = sala.capacidad - len(sala.asientos_ocupados)
                        
                        self.tabla.insert(
                            "",
                            tk.END,
                            values=(
                                sala.sala_id,
                                sala.numero,
                                sala.capacidad,
                                asientos_libres,
                                len(sala.asientos_ocupados)
                            )
                        )
                    except (ValueError, TypeError) as e:
                        # Capturamos el intento de corrupcion: la app no se cae.
                        # Imprime una alerta en consola para el desarrollador y continua con la siguiente sala.
                        print(f"[ALERTA DEFENSIVA] Registro de sala corrupto omitido en JSON: {e}")
                        continue

            except (OSError, json.JSONDecodeError) as e:
                messagebox.showerror("Error de Sistema", f"No se pudo leer la estructura del archivo de datos: {e}")

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
            
            # Refrescar la tabla despues de agregar una sala
            self.actualizar_tabla()
            
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

    def reservar_asiento_ui(self) -> None:
        """Lee el asiento ingresado y lo reserva en la sala seleccionada de la tabla."""
        selected_item = self.tabla.selection()
        if not selected_item:
            messagebox.showerror("Seleccion Requerida", "Por favor, seleccione una sala de la tabla primero.")
            return

        # Obtener los valores de la fila seleccionada
        valores_fila = self.tabla.item(selected_item[0], "values")
        sala_id_seleccionada = valores_fila[0]
        asiento_cod = self.entry_asiento.get()

        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                messagebox.showerror("Error", "No se encontraron datos de salas.")
                return

            sala_encontrada = False
            items_actualizados = []

            for item in data.get("items", []):
                if item.get("sala_id") == sala_id_seleccionada:
                    sala_encontrada = True
                    # Reconstruir la sala usando el core
                    sala = Sala.from_dict(item)
                    
                    # Intentar reservar (aqui saltaran TypeError o ValueError si el dato es incorrecto)
                    sala.reservar_asiento(asiento_cod)
                    
                    # Guardar el diccionario actualizado
                    items_actualizados.append(sala.to_dict())
                else:
                    items_actualizados.append(item)

            if not sala_encontrada:
                messagebox.showerror("Error", "La sala seleccionada no existe en el archivo de datos.")
                return

            # Escribir los cambios actualizados en el JSON
            data["items"] = items_actualizados
            with open(self.json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            messagebox.showinfo("Exito", f"Asiento registrado correctamente en la sala {sala_id_seleccionada}.")
            self.entry_asiento.delete(0, tk.END)
            
            # Refrescar la tabla con la nueva disponibilidad
            self.actualizar_tabla()

        except (ValueError, TypeError) as e:
            # Captura errores como: codigo vacio, duplicado o sala llena
            messagebox.showerror("Error de Validacion", str(e))
        except (OSError, json.JSONDecodeError) as e:
            messagebox.showerror("Error de Sistema", f"No se pudo actualizar el asiento: {e}")