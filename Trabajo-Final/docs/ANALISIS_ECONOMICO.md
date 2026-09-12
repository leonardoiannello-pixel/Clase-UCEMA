# Análisis económico

Este análisis separa tres capas de costo que no deben mezclarse: el workflow determinístico local, la coordinación mediante el host de IA y el tiempo humano. Las tres corridas finales fueron ejecutadas realmente en Codex desktop y quedaron registradas en `corridas/`. El host no expuso de forma verificable los contadores de tokens ni el identificador exacto del modelo en la metadata de las corridas; por eso esos campos permanecen en `null` y no se reconstruyen retrospectivamente.

## 1. Evidencia económica observada

| Variable | Evidencia disponible | Tratamiento |
|---|---|---|
| Host de las corridas | Codex desktop | Verificado en los registros de las tres corridas |
| Modelo seleccionado | `GPT-6 Astra Light`, informado por el usuario como configuración visible en Codex desktop | Declaración del usuario; no se presenta como metadata capturada por el host |
| Input tokens | No expuestos | `null`; no se estiman |
| Cached input tokens | No expuestos | `null`; no se estiman |
| Output tokens | No expuestos | `null`; no se estiman |
| Pago adicional por las tres corridas | Ninguno | Costo marginal de caja observado: 0 |
| API paga | No utilizada | No se asigna tarifa API a corridas que no usaron API |
| Créditos/extends adicionales comprados | Ninguno | Se utilizaron únicamente extends incluidos/disponibles en la cuenta |
| Suscripción existente | No se imputa por corrida | Es un costo fijo preexistente y no hay una regla objetiva para asignarlo a este workflow |

Por lo tanto, el **costo marginal de caja efectivamente observado para ejecutar estas tres corridas fue 0**: no se compraron créditos adicionales ni se realizó una llamada paga a una API. Esto no significa que el sistema tenga costo económico total cero. La suscripción existente, el equipo, el tiempo humano, el desarrollo, el mantenimiento, la seguridad y eventuales excesos de uso son costos distintos y no se convierten artificialmente en cero.

La ausencia de tokens medidos es una limitación de evidencia, no una razón para inventarlos. El costo API teórico por token queda fuera del cálculo real de estas corridas porque no hubo una factura API asociada ni usage metadata verificable.

## 2. Workflow determinístico

Python y Node realizan localmente el cálculo salarial, generación y protección de Excel, controles de integridad, budgets y consolidación. La interfaz no llama a una API LLM para hacer los cálculos. En consecuencia, el salario final no depende de razonamiento numérico libre del modelo: el modelo coordina y la herramienta determinística es la fuente autoritativa para porcentajes, redondeos, caps, budgets y validaciones.

En el dataset DEMO el subprocess local tarda segundos por ejecución. No se transforma esa duración en un costo monetario porque no se midieron consumo de CPU, energía, amortización del equipo ni tarifa de infraestructura. El costo computacional local se considera pequeño para esta escala, pero no se presenta como importe medido.

## 3. Costo humano

El costo humano es probablemente más importante que el costo marginal del modelo en este caso. Incluye preparar y validar inputs, revisar propuestas, editar ajustes discrecionales, resolver excepciones, verificar destinatarios y aprobar el ciclo.

La Corrida 2 incorpora una intervención humana real: edición manual de `Discretionary Adjustment %` para A001. Sin embargo, no se cronometró esa intervención ni el resto de las tareas del usuario, por lo que no se asigna un costo horario ficticio.

Para una implementación operativa futura deberían registrarse minutos por rol y actividad, cantidad de excepciones y retrabajos, y una tasa interna autorizada. Sólo entonces sería válido comparar el proceso asistido contra un baseline manual y calcular ahorro, ROI o payback.

## 4. Proyección operativa

Este workflow corresponde a un proceso de Compensation por ciclo, no a una tarea que deba ejecutarse semanalmente. Para poder proyectar sin confundir observación con supuesto se usa el siguiente escenario de planificación:

- **1 ciclo salarial por año** como hipótesis de proyección, no como frecuencia observada del repositorio;
- por ciclo, una operación `generate` y al menos una operación `consolidate`;
- pueden existir reintentos cuando una devolución es rechazada, como ocurrió en Corrida 2;
- bajo el mismo esquema observado —uso de Codex desktop dentro de los límites incluidos y sin comprar créditos adicionales— el desembolso marginal de caja atribuible al host sería **0 por ciclo** y, por lo tanto, **0 por año**;
- esta proyección deja de ser válida si el volumen supera los límites incluidos, se compran créditos, se migra a una API paga o se incurre en infraestructura adicional.

No se presenta una cifra semanal artificial porque el proceso no tiene cadencia semanal. Si en producción se adoptara otra frecuencia, la proyección debe recalcularse con esa frecuencia real.

## 5. Elección del modelo

El principio de diseño es utilizar **el modelo más liviano que pueda coordinar la tarea de manera confiable**, porque el modelo no necesita resolver la matemática salarial. Sus funciones son interpretar la solicitud, elegir la operación (`verify`, `generate` o `consolidate`), invocar la herramienta, leer una salida estructurada, explicar excepciones y detenerse cuando se requiere intervención humana.

El usuario informa que las corridas se realizaron con la configuración **GPT-6 Astra Light** de Codex desktop. Esa elección es coherente con el principio anterior: una configuración `Light` resultó suficiente para coordinar tres ejecuciones reales, incluida una falla y su posterior reejecución con V4.1, mientras los controles críticos permanecieron en código determinístico.

No se afirma que `GPT-6 Astra Light` sea el mínimo absoluto posible porque no se hizo un benchmark controlado contra otros modelos. La conclusión respaldada por la evidencia es más acotada: **no fue necesario utilizar deliberadamente un modelo más pesado para que el workflow ejecutara y documentara correctamente estas corridas**.

## 6. Método para una medición futura con API o usage expuesto

Si el sistema se migrara a un entorno que expone uso facturable, cada llamada debería registrar modelo, timestamp, input tokens, cached input tokens, output tokens, retries y precio oficial aplicable en esa fecha. Para precios por millón de tokens:

`costo_llamada = (input_no_cacheado × precio_input + input_cacheado × precio_cached + output × precio_output) / 1.000.000`

Cuando el proveedor incluya cached tokens dentro de input total:

`input_no_cacheado = input_total - input_cacheado`

Luego:

`costo_corrida = suma(costo_llamada) + cargos_adicionales_verificados`

`proyeccion_anual = suma(costo_medido_por_tipo × frecuencia_anual_documentada_por_tipo)`

La fuente de precios, moneda, fecha y modalidad deben conservarse junto a la corrida. Hasta contar con esa evidencia, una estimación de tokens o tarifa puede presentarse únicamente como escenario hipotético, nunca como costo real medido.

## Conclusión económica

Para las tres corridas documentadas, el dato económico real disponible es simple: **no hubo desembolso incremental por uso del modelo**. La limitación es igualmente clara: el host no expuso tokens ni usage metadata, por lo que no existe un costo por token verificable de estas corridas. El diseño reduce la necesidad de un modelo pesado al delegar la lógica salarial a herramientas determinísticas, pero el beneficio económico total del sistema sólo podría demostrarse midiendo tiempo humano, retrabajo y costos operativos contra un proceso manual comparable.