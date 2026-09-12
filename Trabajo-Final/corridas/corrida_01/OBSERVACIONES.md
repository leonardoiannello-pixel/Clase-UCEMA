# Observaciones y alcance de la evidencia

## Qué ocurrió

El usuario autorizó la Corrida 1, exclusivamente `generate`, sobre la rama `leonardo/final-academic-package`. El agente leyó los dos prompts finales y los aplicó como contrato y solicitud de tarea en la conversación existente de Codex desktop. Primero verificó referencias mediante el CLI y después invocó realmente `generate`, con datos sintéticos del catálogo. Los tiempos y argumentos efectivos se conservan en `verificacion_invocacion.json` y `cli_invocacion.json`.

Esta es una ejecución real del sistema coordinada por el agente en el host. No es una llamada nueva/aislada a una API LLM ni una sustitución del system prompt interno de Codex. Las instrucciones vigentes de esta conversación también restringieron el alcance: sólo generación, sin consolidación, sin ajustes humanos y sin merge. Las copias de los prompts del paquete son exactas; no se pretende que representen todo el contexto interno del host.

## Evidencia primaria

- `prompts/`: copias exactas de los dos archivos leídos y usados como instrucciones de tarea.
- `fuentes/`: CLI y catálogos/contrato efectivamente utilizados. La revisión del repositorio está registrada en `registro.json`.
- `cli_stdout.txt`, `cli_stderr.txt`: bytes capturados del proceso CLI. `verificacion_*` conserva el control previo, que no es una segunda generación.
- `ejecucion/reporte.json`, `ejecucion/tool_invocation.json`, `ejecucion/tool_stdout.txt`, `ejecucion/tool_stderr.txt`: archivos emitidos realmente por la interfaz.
- `ejecucion/runtime/`: copias exactas de inputs y código V4 utilizadas en esa invocación.
- `ejecucion/artifacts/`: Excel, manifest, validación e inspecciones emitidas.
- `salida_agente.md`: respuesta del agente redactada después de observar los resultados. Es distinta del JSON del CLI.
- `host_metadata.json`: host/runtime observado y campos de modelo/usage no expuestos en `null`.

El CLI sólo permite crear outputs nuevos bajo `Trabajo-Final/ejecuciones/` dentro del repositorio. Por eso se ejecutó allí y se archivó la evidencia byte a byte en esta carpeta, sin modificar el CLI ni V4. `ubicaciones.json` conserva el mapeo. Los paths absolutos originales de los reportes no se reescribieron: describen la ejecución observada. Se omitieron únicamente caches `__pycache__` y `.pyc`; el runtime fuente y las entradas sí están incluidos.

Para repetir en otro entorno, usar una carpeta nueva bajo `ejecuciones/`, las fuentes/inputs verificados y la misma operación. No sobrescribir este registro ni ejecutar el capturador de nuevo sobre él. Los hashes prueban identidad de archivos archivados; no garantizan una salida binaria idéntica en otra ejecución, ya que el renderer puede generar IDs internos diferentes.

## Resultado y límites

El proceso terminó con código 0 y `GENERATED_WITH_EXCEPTIONS`. El caso normal de generación contiene excepciones de negocio ya presentes en los inputs sintéticos: mercado faltante para B004 y budget protegido insuficiente en Gamma. No se alteraron reglas ni parámetros para eliminarlas. Ver `salida_agente.md` y los logs para los valores efectivos.

Los campos llamados final en los archivos de revisión son fórmulas preparadas con ajuste inicial cero; no significan que hubo revisión, consolidación o aprobación. La decisión salarial sigue `PENDING_HUMAN_APPROVAL`. No se simularon devoluciones, no se editaron ajustes y no se enviaron archivos.

`llm_invocado=false` en el reporte es un campo del CLI determinístico, que no llama a una API. No niega que esta sesión de agente leyó los prompts, eligió la operación y produjo una respuesta. No se atribuye un modelo exacto sin metadata verificable. Los contadores de longitud de resultados de herramientas no se trataron como tokens del modelo; métricas y costos permanecen en `null`.

## Contraseña y confidencialidad

La contraseña de hoja se generó en memoria y se pasó sólo por entorno. Se buscó su valor en toda la evidencia disponible y en cada parte descomprimida de los XLSX antes de descartarlo; no se encontró en claro. El control queda en `control_password.json`. Excel conserva un verificador de protección, no cifrado ni control de acceso. No se publica una contraseña para desproteger las hojas.

Los inputs archivados coinciden por hash con el catálogo sintético ya aprobado; no se incorporó otra fuente salarial. Se verifican IDs/población, campos de ajuste cero y ausencia de artefactos de consolidación en los tests de evidencia. Esto acredita procedencia del dataset de esta corrida, no un detector universal de datos confidenciales.

Los tests de esta carpeta son de lectura sobre la evidencia ya generada. No ejecutan consolidación, no modifican los Excel y no simulan ajustes. Los registros de corrida_02 y corrida_03 permanecen intactos.
