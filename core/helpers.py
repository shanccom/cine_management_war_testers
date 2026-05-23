"""
Helpers de persistencia y utilidades.

TODO: definir manejo centralizado de errores.
"""

import json
from pathlib import Path


def load_json_file(path: str) -> dict:
    # TODO: agregar validaciones y control de errores con registro
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        # TODO: registrar error de archivo no encontrado
        raise exc
    except json.JSONDecodeError as exc:
        # TODO: registrar error de JSON invalido
        raise exc
    except OSError as exc:
        # TODO: registrar error de lectura
        raise exc


def save_json_file(path: str, payload: dict) -> None:
    # TODO: agregar validaciones y control de errores con registro
    file_path = Path(path)
    try:
        with file_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
    except OSError as exc:
        # TODO: registrar error de escritura
        raise exc


def log_error(message: str) -> None:
    # TODO: implementar registro de errores en archivo o consola
    _ = message
