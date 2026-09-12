# Solicitud de ejecución del ciclo sintético

Usá `prompts/system_prompt.md` como contrato del agente. Generá una propuesta del ciclo de salary review con los tres inputs sintéticos del catálogo `inputs/referencias.json`: Employees_Input.xlsx, Market_Data.xlsx y Parameters.xlsx de V4.

Verificá las referencias y ejecutá `generate` mediante la interfaz de `agente/`, en un directorio nuevo bajo `ejecuciones/`. La contraseña de protección debe obtenerse de `SALARY_REVIEW_PASSWORD`, nunca guardarse en el prompt ni en el reporte.

Generá el master, los archivos protegidos por revisor y el archivo Leadership para revisión superior. Aplicá las validaciones del motor, informá excepciones y budgets, e identificá el próximo paso humano. No cambies porcentajes ni parámetros para consumir budget o resolver excepciones.

No consolides todavía: no estoy entregando devoluciones de líderes en esta solicitud. No simules ajustes humanos. Dejá la decisión final en `PENDING_HUMAN_APPROVAL` y no envíes archivos a terceros.

Entregá el reporte estructurado definido en el system prompt. Si no podés ejecutar una herramienta, informalo sin inventar outputs. No infieras métricas de modelo, tokens o costo que no se hayan medido.
