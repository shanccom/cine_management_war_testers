# Sistema de Gestion de Cine

Proyecto academico para la competencia de testing "Guerra de Testers". El sistema permite gestionar peliculas, salas, asientos y ventas de entradas usando una arquitectura modular con persistencia en archivos JSON.

El punto principal de ejecucion es `main.py`, que inicializa los datos base, conecta los modulos existentes y muestra el menu principal del sistema.

## Integrantes
- Persona 1: Modulo de peliculas y validaciones asociadas.
- Persona 2: Modulo de salas y gestion de asientos.
- Persona 3: Modulo de venta de entradas, tickets y pruebas PE/AVL.
- Persona 4: Integracion general, documentacion y estabilizacion desde `main.py`.

## Requisitos
- Python 3.10 o superior
- Tkinter (incluido con Python)
- pytest para ejecutar las pruebas automatizadas

## Instalacion
1. Clonar el repositorio.
2. Ingresar a la carpeta `cine_management_war_testers`.
3. Crear un entorno virtual (opcional) y activarlo.
4. Instalar dependencias:
   - `pip install -r requirements.txt`

## Como ejecutar
1. Ubicarse en la carpeta `cine_management_war_testers`.
2. Ejecutar: `python main.py`
3. Seleccionar una opcion del menu principal:
   - `1. Peliculas`
   - `2. Salas y asientos`
   - `3. Venta de entradas`
   - `4. Reportes`
   - `0. Salir`

Para ejecutar las pruebas:

```bash
pytest -q
```

## Estructura del proyecto
```
cine_management_war_testers/
|-- main.py
|-- requirements.txt
|-- README.md
|-- assets/
|-- config/
|-- core/
|-- data/
|-- docs/
|-- services/
|-- storage/
|-- tests/
|-- ui/
`-- validators/
```

## Explicacion de PE y AVL
- Particion de Equivalencia (PE): tecnica que agrupa entradas en clases que se espera tengan el mismo comportamiento.
- Analisis de Valores Limite (AVL): tecnica que prioriza valores en los limites de cada rango valido o invalido.

## Reglas basicas del sistema
- El sistema debe ejecutarse desde `main.py`.
- Los datos se almacenan en archivos JSON dentro de `data/`.
- Las peliculas deben tener nombre, genero, duracion, clasificacion y sala asociada.
- Las salas deben tener identificador, numero, capacidad y listado de asientos ocupados.
- La capacidad de una sala debe estar entre 1 y 300 asientos.
- Los asientos deben tener formato valido, por ejemplo `A1` o `B12`.
- No se permite reservar dos veces el mismo asiento para la misma pelicula y sala.
- La venta de entradas valida pelicula, sala, funcion, cliente, edad, documento, metodo de pago, cantidad y asientos.
- El metodo de pago permitido actualmente es `efectivo`.
- Cada compra genera un ticket y registra la venta en `data/ventas.json`.
- Las ventas actualizan la ocupacion de asientos en `data/salas.json`.

Flujo principal de usuario:

1. Ejecutar `python main.py`.
2. Registrar o revisar peliculas.
3. Registrar salas y disponibilidad de asientos.
4. Abrir el modulo de venta de entradas.
5. Seleccionar pelicula, sala y asientos.
6. Completar datos del cliente.
7. Calcular total o comprar entrada.
8. Consultar el ticket con el identificador de venta.

## Posibles validaciones futuras
- Ampliar metodos de pago y validar estados de transaccion.
- Validar horarios reales de funciones por pelicula y sala.
- Evitar cruces de funciones cuando una sala ya este ocupada en el mismo horario.
- Agregar control de roles para administradores y vendedores.
- Registrar logs de errores en archivo.
- Generar reportes de ventas por fecha, pelicula y sala.
- Agregar respaldo automatico de archivos JSON.
- Ampliar la interfaz de reportes.
