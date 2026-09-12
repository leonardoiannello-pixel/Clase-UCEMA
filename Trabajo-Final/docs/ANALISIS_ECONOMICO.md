# Análisis económico y plan de medición

No hay una corrida instrumentada del agente final con un registro verificable de modelo, tokens y precio. Por lo tanto **costo LLM por corrida y proyección anual están pendientes de medición**. No se usa cero para representar datos faltantes ni se atribuyen costos al historial de desarrollo sin evidencia.

## A. Workflow determinístico

Python y Node ejecutan localmente cálculo, autoría de Excel, protección y consolidación. Para el pequeño dataset DEMO el costo marginal computacional se considera prácticamente nulo como apreciación cualitativa de escala, **no como importe medido ni como garantía de gratuidad**. No hay una tarifa por token en estas funciones ni llamadas a una API LLM desde la interfaz.

El principal costo operativo esperado es tiempo humano: preparar y validar inputs, revisar propuestas, resolver excepciones, controlar destinatarios y aprobar. La magnitud relativa no fue medida. Equipamiento, licencias/runtime, mantenimiento, seguridad, soporte y tiempo de desarrollo son costos distintos; no se imputan como cero.

Para medirlos, registrar por ejecución duración del proceso, recursos si están disponibles, minutos por rol y actividad, cantidad de excepciones/retrabajos y tasas internas autorizadas. Comparar contra un proceso manual comparable con igual población y calidad. Sin baseline ni medición no se afirma ahorro, ROI ni payback.

## B. Componente LLM

Los prompts finales definen la coordinación; el host/modelo para las corridas a evaluar todavía debe registrarse. Las suscripciones de herramientas de desarrollo no equivalen automáticamente a costo API por corrida. No se asigna un modelo porque aparezca el nombre de una aplicación.

| Variable | Fuente a registrar | Estado actual |
|---|---|---|
| Modelo y versión exactos | Respuesta del proveedor o metadata verificable del host | Pendiente |
| Input tokens totales y cacheados | Usage real por llamada | Pendiente |
| Output tokens | Usage real; incluir categorías facturables según proveedor | Pendiente |
| Precios por categoría y moneda | Fuente oficial, URL, fecha, modalidad efectiva | Pendiente; no se consulta ni inventa una tarifa ahora |
| Costo por corrida | Suma de llamadas, retries y herramientas facturables | Pendiente |
| Frecuencia anual | Número de ciclos y operaciones aprobado/observado | Pendiente |
| Proyección anual | Costo medido por tipo × frecuencia documentada | Pendiente |

## Método reproducible

1. Registrar prompts efectivos, inputs/hashes e invocaciones en `corridas/corrida_XX/` cuando se ejecute. No cargar datos reales ni credenciales.
2. Capturar metadata por **cada llamada** LLM, incluidas reintentos y fallos facturables: modelo, timestamp, tokens y fuente. Separar herramientas determinísticas de llamadas LLM.
3. Verificar el precio oficial aplicable en esa fecha y guardar su URL, moneda, unidad, modalidad y categorías. Si un host no expone uso/facturación, marcar el costo como no medible con esa evidencia; no estimarlo como medición.
4. Cuando el proveedor incluya cached tokens dentro de input total, usar `input_no_cacheado = input_total - input_cacheado`. No contarlos dos veces. Si define las categorías de otra manera, adaptar y documentar la fórmula.
5. Para precios por millón: `costo_llamada = (input_no_cacheado × precio_input + input_cacheado × precio_cached + output × precio_output) / 1.000.000`. Añadir sólo cargos efectivamente aplicables y medidos. Sin todos los datos necesarios, el resultado es pendiente.
6. `costo_corrida = suma(costo_llamada) + cargos_adicionales_verificados`. Registrar generación y consolidación por separado si requieren distintas interacciones.
7. `proyeccion_anual = suma(costo_medido_por_tipo × frecuencia_anual_documentada_por_tipo)`. La frecuencia es una hipótesis explícita si aún no fue observada. Separar infraestructura fija, tiempo humano y licencias; no convertir monedas sin tasa/fecha documentada.

Los campos están preparados en los [registros de corridas](../corridas/README.md). Las tres plantillas conservan tokens, precio, frecuencia y costo en `null`. Un escenario hipotético futuro debe rotularse como estimación, nunca como costo real del proyecto.

## Criterio económico pendiente

El beneficio esperado es reducir preparación manual y errores de devolución manteniendo revisión humana. Para evaluarlo se necesitan tiempos comparables, calidad, retrabajo y costos autorizados. Los tests técnicos prueban comportamiento, no productividad ni ahorro económico.
