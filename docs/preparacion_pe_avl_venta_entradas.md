# Preparacion PE y AVL - Modulo Venta de Entradas

Objetivo:
- Preparar la matriz de pruebas de Particion de Equivalencia (PE) y Analisis de Valores Limite (AVL) para el modulo "Venta de Entradas".
- Proveer casos de prueba, muestras de datos JSON, y una lista de tareas para el integrante 3 (Venta de Entradas) para facilitar la implementacion y las pruebas automatizadas con pytest.

Alcance:
- Cobertura de validadores de entrada, calculo de totales, flujo de compra, manejo de persistencia JSON y generacion de ticket.
- Casos negativos y ataques de QA ofensivo incluidos.

1. Clases y particiones (PE)
- Clase valida - Cantidad: entero en [1,10]
- Clase invalida - Cantidad: 0, <0, >10, no entero (p.ej. 'diez', 1.5)
- Clase valida - Edad: entero >=0 (y >= restriccion_edad cuando aplica)
- Clase invalida - Edad: null, negativo, cadena no numerica
- Clase valida - Metodo_pago: 'tarjeta', 'efectivo', 'transferencia'
- Clase invalida - Metodo_pago: '', null, 'bitcoin'
- Clase valida - Campos texto: no vacios, longitud <= 100
- Clase invalida - Campos texto: vacio, espacios, payloads de inyeccion

2. Valores limite (AVL)
- Limite inferior cantidad: 0 (error esperado)
- Valor frontera aceptado: 1 (ok)
- Valor frontera aceptado: 10 (ok)
- Limite superior: 11 (error esperado)
- Edad frontera: 17 (rechazar si restriccion 18), 18 (aceptar)

3. Casos de prueba ejemplares (PE y AVL)
- TC-PE-001: cantidad=2, edad=25, metodo_pago='tarjeta' -> exito
- TC-PE-002: cantidad=0, edad=25 -> error ERR_CANTIDAD_MIN
- TC-PE-003: cantidad=11, edad=25 -> error ERR_CANTIDAD_MAX
- TC-PE-004: pelicula.restriccion_edad=18, cliente.edad=17 -> error ERR_EDAD_INSUFICIENTE
- TC-AVL-001: cantidad=1 -> exito
- TC-AVL-002: cantidad=10 -> exito
- TC-FUZZ-001: cantidad='1000000000000' -> validar rechazo y sin crash
- TC-INYECCION-001: nombre_cliente='{"$or": [1,1]}' -> sanitizar y rechazar o aceptar como texto seguro
- TC-PERSIST-FAIL-001: simular fallo I/O despues de reservar y antes de persistir -> verificar rollback

4. Matriz de cobertura recomendada
- Dimensiones: cantidad x edad x metodo_pago x existencia_funcion x estado_storage
- Priorizar combinaciones que toquen limites: cantidad {0,1,10,11}, edad {17,18}, metodo_pago {valido, invalido}, storage {ok, fallo}

5. Datos de prueba JSON (muestras)
- Pelicula ejemplo:
  {
    "pelicula_id": "P001",
    "titulo": "Ejemplo Pelicula",
    "restriccion_edad": 18
  }
- Funcion ejemplo:
  {
    "funcion_id": "F001",
    "pelicula_id": "P001",
    "sala_id": "S1",
    "fecha_hora": "2026-06-01T20:00:00",
    "capacidad": 100,
    "ocupadas": 90
  }
- Venta ejemplo valida (para assert y comparacion):
  {
    "venta_id": "V-UUID-1234",
    "pelicula_id": "P001",
    "funcion_id": "F001",
    "cliente": {"nombre":"Juan Perez","documento":"12345678","edad":25},
    "cantidad": 2,
    "total": 20.00,
    "metodo_pago":"efectivo",
    "timestamp":"2026-05-24T12:00:00",
    "_schema_version": 1
  }

6. Estrategia de ejecucion de pruebas
- Unitarias: validar cada validador (cantidad, edad, metodo_pago, campos texto) con parametrizacion PE/AVL.
- Integracion: flujo comprar_entrada con storage mockeado (exito, fallo I/O), pago mockeado (exito, rechazo).
- End-to-end (sin UI): invocar services/comprar_entrada con `tmp_path` para storage real en disco de pruebas.
- Fuzzing: generar inputs aleatorios para campos texto y numericos para detectar crash.

7. Checklist de implementacion para Integrante 3 (Venta de Entradas)
- [ ] Crear modulo `services/ventas.py` con funciones publicas: `comprar_entrada()`, `mostrar_ticket()`, `calcular_total()`.
- [ ] Crear modulo `validators/venta_validators.py` con funciones: `valida_cantidad()`, `valida_edad()`, `valida_metodo_pago()`, `valida_campos_texto()`.
- [ ] Crear interfaz `storage/json_store.py` con metodos: `load_ventas()`, `save_venta(venta)` y soporte de version de esquema.
- [ ] Implementar escrituras atomicas y backups automaticos en storage.
- [ ] Implementar manejo de excepciones y codigos de error estandarizados.
- [ ] Proveer hooks de mock para `procesar_pago()` y para forcear fallos I/O en pruebas.
- [ ] Añadir logs estructurados con `venta_id` y `request_id` en pasos clave.
- [ ] Definir constantes: `MAX_POR_COMPRA=10`, codigos de error y lista_permitida_metodos.
- [ ] Crear muestras JSON en `tests/fixtures/` para PE y AVL.
- [ ] Crear tests iniciales:
    - `tests/test_validadores.py` (parametrizado PE/AVL)
    - `tests/test_calculo_total.py` (casos base y descuentos)
    - `tests/test_compra_end2end.py` (flujo con storage tmp_path y mocks)
- [ ] Documentar en `docs/` los endpoints/funciones y contratos de entrada/salida.

8. Templates de casos pytest (sin codigo)
- test_validadores parametrizados:
  - param cantidad: [0,1,10,11,-1,'diez'] => esperar errores o exito segun caso
  - param edad: [16,17,18,25,'veinte'] => frontera +18
- test_compra_end2end:
  - fixture storage tmp_path con ventas.json vacio
  - monkeypatch para simular procesar_pago() devolviendo exito/fracaso

9. Recomendaciones para integracion en CI
- Ejecutar suites: unitarias rapidas primero, integracion despues.
- Fijar coverage minimo para `validators` y `calculo_total`.
- Añadir test de integridad de esquema JSON en pipeline.

10. Checklist de entregables para Integrante 3
- `services/ventas.py` con interfaces documentadas
- `validators/venta_validators.py`
- `storage/json_store.py` (inyectable)
- `tests/test_validadores.py`, `tests/test_calculo_total.py`, `tests/test_compra_end2end.py`
- fixtures JSON en `tests/fixtures/`
- Documentacion en `docs/preparacion_pe_avl_venta_entradas.md` y `docs/requerimientos_venta_entradas.md`

Notas finales:
- Evitar tildes en nombres de archivos y comentarios segun la pauta del equipo.
- Mantener todo el codigo testable y desacoplado del UI Tkinter.

-- Fin del documento
