# Manual de usuario

Manual de uso del Sistema de Gestion de Cine.

## Descripcion
El sistema permite administrar peliculas, salas y ventas de entradas desde un punto principal de ejecucion. Al iniciar, el programa prepara los archivos JSON necesarios y muestra un menu para acceder a los modulos disponibles.

## Pasos basicos
1. Abrir una terminal en la carpeta raiz del proyecto.
2. Ejecutar:

```bash
python main.py
```

3. Elegir una opcion del menu principal:

- `1. Peliculas`: registrar, editar, eliminar o listar peliculas desde consola.
- `2. Salas y asientos`: abrir la ventana grafica para registrar salas y reservar asientos.
- `3. Venta de entradas`: abrir la ventana grafica para vender entradas, seleccionar pelicula, sala y asientos.
- `4. Reportes`: acceder al modulo de reportes disponible.
- `0. Salir`: cerrar el sistema.

## Requisitos previos

- Python 3.10 o superior.
- Tkinter instalado. En Windows normalmente viene incluido con Python.
- Ejecutar los comandos desde la raiz del proyecto, donde se encuentra `main.py`.
- Archivos JSON dentro de `data/`. Si faltan, el sistema crea estructuras base al iniciar.

## Estructura basica del proyecto

- `main.py`: punto principal de ejecucion e inicializacion.
- `config/`: rutas y constantes globales.
- `core/`: modelos y logica principal.
- `services/`: flujos operativos, como venta de entradas.
- `storage/`: persistencia en JSON.
- `validators/`: validaciones de datos.
- `ui/`: menus e interfaces.
- `data/`: archivos `peliculas.json`, `salas.json` y `ventas.json`.
- `tests/`: pruebas automatizadas con pytest.
- `docs/`: documentacion del proyecto.

## Funcionamiento general

Al ejecutar `main.py`, el sistema revisa los archivos de datos y completa campos minimos para evitar errores de lectura. Luego muestra el menu principal.

En peliculas se trabaja por consola. En salas y ventas se abren ventanas graficas. El modulo de ventas usa los catalogos de peliculas y salas, valida los datos del cliente, calcula el total, registra la venta en `data/ventas.json` y actualiza los asientos ocupados en `data/salas.json`.

## Ejemplos de uso

Registrar una pelicula:

1. Ejecutar `python main.py`.
2. Seleccionar `1. Peliculas`.
3. Elegir `1. Registrar pelicula`.
4. Completar nombre, genero, duracion, clasificacion y sala.

Registrar una sala:

1. Ejecutar `python main.py`.
2. Seleccionar `2. Salas y asientos`.
3. Ingresar numero de sala y capacidad.
4. Presionar `Guardar Sala`.

Vender una entrada:

1. Ejecutar `python main.py`.
2. Seleccionar `3. Venta de entradas`.
3. Elegir pelicula y sala.
4. Seleccionar asientos.
5. Completar nombre, documento, edad y metodo de pago.
6. Presionar `Calcular total` o `Comprar entrada`.

## Errores comunes y soluciones

- `ModuleNotFoundError`: ejecutar el sistema desde la carpeta raiz del proyecto.
- `No se pudo abrir el modulo grafico`: verificar que Tkinter este instalado y que el entorno permita ventanas graficas.
- `JSONDecodeError`: revisar que los archivos dentro de `data/` tengan formato JSON valido.
- `cliente_documento debe tener 8 digitos`: usar DNI de 8 digitos o seleccionar carnet cuando corresponda.
- `No hay suficientes asientos disponibles`: elegir otra sala, reducir cantidad o seleccionar asientos libres.
- `asiento ocupado`: seleccionar un asiento disponible para la pelicula y sala actuales.

