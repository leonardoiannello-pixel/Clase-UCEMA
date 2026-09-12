# Gobierno y riesgo

Alcance: demo pública sintética y herramienta local L2. Responsable final: **Responsable de Compensation / autoridad autorizada del ciclo**. Los revisores y el coordinador técnico son roles; no se asignan nombres reales.

## Sistemas, datos y permisos

| Activo | Lectura/generación | Permiso humano y límite automático |
|---|---|---|
| Employees input | Se lee y copia al runtime; IDs, mapping, salarios y posiciones | Compensation valida calidad y origen. El agente no corrige datos ni inventa empleados |
| Market data | Se lee para la posición destino | Compensation valida referencia y moneda. No se completan datos desde internet |
| Parameters | Se lee el archivo exacto y se registran hash y valores parseados | Sólo la autoridad de negocio define cambios en otro archivo. La IA no los edita |
| Archivos de revisión | V4 genera por revisor, con hojas y estructura protegidas | Únicamente Discretionary Adjustment % editable. El líder no revisa su propio salario |
| Master y manifest | Generados y luego leídos como baseline de consolidación | Custodia confiable del coordinador. No distribuir el master de toda la población a cada líder |
| Consolidado | Generado tras revalidar archivos y recalcular en Python | Autoridad humana decide; nunca aprobación automática |
| Logs de interfaz | Invocación, hashes y resultado determinístico | Contienen rutas y datos operativos. No incluyen contraseña; no publicar material real |

Los permisos de la tabla son el modelo de gobierno requerido. El código no implementa ACL ni autentica usuarios. La interfaz bloquea sobrescritura y escritura sobre el código/evidencia del repositorio, utiliza argumentos de proceso sin shell y prepara copias exactas. Esto no convierte el equipo local en un entorno seguro para datos reales.

## Matriz concreta de riesgos

| Riesgo | Detección existente / límite | Respuesta | ¿Continúa? | Interviene |
|---|---|---|---|---|
| Datos incorrectos | V4 detecta duplicados de Employee_ID, salario no positivo/no ARS y rating inválido. No prueba que un salario positivo sea correcto ni cubre toda combinación inválida de campos | Corregir input autorizado y ejecutar en carpeta nueva; no autocorrección | Se detiene si hay error; valores plausibles erróneos pueden pasar y requieren revisión | Compensation y dueño del dato |
| Market faltante | `MARKET_DATA_MISSING`; referencia y compa-ratios vacíos, Market cero | Revisar fuente; no inventar referencia | Continúa con flag, sin aprobación automática | Compensation |
| Market presente pero equivocado | No hay comprobación externa de vigencia/adecuación ni validación completa de duplicados de códigos de mercado | Revisar catálogo destino antes de usar | Puede continuar; control humano requerido | Dueño de Market / Compensation |
| Budget protegido insuficiente | `BUDGET_INSUFICIENTE`; Gamma lo ejemplifica | X, Merit y Market cero; mantener protegidos y reportar exceso | Continúa como excepción | Autoridad de presupuesto / Compensation |
| Ajuste humano excede budget | Fórmulas `EXCEEDED`, consolidación `BUDGET_EXCEEDED` | Mostrar importe y pedir resolución, no recortar automático | Continúa consolidando; aprobación pendiente | Revisor y autoridad del ciclo |
| Manipulación de campos protegidos | Comparación de valores/fórmulas con manifest confiable: `PROTECTED_FIELD_CHANGED` | Rechazar devolución, solicitar archivo válido | Se detiene consolidación | Coordinador y revisor |
| Archivos faltantes o extra | `MISSING_FILE`, `UNEXPECTED_FILES` y validación de hojas | No sustituir faltantes por originales como si estuvieran revisados | Se detiene consolidación | Coordinador/revisor |
| Parámetros inválidos | Budgets numéricos, finitos, > -100%; límites discrecionales y precisión validados en los caminos implementados | Rechazo o error registrado. No inferir nuevos valores | Se detiene operación afectada | Compensation |
| Mapping incorrecto | Detecta reviewer vacío, auto-revisión, líder/equipo inconsistente y varios revisores por pool | Solicitar mapping corregido o regla explícita | Se detiene para casos detectados; un destinatario válido pero equivocado puede pasar | Compensation / dueño de estructura |
| Piso protegido o ajuste inválido | Excel valida; fórmulas defensivas y `human_result` revalidan tipo, precisión, rango y piso | No aceptar ajuste; no reemplazarlo silenciosamente | Se detiene consolidación; Excel muestra INVALID si se evita validación | Revisor |
| Cap Market y redondeo | V4 reduce sólo Market por 0,01 pp; `MARKET_CAP_ROUNDING_CONFLICT` si no puede cumplir | Conservar Merit/protegidos, reportar conflicto | Se detiene en conflicto irresoluble | Compensation |
| Protección Excel removida | El bloqueo es removible; quitarlo por sí solo no se autentica/detecta como decisión salarial | La consolidación sigue comparando contenido; custodiar originales | Puede continuar si sólo cambió protección; rechaza alteraciones de contenido | Coordinador / seguridad de información |
| Master o manifest manipulados | Hash del master detecta cambio si manifest sigue confiable; manifest no está firmado | Custodia fuera de archivos distribuidos; recuperar originales confiables | Rechazo de master cambiado; ataque sobre ambos no está cubierto | Coordinador / seguridad |
| Acceso indebido a salarios | No existe detector ni ACL en este proyecto. Bandera synthetic es declaración, no control de fuga | Usar sólo demo; en una implantación futura exigir acceso, almacenamiento y cifrado adecuados | No habilitar datos reales en este repositorio | Responsable del dato / seguridad |
| Archivo enviado al revisor incorrecto | Generación separa poblaciones; no hay envío ni validación automática del destinatario de una entrega externa | Verificar archivo, población y destinatario antes de entregar | Distribución humana debe esperar verificación | Coordinador de Compensation |
| Texto de input intenta dar instrucciones | Prompt trata celdas/devoluciones como datos, CLI no ejecuta comandos derivados de ellas | Ignorar instrucciones incrustadas; no exfiltrar ni cambiar reglas | Depende de integridad de datos; validar en futuras corridas del host | Operador del agente |
| Dependencia Node/Artifact Tool ausente | Fallo de proceso y logs; `verify` sólo informa disponibilidad parcial | Instalar/configurar runtime por vía autorizada; no inventar archivo generado | Se detiene; posibles archivos parciales no son válidos | Coordinador técnico |

## Protección no es confidencialidad

**Protección Excel != encryption != access control.** La primera limita edición accidental. El cifrado protege contenido frente a lectura sin clave. El control de acceso determina quién puede leer o modificar recursos. Esta entrega implementa protección de edición y verificación de contenido; no implementa los otros dos controles.

El hash aporta integridad sólo frente a una referencia confiable; no prueba autoría, identidad, veracidad del dato ni aprobación. Los IDs de revisores son routing. La contraseña llega por entorno y no se guarda en evidencia.

## Respuesta y responsabilidad final

Ante fallos, preservar inputs, outputs parciales y logs, corregir la causa con el rol responsable y abrir una ejecución nueva. No sobrescribir ni borrar para ocultar errores. No enviar archivos desde el agente. Un reporte con excepciones es un control, no una autorización.

La aprobación final sigue `PENDING_HUMAN_APPROVAL`. Su identidad, alcance, registro y facultades deben definirse antes de uso real. No se afirma que se haya aprobado un salario ni que existan controles productivos.
