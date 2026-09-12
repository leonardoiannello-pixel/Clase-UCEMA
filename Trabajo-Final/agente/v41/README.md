# V4.1: equivalencia mínima de representación de fórmulas

Variante académica derivada de V4 histórica (`Entrega-2/v4`, base fijada por `agente/v4_referencias.json`). Se incorpora después del rechazo real de Corrida 2. Esa evidencia no se corrige ni reescribe. No constituye la ejecución de Corrida 3.

`workflow_v41.py` es una copia explícita del workflow V4 con exactamente dos cambios de líneas: importar `equivalent_formulas` y usarlo en la comparación no numérica de campos protegidos. Una prueba verifica esa derivación completa. Engine, renderer y protección se reutilizan byte a byte, sin cambios. No se alteran cálculos, parámetros, budgets, permisos de edición ni aprobación.

La interfaz conserva `generate` en V4. Para `consolidate`, copia además los dos ejecutables V4.1 al runtime aislado y ejecuta `workflow_v41.py`. Conserva también el workflow V4 original, sin sobrescribirlo. `agente/v41_referencias.json` fija los hashes del código variante; `verify` comprueba ambos catálogos. Invocación y reporte identifican la versión y los hashes exactos de las copias utilizadas.

La comparación mantiene igualdad numérica de V4. Para valores no numéricos, primero acepta igualdad exacta. Sólo si ambos son strings que empiezan con `=`, compara representaciones canonicalizadas:

- Se reconocen átomos léxicos: strings Excel entre comillas dobles (incluido escape `""`), nombres entre comillas simples (incluido escape `''`) y referencias entre corchetes. No se sustituyen subcadenas dentro de esos átomos.
- Sólo se retiran las comillas simples de los nombres exactos **Detail** y **Summary**, una lista deliberadamente limitada a las hojas del workflow. Deben ser un calificador completo seguido de `!` y precedido de un delimitador de fórmula. No se generaliza a todos los nombres posibles de Excel.
- No se quitan comillas en nombres con espacios, puntuación, apóstrofes, otros nombres, libros externos, referencias estructuradas o calificadores 3D. Sintaxis léxica incompleta o no soportada queda sin normalizar.
- No se cambian referencias de celdas, `$`, operadores, constantes, espacios, mayúsculas/minúsculas ni strings literales. No se usan valores cacheados para comparar fórmulas. Cualquier diferencia restante sigue produciendo `PROTECTED_FIELD_CHANGED`.

Ejemplo: `=SUM('Detail'!Q2:Q6)` y `=SUM(Detail!Q2:Q6)` son equivalentes; `=SUM(Detail!Q3:Q6)` sigue siendo distinto. Una cadena como `="'Detail'!A1"` se preserva literalmente.

Los tests leen las 13 diferencias registradas en Corrida 2 y comprueban su equivalencia, sin editar ni consolidar esos reviewed. Las integraciones usan exclusivamente fixtures temporales generados para tests, no decisiones humanas ni corridas académicas. Los tests anteriores de manipulación continúan comprobando rechazo. Los logs de validación están en `docs/validacion_v41/`.
