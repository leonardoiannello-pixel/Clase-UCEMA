# Reproducción e interfaz del agente

## Requisitos y alcance

Clonar el repositorio completo y usar la rama del paquete. `Trabajo-Final/` contiene guía, prompts, registros y herramienta; actualmente referencia V4/V4.1 mediante catálogos y por eso todavía no es una distribución independiente de un solo directorio. El repositorio final de entrega promoverá este contenido a raíz e incluirá las dependencias necesarias para eliminar las rutas hermanas.

- Python 3.11 o superior con `openpyxl` conforme a [requirements V4](../../Entrega-2/v4/requirements.txt).
- Node con `@oai/artifact-tool` disponible en un `node_modules` ancestro del runtime de ejecución.
- Contraseña de protección por `SALARY_REVIEW_PASSWORD`. `DEMO-only` es únicamente un valor sintético de prueba.

En un runtime Codex, `load_workspace_dependencies` informa ejecutables Python/Node y el directorio de paquetes. Usar esos valores locales sin versionarlos. `SALARY_NODE` puede apuntar al ejecutable Node. Para que Node resuelva ESM, puede requerirse una junction/symlink `node_modules` en `Trabajo-Final/` al directorio de paquetes informado por el runtime.

```powershell
# Asignar $paquetesRuntime y SALARY_NODE con las rutas reales del entorno.
New-Item -ItemType Junction -Path node_modules -Target $paquetesRuntime
```

Fuera de ese runtime debe proveerse una instalación compatible de Artifact Tool. La falta de la dependencia debe registrarse como bloqueo de entorno, no como corrida exitosa.

## Verificar y generar

Desde `Trabajo-Final/`:

```powershell
python agente/cli.py verify
$env:SALARY_REVIEW_PASSWORD = 'DEMO-only'
python agente/cli.py generate --output ejecuciones/generacion_01 --synthetic-data
```

`verify` comprueba las referencias y hashes del código/inputs y reporta disponibilidad básica de dependencias. `generate` hace la comprobación efectiva del renderer al ejecutar.

Rutas alternativas para otra muestra sintética:

```powershell
python agente/cli.py generate --employees ruta/Employees_Input.xlsx --market ruta/Market_Data.xlsx --parameters ruta/Parameters.xlsx --output ejecuciones/otra_muestra --synthetic-data
```

No cambiar catálogos ni evidencia para forzar un `verify` exitoso. Los Excel se verifican byte a byte y las copias de ejecución registran SHA256. No se modifica el código copiado.

`generate` usa V4. La interfaz crea un runtime con código e inputs exactos y deja los artefactos bajo `artifacts/`.

## Revisar y consolidar

Desde la corrección posterior a Corrida 2, `consolidate` usa la [variante V4.1](../agente/v41/README.md). V4.1 difiere de V4 únicamente en la equivalencia conservadora de comillas opcionales para los calificadores `Detail` y `Summary` al comparar fórmulas protegidas. Toda diferencia semántica restante sigue siendo rechazada.

Después de recibir los cuatro archivos reviewed:

```powershell
python agente/cli.py consolidate --original ejecuciones/generacion_01/artifacts --reviewed ejecuciones/devoluciones_01 --output ejecuciones/consolidacion_01 --synthetic-data
```

`--original` apunta al directorio con master y manifest confiables. `--reviewed` contiene `team_L-A.xlsx`, `team_L-B.xlsx`, `team_L-C.xlsx` y `leadership_review.xlsx`. La interfaz nunca crea un archivo faltante ni presume que ocurrió una revisión.

Para una prueba técnica de ajuste cero puede reutilizarse la carpeta generada como reviewed, pero esa prueba **no constituye intervención humana ni corrida final**.

## Reporte y fallos

stdout contiene JSON y `reporte.json` conserva el resultado determinístico. `tool_invocation.json` guarda argumentos sin shell y sin contraseña. `tool_stdout.txt` y `tool_stderr.txt` preservan evidencia técnica.

| Resultado | Interpretación |
|---|---|
| `GENERATED` / `GENERATED_WITH_EXCEPTIONS` | Herramienta terminó; revisar archivos/excepciones, sin aprobación |
| `CONSOLIDATED` / `CONSOLIDATED_WITH_EXCEPTIONS` | Consolidado disponible; autoridad debe decidir |
| `REJECTED` | Precondición o devolución rechazada; revisar causa |
| `FAILED` | Proceso falló; no usar parciales como salida válida |

Código CLI 0 significa operación terminada, no ausencia de excepciones ni aprobación. Códigos 1/2 indican rechazo/fallo o argumentos incorrectos. El CLI no llama a un LLM, por lo que sus propios campos `modelo`, `tokens` y `costo_llm` no sustituyen metadata del host.

## Invocación desde un host LLM

Cargar `prompts/system_prompt.md` y enviar la solicitud al host con acceso a la herramienta de procesos. El modelo selecciona la operación y argumentos conforme a [contrato_herramienta.json](../agente/contrato_herramienta.json). La aplicación de ejecución debe conservar las restricciones del host y pasar argumentos sin shell.

Las **tres corridas finales ya fueron ejecutadas en Codex desktop** y se conservan bajo `corridas/`. Cada una archiva el prompt operativo usado, hashes, invocación, salida estructurada, reporte determinístico y artefactos o rechazo. La Corrida 2 preserva una falla real; Corrida 3 reutiliza exactamente los mismos reviewed con V4.1.

Las copias de prompts dentro de cada corrida son la evidencia histórica de esa ejecución. El `system_prompt.md` de raíz representa el contrato vigente del sistema y puede evolucionar después de una corrida sin reescribir las copias históricas.

El host no expuso de manera verificable tokens ni modelo exacto en metadata de las corridas. Esos valores se mantienen `null`; la configuración visible declarada por el usuario se trata por separado en el análisis económico.

## Pruebas

Desde `Trabajo-Final/`, con dependencias disponibles:

```powershell
python -m unittest discover -s ../Entrega-2/v4/tests -v
python -m unittest discover -s agente/tests -v
```

La suite histórica conserva las pruebas V4. Las pruebas del paquete verifican interfaz, copias exactas, rechazo de manipulación y regresiones V4.1. Además, cada corrida final conserva tests de lectura/consistencia específicos de su evidencia; esos tests no sustituyen la corrida real.
