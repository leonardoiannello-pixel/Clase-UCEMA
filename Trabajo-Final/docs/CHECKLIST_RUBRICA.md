# Checklist de rúbrica

Mapeo según las cinco dimensiones y ponderaciones indicadas para este trabajo. **No se autoasigna puntaje ni se afirma cumplimiento académico total.** Las ponderaciones son las de la consigna, no resultados obtenidos.

| Dimensión / ponderación | Evidencia existente | Limitación o pendiente | Ubicación de evaluación |
|---|---|---|---|
| Sistema completo y funcionando — 30 | Contrato de agente, prompts finales, interfaz local, herramienta real, salida estructurada, supervisión L2 y tres ejecuciones reales en Codex desktop. `generate` usa V4; `consolidate` usa V4.1 después de una falla real documentada. | Los datos publicados son sintéticos por confidencialidad. La aprobación final sigue fuera del motor. | [README](../README.md), [CLI](../agente/cli.py), [contrato](../agente/contrato_herramienta.json), [corridas](../corridas/README.md), [validación](VALIDACION_TECNICA.md) |
| Proceso documentado — 25 | Evolución V1–V4, Corrida 2 rechazada por falso positivo real de Excel, corrección V4.1 acotada y Corrida 3 exitosa con los mismos reviewed. La decisión humana de A001 queda separada de las decisiones del agente. El recorte de bonus y la decisión de usar datos públicos sintéticos están documentados. | Revisión académica final del relato y simplificación editorial si fuera necesaria. | [DECISIONES](../DECISIONES.md), [corrida_01](../corridas/corrida_01/registro.json), [corrida_02](../corridas/corrida_02/registro.json), [corrida_03](../corridas/corrida_03/registro.json) |
| Formato y reproducibilidad — 15 | Prompts, corridas con fecha/evidencia/hashes, CLI, catálogos, logs, outputs y tests. Una tercera parte puede reconstruir las operaciones con el repositorio completo. | Para la entrega final debe promoverse el contenido de `Trabajo-Final/` a la raíz de un repositorio público limpio para cumplir literalmente la estructura exigida. El paquete actual todavía referencia archivos hermanos de V4. | [REPRODUCCION](REPRODUCCION.md), [inputs](../inputs/README.md), [referencias V4](../agente/v4_referencias.json), [referencias V4.1](../agente/v41_referencias.json) |
| Análisis económico — 15 | Auditoría posterior recuperó modelo verificable `gpt-6-astra` con effort `low` y tokens reales para los turnos completos de las tres corridas: input/cached/output/total por corrida. No hubo desembolso adicional; se usaron extends incluidos. Se separan costo marginal, suscripción fija, costo humano y proyección semanal/anual. | Los tokens corresponden al turno completo de Codex, no sólo al subprocess salarial. No existe una partición verificable más fina. No se midieron minutos humanos ni ROI. | [ANALISIS_ECONOMICO](ANALISIS_ECONOMICO.md), [auditoría de metadata](METADATA_USO_CODEX.md), `usage_metadata.json` de cada corrida |
| Gobierno y riesgo — 15 | L2, responsabilidades por rol, matriz de detección/respuesta/continuidad/intervención, rechazo ante alteraciones, custodia de originales, límites explícitos de protección Excel y aprobación humana pendiente. | Identidad/ACL/cifrado/distribución segura serían requisitos de producción; no se presentan como implementados. | [SUPERVISION](SUPERVISION.md), [GOBIERNO_Y_RIESGO](GOBIERNO_Y_RIESGO.md), [system prompt](../prompts/system_prompt.md) |

## Comprobaciones para cierre de la entrega

- [x] Contrato final con las seis piezas trabajadas en clase.
- [x] Herramienta real basada en archivos/Excel y salida estructurada.
- [x] Interfaz local con separación entre coordinación del agente y cálculo determinístico.
- [x] Supervisión L2 y autoridad final humana.
- [x] Corrida 1 real: generación con excepciones de negocio.
- [x] Corrida 2 real: consolidación rechazada por una incompatibilidad de serialización de Excel.
- [x] Falla preservada y documentada sin reescribir la historia.
- [x] Corrección V4.1 mínima y auditable con regresiones.
- [x] Corrida 3 real sobre los mismos reviewed: consolidación exitosa con excepciones reportadas.
- [x] Intervención humana real en A001 preservada y separada de la decisión del agente.
- [x] Modelo y tokens por corrida recuperados de metadata verificable del host, con alcance y limitaciones documentados.
- [x] Análisis económico actualizado sin inventar precio API ni costos no observados.
- [x] Preservación de V1–V4 y de outputs históricos.
- [ ] Revisión final con el evaluador del Grupo 23.
- [ ] Ajustes editoriales finales de README/DECISIONES si el evaluador detecta gaps.
- [ ] Crear repositorio público final con la estructura obligatoria en la raíz y dependencias necesarias autocontenidas.
- [ ] Validar ese repositorio final antes de entregar el link.

La utilización de datos sintéticos en lugar de entradas laborales reales se declara como una desviación consciente de la consigna motivada por confidencialidad y por el requisito de repositorio público. No se presenta como si cumpliera literalmente ese punto.
