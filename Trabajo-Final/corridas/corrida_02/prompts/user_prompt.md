# Corrida 2 — solicitud operativa usada en esta sesión

Ejecutá y documentá únicamente `consolidate` mediante `Trabajo-Final/agente/cli.py`, sobre la rama `leonardo/final-academic-package`, con datos sintéticos. Usá como original confiable `Trabajo-Final/corridas/corrida_01/ejecucion/artifacts` y como reviewed `Trabajo-Final/ejecuciones/corrida_02_devoluciones_20260912T221754742175Z`. La salida debe estar en un directorio nuevo bajo `Trabajo-Final/ejecuciones/`.

El usuario declara que hubo una intervención humana real, manual en Excel fuera del agente: `team_L-A.xlsx`, Employee_ID `A001`, campo `Discretionary Adjustment %`, +1,00 punto porcentual. Los demás archivos no recibieron ajustes manuales. Observá y registrá el valor del archivo; no lo edites, normalices ni reemplaces. El agente no decidió el ajuste. No atribuyas el reviewer_id sintético a una identidad real.

Archivá bajo `Trabajo-Final/corridas/corrida_02/` fechas, host, prompts y hashes, referencias y hashes del original, copias exactas y hashes de los cuatro reviewed, intervención declarada y valor observado, invocaciones, reporte, stdout/stderr, outputs, budgets, excepciones, salida estructurada del agente y observaciones. Registrá sólo resultados efectivos. Actualizá registro.json solamente tras ejecutar realmente la operación.

Validá que Proposed se conserve, que el ajuste sólo impacte Final, que Final Salary y Final Compa Ratio reflejen la intervención y que los budgets se recalculen. Los excesos se informan sin corrección automática. La aprobación debe seguir PENDING_HUMAN_APPROVAL. Comprobá campos protegidos, preservación de la edición, procedencia sintética y ausencia de contraseñas en evidencia.

Modelo exacto, input tokens, cached input tokens, output tokens y usage metadata sólo se registran si el host los expone de manera verificable; de lo contrario null y explicación. No estimar costos. Separá la salida del agente del reporte determinístico del CLI.

No modificar V1–V4, corrida_01 ni corrida_03. Ejecutar tests de lectura/consistencia, hacer un commit separado, push a la misma rama y actualizar PR #5. No mergear. Informar commit, estado real, ajuste y Final Salary de A001, budget Alpha, excepciones, host/modelo/métricas y archivos creados.

Este archivo es la formulación operativa específica preparada y leída por el agente a partir del pedido del usuario; no se presenta como exportación literal del mensaje ni como un nuevo mensaje de API.
