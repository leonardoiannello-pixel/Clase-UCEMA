# Auditoría de metadata de uso de Codex

Después de completar las tres corridas finales se realizó una auditoría **sin reejecutar el agente ni modificar las corridas** para determinar si Codex Desktop había conservado métricas verificables de uso.

## Fuente

La sesión quedó registrada localmente en:

```text
C:\Users\Usuario\.codex\sessions\2026\09\12\rollout-2026-09-12T15-44-38-01a096ef-9206-7951-b814-6eeb3326933f.jsonl
```

Los registros finales `token_usage_record` asociados a las tres corridas se localizaron en las líneas **832, 1062 y 1364**. La identificación de la sesión se corroboró además en `C:\Users\Usuario\.codex\state_5.sqlite`, tabla `threads`.

La asociación con cada corrida se hizo mediante `turn_id`, pedido del usuario, invocaciones y timestamps. No se estimaron tokens ni se reconstruyeron con un tokenizer.

## Modelo verificable

Los tres `turn_context` registran:

- modelo: `gpt-6-astra`;
- effort: `low`.

La etiqueta comercial visible informada por el usuario fue “GPT-6 Astra Light”, pero esa denominación exacta **no aparece como metadata verificable** en los logs. Para evidencia técnica se usa `gpt-6-astra` + `effort: low`.

## Uso observado por turno

| Corrida | Ventana UTC del turno | Input total | Cached input | Input no cacheado | Output | Reasoning output* | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Corrida 1 | 22:00:18–22:14:46 | 3.874.830 | 3.833.728 | 41.102 | 19.644 | 7.751 | 3.894.474 |
| Corrida 2 | 22:24:15–22:34:48 | 1.265.275 | 1.221.632 | 43.643 | 13.851 | 766 | 1.279.126 |
| Corrida 3 | 22:50:36–22:57:34 | 1.622.409 | 1.600.128 | 22.281 | 9.627 | 417 | 1.632.036 |
| **Total** | — | **6.762.514** | **6.655.488** | **107.026** | **43.122** | **8.934** | **6.805.636** |

\* `reasoning_output_tokens` es metadata adicional del host y no se suma nuevamente al total cuando ya está incluida en output/usage total. `cache_write_input_tokens` fue 0 en los tres turnos.

## Alcance de la medición

Estas métricas corresponden al **turno completo de Codex** asociado a cada corrida. Incluyen contexto acumulado de la conversación, coordinación, uso de herramientas, validaciones, documentación y publicación realizada durante ese turno.

Por lo tanto:

- son métricas reales y verificables del uso del host para cada corrida;
- pueden asociarse sin ambigüedad a Corrida 1, 2 y 3;
- **no equivalen al consumo exclusivo del subprocess `generate`/`consolidate`**;
- tampoco equivalen únicamente a los dos prompts académicos archivados;
- no existe en la evidencia una partición verificable más fina que permita atribuir tokens sólo al CLI.

Esta limitación se mantiene explícita en el análisis económico. No se presenta una desagregación inventada como medición real.
