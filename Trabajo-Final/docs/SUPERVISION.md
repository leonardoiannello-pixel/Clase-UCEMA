# Supervisión L0–L4

Esta tabla fija definiciones operativas para evaluar este proyecto. No se presenta como una taxonomía universal ni como cita textual de material de clase no adjuntado. El sistema se documenta como **L2**: el agente y las herramientas ejecutan trabajo y controles, mientras una persona conserva decisiones salariales y aprobación final.

| Nivel | Alcance operativo definido aquí | Decisión humana |
|---|---|---|
| L0 | Proceso manual, sin agente ejecutando trabajo | Realiza todas las acciones y decisiones |
| L1 | Asistencia: redacta, explica o recomienda; el humano ejecuta el proceso | Ejecuta y valida cada acción |
| **L2** | Agente ejecuta herramientas, prepara propuestas y controles con intervención humana acotada | Revisa ajustes y excepciones; conserva aprobación final |
| L3 | Ejecución y acciones delegadas dentro de un perímetro previamente autorizado, con supervisión por excepción | Define perímetro y atiende escalaciones; no implementado aquí |
| L4 | Autonomía completa dentro del alcance definido, incluida decisión final | Gobierno externo del sistema; no implementado ni apropiado para este alcance salarial |

## Aplicación L2 a Salary Review

El agente coordina recepción, procesamiento, cálculo determinístico, generación de master y archivos de revisión, controles y consolidación. Los prompts especifican la coordinación y `agente/cli.py` expone la herramienta local. Las tres corridas finales fueron ejecutadas en Codex desktop y se conservan bajo `corridas/`: generación, una consolidación rechazada y una consolidación posterior con V4.1.

El líder revisa solamente su población y edita `Discretionary Adjustment %`. No modifica General, Promotion, Progression ni la propuesta original. Los límites son parámetros; la herramienta no los inventa ni los adapta para aceptar una devolución. El propio líder se revisa en Leadership por un nivel superior.

La Corrida 2/3 contiene una intervención humana real y acotada: A001 recibió +1,00 pp de ajuste discrecional mediante edición manual en Excel fuera del agente. Esa decisión no fue tomada ni escrita por el modelo. La Corrida 3 demuestra que el sistema conserva `Proposed` y aplica la decisión sólo sobre `Final`.

El Responsable de Compensation / autoridad autorizada del ciclo revisa mapping y destinatarios, atiende errores de datos y excepciones, valida el budget y toma la decisión salarial final. No se inventan nombres, facultades específicas ni una aprobación efectivamente tomada.

## Puertas de intervención

| Momento | Trabajo automático | Intervención requerida |
|---|---|---|
| Antes de generar | Verificación de archivos y validaciones disponibles | Confirmar origen, corrección de datos y parámetros autorizados |
| Después de generar | Propuesta y flags; separado por revisor | Resolver excepciones y verificar destinatarios antes de entregar |
| Devolución | Validación de campos protegidos, ajustes y budgets | Revisar ajustes; pedir archivos válidos ante rechazo |
| Después de consolidar | Resultado con `PENDING_HUMAN_APPROVAL` | Aprobar o rechazar fuera del motor por autoridad autorizada |

La clasificación L2 describe la asignación de responsabilidades; no prueba que el repositorio tenga autenticación, firmas, aprobación electrónica o control de acceso. Esos controles serían requisitos adicionales para una implantación con datos reales.

El nivel es adecuado por el impacto de las decisiones sobre personas y remuneración, la sensibilidad de los datos y el compromiso económico. Un cálculo correcto es condición necesaria, pero no acredita legitimidad de los inputs, juicio de negocio ni autoridad para aprobar.
