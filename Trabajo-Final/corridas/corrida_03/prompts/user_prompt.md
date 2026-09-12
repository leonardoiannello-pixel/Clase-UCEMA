# Corrida 3 — solicitud operativa usada en esta sesión

Ejecutá realmente `consolidate` mediante `Trabajo-Final/agente/cli.py` en la rama `leonardo/final-academic-package`, con la corrección V4.1 existente y validada. Usá los mismos originales confiables de Corrida 1 y exactamente los mismos cuatro reviewed utilizados en Corrida 2, en `Trabajo-Final/ejecuciones/corrida_02_devoluciones_20260912T221754742175Z`. Confirmá igualdad de bytes y hashes antes de invocar. Preservá el ajuste humano existente de A001, +1,00 pp; no edites ni normalices archivos humanos.

Usá un directorio nuevo bajo `Trabajo-Final/ejecuciones/` y archivá toda la evidencia en `Trabajo-Final/corridas/corrida_03/`: fecha, host, prompts y hashes, originales y reviewed con hashes, ajuste observado, workflow_version, invocación, reporte, stdout/stderr, consolidated_final.xlsx si se genera, validation_exceptions.json, budgets, excepciones, Final Salary/Increase/Compa Ratio de A001, respuesta estructurada del agente y aprobación.

Registrá hechos observados, sin hardcodear resultados. Comprobá que los 13 falsos positivos de comillas no bloqueen, que Proposed permanezca intacto y que el ajuste sólo afecte Final; los excesos deben informarse sin corregirse automáticamente y la aprobación seguir PENDING_HUMAN_APPROVAL. Verificá reviewed intactos y ausencia de contraseña en evidencia. Los datos salariales siguen siendo sintéticos. No atribuyas una identidad real al reviewer_id sintético ni al agente la decisión humana ya existente.

No desarrollar funcionalidades ni modificar V1–V4, V4.1 o Corridas 1 y 2. Si surge una causa nueva de fallo, documentarla y detener la ejecución sin corregir código automáticamente. Ejecutar sólo tests necesarios de lectura/consistencia de esta corrida. Modelo/tokens/usage sólo si el host los expone verificablemente; en otro caso null. No estimar costos.

Actualizar registro.json con lo ocurrido, hacer un commit separado y push a la misma rama, actualizar PR #5. No mergear. Respuesta final sólo con commit, estado, workflow_version, ajuste/Final Salary de A001, estado Alpha, excepciones, existencia de consolidado y disponibilidad de modelo/tokens.

Formulación operativa preparada y leída a partir del pedido del usuario; no es exportación literal de un mensaje API. El system prompt del paquete se usa como instrucciones de tarea en la conversación existente, sin sustituir las instrucciones del host.
