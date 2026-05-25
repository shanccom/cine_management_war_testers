# Prompts usados

TODO: registrar prompts relevantes usados durante el desarrollo.

## Descripcion
TODO: explicar el contexto de cada prompt.

## Resultados esperados
TODO: indicar resultados esperados del prompt.

## Resultados obtenidos
TODO: indicar resultados obtenidos del prompt.

---

### Entrada creada: Venta de Entradas - Documentacion y Requisitos

- Fecha: 2026-05-24
- Autor: Persona 3 (asistente automatizado)
- Contexto: Generacion de requerimientos funcionales y no funcionales para el modulo "Venta de Entradas" del "Sistema de Gestion de Cine" enfocado a pruebas academicas (Guerra de Testers). Interfaz: Tkinter. Persistencia: JSON. Tests: pytest. Documento generado para preparar PE, AVL y pruebas Black Box.
- Prompt: Solicitud para definir RF, RNF, reglas de negocio, riesgos QA, preparacion PE/AVL y recomendaciones para pytest y arquitectura. No generar codigo ni implementar funcionalidades.
- Resultado esperado: Documento tecnico y estructurado con RF-01..RF-03, RNF-01..RNF-03, reglas de negocio, riesgos, casos PE/AVL y guia de pruebas pytest.
- Resultado obtenido: Entrada registrada. Documento tecnico entregado en la conversacion (ver mensaje del asistente).

---

### Entrada creada: Venta de Entradas - Definir reglas de negocio

- Fecha: 2026-05-24
- Autor: Persona 3 (asistente automatizado)
- Contexto: Solicitud para definir las reglas de negocio del modulo "Venta de Entradas" dentro del "Sistema de Gestion de Cine". Enfoque en QA ofensivo, PE/AVL y preparacion para pruebas con pytest. Se requiere documentacion tecnica sin generar codigo.
- Prompt: "definir las reglas de negocio, quiero que todos los prompts los estes añadiendo, recuerda eso ademas"
- Resultado esperado: Lista profesional y tecnica de reglas de negocio, con limites de compra, restricciones de edad, reglas de tickets, validaciones de pago y restricciones de datos.
- Resultado obtenido: Reglas de negocio definidas y registradas en la conversacion; entrada añadida al registro de prompts.

---

### Entrada creada: Venta de Entradas - Listar riesgos y vulnerabilidades QA

- Fecha: 2026-05-24
- Autor: Persona 3 (asistente automatizado)
- Contexto: Solicitud para listar riesgos y vulnerabilidades generales del modulo "Venta de Entradas" con enfoque en QA ofensivo y preparacion para pruebas Black Box (PE/AVL). No generar codigo; documentacion tecnica requerida.
- Prompt: "lista los riesgos y vulnerabilidades QA en general para estar preparado ante cualquier eventualidad"
- Resultado esperado: Lista detallada y priorizada de riesgos, vulnerabilidades y vectores de ataque comunes, con recomendaciones de mitigacion y deteccion.
- Resultado obtenido: Entrada registrada; riesgos y vulnerabilidades entregados en la conversacion.

---

### Entrada creada: Venta de Entradas - Preparacion PE y AVL

- Fecha: 2026-05-24
- Autor: Persona 3 (asistente automatizado)
- Contexto: Solicitud para preparar la matriz PE/AVL, casos de prueba, muestras JSON y checklist de implementacion para Integrante 3 (Venta de Entradas). Enfoque en QA ofensivo y pytest.
- Prompt: "Prepara todo para PE y AVL, ademas quiero que nos alistemos enumerando todo para la implementacion en el modulo correspondiente al integrante 3"
- Resultado esperado: Documento con clases PE/AVL, casos de prueba, muestras JSON, guia de implementacion y lista de tests recomendados.
- Resultado obtenido: Documento `docs/preparacion_pe_avl_venta_entradas.md` creado y registro actualizado.

---

### Entrada creada: Venta de Entradas - Plan UI (sin codigo)

- Fecha: 2026-05-24
- Autor: Persona 3 (asistente automatizado)
- Contexto: Solicitud para implementar todo en la interfaz; en respuesta se genero un plan de implementacion UI sin codigo para guiar al Integrante 3 y al equipo de QA.
- Prompt: "ahora implementa todo en la interfaz , analizando todos los documentos pertinente"
- Resultado esperado: Documento tecnico `docs/ui_implementacion_venta_entradas.md` describiendo componentes, flujos, validaciones UI, hooks para tests y checklist de integracion.
- Resultado obtenido: Documento creado y registrado; no se genero codigo conforme a restricciones del proyecto.

---

### Entrada creada: Venta de Entradas - Ajuste UI con seleccion de peliculas

- Fecha: 2026-05-24
- Autor: Persona 3 (asistente automatizado)
- Contexto: Solicitud para ajustar la interfaz de ventas usando una barra desplegable para peliculas, con formulario minimalista y opciones realistas.
- Prompt: "En la opción de peliculas, se precisa un campo de selección con una barra desplegable, no se requiere campo, quiero que el rellenado del formulario sea el más real posible y minimalista, evita poner id de pelicula, queremos opciones reales"
- Resultado esperado: Interfaz de ventas actualizada para usar seleccion desplegable de peliculas con datos reales o realistamente simulados, ocultando el id al usuario.
- Resultado obtenido: UI actualizada con combobox de peliculas y salas, ids ocultos y formulario minimalista.

