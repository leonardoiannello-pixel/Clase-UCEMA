# V4 — notas de implementación

## Alcance y preservación

V4 agrega revisión humana, Excel protegidos, controles de budget y consolidación trazable. Todo lo agregado vive bajo `Entrega-2/v4/`. Baseline: commit `443943fd3f9e9cb99664006efdd6bf7d1fe3bc63` de `main`.

V1, V2 y V3 no se modifican: se conservan sus prompts, inputs, runs, observaciones y Excel históricos. No se modifica ningún README. Todos los datos del ejemplo son sintéticos. No se incorporan bonus, HRIS, emails ni Power BI. No se hace merge a main.

El repositorio original **no contiene código ejecutable del motor V3**. `engine.py` implementa las reglas de `prompts/system_prompt_v3.md` y se contrasta con cada campo del detalle de los 15 empleados de los tres Excel históricos. Esto es una implementación reproducible de la especificación, no una modificación de la baseline.

## Archivos agregados

| Archivo | Propósito |
|---|---|
| `engine.py` | Componentes V3, bandas, cap, búsqueda de X, redondeo y validación del ajuste humano |
| `workflow.py` | Lectura, mapping, generación, comparación de campos protegidos, consolidación y logs |
| `render.mjs` | Excel con fórmulas y formatos, usando `@oai/artifact-tool` |
| `protection.py` | Protección de hojas/workbook y validación de datos mediante OOXML |
| `inputs/Parameters.xlsx` | Copia V4 de parámetros originales más tres parámetros DEMO |
| `requirements.txt` | Dependencia Python de lectura de Excel |
| `tests/test_workflow.py`, `tests/recalculate.mjs` | Pruebas de cálculo, workflow y recálculo de fórmulas exportadas |
| `demo/generated/` | Master, tres archivos de equipos, Leadership, manifest y log inicial |
| `demo/consolidated/` | Consolidación sintética sin ajustes, pendiente de aprobación |
| `demo/test_results.txt` | Resultado de la suite |
| `.gitignore` | Exclusión de cachés y dependencias locales |

Los archivos `.inspect.ndjson`, si existen localmente, son auxiliares del renderer y no se versionan.

## Reglas y decisiones técnicas

- Salario base junio; aumentos aditivos; General, Promotion y Progression protegidos; mérito excluido para promociones/progresiones; mercado contra posición destino y después del mérito.
- X se busca por intervalos de bandas de mercado. El payroll puede caer al cruzar una banda, por lo que una búsqueda binaria global no es válida. Dentro de cada intervalo se usa búsqueda binaria reproducible, luego el redondeo y reducción de X en pasos de 0,01 puntos porcentuales exigidos por V3.
- Importes se calculan con `Decimal`; salarios se redondean al múltiplo de ARS 100 más cercano, empate hacia arriba. Tasas se almacenan como fracciones con cuatro decimales (dos decimales porcentuales); compa-ratios se muestran con tres decimales.
- El salario propuesto y el porcentaje efectivo propuesto se conservan por separado. La etapa humana aplica exactamente `ROUND(Proposed Increase % + Discretionary Adjustment %,4)` y `ROUND(June Salary*(1+Final Increase %),-2)`.
- El floor verifica tanto el porcentaje protegido como el salario protegido redondeado según V3. No se recortan ni compensan componentes protegidos. Un valor inválido se rechaza al consolidar; no se sustituye silenciosamente por otro.
- Excel aplica validación de datos a R y fórmulas defensivas: si pegar datos evita la validación, los importes finales muestran error y Budget Status pasa a `INVALID`. El exceso de budget por un ajuste válido sí está permitido y muestra `EXCEEDED`.
- `Discretionary Adjustment Amount` = payroll final menos payroll propuesto, incluyendo efecto del redondeo. `Budget Utilization %` = payroll final / máximo payroll. `Budget Remaining` conserva el signo negativo cuando hay exceso.
- El input original ya tiene `Leader_Employee_ID`; no se cambia su esquema. Cada equipo tiene un líder y los tres líderes apuntan a `CEO001`, identificador sintético del nivel superior. Leadership usa las mismas reglas de cálculo como pool independiente y su propio budget configurable. Nunca se mezcla con payroll de equipos.
- Se exige mapping no vacío, sin auto-revisión y un único revisor por pool. Si aparece más de un revisor dentro de un mismo budget, se detiene para definir la asignación; no se divide el budget arbitrariamente.
- Un grupo factible sin peso de mérito puede no tener máximo X finito una vez saturado mercado: se informa `X_UNBOUNDED` y se requiere una decisión, en vez de inventar una cota. No ocurre con los datos actuales.

## Parámetros configurables

En `v4/inputs/Parameters.xlsx`, hoja `Global_Parameters`:

| Parámetro | Valor DEMO sintético | Estado |
|---|---:|---|
| `Discretionary_Min_Pct` | -5,00% | Configurable, requiere definición de negocio |
| `Discretionary_Max_Pct` | +5,00% | Configurable, requiere definición de negocio |
| `Leadership_Budget_Pct` | 20,00% | Independiente de los equipos, requiere aprobación de negocio |

Estos valores sólo permiten ejecutar la demostración y no constituyen recomendaciones. Los parámetros originales se copian sin cambiar sus valores; los tres inputs históricos permanecen intactos. La contraseña llega por `SALARY_REVIEW_PASSWORD` o `--password`. La demostración y los tests usan únicamente `DEMO-only`, sin secretos reales.

## Ejecución reproducible

Se requiere Python 3.11 o superior con `openpyxl` y Node con `@oai/artifact-tool` disponible. En Codex Desktop, usar `load_workspace_dependencies` para resolver los ejecutables y crear una junction Windows o symlink `node_modules` hacia las dependencias del runtime en un directorio ancestro de `v4/`. No se versionan dependencias ni rutas absolutas del equipo.

Desde `Entrega-2/v4/`, con los ejecutables disponibles en PATH:

```powershell
$env:SALARY_REVIEW_PASSWORD = 'DEMO-only'
# Opcional: SALARY_NODE contiene la ruta al ejecutable Node del runtime.
python workflow.py generate --output nueva_corrida/generated
# Entregar solamente team_L-A.xlsx, team_L-B.xlsx, team_L-C.xlsx a cada revisor.
# Entregar leadership_review.xlsx exclusivamente al nivel superior.
# Guardar los cuatro archivos recibidos en nueva_corrida/reviewed.
python workflow.py consolidate --original nueva_corrida/generated --reviewed nueva_corrida/reviewed --output nueva_corrida/consolidated
python -m unittest discover -s tests -v
```

`--parameters` permite seleccionar otro Parameters de V4. La generación y consolidación requieren directorios de salida vacíos para no sobrescribir evidencia de otro ciclo. `SALARY_PREVIEW_DIR` habilita PNGs de inspección fuera de los entregables.

El runtime JS es necesario para generar Excel y para la prueba independiente de fórmulas. `openpyxl` sólo lee archivos: la autoría se hace con Artifact Tool. Su API consultada no ofrece protección de hojas/celdas; `protection.py` agrega esa capacidad puntual al ZIP OOXML, conservando fórmulas y valores calculados.

## Protección, integridad y aprobación

La protección Excel previene modificaciones accidentales y controla qué celdas se editan. **No cifra el archivo, no pide contraseña de apertura y no reemplaza controles de acceso ni encryption real.** Una persona con acceso al archivo puede quitarla.

Sólo las celdas de Discretionary Adjustment % están desbloqueadas en archivos de revisión. En el master y consolidado todo queda bloqueado. El resto de la hoja, incluyendo Summary, fórmulas y parámetros, queda protegido.

El coordinador conserva `master_proposal.xlsx` y `manifest.json` en una ubicación confiable, fuera de las carpetas distribuidas. El manifest guarda la propuesta, fórmulas y campos esperados, hashes de fuentes y hash del master. **No es una firma digital**: un atacante que también pueda editar el manifest confiable queda fuera de esta protección. Se requieren permisos de almacenamiento y distribución en un uso real.

La consolidación compara todos los valores y fórmulas no editables con esa copia confiable, detecta archivos ausentes/extra, hojas distintas y valores discrecionales inválidos. No confía en valores cacheados de fórmulas editadas: recalcula en Python. Ante una alteración se emite `validation_exceptions.json` con estado `REJECTED` y no se crea un consolidado final. Cambios puramente visuales no se consideran decisiones salariales. Se registran hashes de archivos recibidos, revisor asignado, ajustes, indicadores de modificación humana y excesos.

La consolidación válida se entrega como `PENDING_HUMAN_APPROVAL`, incluso si todos los budgets están OK. La aprobación final es una intervención del responsable autorizado fuera de este motor; no se inventan su identidad, facultades ni una aprobación automática. La carpeta DEMO contiene ajustes en cero y no representa una revisión efectuada por personas. El revisor asignado es trazabilidad de routing, no identidad autenticada de quien editó el archivo.

## Validación y resultados

La suite incluye 15 pruebas: regresión de todos los campos históricos, exclusión y mapping de líderes, protección de todas las hojas, única columna editable, floor, límites/precisión/tipos, bandas/cap/mercado faltante, Gamma insuficiente, redondeo ARS 100, consolidación y conservación de la propuesta, manipulación de salarios y fórmulas, archivos faltantes, pegado inválido, ajuste cero y recálculo real de fórmulas exportadas con Artifact Tool.

| Pool | X | Payroll propuesto y final DEMO | Máximo | Remanente | Estado |
|---|---:|---:|---:|---:|---|
| Team Alpha | 11,76% | 11.520.000 | 11.520.000 | 0 | OK |
| Team Beta | 4,32% | 10.736.500 | 10.738.000 | 1.500 | OK |
| Team Gamma | 0,00% | 9.322.000 | 8.800.000 | -522.000 | EXCEEDED |
| Leadership | 4,43% | 14.038.500 | 14.040.000 | 1.500 | OK |

Se procesan 15 empleados y 3 líderes separados. En el test A001 recibe +1 punto porcentual: el salario pasa de 1.923.600 a 1.937.600 y Alpha muestra EXCEEDED por 14.000. El Excel recalcula esto sin Python. Se inspeccionan fórmulas sin errores en las salidas DEMO y previews de hojas representativas. No se ejecutó Microsoft Excel de escritorio: la prueba de recálculo utiliza Artifact Tool y lectura independiente del XLSX exportado.

## Pendientes y límites explícitos

1. Ratificar los tres parámetros DEMO y la política de propuesta del pool Leadership; no se asume igualdad con presupuestos de equipos.
2. Definir aprobación final, identidad autenticada, permisos, entrega/recepción y eventual registro de firma. No se automatiza esa aprobación en esta entrega.
3. Resolver reglas para varios revisores por pool y X sin máximo finito antes de incorporar esos casos.
4. Con otros salarios, recalcular un porcentaje efectivo de dos decimales puede cambiar el salario aun con ajuste cero. V4 respeta la fórmula solicitada y registra `PROPOSAL_RATE_ROUNDTRIP_REVIEW_REQUIRED`; no altera V3. No ocurre en los 18 registros actuales.
5. Una referencia de mercado no múltiplo de ARS 100 podría entrar en tensión con el redondeo del salario. Se informa `MARKET_SALARY_ROUNDING_REVIEW_REQUIRED` sin cambiar silenciosamente las reglas V3. No ocurre en la muestra.
6. Validar usabilidad y recálculo en la versión de Excel del destinatario antes de un ciclo real. No hay cifrado, HRIS ni envío automático.

Desviaciones respecto del pedido: V3 sólo existía como especificación y evidencia, por lo que hubo que implementar su motor; no fue posible importar un motor Python preexistente. La aprobación permanece humana y pendiente, sin ejecutar una decisión de negocio. La protección usa una extensión OOXML por falta de esa capacidad en el renderer. Ninguna de estas decisiones modifica la historia V1–V3.
