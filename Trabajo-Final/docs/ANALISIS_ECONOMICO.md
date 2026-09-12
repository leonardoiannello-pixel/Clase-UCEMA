# Análisis económico

Este análisis separa tres capas de costo que no deben mezclarse: el workflow determinístico local, la coordinación mediante el host de IA y el tiempo humano. Las tres corridas finales fueron ejecutadas realmente en Codex desktop y quedaron registradas en `corridas/`.

Después de completar las corridas se auditó la metadata local de Codex **sin reejecutar el agente**. Esa auditoría permitió recuperar modelo y tokens verificables para los turnos completos asociados a Corrida 1, 2 y 3. La evidencia y su alcance están documentados en [METADATA_USO_CODEX.md](METADATA_USO_CODEX.md).

## 1. Evidencia económica observada

El host registró `gpt-6-astra` con `effort: low` en los tres turnos. La denominación visible “GPT-6 Astra Light” fue informada por el usuario, pero para la evidencia técnica se conserva la identificación que aparece en los logs: `gpt-6-astra` + `low`.

| Corrida | Input total | Cached input | Input no cacheado | Output | Total tokens |
|---|---:|---:|---:|---:|---:|
| Corrida 1 | 3.874.830 | 3.833.728 | 41.102 | 19.644 | 3.894.474 |
| Corrida 2 | 1.265.275 | 1.221.632 | 43.643 | 13.851 | 1.279.126 |
| Corrida 3 | 1.622.409 | 1.600.128 | 22.281 | 9.627 | 1.632.036 |
| **Total** | **6.762.514** | **6.655.488** | **107.026** | **43.122** | **6.805.636** |

También se registraron `reasoning_output_tokens` de 7.751, 766 y 417 respectivamente, y `cache_write_input_tokens = 0` en los tres turnos.

### Qué miden estos tokens

Los tokens corresponden al **turno completo de Codex asociado a cada corrida**. Incluyen contexto de conversación, coordinación, herramientas, validaciones, documentación y publicación realizadas durante ese turno. No existe una separación verificable del consumo atribuible exclusivamente al subprocess `generate`/`consolidate` ni sólo a los prompts académicos.

Esto hace que la medición sea conservadora para describir el costo de usar el agente en el entorno observado: refleja todo el trabajo de coordinación del turno, pero no debe interpretarse como costo puro del motor determinístico.

## 2. Costo monetario observado

No se compraron créditos adicionales, no se utilizó una API paga y los extends consumidos estaban incluidos/disponibles en la cuenta. Por lo tanto, el **desembolso marginal de caja observado para ejecutar estas tres corridas fue 0**.

Esto no significa que el sistema tenga costo económico total cero. La suscripción existente, el equipo, el tiempo humano, el desarrollo, el mantenimiento, la seguridad y eventuales excesos de uso son costos distintos.

No se convierte retrospectivamente el uso de Codex en un supuesto costo API por token: las corridas no fueron facturadas como llamadas API y no existe una tarifa por token observada para ese uso incluido que permita imputar un importe real por corrida sin introducir una hipótesis externa.

En consecuencia:

- **Costo marginal de caja observado — Corrida 1:** 0.
- **Costo marginal de caja observado — Corrida 2:** 0.
- **Costo marginal de caja observado — Corrida 3:** 0.
- **Costo marginal total observado:** 0.

Los tokens sí se informan porque fueron medidos; el precio por token no se inventa.

## 3. Workflow determinístico

Python y Node realizan localmente el cálculo salarial, generación y protección de Excel, controles de integridad, budgets y consolidación. La interfaz no llama a una API LLM para hacer los cálculos. El salario final no depende de razonamiento numérico libre del modelo: el agente coordina y la herramienta determinística es la fuente autoritativa para porcentajes, redondeos, caps, budgets y validaciones.

En el dataset DEMO el subprocess local tarda segundos por ejecución. No se transforma esa duración en un costo monetario porque no se midieron CPU, energía, amortización del equipo ni una tarifa de infraestructura separada.

## 4. Costo humano

El costo humano probablemente sea más relevante que el costo marginal del modelo en este caso. Incluye preparar y validar inputs, revisar propuestas, editar ajustes discrecionales, resolver excepciones, verificar destinatarios y aprobar el ciclo.

La Corrida 2 incorpora una intervención humana real: edición manual de `Discretionary Adjustment %` para A001. No se cronometró esa intervención ni el resto de las tareas del usuario, por lo que no se asigna un costo horario ficticio.

Para una implementación operativa futura deberían registrarse minutos por rol y actividad, cantidad de excepciones y retrabajos, y una tasa interna autorizada. Recién entonces sería válido comparar el proceso asistido contra un baseline manual y calcular ahorro, ROI o payback.

## 5. Proyección operativa: semana y año

Este workflow corresponde a un ciclo de Compensation, no a una operación semanal. Para satisfacer la proyección económica sin inventar una cadencia artificial se explicita la hipótesis:

- **frecuencia de planificación:** 1 ciclo salarial por año;
- un ciclo normal requiere al menos una operación `generate` y una `consolidate`;
- pueden existir reintentos cuando una devolución se rechaza, como ocurrió en Corrida 2;
- el ciclo observado de prueba, incluyendo ese rechazo y posterior reintento, utilizó **6.805.636 tokens de turno** en total;
- bajo el mismo esquema observado —Codex desktop dentro de uso incluido, sin créditos adicionales ni API paga— el **desembolso marginal de caja proyectado es 0 por ciclo y 0 por año**;
- expresado como promedio semanal de caja dentro de esa hipótesis anual, el costo marginal sigue siendo **0 por semana**. Esta equivalencia no significa que el proceso se ejecute semanalmente.

La proyección deja de ser válida si se compran créditos, se migra a una API paga, aumenta la frecuencia o el uso supera los límites incluidos. En ese caso deben utilizarse el consumo medido del nuevo entorno y su tarifa efectiva.

No se anualizan los 6,8 millones de tokens como si fueran una demanda estable sin advertencia: ese valor proviene de una única experiencia final que además incluyó documentación extensa y un retry por una falla real.

## 6. Elección del modelo

El criterio del curso es utilizar **el modelo más chico que hace bien la tarea**. En este sistema el modelo no necesita resolver la matemática salarial: interpreta la solicitud, selecciona `verify`, `generate` o `consolidate`, invoca la herramienta, lee la salida estructurada, comunica excepciones y detiene/escalona cuando corresponde.

La metadata de los tres turnos registra **`gpt-6-astra` con `effort: low`**. Esa configuración coordinó exitosamente las tres corridas, incluida una corrida rechazada y la posterior consolidación con V4.1, mientras la lógica crítica permaneció en código determinístico.

No se afirma que sea el mínimo absoluto posible porque no se realizó un benchmark controlado frente a modelos menores. La conclusión respaldada por evidencia es: **no fue necesario elevar el effort ni delegar los cálculos críticos al modelo para que el workflow funcionara**.

## 7. Cómo mediría el sistema si se migrara a uso facturable

Si el sistema se migrara a un entorno con tarifa por token, cada llamada debería registrar modelo, timestamp, input total, cached input, output, retries y precio oficial aplicable en esa fecha.

Si el proveedor incluye cached tokens dentro de input total:

`input_no_cacheado = input_total - input_cacheado`

Para precios por millón:

`costo_llamada = (input_no_cacheado × precio_input + input_cacheado × precio_cached + output × precio_output) / 1.000.000`

Luego:

`costo_corrida = suma(costo_llamada) + cargos_adicionales_verificados`

`proyeccion_anual = suma(costo_medido_por_tipo × frecuencia_anual_documentada_por_tipo)`

La fuente de precios, moneda, fecha y modalidad deben conservarse junto con la evidencia. Una tarifa hipotética puede usarse para un escenario, pero debe rotularse como estimación y no confundirse con el costo observado de estas corridas.

## Conclusión económica

Ahora existen dos datos económicos verificables que antes faltaban:

1. **consumo de tokens por turno** para cada una de las tres corridas;
2. **desembolso incremental observado = 0**, porque el trabajo se realizó dentro del uso disponible de Codex desktop y no mediante API paga o créditos comprados.

La principal limitación remanente es de atribución: los tokens cubren el turno completo de coordinación y no pueden separarse de manera verificable entre contexto, herramientas, documentación y el subprocess salarial. Esa limitación se declara en lugar de fabricar una precisión inexistente.
