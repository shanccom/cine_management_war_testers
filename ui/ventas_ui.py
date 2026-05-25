"""
Interfaz del modulo de ventas.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from config.constants import PELICULAS_DATA_FILE, SALAS_DATA_FILE
from core.helpers import load_json_file
from services.ventas_service import VentasService


class VentasUI:
    def __init__(self, parent: tk.Tk, service: VentasService | None = None) -> None:
        self.parent = parent
        self.service = service or VentasService()
        self.window: tk.Toplevel | None = None
        self._clock_job: str | None = None
        self.fields: dict[str, tk.StringVar] = {}
        self.result_text: tk.Text | None = None
        self.movie_combo: ttk.Combobox | None = None
        self.room_combo: ttk.Combobox | None = None
        self.movie_lookup: dict[str, dict[str, str]] = {}
        self.room_lookup: dict[str, dict[str, str]] = {}
        self.summary_var = tk.StringVar(master=self.parent, value="Selecciona una pelicula para cargar precio y restriccion.")

    def show(self) -> None:
        if self.window is not None and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Venta de Entradas")
        self.window.geometry("980x760")
        self.window.configure(bg="#f2f2f2")
        self.window.protocol("WM_DELETE_WINDOW", self._hide_window)

        self._build_catalogs()
        self._build_form()
        self._set_default_values()
        self._start_clock()

    def _hide_window(self) -> None:
        if self.window is not None:
            self.window.withdraw()

    def _build_catalogs(self) -> None:
        self.movie_lookup = self._load_movie_catalog()
        self.room_lookup = self._load_room_catalog()

    def _load_movie_catalog(self) -> dict[str, dict[str, str]]:
        catalog = self._load_items(PELICULAS_DATA_FILE)
        if not catalog:
            catalog = [
                {"pelicula_id": "P001", "titulo": "Oppenheimer", "precio_unitario": "32.00", "restriccion_edad": "15"},
                {"pelicula_id": "P002", "titulo": "Intensamente 2", "precio_unitario": "24.00", "restriccion_edad": "0"},
                {"pelicula_id": "P003", "titulo": "Deadpool y Wolverine", "precio_unitario": "35.00", "restriccion_edad": "18"},
                {"pelicula_id": "P004", "titulo": "Garfield: Fuera de Casa", "precio_unitario": "22.00", "restriccion_edad": "0"},
            ]

        lookup: dict[str, dict[str, str]] = {}
        for item in catalog:
            titulo = self._value_as_text(item, ("titulo", "nombre", "pelicula", "label"), "Pelicula")
            lookup[titulo] = {
                "pelicula_id": self._value_as_text(item, ("pelicula_id", "id"), titulo),
                "titulo": titulo,
                "precio_unitario": self._value_as_text(item, ("precio_unitario", "precio", "tarifa"), "25.00"),
                "restriccion_edad": self._value_as_text(item, ("restriccion_edad", "edad"), "0"),
            }
        return lookup

    def _load_room_catalog(self) -> dict[str, dict[str, str]]:
        catalog = self._load_items(SALAS_DATA_FILE)
        if not catalog:
            catalog = [
                {"sala_id": "S1", "numero": "1", "capacidad": "120"},
                {"sala_id": "S2", "numero": "2", "capacidad": "90"},
                {"sala_id": "S3", "numero": "3", "capacidad": "80"},
            ]

        lookup: dict[str, dict[str, str]] = {}
        for item in catalog:
            numero = self._value_as_text(item, ("numero", "sala_numero", "room_number"), "1")
            etiqueta = f"Sala {numero}"
            lookup[etiqueta] = {
                "sala_id": self._value_as_text(item, ("sala_id", "id"), etiqueta),
                "sala_numero": numero,
                "funcion_id": self._value_as_text(item, ("funcion_id", "function_id"), f"F-{numero}"),
                "capacidad_sala": self._value_as_text(item, ("capacidad", "capacity"), "0"),
                "ocupadas_actuales": self._value_as_text(item, ("ocupadas", "ocupacion", "occupied"), "0"),
            }
        return lookup

    def _load_items(self, path: Path) -> list[dict[str, str]]:
        try:
            data = load_json_file(str(path))
        except Exception:
            return []
        if not isinstance(data, dict):
            return []
        items = data.get("items", [])
        if not isinstance(items, list):
            return []
        normalized_items: list[dict[str, str]] = []
        for item in items:
            if isinstance(item, dict):
                normalized_items.append({key: str(value) for key, value in item.items()})
        return normalized_items

    def _value_as_text(self, item: dict[str, str], keys: tuple[str, ...], fallback: str) -> str:
        for key in keys:
            if key in item and str(item[key]).strip():
                return str(item[key]).strip()
        return fallback

    def _build_form(self) -> None:
        if self.window is None:
            return

        container = tk.Frame(self.window, bg="#f2f2f2", padx=16, pady=16)
        container.pack(expand=True, fill="both")

        title = tk.Label(
            container,
            text="Modulo de Venta de Entradas",
            bg="#f2f2f2",
            fg="#222222",
            font=("Arial", 16, "bold"),
        )
        title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 14))

        form = tk.Frame(container, bg="#f2f2f2")
        form.grid(row=1, column=0, columnspan=4, sticky="nsew")

        self.fields = {
            "pelicula_id": tk.StringVar(),
            "pelicula_titulo": tk.StringVar(),
            "sala_id": tk.StringVar(),
            "sala_numero": tk.StringVar(),
            "precio_unitario": tk.StringVar(),
            "restriccion_edad": tk.StringVar(),
            "capacidad_sala": tk.StringVar(),
            "ocupadas_actuales": tk.StringVar(),
            "funcion_id": tk.StringVar(),
            "fecha": tk.StringVar(),
            "hora": tk.StringVar(),
            "cliente_nombre": tk.StringVar(),
            "cliente_documento": tk.StringVar(),
            "cliente_edad": tk.StringVar(),
            "cantidad_entradas": tk.StringVar(),
            "metodo_pago": tk.StringVar(),
            "venta_id_buscar": tk.StringVar(),
            "tipo_cliente": tk.StringVar(value="general"),
        }

        visible_labels = [
            ("pelicula_combo", "Pelicula"),
            ("sala_combo", "Sala"),
            ("fecha", "Fecha"),
            ("hora", "Hora"),
            ("cliente_nombre", "Cliente nombre"),
            ("cliente_documento", "Cliente documento"),
            ("cliente_edad", "Cliente edad"),
            ("cantidad_entradas", "Cantidad entradas"),
            ("metodo_pago", "Metodo pago"),
        ]

        for index, (key, label_text) in enumerate(visible_labels):
            row = index // 2
            col = (index % 2) * 2
            label = tk.Label(form, text=label_text, bg="#f2f2f2", fg="#333333", anchor="w")
            label.grid(row=row, column=col, sticky="w", padx=(0, 8), pady=4)

            if key == "pelicula_combo":
                self.movie_combo = ttk.Combobox(form, values=tuple(self.movie_lookup.keys()), state="readonly", width=36)
                self.movie_combo.grid(row=row, column=col + 1, sticky="ew", padx=(0, 14), pady=4)
                self.movie_combo.bind("<<ComboboxSelected>>", self._on_movie_selected)
            elif key == "sala_combo":
                self.room_combo = ttk.Combobox(form, values=tuple(self.room_lookup.keys()), state="readonly", width=36)
                self.room_combo.grid(row=row, column=col + 1, sticky="ew", padx=(0, 14), pady=4)
                self.room_combo.bind("<<ComboboxSelected>>", self._on_room_selected)
            elif key == "metodo_pago":
                combo = ttk.Combobox(form, textvariable=self.fields[key], values=("efectivo",), state="readonly", width=36)
                combo.grid(row=row, column=col + 1, sticky="ew", padx=(0, 14), pady=4)
            elif key in {"fecha", "hora"}:
                entry = tk.Entry(form, textvariable=self.fields[key], width=18, state="readonly")
                entry.grid(row=row, column=col + 1, sticky="w", padx=(0, 14), pady=4)
            else:
                entry = tk.Entry(form, textvariable=self.fields[key], width=40)
                entry.grid(row=row, column=col + 1, sticky="ew", padx=(0, 14), pady=4)

        summary = tk.Label(
            container,
            textvariable=self.summary_var,
            bg="#f2f2f2",
            fg="#5b5b5b",
            anchor="w",
            justify="left",
        )
        summary.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 6))

        ticket_frame = tk.LabelFrame(container, text="Ticket", bg="#f2f2f2", fg="#333333", padx=10, pady=8)
        ticket_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(8, 10))

        tk.Label(ticket_frame, text="Venta ID", bg="#f2f2f2", fg="#333333").grid(row=0, column=0, sticky="w", padx=(0, 8))
        tk.Entry(ticket_frame, textvariable=self.fields["venta_id_buscar"], width=42).grid(row=0, column=1, sticky="w", padx=(0, 8))
        tk.Button(ticket_frame, text="Mostrar ticket", command=self._on_mostrar_ticket, bg="#d9d9d9", relief="flat", padx=12, pady=6).grid(row=0, column=2, sticky="w")

        button_frame = tk.Frame(container, bg="#f2f2f2")
        button_frame.grid(row=4, column=0, columnspan=4, sticky="w", pady=(8, 10))

        tk.Button(button_frame, text="Calcular total", command=self._on_calcular_total, bg="#d9d9d9", relief="flat", padx=12, pady=6).pack(side="left", padx=(0, 8))
        tk.Button(button_frame, text="Comprar entrada", command=self._on_comprar, bg="#cfe8cf", relief="flat", padx=12, pady=6).pack(side="left", padx=(0, 8))
        tk.Button(button_frame, text="Limpiar", command=self._clear_form, bg="#e8d6cf", relief="flat", padx=12, pady=6).pack(side="left")

        self.result_text = tk.Text(container, height=18, width=100, wrap="word")
        self.result_text.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=(10, 0))
        self.result_text.configure(state="disabled")

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_columnconfigure(2, weight=1)
        container.grid_columnconfigure(3, weight=1)
        container.grid_rowconfigure(5, weight=1)

    def _set_default_values(self) -> None:
        defaults = {
            "metodo_pago": "efectivo",
            "tipo_cliente": "general",
            "cantidad_entradas": "1",
            "cliente_edad": "18",
            "venta_id_buscar": "",
        }
        for key, value in defaults.items():
            self.fields[key].set(value)

        self._sync_datetime_fields()

        if self.movie_combo and self.movie_combo["values"]:
            self.movie_combo.current(0)
            self._on_movie_selected()
        if self.room_combo and self.room_combo["values"]:
            self.room_combo.current(0)
            self._on_room_selected()

    def _sync_datetime_fields(self) -> None:
        current = datetime.now().replace(microsecond=0)
        self.fields["fecha"].set(current.strftime("%Y-%m-%d"))
        self.fields["hora"].set(current.strftime("%H:%M:%S"))

    def _start_clock(self) -> None:
        self._sync_datetime_fields()
        if self.window is None or not self.window.winfo_exists():
            return
        self._clock_job = self.window.after(1000, self._start_clock)

    def _current_movie(self) -> dict[str, str]:
        selected = self.movie_combo.get() if self.movie_combo else ""
        return self.movie_lookup.get(selected, {})

    def _current_room(self) -> dict[str, str]:
        selected = self.room_combo.get() if self.room_combo else ""
        return self.room_lookup.get(selected, {})

    def _on_movie_selected(self, _event: object | None = None) -> None:
        movie = self._current_movie()
        if not movie:
            return
        self.fields["pelicula_id"].set(movie.get("pelicula_id", ""))
        self.fields["pelicula_titulo"].set(movie.get("titulo", ""))
        self.fields["precio_unitario"].set(movie.get("precio_unitario", "0.00"))
        self.fields["restriccion_edad"].set(movie.get("restriccion_edad", "0"))
        self.summary_var.set(
            f"Pelicula seleccionada: {movie.get('titulo', '')} | Precio: ${movie.get('precio_unitario', '0.00')} | Restriccion: +{movie.get('restriccion_edad', '0')}"
        )

    def _on_room_selected(self, _event: object | None = None) -> None:
        room = self._current_room()
        if not room:
            return
        self.fields["sala_id"].set(room.get("sala_id", ""))
        self.fields["sala_numero"].set(room.get("sala_numero", "0"))
        self.fields["funcion_id"].set(room.get("funcion_id", f"F-{room.get('sala_numero', '0')}"))
        self.fields["capacidad_sala"].set(room.get("capacidad_sala", "0"))
        self.fields["ocupadas_actuales"].set(room.get("ocupadas_actuales", "0"))

    def _collect_payload(self) -> dict[str, str]:
        payload = {key: var.get() for key, var in self.fields.items()}
        payload.pop("venta_id_buscar", None)
        fecha = payload.pop("fecha", "")
        hora = payload.pop("hora", "")
        payload["fecha_hora"] = f"{fecha}T{hora}"
        return payload

    def _render_result(self, title: str, message: str) -> None:
        if self.result_text is None:
            return
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"{title}\n\n{message}")
        self.result_text.configure(state="disabled")

    def _on_calcular_total(self) -> None:
        try:
            payload = self._collect_payload()
            result = self.service.calcular_total(
                precio_unitario=payload.get("precio_unitario", "0"),
                cantidad_entradas=payload.get("cantidad_entradas", "0"),
                tipo_cliente=payload.get("tipo_cliente", "general"),
            )
            self._render_result(
                "Resumen de total",
                f"Subtotal: {result['subtotal']:.2f}\n"
                f"Descuentos: {result['descuentos']:.2f}\n"
                f"Recargos: {result['recargos']:.2f}\n"
                f"Impuestos: {result['impuestos']:.2f}\n"
                f"Total: {result['total']:.2f}",
            )
        except Exception as exc:  # pragma: no cover - defensivo de UI
            messagebox.showerror("Error", str(exc))

    def _on_comprar(self) -> None:
        try:
            payload = self._collect_payload()
            result = self.service.comprar_entrada(payload)
            if result.get("status") == "ok":
                self.fields["venta_id_buscar"].set(result.get("venta_id", ""))
                self._render_result("Venta exitosa", result.get("ticket_texto", ""))
                messagebox.showinfo("Venta registrada", f"Venta creada correctamente.\nVenta ID: {result.get('venta_id', '')}")
            else:
                codigo = result.get("codigo_error", "ERR_GENERAL")
                mensaje = result.get("mensaje", "Error inesperado")
                self._render_result("Error en venta", f"{codigo}: {mensaje}")
                messagebox.showwarning("Venta no completada", f"{codigo}: {mensaje}")
        except Exception as exc:  # pragma: no cover - defensivo de UI
            messagebox.showerror("Error", str(exc))

    def _on_mostrar_ticket(self) -> None:
        venta_id = self.fields.get("venta_id_buscar", tk.StringVar()).get()
        result = self.service.mostrar_ticket(venta_id)
        if result.get("status") == "ok":
            self._render_result("Ticket", result.get("ticket_texto", ""))
        else:
            codigo = result.get("codigo_error", "ERR_GENERAL")
            mensaje = result.get("mensaje", "Error inesperado")
            self._render_result("Ticket no encontrado", f"{codigo}: {mensaje}")
            messagebox.showwarning("Ticket no encontrado", f"{codigo}: {mensaje}")

    def _clear_form(self) -> None:
        for key, var in self.fields.items():
            if key == "metodo_pago":
                var.set("efectivo")
            elif key == "tipo_cliente":
                var.set("general")
            elif key in {"fecha", "hora"}:
                self._sync_datetime_fields()
            elif key in {"cantidad_entradas"}:
                var.set("1")
            elif key in {"cliente_edad"}:
                var.set("18")
            elif key in {"precio_unitario", "restriccion_edad", "capacidad_sala", "ocupadas_actuales", "sala_numero"}:
                var.set("0")
            else:
                var.set("")

        if self.movie_combo and self.movie_combo["values"]:
            self.movie_combo.current(0)
            self._on_movie_selected()
        if self.room_combo and self.room_combo["values"]:
            self.room_combo.current(0)
            self._on_room_selected()
        self._render_result("Formulario limpio", "Los campos han sido reiniciados.")
