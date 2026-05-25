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
        self._doc_entries: dict[str, tk.Entry] = {}
        self.result_text: tk.Text | None = None
        self.movie_combo: ttk.Combobox | None = None
        self.room_combo: ttk.Combobox | None = None
        self.movie_lookup: dict[str, dict[str, str]] = {}
        self.room_lookup: dict[str, dict[str, str]] = {}
        self.summary_var = tk.StringVar(master=self.parent, value="Selecciona una pelicula para cargar precio y restriccion.")
        self._selected_seats: list[str] = []
        self._seat_buttons: dict[str, tk.Button] = {}
        self.seats_var = tk.StringVar(master=self.parent, value="Selecciona asientos en la cuadricula.")

    @staticmethod
    def _format_currency(amount: float) -> str:
        return f"S/. {amount:.2f}"

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
            asientos_ocupados = self._value_as_text(item, ("asientos_ocupados", "occupied_seats"), "")
            asientos_por_pelicula = item.get("asientos_ocupados_por_pelicula", {}) if isinstance(item, dict) else {}
            if not isinstance(asientos_por_pelicula, dict):
                asientos_por_pelicula = {}
            ocupadas_actuales = self._value_as_text(item, ("ocupadas_actuales", "ocupadas", "ocupacion", "occupied"), "0")
            lookup[etiqueta] = {
                "sala_id": self._value_as_text(item, ("sala_id", "id"), etiqueta),
                "sala_numero": numero,
                "funcion_id": self._value_as_text(item, ("funcion_id", "function_id"), f"F-{numero}"),
                "capacidad_sala": self._value_as_text(item, ("capacidad", "capacity"), "0"),
                "ocupadas_actuales": ocupadas_actuales,
                "asientos_ocupados": asientos_ocupados,
                "asientos_ocupados_por_pelicula": {str(key): value for key, value in asientos_por_pelicula.items()},
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
                normalized_item: dict[str, str] = {}
                for key, value in item.items():
                    if isinstance(value, (dict, list, tuple, set)):
                        normalized_item[key] = value  # type: ignore[assignment]
                    else:
                        normalized_item[key] = str(value)
                normalized_items.append(normalized_item)
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
            "documento_tipo": tk.StringVar(value="dni"),
            "cliente_documento_dni": tk.StringVar(),
            "cliente_documento_carnet": tk.StringVar(),
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
            ("cliente_documento", "Cliente documento (DNI/Carnet)"),
            ("cliente_edad", "Cliente edad"),
            ("asientos", "Asientos"),
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
            elif key == "cliente_documento":
                sub = tk.Frame(form, bg="#f2f2f2")
                sub.grid(row=row, column=col + 1, sticky="w", padx=(0, 14), pady=4)
                v = self.fields["documento_tipo"]
                rb1 = tk.Radiobutton(sub, text="DNI", variable=v, value="dni", bg="#f2f2f2", command=self._on_document_type_changed)
                rb1.pack(side="left")
                entry_dni = tk.Entry(sub, textvariable=self.fields["cliente_documento_dni"], width=18)
                entry_dni.pack(side="left", padx=(6, 10))
                rb2 = tk.Radiobutton(sub, text="Carnet ext.", variable=v, value="carnet", bg="#f2f2f2", command=self._on_document_type_changed)
                rb2.pack(side="left")
                entry_carnet = tk.Entry(sub, textvariable=self.fields["cliente_documento_carnet"], width=18)
                entry_carnet.pack(side="left", padx=(6, 0))
                self._doc_entries = {"dni": entry_dni, "carnet": entry_carnet}
            elif key == "metodo_pago":
                combo = ttk.Combobox(form, textvariable=self.fields[key], values=("efectivo",), state="readonly", width=36)
                combo.grid(row=row, column=col + 1, sticky="ew", padx=(0, 14), pady=4)
            elif key in {"fecha", "hora"}:
                entry = tk.Entry(form, textvariable=self.fields[key], width=18, state="readonly")
                entry.grid(row=row, column=col + 1, sticky="w", padx=(0, 14), pady=4)
            elif key == "asientos":
                sub = tk.Frame(form, bg="#f2f2f2")
                sub.grid(row=row, column=col + 1, sticky="w", padx=(0, 14), pady=4)
                tk.Button(sub, text="Seleccionar asientos", command=self._open_seat_selector, bg="#d9d9d9", relief="flat", padx=10, pady=4).pack(side="left")
                tk.Label(sub, textvariable=self.seats_var, bg="#f2f2f2", fg="#444444", padx=8).pack(side="left")
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
            "cantidad_entradas": "0",
            "cliente_edad": "",
            "venta_id_buscar": "",
        }
        for key, value in defaults.items():
            self.fields[key].set(value)

        # default documento tipo
        if "documento_tipo" in self.fields:
            self.fields["documento_tipo"].set("dni")

        self._sync_datetime_fields()

        if self.movie_combo and self.movie_combo["values"]:
            self.movie_combo.current(0)
            self._on_movie_selected()
        if self.room_combo and self.room_combo["values"]:
            self.room_combo.current(0)
            self._on_room_selected()
        # ensure document entries reflect the tipo
        self._on_document_type_changed()
        self._set_selected_seats([])

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
        self.room_lookup = self._load_room_catalog()
        return self.room_lookup.get(selected, {})

    def _current_movie_id(self) -> str:
        movie = self._current_movie()
        return movie.get("pelicula_id", "")

    def _on_movie_selected(self, _event: object | None = None) -> None:
        movie = self._current_movie()
        if not movie:
            return
        self.fields["pelicula_id"].set(movie.get("pelicula_id", ""))
        self.fields["pelicula_titulo"].set(movie.get("titulo", ""))
        self.fields["precio_unitario"].set(movie.get("precio_unitario", "0.00"))
        self.fields["restriccion_edad"].set(movie.get("restriccion_edad", "0"))
        self.summary_var.set(
            f"Pelicula seleccionada: {movie.get('titulo', '')} | Precio: {self._format_currency(float(movie.get('precio_unitario', '0.00')))} | Restriccion: +{movie.get('restriccion_edad', '0')}"
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
        self._set_selected_seats([])

    def _seat_codes(self, capacity: int) -> list[str]:
        seats: list[str] = []
        for index in range(max(capacity, 0)):
            row = index // 10
            seat = index % 10 + 1
            seats.append(f"{chr(ord('A') + row)}{seat}")
        return seats

    def _occupied_seats_for_room(self) -> set[str]:
        room = self._current_room()
        if not room:
            return set()
        occupied: set[str] = set()
        movie_id = self._current_movie_id()
        per_movie = room.get("asientos_ocupados_por_pelicula", {})
        raw = per_movie.get(movie_id, []) if isinstance(per_movie, dict) and movie_id else []
        if isinstance(raw, str) and raw.strip():
            for item in raw.split(","):
                item = item.strip().upper()
                if item:
                    occupied.add(item)
        elif isinstance(raw, (list, tuple, set)):
            for item in raw:
                text = str(item).strip().upper()
                if text:
                    occupied.add(text)
        return occupied

    def _seat_sort_key(self, seat: str) -> tuple[int, int]:
        row = ord(seat[0]) - ord("A") if seat else 0
        try:
            number = int(seat[1:])
        except ValueError:
            number = 0
        return row, number

    def _set_selected_seats(self, seats: list[str]) -> None:
        self._selected_seats = sorted({seat.upper() for seat in seats}, key=self._seat_sort_key)
        self.fields["cantidad_entradas"].set(str(len(self._selected_seats)))
        if self._selected_seats:
            self.seats_var.set(f"Seleccionados: {', '.join(self._selected_seats)}")
        else:
            self.seats_var.set("Selecciona asientos en la cuadricula.")

    def _open_seat_selector(self) -> None:
        if self.window is None:
            return
        self.room_lookup = self._load_room_catalog()
        room = self._current_room()
        if not room:
            messagebox.showwarning("Sala requerida", "Selecciona una sala antes de marcar asientos.")
            return

        capacity = int(self.fields.get("capacidad_sala", tk.StringVar()).get() or 0)
        if capacity <= 0:
            messagebox.showwarning("Capacidad invalida", "La sala no tiene capacidad disponible.")
            return

        occupied = self._occupied_seats_for_room()
        selected = set(self._selected_seats)
        dialog = tk.Toplevel(self.window)
        dialog.title("Seleccion de asientos")
        dialog.geometry("760x520")
        dialog.configure(bg="#f2f2f2")
        dialog.transient(self.window)
        dialog.grab_set()

        info = tk.StringVar(value="Maximo 10 asientos. Verde: disponible, gris: ocupado, azul: seleccionado.")
        tk.Label(dialog, textvariable=info, bg="#f2f2f2", fg="#333333", anchor="w", justify="left").pack(fill="x", padx=12, pady=(12, 8))

        grid_frame = tk.Frame(dialog, bg="#f2f2f2")
        grid_frame.pack(expand=True, fill="both", padx=12, pady=8)

        buttons: dict[str, tk.Button] = {}

        def refresh() -> None:
            for seat, button in buttons.items():
                if seat in occupied:
                    button.configure(state="disabled", bg="#bdbdbd", relief="flat")
                elif seat in selected:
                    button.configure(state="normal", bg="#7cc4ff", relief="sunken")
                else:
                    button.configure(state="normal", bg="#dff5df", relief="raised")

        def toggle(seat: str) -> None:
            if seat in occupied:
                return
            if seat in selected:
                selected.remove(seat)
            else:
                if len(selected) >= 10:
                    messagebox.showwarning("Límite de selección", "No puedes seleccionar más de 10 asientos.", parent=dialog)
                    return
                selected.add(seat)
            refresh()

        for index, seat in enumerate(self._seat_codes(capacity)):
            row = index // 10
            column = index % 10
            button = tk.Button(grid_frame, text=seat, width=6, command=lambda s=seat: toggle(s))
            button.grid(row=row, column=column, padx=4, pady=4, sticky="nsew")
            buttons[seat] = button

        for column in range(10):
            grid_frame.grid_columnconfigure(column, weight=1)

        footer = tk.Frame(dialog, bg="#f2f2f2")
        footer.pack(fill="x", padx=12, pady=(0, 12))

        def confirm() -> None:
            self._set_selected_seats(list(selected))
            dialog.destroy()

        def clear() -> None:
            selected.clear()
            refresh()

        tk.Button(footer, text="Limpiar", command=clear, bg="#e8d6cf", relief="flat", padx=10, pady=5).pack(side="left")
        tk.Button(footer, text="Confirmar", command=confirm, bg="#cfe8cf", relief="flat", padx=10, pady=5).pack(side="right")
        refresh()

    def _collect_payload(self) -> dict[str, str]:
        payload = {key: var.get() for key, var in self.fields.items()}
        payload.pop("venta_id_buscar", None)
        fecha = payload.pop("fecha", "")
        hora = payload.pop("hora", "")
        payload["fecha_hora"] = f"{fecha}T{hora}"
        tipo = payload.get("documento_tipo", "dni")
        dni = payload.pop("cliente_documento_dni", "")
        carnet = payload.pop("cliente_documento_carnet", "")
        payload["tipo_documento"] = tipo
        payload["cliente_documento"] = dni if tipo == "dni" else carnet
        # seats
        payload["asientos_seleccionados"] = list(self._selected_seats)
        payload["asientos_ocupados"] = sorted(self._occupied_seats_for_room())
        payload["cantidad_entradas"] = str(len(self._selected_seats)) if self._selected_seats else payload.get("cantidad_entradas", "0")
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
                cliente_edad=payload.get("cliente_edad", "0"),
            )
            self._render_result(
                "Resumen de total",
                f"Subtotal: {self._format_currency(result['subtotal'])}\n"
                f"Descuentos: {self._format_currency(result['descuentos'])}\n"
                f"Recargos: {self._format_currency(result['recargos'])}\n"
                f"Impuestos: {self._format_currency(result['impuestos'])}\n"
                f"Total: {self._format_currency(result['total'])}",
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
                self.room_lookup = self._load_room_catalog()
                self._set_selected_seats([])
                if self.room_combo and self.room_combo["values"]:
                    self._on_room_selected()
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
                var.set("0")
            elif key in {"cliente_edad"}:
                var.set("")
            elif key == "documento_tipo":
                var.set("dni")
            elif key == "cliente_documento_dni":
                var.set("")
            elif key == "cliente_documento_carnet":
                var.set("")
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
        self._on_document_type_changed()
        self._render_result("Formulario limpio", "Los campos han sido reiniciados.")

    def _on_document_type_changed(self) -> None:
        # Enable the selected entry and disable the other
        tipo = self.fields.get("documento_tipo", tk.StringVar()).get()
        if not self._doc_entries:
            return
        for key, entry in self._doc_entries.items():
            if key == tipo:
                entry.configure(state="normal")
            else:
                entry.configure(state="disabled")
