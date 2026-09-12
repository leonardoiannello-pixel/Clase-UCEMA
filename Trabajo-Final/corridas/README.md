# Registro de corridas

`corrida_01`, `corrida_02` y `corrida_03` son **espacios reservados, no corridas ejecutadas**. Cada `registro.json` tiene estado `PENDIENTE_NO_EJECUTADA` y campos no medidos en `null`. No inferir resultados de sus nombres.

La [demo_sintetica](demo_sintetica/README.md) enlaza evidencia técnica V4 ya existente. Las verificaciones de la interfaz se registran por separado en [validación técnica](../docs/VALIDACION_TECNICA.md). Ninguna equivale a tres corridas instrumentadas del agente final con LLM.

## Cómo completar una corrida cuando ocurra

1. Guardar fecha/hora UTC real, objetivo, modelo exacto y versión del runtime; no deducir el modelo de la aplicación utilizada.
2. Guardar las versiones exactas del system y user prompt efectivamente usados. Hasta entonces, las rutas al prompt final son sólo referencias de plantilla.
3. Registrar inputs sintéticos y SHA256, invocaciones reales de herramientas, archivos producidos y hashes. Nunca incluir contraseñas ni credenciales.
4. Guardar la salida real del agente, excepciones, decisiones/intervenciones humanas efectivamente realizadas y observaciones.
5. Copiar el uso de tokens desde la medición del proveedor/host. Si no existe medición, dejar `null`, no cero.
6. Registrar precio, moneda, fecha y fuente verificada, y calcular el costo con la [metodología económica](../docs/ANALISIS_ECONOMICO.md).
7. Vincular las evidencias y cambiar el estado sólo al finalizar la ejecución. Una llamada fallida también se registra como tal, sin inventar outputs.

Casos sugeridos para futuras corridas: generación sintética, devolución con ajuste sintético documentado y devolución manipulada para verificar rechazo. Son propuestas de evaluación, no resultados ni decisiones humanas ya ocurridas.
