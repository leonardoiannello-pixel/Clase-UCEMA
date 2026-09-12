# Reproducción e interfaz del agente

## Requisitos y alcance

Clonar el repositorio completo y usar la rama del paquete. `Trabajo-Final/` contiene la guía, prompts, registro y herramienta; referencia V4 sin exigir leer Entrega-2 completa. No es una distribución independiente de un solo directorio. Los catálogos fijan la versión integrada `2c55ad6fb9862203d534892e55087c4016479661`.

- Python 3.11 o superior con `openpyxl` conforme a [requirements V4](../../Entrega-2/v4/requirements.txt).
- Node con `@oai/artifact-tool` disponible en un `node_modules` ancestro del runtime de ejecución. El paquete no descarga ni integra servicios externos.
- Contraseña de protección por `SALARY_REVIEW_PASSWORD`. `DEMO-only` es únicamente el valor sintético utilizado en pruebas.

En un runtime Codex, `load_workspace_dependencies` informa ejecutables Python/Node y el directorio de paquetes. Usar esos valores locales sin versionarlos. `SALARY_NODE` puede apuntar al ejecutable Node. Para que Node resuelva ESM, crear una junction/symlink `node_modules` en `Trabajo-Final/` al directorio de paquetes informado por el runtime; no usar `NODE_PATH` como sustituto de resolución ESM. En PowerShell:

```powershell
# Asignar $paquetesRuntime y SALARY_NODE con las rutas reales informadas por el runtime.
# Si node_modules ya existe y resuelve Artifact Tool, no recrearlo.
New-Item -ItemType Junction -Path node_modules -Target $paquetesRuntime
```

Fuera de ese runtime debe proveerse una instalación compatible de Artifact Tool; no se garantiza acceso mediante un paquete público de npm. Python por sí solo no genera los Excel. La falta de esta dependencia debe quedar como bloqueo de entorno, no como corrida exitosa.

## Verificar y generar

Desde `Trabajo-Final/`, reemplazar `python` por la ruta del ejecutable disponible cuando sea necesario:

```powershell
python agente/cli.py verify
$env:SALARY_REVIEW_PASSWORD = 'DEMO-only'
python agente/cli.py generate --output ejecuciones/generacion_01 --synthetic-data
```

`verify` verifica ocho referencias (cinco archivos V4 y tres inputs) y reporta disponibilidad básica de Python/Node. No ejecuta ni garantiza el renderer; `generate` hace la comprobación efectiva.

Rutas alternativas para otra muestra **sintética**:

```powershell
python agente/cli.py generate --employees ruta/Employees_Input.xlsx --market ruta/Market_Data.xlsx --parameters ruta/Parameters.xlsx --output ejecuciones/otra_muestra --synthetic-data
```

No cambiar el catálogo ni la evidencia para hacer pasar `verify`. Una discrepancia indica otra versión y exige revisar procedencia. La interfaz verifica texto normalizando sólo CRLF a LF para permitir clones Windows; los Excel se verifican byte a byte. Las copias de ejecución preservan todos los bytes del checkout/input y registran SHA256 exacto. No se modifica el código copiado.

La interfaz crea `runtime/v4/` con los ejecutables originales, `runtime/inputs/` con copias exactas de los tres archivos y `artifacts/` con salidas V4. Esta disposición satisface las rutas relativas originales del motor sin parchearlo. No necesita copiar outputs V1–V3; el manifest nuevo describe los inputs efectivamente usados en esta ejecución, y el reporte conserva sus rutas de origen. Los históricos siguen accesibles por sus enlaces.

## Revisar y consolidar

Desde la corrección posterior a Corrida 2, `consolidate` usa la [variante V4.1](../agente/v41/README.md). La única diferencia frente a V4 es reconocer comillas opcionales de los calificadores Detail/Summary al comparar fórmulas protegidas. Se verifican `agente/v41_referencias.json` y los hashes base V4; reporte e invocación identifican la versión usada. La generación sigue en V4 y las evidencias de corridas anteriores conservan sus versiones originales.

Compensation verifica destinatarios antes de entregar archivos. El líder sólo edita Discretionary Adjustment %. No entregar a cada líder el master global. La identidad real del remitente debe comprobarse fuera de esta herramienta.

Después de recibir los cuatro archivos:

```powershell
python agente/cli.py consolidate --original ejecuciones/generacion_01/artifacts --reviewed ejecuciones/devoluciones_01 --output ejecuciones/consolidacion_01 --synthetic-data
```

`--original` apunta al directorio que contiene master y manifest confiables, no al directorio padre del reporte. `--reviewed` contiene `team_L-A.xlsx`, `team_L-B.xlsx`, `team_L-C.xlsx` y `leadership_review.xlsx` devueltos. La interfaz nunca crea un archivo faltante ni presume que ocurrió una revisión.

Para comprobar el circuito sin interacción humana, **sólo como prueba técnica de ajuste cero**, puede reutilizarse la carpeta generada como reviewed:

```powershell
python agente/cli.py consolidate --original ejecuciones/generacion_01/artifacts --reviewed ejecuciones/generacion_01/artifacts --output ejecuciones/prueba_cero --synthetic-data
```

Este comando no constituye devolución de líderes ni aprobación. No debe registrarse como corrida real del agente final con personas.

## Reporte y fallos

stdout contiene JSON; `reporte.json` lo conserva en una ejecución iniciada. `tool_invocation.json` guarda argumentos sin shell y sin contraseña. `tool_stdout.txt` y `tool_stderr.txt` contienen evidencia del motor; los archivos parciales de un fallo no se validan automáticamente.

| Resultado | Interpretación |
|---|---|
| `GENERATED` / `GENERATED_WITH_EXCEPTIONS` | Herramienta terminó; revisar archivos/excepciones, sin aprobación |
| `CONSOLIDATED` / `CONSOLIDATED_WITH_EXCEPTIONS` | Consolidado disponible; autoridad debe decidir |
| `REJECTED` | Precondición o devolución rechazada; revisar causa |
| `FAILED` | Proceso falló; revisar log, no usar parciales como salida válida |

Código CLI 0 significa operación terminada, no ausencia de excepciones ni aprobación. Códigos 1/2 indican fallo/rechazo o argumentos incorrectos. `modelo`, `tokens` y `costo_llm` permanecen `null` porque el CLI no llama a un LLM.

Sólo se aceptan directorios nuevos. Dentro del repositorio, outputs deben ir en `Trabajo-Final/ejecuciones/` (ignorado por Git). No se borran ejecuciones previas ni se escribe sobre fuentes. Los outputs externos también requieren resolución de dependencias Node desde su ubicación.

## Invocación desde un host LLM

Cargar `prompts/system_prompt.md` y enviar el user prompt final al host que disponga de herramienta de procesos. El modelo selecciona una operación y argumentos conforme a [contrato_herramienta.json](../agente/contrato_herramienta.json). La aplicación de ejecución debe pasar argumentos como lista y conservar las restricciones del host. El CLI no es un servicio MCP ni una API paga.

Luego guardar transcripción efectiva, metadata del modelo, invocaciones y métricas en la corrida correspondiente. Los prompts publicados son contrato/solicitud, no evidencia de que ya se ejecutaron tres veces.

## Pruebas

Desde `Trabajo-Final/`, con los mismos ejecutables/dependencias:

```powershell
python -m unittest discover -s ../Entrega-2/v4/tests -v
python -m unittest discover -s agente/tests -v
```

La primera suite conserva las 20 pruebas V4, sin editarlas. La segunda prueba la interfaz, copias exactas, inputs alternativos sintéticos, reporte, rechazo, rutas y no aprobación. Ver [validación técnica](VALIDACION_TECNICA.md) para resultados efectivamente registrados.
