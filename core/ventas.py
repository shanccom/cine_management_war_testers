"""
Modelo base de ventas.
"""

from __future__ import annotations

from typing import Any


class Venta:
    def __init__(
        self,
        venta_id: str = "",
        pelicula_id: str = "",
        pelicula_titulo: str = "",
        sala_id: str = "",
        sala_numero: int = 0,
        funcion_id: str = "",
        fecha_hora: str = "",
        cliente_nombre: str = "",
        cliente_documento: str = "",
        cliente_edad: int = 0,
        cantidad: int = 0,
        precio_unitario: float = 0.0,
        subtotal: float = 0.0,
        descuentos: float = 0.0,
        recargos: float = 0.0,
        impuestos: float = 0.0,
        total: float = 0.0,
        metodo_pago: str = "",
        restriccion_edad: int = 0,
        estado: str = "registrada",
        ticket_texto: str = "",
        timestamp: str = "",
        schema_version: int = 1,
        **extra: Any,
    ) -> None:
        self.venta_id = venta_id
        self.pelicula_id = pelicula_id
        self.pelicula_titulo = pelicula_titulo
        self.sala_id = sala_id
        self.sala_numero = sala_numero
        self.funcion_id = funcion_id
        self.fecha_hora = fecha_hora
        self.cliente_nombre = cliente_nombre
        self.cliente_documento = cliente_documento
        self.cliente_edad = cliente_edad
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = subtotal
        self.descuentos = descuentos
        self.recargos = recargos
        self.impuestos = impuestos
        self.total = total
        self.metodo_pago = metodo_pago
        self.restriccion_edad = restriccion_edad
        self.estado = estado
        self.ticket_texto = ticket_texto
        self.timestamp = timestamp
        self.schema_version = schema_version
        self.extra = extra

    def to_dict(self) -> dict[str, Any]:
        data = {
            "venta_id": self.venta_id,
            "pelicula_id": self.pelicula_id,
            "pelicula_titulo": self.pelicula_titulo,
            "sala_id": self.sala_id,
            "sala_numero": self.sala_numero,
            "funcion_id": self.funcion_id,
            "fecha_hora": self.fecha_hora,
            "cliente": {
                "nombre": self.cliente_nombre,
                "documento": self.cliente_documento,
                "edad": self.cliente_edad,
            },
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
            "descuentos": self.descuentos,
            "recargos": self.recargos,
            "impuestos": self.impuestos,
            "total": self.total,
            "metodo_pago": self.metodo_pago,
            "restriccion_edad": self.restriccion_edad,
            "estado": self.estado,
            "ticket_texto": self.ticket_texto,
            "timestamp": self.timestamp,
            "_schema_version": self.schema_version,
        }
        data.update(self.extra)
        return data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Venta":
        cliente = data.get("cliente", {}) if isinstance(data, dict) else {}
        return Venta(
            venta_id=data.get("venta_id", ""),
            pelicula_id=data.get("pelicula_id", ""),
            pelicula_titulo=data.get("pelicula_titulo", data.get("titulo", "")),
            sala_id=data.get("sala_id", ""),
            sala_numero=data.get("sala_numero", data.get("numero_sala", 0)),
            funcion_id=data.get("funcion_id", ""),
            fecha_hora=data.get("fecha_hora", ""),
            cliente_nombre=cliente.get("nombre", data.get("cliente_nombre", "")),
            cliente_documento=cliente.get("documento", data.get("cliente_documento", "")),
            cliente_edad=cliente.get("edad", data.get("cliente_edad", 0)),
            cantidad=data.get("cantidad", 0),
            precio_unitario=data.get("precio_unitario", 0.0),
            subtotal=data.get("subtotal", 0.0),
            descuentos=data.get("descuentos", 0.0),
            recargos=data.get("recargos", 0.0),
            impuestos=data.get("impuestos", 0.0),
            total=data.get("total", 0.0),
            metodo_pago=data.get("metodo_pago", ""),
            restriccion_edad=data.get("restriccion_edad", 0),
            estado=data.get("estado", "registrada"),
            ticket_texto=data.get("ticket_texto", ""),
            timestamp=data.get("timestamp", ""),
            schema_version=data.get("_schema_version", 1),
        )
