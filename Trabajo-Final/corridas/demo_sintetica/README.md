# Demo sintética V4 existente

Esta carpeta referencia una demostración del workflow determinístico. **No es una corrida real instrumentada del agente final ni evidencia de uso en producción.** No se copian ni reescriben los outputs históricos.

- [Propuesta y archivos por revisor](../../../Entrega-2/v4/demo/generated/)
- [Master automático](../../../Entrega-2/v4/demo/generated/master_proposal.xlsx)
- [Manifest e inputs utilizados](../../../Entrega-2/v4/demo/generated/manifest.json)
- [Excepciones iniciales](../../../Entrega-2/v4/demo/generated/generation_validation.json)
- [Consolidado](../../../Entrega-2/v4/demo/consolidated/consolidated_final.xlsx)
- [Validación de consolidación](../../../Entrega-2/v4/demo/consolidated/validation_exceptions.json)
- [Resultado histórico de 20 tests](../../../Entrega-2/v4/demo/test_results.txt)

| Pool | Payroll propuesto/final DEMO (ARS) | Máximo (ARS) | Resultado |
|---|---:|---:|---|
| Team Alpha | 11.520.000 | 11.520.000 | OK |
| Team Beta | 10.736.500 | 10.738.000 | OK |
| Team Gamma | 9.322.000 | 8.800.000 | EXCEEDED: 522.000 |
| Leadership | 14.038.500 | 14.040.000 | OK |

Fuente: artefactos enlazados, versión integrada por [PR #4](https://github.com/leonardoiannello-pixel/Clase-UCEMA/pull/4), commit de corrección `1bf9617ac5172a10297b02884bf11ff855d9ce65`. El paquete parte del merge `2c55ad6fb9862203d534892e55087c4016479661`.

Todos los ajustes de esta demo son cero. `PENDING_HUMAN_APPROVAL` no significa aprobación. El test con +1 pp a A001 es un cambio sintético automatizado, no una decisión acreditada de un líder. B004 conserva `MARKET_DATA_MISSING`; Gamma conserva la insuficiencia de budget protegido.

No hay en estos artefactos medición de modelo, tokens ni costo LLM. No se reconstruyen esas métricas a partir del historial de desarrollo ni se inventa una fecha de ejecución del agente final.
