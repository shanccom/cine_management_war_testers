# Plan de implementacion UI - Modulo Venta de Entradas (sin codigo)

Nota: conforme a la restriccion del proyecto, este documento NO contiene codigo. Es un plan tecnico y operativo para implementar la interfaz (Tkinter) del modulo `Venta de Entradas`. Está orientado al integrante 3 y preparado para facilitar pruebas con pytest, mocks y QA ofensivo.

1. Objetivo
- Definir la estructura de la interfaz, eventos, validaciones en UI, puntos de integracion con `services`, y hooks para testing/mocks.

2. Principios de diseño
- UI ligera: la logica de negocio NO vive en la UI; la UI orquesta llamadas a `services/ventas` y `validators`.
- Todo I/O y persistencia son responsabilidad de `storage` y deben ser inyectables para pruebas.
- Errores mostrados al usuario como mensajes claros y tambien registrados en logs con `request_id` y `venta_id` cuando proceda.
- No exponer datos sensibles en UI ni logs.

3. Pantallas y componentes (mapa)
- Ventana principal de venta (MainWindowVenta):
  - Campo `pelicula` (ComboBox) -> lista de peliculas cargadas desde `storage`.
  - Campo `funcion` (ComboBox) -> funciones filtradas por pelicula.
  - Campo `cantidad` (Spinbox/Entry numerico) -> enteros 1..MAX_POR_COMPRA.
  - Campos `cliente_nombre`, `cliente_documento`, `cliente_edad` (Entry).
  - Selector `metodo_pago` (Combobox) -> valores permitidos.
  - Boton `Calcular total` -> muestra desglose en area `resumen`.
  - Boton `Comprar` -> inicia flujo `comprar_entrada` (ver secuencia).
  - Boton `Mostrar ticket` -> solicita `venta_id` y llama a `mostrar_ticket()`.
  - Area `mensajes` -> mensajes de validacion y errores (texto legible para asserts).

4. Validaciones en UI (preventivas) — antes de llamar a services
- Campos obligatorios: pelicula, funcion, cantidad, cliente_nombre, cliente_documento, metodo_pago.
- Validar formatos basicos: cantidad es entero >0, edad es entero >=0, no strings vacios.
- Validar limites: cantidad <= MAX_POR_COMPRA; mostrar mensaje especifico si viola.
- Para peliculas +18, advertir y bloquear si edad < restriccion.
- Estas validaciones evitan roundtrips innecesarios y mejoran UX; todas deben replicarse en `validators` en backend.

5. Secuencia de compra (UI -> Services)
1. Usuario completa formulario y pulsa `Comprar`.
2. UI realiza validaciones basicamente sintacticas y de rango.
3. UI muestra un dialogo de confirmacion con resumen y total (opcional: confirmar pago).
4. UI llama a `services.comprar_entrada(payload)` y muestra spinner/estado de procesamiento.
5. `services` realiza reserva interna, procesa pago (hook mockeable) y persiste la venta.
6. UI recibe respuesta: si `status == 'ok'` muestra ticket y `venta_id`; si `error` muestra mensaje estandarizado y acciones sugeridas.
7. UI limpia/formatea formulario segun politica (no limpiar automatico si fallo para permitir correccion).

6. Manejo de errores en UI
- Errores de validacion: mostrar en `area mensajes` con codigo y descripcion breve.
- Errores de red/pago/storage: mostrar mensaje amigable y un boton "Reintentar" que reejecute el flujo (si idempotente) o permita cancelar.
- Excepciones no controladas: capturarlas a nivel global en el mainloop, registrar en logs y mostrar mensaje genérico sin stacktrace.

7. Mensajes estandarizados para aserciones en tests
- Mensajes UI deben contener `codigo_error` en formato legible (p.ej. "ERR_CANTIDAD_MAX: Maximo 10 entradas").
- Mensajes de exito deben incluir `venta_id` y `total`.
- Facilitar que tests hagan `assert 'ERR_CANTIDAD_MAX' in area_mensajes.get()`.

8. Hooks para testing y QA ofensivo
- Exponer funciones/facades que la UI usa (ej: `ui_handler.comprar(payload, storage, payment_processor)`) para inyectar mocks.
- Permitir `simulate_io_failure` y `simulate_payment_failure` via monkeypatch en pruebas.
- Proveer fixture `ui_with_tmp_storage` que arranca la ventana en modo headless o en un hilo para pruebas integradas (sin dependencia visual). Documentar su uso.

9. Consideraciones de concurrencia y threading
- No ejecutar operaciones I/O pesadas en el hilo principal; usar `after()` o hilo separado y comunicar resultados al hilo UI via colas seguras.
- Tests deben simular concurrencia con threads o procesos y validar locking/consistencia del storage.

10. Accesibilidad y usabilidad
- Labels claros y placeholders; mensajes de error proximos al campo.
- Soporte minimo para teclado: tabs y foco en campos obligatorios.

11. Logging y trazabilidad desde UI
- Cada accion de compra genera `request_id` unico (UUID) asociado al intento; incluirlo en logs y en respuestas de error para reproducibilidad.
- No loguear datos sensibles (CVV, numero completo de tarjeta).

12. Lista de checks pre-implementacion para Integrante 3
- [ ] Revisar y versionar el esquema JSON en `data/` y documentar campos necesarios.
- [ ] Definir constantes compartidas en `config/constants.py` (MAX_POR_COMPRA, metodos_permitidos).
- [ ] Confirmar contratos de funciones en `services/ventas.py` (parametros y respuestas esperadas).
- [ ] Implementar mensajes UI estandarizados y codigos de error.
- [ ] Añadir fixtures UI para pytest y ejemplos de uso en `tests/`.

13. Entregables (documentacion) que preparara el integrante 3
- Interfaz: mapeo de widgets y eventos (este documento).
- Contratos: entradas/salidas JSON para `comprar_entrada`, `mostrar_ticket`, `calcular_total`.
- Guia de pruebas UI: casos de PE/AVL ejecutables con `pytest` y `monkeypatch`.

14. Recomendaciones finales
- Mantener la UI lo mas delgada posible; delegar validaciones criticas al backend (services/validators).
- Preparar hooks de testing desde el inicio para que QA ofensivo pueda inyectar fallos.
- Documentar claramente los codigos de error y mensajes para facilitar aserciones automatizadas.

-- Fin del plan UI
