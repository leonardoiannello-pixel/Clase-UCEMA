# Decisiones y evolución del proyecto

Reconstrucción basada en prompts, observaciones y artefactos conservados. No se atribuyen a un descubrimiento autónomo de la IA las instrucciones o correcciones solicitadas por revisión humana. Las observaciones históricas describen lo ocurrido en su momento; no se reescriben retrospectivamente para hacer parecer que una versión anterior ya contenía decisiones posteriores.

## Decisiones de alcance

### De salary review + bonus a salary review

**Idea inicial:** modelar un proceso más amplio de Compensation que incluyera revisión salarial y bono anual.

**Decisión:** acotar el sistema al salary review de población fuera de convenio. El bonus quedó fuera de alcance.

**Motivo:** el ciclo salarial ya contenía suficiente complejidad para probar contrato, herramientas, reglas, budget, mercado, revisión humana, protección, consolidación y supervisión. Incorporar bonus aumentaba superficie de error sin mejorar la demostración central del sistema agéntico.

### Caso real, datos públicos sintéticos

**Caso:** el workflow resuelve una tarea real y recurrente de Compensation: preparar, distribuir, revisar y consolidar propuestas salariales bajo reglas y presupuestos.

**Restricción:** la consigna final pide corridas con entradas reales, pero también exige entregar un repositorio público. Los salarios individuales y referencias de mercado de un ciclo laboral real son información confidencial/proprietaria y no se contaba con autorización para publicarlos.

**Decisión:** ejecutar el sistema de verdad sobre una muestra salarial completamente sintética, diseñada para representar el proceso y casos límite reales sin publicar información confidencial. No se presenta esta decisión como cumplimiento literal del requisito de “entradas reales”; se documenta como una desviación consciente de gobierno y confidencialidad.

**Efecto:** las tres corridas finales son ejecuciones reales y reconstruibles del sistema, incluida una intervención humana manual real, pero los valores salariales y de mercado publicados son sintéticos.

## Evolución técnica y del contrato

| Etapa | Problema / necesidad | Decisión registrada | Efecto verificable y procedencia |
|---|---|---|---|
| V1 | Preparar revisión de empleados fuera de convenio con budget por equipo | Componentes aditivos sobre junio; General/Promotion/Progression protegidos; X por equipo; líderes excluidos | Primera propuesta para 15 empleados. Gamma ya presentaba insuficiencia de 522.000. [Prompt V1](../Entrega-2/prompts/system_prompt_v1.md), [observaciones V1](../Entrega-2/runs/run_1_v1/run_1_observations.md) |
| V1: problemas observados | Mercado calculado antes del mérito y sin cap; centavos y demasiados decimales; flags y disponible negativo en Gamma | Se documentaron hallazgos sin corregir ni reescribir esa corrida | A003/B003 podían recibir Market innecesario aun con gap cerrado por mérito. [Observaciones V1](../Entrega-2/runs/run_1_v1/run_1_observations.md) |
| V2: posición destino | Ambigüedad de `Market_Job_Code` | Interpretarlo como posición destino/post-ciclo, sin editar los inputs originales | Referencia correspondiente a New Rank/New Grade para decisiones. [Prompt V2](../Entrega-2/prompts/system_prompt_v2.md) |
| V2: mérito y cap | Merit podía cerrar el gap antes del componente Market | Evaluar mercado después del mérito y limitarlo al gap individual | A003/B003 dejan de recibir Market. Pueden superar compa 1 por mérito, permitido. Se redistribuye budget mediante X. [Observaciones V2](../Entrega-2/runs/run_2_v2/run_2_observations.md) |
| V3: redondeo | Precisión técnica de V2 poco utilizable | Salarios a ARS 100, porcentajes hasta dos decimales, compa-ratios con tres decimales visibles | Importes sin centavos y porcentajes auditables. [Prompt V3](../Entrega-2/prompts/system_prompt_v3.md) |
| V3: budget redondeado | X redondeado podía superar el máximo | Recalcular salarios/payroll y reducir X por 0,01 pp si fuera necesario | Beta: X 4,32%, payroll 10.736.500, remanente 1.500. Gamma conserva insuficiencia. [Observaciones V3](../Entrega-2/runs/run_3_v3/run_3_observations.md) |
| V4: de cálculo a workflow | Faltaba revisión acotada por líderes y recuperación de devoluciones | Generar propuesta preservada y archivos por revisor; editar sólo `Discretionary Adjustment %` | Ajuste separado de la propuesta y controles de piso/límites. [Notas V4](../Entrega-2/v4/V4_IMPLEMENTATION_NOTES.md) |
| V4: implementación | No existía motor Python de V3 en el repositorio | Implementar especificación determinística y contrastar todos los campos históricos | Regresión contra tres Excel V3; no reescritura de V3. [Tests V4](../Entrega-2/v4/tests/test_workflow.py) |
| V4: Leadership | Líderes no deben decidir su propio salario | Pool separado usando mapping existente y `Leadership_Budget_Pct` independiente | Tres líderes separados de los archivos de equipo; 20% sólo DEMO. [Parameters V4](../Entrega-2/v4/inputs/Parameters.xlsx) |
| V4: protección y budget dinámico | Evitar edición accidental y observar impacto sin ejecutar Python | Bloquear hojas/workbook, desbloquear sólo ajuste; fórmulas de salarios y presupuesto | Edición válida puede mostrar EXCEEDED; protección no implica cifrado. [Renderer](../Entrega-2/v4/render.mjs), [protección](../Entrega-2/v4/protection.py) |
| V4: consolidación | No confiar en fórmulas/valores devueltos | Comparar campos protegidos con manifest y recalcular en Python | Rechazo de manipulación; propuesta y decisión humana separadas. [Workflow](../Entrega-2/v4/workflow.py) |
| V4: aprobación | Cálculo válido no acredita autoridad para aprobar | Dejar `PENDING_HUMAN_APPROVAL` y resolver decisión fuera del motor | No hay salarios aprobados automáticamente. [Log DEMO](../Entrega-2/v4/demo/consolidated/validation_exceptions.json) |
| Revisión humana PR #4: nombres | `Final_Compa_Ratio` conservaba propuesta y `Human_Final_Compa_Ratio` la etapa final | Renombrar propuesta como Proposed Compa Ratio y usar Final para el resultado humano | Columnas de consolidación inequívocas. [Commit](https://github.com/leonardoiannello-pixel/Clase-UCEMA/commit/1bf9617ac5172a10297b02884bf11ff855d9ce65) |
| Revisión humana PR #4: Parameters | Se hasheaban inputs históricos, no el Parameters V4 específico | Registrar path, SHA256 y parámetros parseados utilizados | Test con Parameters alternativo. |
| Revisión humana PR #4: Market redondeado | Un flag no hacía cumplir el cap para referencias no múltiplo de 100 | Reducir sólo Market por 0,01 pp; excepción si el piso impide cumplir | Caso 110.075 produce salario 110.000; Merit/protegidos no cambian. |
| Revisión humana PR #4: budgets | Faltaba validar tipo, finitud y rango | Team/Leadership budgets numéricos, finitos y > -100% | Rechazo explícito y suite V4 de 20 tests. |
| Paquete académico | El evaluador necesita contrato, evidencia y reproducción accesibles | Crear `Trabajo-Final/` con prompts finales, interfaz, documentación, corridas y catálogos | V1–V4 y sus outputs históricos permanecen preservados. Base: merge `2c55ad6fb9862203d534892e55087c4016479661`. |
| Preparación de corridas | Antes de ejecutar no había evidencia final instrumentada | Crear plantillas explícitamente pendientes, sin convertir demos/tests en corridas inexistentes | Estado histórico preservado en commits previos; luego se ejecutaron las tres corridas finales. |

## Tres corridas finales y la falla que produjo V4.1

### Corrida 1 — generación

Se ejecutó `generate` realmente en Codex desktop. Estado: `GENERATED_WITH_EXCEPTIONS`. Se generaron master, tres archivos de equipo y Leadership. Se reportaron `MARKET_DATA_MISSING` para B004 y `BUDGET_INSUFICIENTE` en Gamma. No se simuló revisión humana ni consolidación. Evidencia en [corrida_01](corridas/corrida_01/registro.json).

### Corrida 2 — intervención humana y rechazo

Un humano editó manualmente `team_L-A.xlsx` en Microsoft Excel y agregó +1,00 pp de `Discretionary Adjustment %` a A001. La consolidación real con V4 fue rechazada porque Excel reserializó 13 fórmulas protegidas eliminando comillas opcionales (`'Detail'!` → `Detail!`; `'Summary'!` → `Summary!`). V4 comparaba texto literal y produjo `PROTECTED_FIELD_CHANGED` aunque no se observó cambio semántico. La corrida rechazada se preservó sin reescritura. Evidencia en [corrida_02](corridas/corrida_02/registro.json).

### V4.1 — corrección mínima

**Problema:** comparación textual demasiado estricta frente a serialización real de Excel.

**Decisión:** introducir [V4.1](agente/v41/README.md), derivada de V4, normalizando únicamente las comillas opcionales de los calificadores conocidos `Detail` y `Summary`. No se ignoran cambios de dirección, operador, constante, hoja, strings, referencias externas ni otras diferencias semánticas. `PROTECTED_FIELD_CHANGED` permanece activo.

**Validación:** tests específicos prueban equivalencia de representación y rechazo de cambios semánticos. La V4 histórica no fue modificada.

### Corrida 3 — mismo input humano, V4.1

Se ejecutó nuevamente `consolidate` utilizando **exactamente los mismos cuatro archivos reviewed de Corrida 2**, verificados por SHA256. V4.1 terminó `CONSOLIDATED_WITH_EXCEPTIONS`, generó `consolidated_final.xlsx`, preservó Proposed y aplicó el +1,00 pp humano sólo a Final. A001 pasó de Proposed Salary ARS 1.923.600 a Final Salary ARS 1.937.600. Team Alpha quedó `EXCEEDED` por ARS 14.000 y Gamma por ARS 522.000; el sistema reportó ambos excesos sin corregirlos automáticamente. Evidencia en [corrida_03](corridas/corrida_03/registro.json).

## Decisiones y limitaciones que permanecen abiertas

- Ratificar parámetros DEMO y política Leadership antes de cualquier uso productivo.
- Formalizar identidad, autoridad y registro de aprobación final.
- Implementar ACL, cifrado, almacenamiento y distribución segura antes de procesar información salarial real.
- Medir tiempo humano y baseline manual si se quisiera demostrar ahorro/ROI.
- Los tokens de las corridas permanecen no medidos porque Codex desktop no los expuso de forma verificable; no se reconstruyen retrospectivamente como hechos.
- El modelo visible informado por el usuario fue `GPT-6 Astra Light`; esa identificación no aparece como metadata verificable del host dentro de las corridas.
- Para la entrega final, promover el contenido a la raíz de un repositorio público autocontenido y eliminar dependencias de rutas hermanas.

Las definiciones L0–L4 del [documento de supervisión](docs/SUPERVISION.md) son operativas para este trabajo. L2 describe la distribución efectiva de responsabilidades; no se atribuye una definición textual a material docente no adjuntado.
