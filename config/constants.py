"""
Constantes compartidas del sistema.
"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

PELICULAS_DATA_FILE = DATA_DIR / "peliculas.json"
SALAS_DATA_FILE = DATA_DIR / "salas.json"
VENTAS_DATA_FILE = DATA_DIR / "ventas.json"

MIN_POR_COMPRA = 1
MAX_POR_COMPRA = 10

METODOS_PAGO_PERMITIDOS = ("efectivo",)

SCHEMA_VERSION_VENTAS = 1

DESCUENTOS_TIPO_CLIENTE = {
    "estudiante": 0.10,
    "senior": 0.15,
}
