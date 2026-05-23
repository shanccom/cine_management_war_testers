"""
Funciones de validacion.
"""

from __future__ import annotations

import re


GENEROS_VALIDOS = ("Accion", "Terror", "Drama", "Comedia", "Ciencia Ficcion")
CLASIFICACIONES_VALIDAS = ("ATP", "+14", "+18")


def _normalizar_texto(valor: object) -> str:
    return "" if valor is None else str(valor)


def validar_nombre(nombre: object) -> tuple[bool, str, str]:
    # Clase valida: texto de 2 a 50 caracteres, solo letras y espacios
    # Clase invalida: vacio, longitud fuera de rango, numeros o caracteres especiales
    # Valor limite inferior: 2
    # Valor limite superior: 50
    texto = _normalizar_texto(nombre).strip()
    if texto == "":
        return False, "Nombre es obligatorio.", ""
    if len(texto) < 2:
        return False, "Nombre debe tener al menos 2 caracteres.", ""
    if len(texto) > 50:
        return False, "Nombre no debe superar 50 caracteres.", ""
    if re.search(r"\d", texto):
        return False, "Nombre no debe contener numeros.", ""
    if re.search(r"[^A-Za-z ]", texto):
        return False, "Nombre no debe contener caracteres especiales.", ""
    return True, "Nombre valido.", texto


def validar_genero(genero: object) -> tuple[bool, str, str]:
    # Clase valida: valor en lista permitida
    # Clase invalida: vacio, valor fuera de lista, numeros o caracteres especiales
    # Valor limite inferior: no aplica (lista cerrada)
    # Valor limite superior: no aplica (lista cerrada)
    texto = _normalizar_texto(genero).strip()
    if texto == "":
        return False, "Genero es obligatorio.", ""
    if re.search(r"\d", texto):
        return False, "Genero no debe contener numeros.", ""
    if re.search(r"[^A-Za-z ]", texto):
        return False, "Genero no debe contener caracteres especiales.", ""
    opciones = {opcion.lower(): opcion for opcion in GENEROS_VALIDOS}
    clave = texto.lower()
    if clave not in opciones:
        return (
            False,
            f"Genero no valido. Use: {', '.join(GENEROS_VALIDOS)}.",
            "",
        )
    return True, "Genero valido.", opciones[clave]


def validar_duracion(duracion: object) -> tuple[bool, str, int | None]:
    # Clase valida: entero entre 30 y 300
    # Clase invalida: vacio, negativo, no entero, fuera de rango, letras o especiales
    # Valor limite inferior: 30
    # Valor limite superior: 300
    texto = _normalizar_texto(duracion).strip()
    if texto == "":
        return False, "Duracion es obligatoria.", None
    if texto.startswith("-"):
        return False, "Duracion no puede ser negativa.", None
    if re.search(r"[A-Za-z]", texto):
        return False, "Duracion no debe contener letras.", None
    if re.search(r"[^0-9]", texto):
        return False, "Duracion no debe contener caracteres especiales.", None
    try:
        numero = int(texto)
    except ValueError:
        return False, "Duracion debe ser un numero entero.", None
    if numero < 30 or numero > 300:
        return (
            False,
            "Duracion fuera de rango. Debe estar entre 30 y 300.",
            None,
        )
    return True, "Duracion valida.", numero


def validar_clasificacion(clasificacion: object) -> tuple[bool, str, str]:
    # Clase valida: valor en lista permitida
    # Clase invalida: vacio, valor fuera de lista, caracteres especiales
    # Valor limite inferior: no aplica (lista cerrada)
    # Valor limite superior: no aplica (lista cerrada)
    texto = _normalizar_texto(clasificacion).strip()
    if texto == "":
        return False, "Clasificacion es obligatoria.", ""
    if re.search(r"[^A-Za-z0-9+]", texto):
        return False, "Clasificacion no debe contener caracteres especiales.", ""
    opciones = {opcion.lower(): opcion for opcion in CLASIFICACIONES_VALIDAS}
    clave = texto.lower()
    if clave not in opciones:
        return (
            False,
            f"Clasificacion no valida. Use: {', '.join(CLASIFICACIONES_VALIDAS)}.",
            "",
        )
    return True, "Clasificacion valida.", opciones[clave]


def validar_sala(sala: object) -> tuple[bool, str, int | None]:
    # Clase valida: entero entre 1 y 20
    # Clase invalida: vacio, negativo, no entero, fuera de rango, letras o especiales
    # Valor limite inferior: 1
    # Valor limite superior: 20
    texto = _normalizar_texto(sala).strip()
    if texto == "":
        return False, "Sala es obligatoria.", None
    if texto.startswith("-"):
        return False, "Sala no puede ser negativa.", None
    if re.search(r"[A-Za-z]", texto):
        return False, "Sala no debe contener letras.", None
    if re.search(r"[^0-9]", texto):
        return False, "Sala no debe contener caracteres especiales.", None
    try:
        numero = int(texto)
    except ValueError:
        return False, "Sala debe ser un numero entero.", None
    if numero < 1 or numero > 20:
        return False, "Sala fuera de rango. Debe estar entre 1 y 20.", None
    return True, "Sala valida.", numero


def validar_pelicula(data: dict) -> tuple[bool, list[str], dict]:
    # Clase valida: pelicula con campos validos
    # Clase invalida: al menos un campo invalido
    # Valor limite inferior: aplica a limites de cada campo
    # Valor limite superior: aplica a limites de cada campo
    if not isinstance(data, dict):
        return False, ["Datos de pelicula no validos."], {}

    errores: list[str] = []
    datos_validos: dict = {}

    ok, mensaje, nombre = validar_nombre(data.get("nombre"))
    if not ok:
        errores.append(mensaje)
    else:
        datos_validos["nombre"] = nombre

    ok, mensaje, genero = validar_genero(data.get("genero"))
    if not ok:
        errores.append(mensaje)
    else:
        datos_validos["genero"] = genero

    ok, mensaje, duracion = validar_duracion(data.get("duracion"))
    if not ok:
        errores.append(mensaje)
    else:
        datos_validos["duracion"] = duracion

    ok, mensaje, clasificacion = validar_clasificacion(data.get("clasificacion"))
    if not ok:
        errores.append(mensaje)
    else:
        datos_validos["clasificacion"] = clasificacion

    ok, mensaje, sala = validar_sala(data.get("sala"))
    if not ok:
        errores.append(mensaje)
    else:
        datos_validos["sala"] = sala

    return len(errores) == 0, errores, datos_validos


def validar_venta(data: dict) -> bool:
    # TODO: definir validaciones PE y AVL para ventas
    _ = data
    return True
