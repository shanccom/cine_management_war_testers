# Informe tecnico

Informe tecnico de integracion del Sistema de Gestion de Cine.

## Descripcion
El proyecto integra modulos de peliculas, salas, ventas, persistencia JSON, validaciones e interfaz de usuario usando `main.py` como punto central de ejecucion. El inicio del sistema prepara la carpeta `data`, verifica los archivos JSON requeridos y normaliza estructuras minimas para que los modulos puedan leer datos sin errores de integracion.

La estructura respetada es:

- `core`: modelos y reglas principales de peliculas, salas y ventas.
- `services`: flujo operativo de ventas y emision de tickets.
- `storage`: lectura y escritura JSON mediante almacenes reutilizables.
- `validators`: validaciones de entradas y payloads de venta.
- `ui`: menus de consola e interfaces Tkinter.
- `config`: rutas y constantes globales.
- `data`: persistencia de peliculas, salas y ventas.

`main.py` ejecuta tres responsabilidades de arranque: posicionar el directorio de trabajo en la raiz del proyecto, inicializar/normalizar los datos base y abrir el menu principal `MainWindow`.

## Validaciones
Validaciones e inicializaciones aplicadas:

- Creacion de `data/` si no existe.
- Verificacion de `peliculas.json`, `salas.json` y `ventas.json`.
- Garantia de estructura base `{"items": []}` cuando un JSON esta vacio o no tiene lista de items.
- Normalizacion de peliculas con claves compatibles para catalogo y ventas: `pelicula_id`, `id`, `titulo`, `nombre`, `genero`, `duracion`, `clasificacion`, `sala`, `precio_unitario` y `restriccion_edad`.
- Normalizacion de salas con datos compatibles para `core.salas.Sala`, `ui.salas_ui` y `ui.ventas_ui`: `sala_id`, `id`, `numero`, `capacidad`, `funcion_id`, `asientos_ocupados`, `asientos_ocupados_por_pelicula`, `ocupadas_actuales`, `ocupadas`, `ocupacion` y `occupied`.
- Conservacion de ventas existentes y garantia de `_schema_version`.
- Menu principal integrado con peliculas, salas, ventas y reportes.
- Reutilizacion de `VentasService`, `PeliculaManager`, `SalasUI`, `VentasUI` y `ReportesUI` sin cambiar sus nombres publicos.

## Resultados esperados
Resultados esperados de la integracion:

- El sistema inicia desde `python main.py`.
- No se producen errores de importacion entre `core`, `services`, `storage`, `validators`, `ui` y `config`.
- Los JSON se cargan con objetos minimos validos.
- El menu principal permite acceder a peliculas, salas, ventas y reportes.
- La venta de entradas puede leer catalogos de peliculas y salas desde `data/`.
- La ocupacion de asientos se mantiene por sala y pelicula.
- La documentacion tecnica y de usuario queda actualizada para ejecucion y soporte.

## Resultados obtenidos
Resultados obtenidos:

- `main.py` quedo como orquestador de arranque e inicializacion.
- `ui/main_window.py` quedo integrado con los modulos disponibles.
- `data/peliculas.json` recibio peliculas base compatibles con la UI de ventas.
- `data/salas.json` quedo normalizado con enteros y listas para evitar errores de tipo en `Sala.from_dict`.
- `data/ventas.json` conserva sus ventas existentes y mantiene `_schema_version`.
- Se verifico compilacion de modulos Python.
- Se ejecuto la suite automatizada con resultado: `258 passed`.
