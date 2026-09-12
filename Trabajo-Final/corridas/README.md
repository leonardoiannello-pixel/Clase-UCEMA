# Registro de corridas

`corrida_01`, `corrida_02` y `corrida_03` son las **tres ejecuciones finales reales del sistema**. Cada carpeta conserva fecha, prompts usados, inputs y hashes, invocaciones de herramientas, outputs o rechazo, excepciones y observaciones suficientes para reconstruir qué ocurrió. Los datos salariales publicados son sintéticos; la ejecución del sistema sí fue real.

- **Corrida 1 — generación:** `GENERATED_WITH_EXCEPTIONS`. Generó master, archivos por equipo y Leadership; reportó Market faltante para B004 y budget protegido insuficiente en Gamma.
- **Corrida 2 — consolidación con intervención humana:** `REJECTED`. El archivo `team_L-A.xlsx` contenía un ajuste humano real de +1,00 pp para A001. Microsoft Excel reserializó 13 fórmulas protegidas de forma textualmente distinta pero semánticamente equivalente y V4 las rechazó. La falla quedó preservada.
- **Corrida 3 — misma devolución, V4.1:** `CONSOLIDATED_WITH_EXCEPTIONS`. Reutilizó exactamente los mismos cuatro reviewed de Corrida 2, verificados por SHA256. V4.1 eliminó sólo el falso positivo de representación, generó `consolidated_final.xlsx` y mantuvo las excepciones reales de budget y Market.

La carpeta `demo_sintetica/` contiene evidencia técnica histórica de V4 y **no cuenta como una de las tres corridas finales**. En el repositorio académico final se moverá fuera de `corridas/` para que esta carpeta contenga únicamente las tres ejecuciones exigidas por la consigna.

## Evidencia conservada

Cada corrida registra, según corresponda:

1. fecha/hora UTC y host utilizado;
2. copias o referencias exactas de los prompts efectivamente usados y sus hashes;
3. inputs, archivos reviewed y SHA256;
4. invocaciones reales de herramientas, stdout/stderr y `reporte.json`;
5. outputs generados o rechazo observado, con hashes;
6. excepciones, budgets e intervención humana efectivamente realizada;
7. estado de aprobación, siempre `PENDING_HUMAN_APPROVAL`;
8. metadata económica disponible.

## Metadata de modelo y tokens

En el momento de cada ejecución el host no expuso estas métricas en la salida de la tarea, por lo que los `registro.json` originales conservaron esos campos en `null`. Posteriormente se realizó una auditoría de la metadata local de Codex, **sin reejecutar ninguna corrida**, y se recuperaron métricas verificables para los turnos completos asociados a cada ejecución.

Cada carpeta contiene ahora un `usage_metadata.json` con la evidencia posterior:

- Corrida 1: `gpt-6-astra`, effort `low`, 3.874.830 input, 3.833.728 cached input, 19.644 output, 3.894.474 total.
- Corrida 2: `gpt-6-astra`, effort `low`, 1.265.275 input, 1.221.632 cached input, 13.851 output, 1.279.126 total.
- Corrida 3: `gpt-6-astra`, effort `low`, 1.622.409 input, 1.600.128 cached input, 9.627 output, 1.632.036 total.

Estas cifras corresponden al **turno completo de Codex** y no exclusivamente al subprocess `generate`/`consolidate`. Incluyen contexto, coordinación, herramientas, validación, documentación y publicación. La metodología y fuente se explican en [METADATA_USO_CODEX.md](../docs/METADATA_USO_CODEX.md) y en el [análisis económico](../docs/ANALISIS_ECONOMICO.md).

Las contraseñas de protección no se versionan. La intervención humana de Corrida 2/3 se conserva como una edición manual de Excel fuera del agente; el `reviewer_id` sintético no se utiliza como identidad o autenticación.
