"""
Servicios de negocio para el modulo de ventas.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from config.constants import DESCUENTOS_TIPO_CLIENTE, MAX_POR_COMPRA, MIN_POR_COMPRA, VENTAS_DATA_FILE, SALAS_DATA_FILE
from core.helpers import log_error, load_json_file, save_json_file
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
    ]
    # include selected seats if present
    seats = []
    try:
        seats = list(venta.extra.get("asientos_seleccionados", [])) if getattr(venta, "extra", None) is not None else []
    except Exception:
        seats = []
    if seats:
        lines.append(f"Asientos: {', '.join(seats)}")
    lines.extend([
        f"Metodo de pago: {venta.metodo_pago}",
        f"Total: S/. {venta.total:.2f}",
        f"Estado: {venta.estado}",
    ])
    return "\n".join(lines)


def _normalizar_lista_asientos(raw: Any) -> list[str]:
    if isinstance(raw, str):
        items = [item.strip().upper() for item in raw.split(",") if item.strip()]
    elif isinstance(raw, (list, tuple, set)):
        items = [str(item).strip().upper() for item in raw if str(item).strip()]
    else:
        items = []
    return list(dict.fromkeys(items))


def _normalizar_mapa_asientos(raw: Any) -> dict[str, list[str]]:
    if not isinstance(raw, dict):
        return {}
    normalizado: dict[str, list[str]] = {}
    for key, value in raw.items():
        key_text = str(key).strip()
        if not key_text:
            continue
        normalizado[key_text] = _normalizar_lista_asientos(value)
    return normalizado


def _actualizar_sala_ocupada(
    sala_id: str,
    pelicula_id: str,
    asientos: list[str],
    sala_numero: int,
    capacidad: int,
) -> None:
    """Persistir asientos ocupados por sala y por pelicula dentro de salas.json.

    La estructura para cada sala en el catalogo será:
    {
      "sala_id": "S1",
      "asientos_ocupados_por_pelicula": {"P001": "A1,A2", "P002": "B1"},
      "asientos_ocupados": "A1,A2,B1",
      ...
    }
    """
    if not asientos:
        return

    try:
        sala_payload = load_json_file(str(SALAS_DATA_FILE))
    except Exception:
        sala_payload = {}

    items = sala_payload.get("items", []) if isinstance(sala_payload, dict) else []
    if not isinstance(items, list):
        items = []

    target_item: dict[str, Any] | None = None
    for item in items:
        if isinstance(item, dict) and (item.get("sala_id") == sala_id or item.get("id") == sala_id):
            target_item = item
            break

    if target_item is None:
        target_item = {
            "sala_id": sala_id,
            "id": sala_id,
            "numero": str(sala_numero),
            "capacidad": str(capacidad),
        }
        items.append(target_item)

    pelicula_key = str(pelicula_id).strip() or "desconocida"
    existing_map = _normalizar_mapa_asientos(target_item.get("asientos_ocupados_por_pelicula", {}))

    occupied_for_movie = list(dict.fromkeys(existing_map.get(pelicula_key, []) + _normalizar_lista_asientos(asientos)))
    existing_map[pelicula_key] = occupied_for_movie

    # write back per-pelicula map (strings)
    target_item["asientos_ocupados_por_pelicula"] = {k: ",".join(v) for k, v in existing_map.items()}

    # combined overall occupied seats across all peliculas
    combined = list(dict.fromkeys(seat for seats in existing_map.values() for seat in seats))
    target_item["asientos_ocupados"] = ",".join(combined)

    # store counts/legacy fields for compatibility
    total_occupied = len(combined)
    target_item["ocupadas_actuales"] = str(total_occupied)
    target_item["ocupadas"] = str(total_occupied)
    target_item["ocupacion"] = str(total_occupied)
    target_item["occupied"] = str(total_occupied)
    target_item["numero"] = str(sala_numero)
    target_item["capacidad"] = str(capacidad)

    save_json_file(str(SALAS_DATA_FILE), {"items": items})


class VentasService:
    def __init__(self, ventas_path: str | Path | None = None) -> None:
        """Crear el servicio de ventas.

        Si se proporciona `ventas_path`, se usará ese archivo para persistir ventas (útil en tests).
        """
        self.store = VentasStore(ventas_path or VENTAS_DATA_FILE)

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
                asientos_seleccionados=data.get("asientos_seleccionados", []),
            )
            venta.ticket_texto = _formatear_ticket(venta)

            payload_store = self.store.load()
            payload_store["items"].append(venta.to_dict())
            self.store.save(payload_store)

            # Mark seats as occupied in the salas catalog so they cannot be selected again
            try:
                _actualizar_sala_ocupada(
                    sala_id=venta.sala_id,
                    pelicula_id=venta.pelicula_id,
                    asientos=data.get("asientos_seleccionados", []),
                    sala_numero=venta.sala_numero,
                    capacidad=data["capacidad_sala"],
                )
            except Exception:
                # non-fatal: log and continue
                log_error("No fue posible actualizar asientos ocupados en el catalogo de salas")

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
