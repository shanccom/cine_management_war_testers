"""
Servicios de negocio para el modulo de ventas.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from config.constants import DESCUENTOS_TIPO_CLIENTE, MAX_POR_COMPRA, MIN_POR_COMPRA, VENTAS_DATA_FILE
from core.helpers import log_error
from core.ventas import Venta
from storage.json_store import VentasStore
from validators.ventas_validators import validar_decimal, validar_entero, validar_payload_venta, validar_texto_no_vacio


PaymentProcessor = Callable[[dict[str, Any]], bool | dict[str, Any]]


def _procesar_pago_defecto(_: dict[str, Any]) -> bool:
    return True


def _normalizar_respuesta_pago(result: bool | dict[str, Any]) -> bool:
    if isinstance(result, bool):
        return result
    if isinstance(result, dict):
        return bool(result.get("approved", result.get("ok", False)))
    return False


def _formatear_ticket(venta: Venta) -> str:
    lines = [
        "TICKET DE VENTA",
        f"Venta ID: {venta.venta_id}",
        f"Pelicula: {venta.pelicula_titulo} ({venta.pelicula_id})",
        f"Sala: {venta.sala_id}",
        f"Funcion: {venta.funcion_id}",
        f"Fecha y hora: {venta.fecha_hora}",
        f"Cliente: {venta.cliente_nombre} - {venta.cliente_documento}",
        f"Cantidad: {venta.cantidad}",
        f"Metodo de pago: {venta.metodo_pago}",
        f"Total: S/. {venta.total:.2f}",
        f"Estado: {venta.estado}",
    ]
    return "\n".join(lines)


class VentasService:
    def __init__(self, ventas_path: str | Path = VENTAS_DATA_FILE) -> None:
        self.store = VentasStore(ventas_path)

    def calcular_total(
        self,
        precio_unitario: float,
        cantidad_entradas: int,
        tipo_cliente: str = "general",
        promociones: list[str] | None = None,
        cliente_edad: int | None = None,
    ) -> dict[str, float]:
        cantidad_normalizada = validar_entero(
            cantidad_entradas,
            "cantidad_entradas",
            minimo=MIN_POR_COMPRA,
            maximo=MAX_POR_COMPRA,
        )
        precio_normalizado = validar_decimal(precio_unitario, "precio_unitario", minimo=0.0)

        tipo_cliente_normalizado = validar_texto_no_vacio(tipo_cliente, "tipo_cliente").lower()
        promociones = promociones or []

        subtotal = round(precio_normalizado * cantidad_normalizada, 2)
        descuento_base = DESCUENTOS_TIPO_CLIENTE.get(tipo_cliente_normalizado, 0.0)
        descuentos = round(subtotal * descuento_base, 2)
        if "promo_grupal" in promociones and cantidad_normalizada >= 4:
            descuentos = round(descuentos + subtotal * 0.05, 2)

        recargos = 0.0
        impuestos = 0.0
        total = round(max(subtotal - descuentos + recargos + impuestos, 0.0), 2)
        return {
            "subtotal": subtotal,
            "descuentos": descuentos,
            "recargos": recargos,
            "impuestos": impuestos,
            "total": total,
        }

    def comprar_entrada(
        self,
        payload: dict[str, Any],
        payment_processor: PaymentProcessor | None = None,
    ) -> dict[str, Any]:
        payment_processor = payment_processor or _procesar_pago_defecto

        try:
            data = validar_payload_venta(payload)

            if data["restriccion_edad"] > 0 and data["cliente_edad"] < data["restriccion_edad"]:
                return {
                    "status": "error",
                    "codigo_error": "ERR_EDAD_INSUFICIENTE",
                    "mensaje": "El cliente no cumple la restriccion de edad de la pelicula.",
                }

            # Si la capacidad es nula o cero, no hay asientos disponibles
            if data["capacidad_sala"] <= 0:
                return {
                    "status": "error",
                    "codigo_error": "ERR_INSUFICIENTE_ASIENTOS",
                    "mensaje": "No hay suficientes asientos disponibles.",
                }

            disponibles = data["capacidad_sala"] - data["ocupadas_actuales"]
            if data["cantidad_entradas"] > disponibles:
                return {
                    "status": "error",
                    "codigo_error": "ERR_INSUFICIENTE_ASIENTOS",
                    "mensaje": "No hay suficientes asientos disponibles.",
                }

            total_data = self.calcular_total(
                precio_unitario=data["precio_unitario"],
                cantidad_entradas=data["cantidad_entradas"],
                tipo_cliente=data["tipo_cliente"],
                cliente_edad=data["cliente_edad"],
            )

            venta_id = f"V-{uuid4().hex.upper()}"
            pago_aprobado = _normalizar_respuesta_pago(
                payment_processor(
                    {
                        "venta_id": venta_id,
                        "total": total_data["total"],
                        "metodo_pago": data["metodo_pago"],
                        "cliente_documento": data["cliente_documento"],
                    }
                )
            )
            if not pago_aprobado:
                return {
                    "status": "error",
                    "codigo_error": "ERR_PAGO_FALLIDO",
                    "mensaje": "El pago fue rechazado.",
                }

            venta = Venta(
                venta_id=venta_id,
                pelicula_id=data["pelicula_id"],
                pelicula_titulo=data["pelicula_titulo"],
                sala_id=data["sala_id"],
                sala_numero=data["sala_numero"],
                funcion_id=data["funcion_id"],
                fecha_hora=data["fecha_hora"],
                cliente_nombre=data["cliente_nombre"],
                cliente_documento=data["cliente_documento"],
                cliente_edad=data["cliente_edad"],
                cantidad=data["cantidad_entradas"],
                precio_unitario=data["precio_unitario"],
                subtotal=total_data["subtotal"],
                descuentos=total_data["descuentos"],
                recargos=total_data["recargos"],
                impuestos=total_data["impuestos"],
                total=total_data["total"],
                metodo_pago=data["metodo_pago"],
                restriccion_edad=data["restriccion_edad"],
                estado="registrada",
                ticket_texto="",
                timestamp=datetime.now().isoformat(timespec="seconds"),
            )
            venta.ticket_texto = _formatear_ticket(venta)

            payload_store = self.store.load()
            payload_store["items"].append(venta.to_dict())
            self.store.save(payload_store)

            return {
                "status": "ok",
                "mensaje": "Venta registrada correctamente.",
                "venta_id": venta.venta_id,
                "ticket_texto": venta.ticket_texto,
                "total": venta.total,
                "venta": venta.to_dict(),
            }
        except (TypeError, ValueError) as exc:
            log_error(f"Error de validacion en comprar_entrada: {exc}")
            return {
                "status": "error",
                "codigo_error": "ERR_VALIDACION",
                "mensaje": str(exc),
            }
        except OSError as exc:
            log_error(f"Error de persistencia en comprar_entrada: {exc}")
            return {
                "status": "error",
                "codigo_error": "ERR_PERSISTENCIA",
                "mensaje": "No fue posible guardar la venta.",
            }
        except Exception as exc:  # pragma: no cover - fallback defensivo
            log_error(f"Error inesperado en comprar_entrada: {exc}")
            return {
                "status": "error",
                "codigo_error": "ERR_GENERAL",
                "mensaje": "Ocurrio un error inesperado.",
            }

    def mostrar_ticket(self, venta_id: str) -> dict[str, Any]:
        try:
            venta_id_normalizado = validar_texto_no_vacio(venta_id, "venta_id")
            payload_store = self.store.load()
            for item in payload_store.get("items", []):
                if isinstance(item, dict) and item.get("venta_id") == venta_id_normalizado:
                    venta = Venta.from_dict(item)
                    ticket = item.get("ticket_texto") or _formatear_ticket(venta)
                    return {
                        "status": "ok",
                        "mensaje": "Ticket encontrado.",
                        "ticket_texto": ticket,
                        "venta": item,
                    }
            return {
                "status": "error",
                "codigo_error": "ERR_VENTA_NO_ENCONTRADA",
                "mensaje": "No se encontro una venta con ese identificador.",
            }
        except (TypeError, ValueError) as exc:
            log_error(f"Error de validacion en mostrar_ticket: {exc}")
            return {
                "status": "error",
                "codigo_error": "ERR_VALIDACION",
                "mensaje": str(exc),
            }
        except Exception as exc:  # pragma: no cover - fallback defensivo
            log_error(f"Error inesperado en mostrar_ticket: {exc}")
            return {
                "status": "error",
                "codigo_error": "ERR_GENERAL",
                "mensaje": "Ocurrio un error inesperado.",
            }


_DEFAULT_SERVICE = VentasService()


def calcular_total(
    precio_unitario: float,
    cantidad_entradas: int,
    tipo_cliente: str = "general",
    promociones: list[str] | None = None,
    cliente_edad: int | None = None,
) -> dict[str, float]:
    return _DEFAULT_SERVICE.calcular_total(precio_unitario, cantidad_entradas, tipo_cliente, promociones, cliente_edad)


def comprar_entrada(
    payload: dict[str, Any],
    payment_processor: PaymentProcessor | None = None,
) -> dict[str, Any]:
    return _DEFAULT_SERVICE.comprar_entrada(payload, payment_processor)


def mostrar_ticket(venta_id: str) -> dict[str, Any]:
    return _DEFAULT_SERVICE.mostrar_ticket(venta_id)
