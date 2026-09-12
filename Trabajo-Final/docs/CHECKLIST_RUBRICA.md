# Checklist de rúbrica

Mapeo según las cinco dimensiones y ponderaciones indicadas para este trabajo. **No se autoasigna puntaje ni se afirma cumplimiento académico total.** Las ponderaciones no son resultados obtenidos.

| Dimensión / ponderación | Evidencia existente | Evidencia pendiente | Ubicación de evaluación |
|---|---|---|---|
| Sistema completo y funcionando — 30 | Motor V4 con generación, archivos por revisor/Leadership, edición acotada, budget dinámico, consolidación y detección de manipulación. Interfaz local probada y contrato de agente con salida estructurada | Ejecutar el agente final en el host/modelo elegido, registrar coordinación LLM y tres corridas. Aprobación humana sigue fuera del motor | [README](../README.md), [CLI](../agente/cli.py), [contrato de herramienta](../agente/contrato_herramienta.json), [validación técnica](VALIDACION_TECNICA.md), [demo](../corridas/demo_sintetica/README.md) |
| Proceso documentado — 25 | Evolución V1–V4 con problema/decisión/efecto, enlaces a evidencia preservada y correcciones de revisión humana. Prompts finales y explicación de cambios | Transcripciones efectivas de las tres corridas, observaciones y decisiones humanas realmente realizadas | [DECISIONES](../DECISIONES.md), [system prompt](../prompts/system_prompt.md), [user prompt](../prompts/user_prompt.md), [corridas](../corridas/README.md) |
| Formato y reproducibilidad — 15 | Carpeta de evaluación, catálogos con hashes, interfaz generate/consolidate, dependencias explícitas, logs y tests, fuentes V4 sin modificar | Reproducción en el entorno del evaluador y usabilidad/recálculo en su Excel; acceso al runtime Artifact Tool si no está disponible | [REPRODUCCION](REPRODUCCION.md), [inputs](../inputs/README.md), [referencias V4](../agente/v4_referencias.json), [tests interfaz](../agente/tests/test_interface.py) |
| Análisis económico — 15 | Separación del workflow local y componente LLM; metodología de tokens, precio, costo por corrida, frecuencia y proyección, sin cifras ficticias | Modelo, usage, precio aplicable, costo, frecuencia y tiempos humanos medidos; no hay ROI acreditado | [ANALISIS_ECONOMICO](ANALISIS_ECONOMICO.md), campos económicos de [corrida_01](../corridas/corrida_01/registro.json), [corrida_02](../corridas/corrida_02/registro.json), [corrida_03](../corridas/corrida_03/registro.json) |
| Gobierno y riesgo — 15 | L2, responsabilidades por rol, matriz de detección/respuesta/continuidad/intervención, límites de protección Excel, custodia de originales y aprobación pendiente | Identidad/autoridad operativa, ACL, cifrado y distribución segura si se considerara una implantación; prueba de comportamiento del host ante instrucciones en datos | [SUPERVISION](SUPERVISION.md), [GOBIERNO_Y_RIESGO](GOBIERNO_Y_RIESGO.md), restricciones del [system prompt](../prompts/system_prompt.md) |

## Comprobaciones para cierre de la entrega

- [x] Contrato final de seis piezas y solicitud realista sin respuestas esperadas inventadas.
- [x] Interfaz local que reutiliza código V4 sin cambiar reglas salariales.
- [x] Evidencia de demo/test separada de corridas del agente final.
- [x] Tres directorios de corridas con registros pendientes y métricas `null`.
- [x] Documentación factual de economía, L2 y gobierno.
- [x] Preservación de V1–V4 y de outputs históricos verificada en el diff del paquete.
- [ ] Ejecutar y registrar corrida_01 con modelo, prompts efectivos, tool invocation y salida reales.
- [ ] Ejecutar y registrar corrida_02 con la misma trazabilidad y observaciones.
- [ ] Ejecutar y registrar corrida_03 con la misma trazabilidad y observaciones.
- [ ] Completar medición económica con fuentes verificables.
- [ ] Revisión académica final por el responsable del trabajo.

La aprobación técnica previa de V4 y los tests no sustituyen las evidencias pendientes de la rúbrica. El README se mantiene como primer borrador, no como una certificación de evaluación.
