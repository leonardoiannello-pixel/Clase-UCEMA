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

El host Codex desktop no expuso de manera verificable contadores de input/cached/output tokens ni el identificador exacto del modelo dentro de la metadata de las corridas. Esos campos permanecen en `null`: no se sustituyen con estimaciones presentadas como medición. La configuración visible informada por el usuario se documenta por separado en el [análisis económico](../docs/ANALISIS_ECONOMICO.md).

Las contraseñas de protección no se versionan. La intervención humana de Corrida 2/3 se conserva como una edición manual de Excel fuera del agente; el `reviewer_id` sintético no se utiliza como identidad o autenticación.
