# Agente de revisión salarial

## Qué construí

Construí con ChatGPT y Codex un agente para asistir un ciclo de revisión salarial de empleados fuera de convenio.

La idea inicial era modelar un proceso más amplio que incluyera aumentos salariales y bono anual, pero para esta entrega decidí acotar el alcance al salary review. El agente toma tres archivos Excel de input: población, referencias de mercado y parámetros del ciclo. A partir de esa información identifica promociones y progresiones, calcula aumentos protegidos, mérito y mercado, determina un valor común de `X` por equipo y genera una propuesta de aumento que respeta el budget disponible.

El modelo utiliza información de mercado asociada a la posición destino/post-ciclo. Los compa-ratios utilizados para decidir el ajuste se calculan contra esa posición futura. Los líderes están identificados en la población pero se excluyen del cálculo y del archivo de su propio equipo.

Para poder publicar y probar el proyecto sin utilizar información confidencial, trabajé con una población y referencias salariales completamente sintéticas.

## Cómo se lo pedí

El trabajo comenzó a partir de una tarea real y recurrente de Compensation: preparar propuestas de aumentos para distintos equipos respetando reglas de promoción, progresión, performance, mercado y un budget máximo de payroll.

Antes de escribir el prompt final fui acotando y formalizando el problema. La idea original incluía salary review y bono anual, pero decidí dejar el bono fuera de alcance. También limité la población a empleados fuera de convenio y definí que todos los inputs y outputs de negocio debían ser archivos Excel.

El contrato se separó en `system prompt` y `user prompt` y se estructuró con las seis piezas trabajadas en clase: rol, contexto, tarea, restricciones, formato y ejemplos.

Las principales reglas definidas fueron:

- todos los porcentajes de aumento son aditivos sobre el salario base de junio;
- General Increase, Promotion Increase y Progression Increase son componentes protegidos;
- una promoción implica cambio de rank y una progresión implica aumento de grade dentro del mismo rank;
- si una persona recibe promoción o progresión no recibe aumento de mérito;
- el mérito depende del performance rating y de un valor `X` común a cada equipo;
- el ajuste de mercado depende del compa-ratio contra la referencia WTW de la posición destino;
- el valor `X` se calcula para utilizar el máximo budget posible sin exceder el payroll autorizado;
- si los componentes protegidos ya exceden el budget, `X = 0` y se informa la excepción;
- los líderes se excluyen del payroll y del budget de su propio equipo.

Para probar el agente construí tres archivos Excel sintéticos con 18 registros: 15 empleados y 3 líderes. La población fue diseñada deliberadamente para incluir casos normales y casos límite: promociones, progresiones, ratings de 1 a 5, distintos tramos de compa-ratio, valores exactamente en los límites 0.70, 0.80, 0.90 y 1.00, una referencia de mercado faltante, un equipo con budget cómodo, uno ajustado y otro donde los aumentos protegidos ya superaban el budget.

Ejecuté tres corridas sobre exactamente los mismos inputs para poder comparar los resultados.

### Corrida 1 — V1

La primera versión aplicó la lógica básica de promociones, progresiones, mérito, mercado y budget.

La corrida confirmó que el agente podía procesar la población, excluir líderes, identificar movimientos, detectar una referencia de mercado faltante y calcular un `X` por equipo. También detectó correctamente un equipo donde los componentes protegidos excedían el budget.

La prueba mostró, sin embargo, que algunos empleados podían seguir recibiendo ajuste de mercado aunque el mérito ya hubiera cerrado o superado el gap contra mercado. También aparecieron valores con una precisión excesiva: salarios con centavos, porcentajes con muchos decimales y diferencias técnicas mínimas de budget.

### Iteración 1 — V2

Para la primera iteración modifiqué una sola pieza del contrato: **Restricciones y reglas de negocio — Mercado**.

Primero aclaré una regla que había quedado ambigua: `Market_Job_Code` representa siempre la posición destino/post-ciclo. Por lo tanto, si una persona es promovida, todos los compa-ratios utilizados para decidir el ajuste se calculan contra la referencia de la nueva posición.

Además, cambié la lógica para que el ajuste de mercado se determine después de considerar el mérito. Market sólo puede cubrir el gap que todavía existe contra compa-ratio 1.00 y nunca puede ser la causa de que el empleado supere la referencia de mercado.

La consecuencia fue que casos como A003 y B003 dejaron de recibir aumento de mercado cuando el mérito ya los había llevado por encima de compa-ratio 1. El espacio de budget liberado se redistribuyó mediante un `X` mayor para el resto del equipo.

### Iteración 2 — V3

Para la segunda iteración volví a modificar solamente **Restricciones y reglas de negocio**, agregando una política explícita de redondeo y precisión.

Definí que:

- todos los salarios finales deben ser múltiplos exactos de ARS 100;
- los porcentajes de aumento y `X` deben tener como máximo dos decimales;
- los compa-ratios mantienen tres decimales;
- el budget debe validarse contra los salarios finales ya redondeados;
- si el redondeo de `X` provoca un exceso de budget, `X` se reduce en pasos de 0.01 puntos porcentuales hasta encontrar el máximo valor que respete el límite;
- el redondeo de Market nunca puede violar el cap individual de mercado.

Esta corrida eliminó los decimales técnicos y produjo archivos más utilizables. Team Alpha consumió exactamente su budget y Team Beta quedó con un remanente de ARS 1.500 porque `X = 4.33%` excedía el límite después del redondeo y tuvo que reducirse a `4.32%`.

Los prompts completos utilizados en cada corrida se encuentran en la carpeta [prompts](prompts), preservados textualmente para permitir la trazabilidad de las iteraciones.

- [system_prompt_v1.md](prompts/system_prompt_v1.md)
- [user_prompt_v1.md](prompts/user_prompt_v1.md)
- [system_prompt_v2.md](prompts/system_prompt_v2.md)
- [user_prompt_v2.md](prompts/user_prompt_v2.md)
- [system_prompt_v3.md](prompts/system_prompt_v3.md)
- [user_prompt_v3.md](prompts/user_prompt_v3.md)

## Qué funciona

La versión V3 procesa los tres equipos utilizando exclusivamente archivos Excel como inputs y outputs.

El agente:

- excluye correctamente a los líderes de la población y del budget de su propio equipo;
- identifica promociones y progresiones;
- aplica componentes protegidos;
- calcula mérito según performance;
- calcula posición de mercado contra la referencia de la posición destino;
- evita que el componente de mercado lleve a una persona por encima de la referencia;
- detecta referencias de mercado faltantes sin inventar información;
- calcula el máximo `X` compatible con el budget;
- identifica cuando los componentes protegidos exceden el budget y calcula la excepción requerida;
- genera un workbook por equipo con hojas `Detail` y `Summary`;
- genera salarios finales múltiplos de ARS 100;
- mantiene porcentajes con un máximo de dos decimales;
- valida el budget usando los salarios finales redondeados.

Los mismos inputs se mantuvieron sin modificaciones durante las tres corridas para que los cambios pudieran atribuirse a las modificaciones del prompt y no a cambios en los datos.

## Qué falta o qué falló

Quedaron deliberadamente fuera del alcance de esta entrega algunas funcionalidades que serían necesarias para utilizar el proceso completo en un ciclo real.

En una siguiente etapa quiero incorporar una columna de ajuste discrecional para que cada líder pueda redistribuir parte del aumento entre sus empleados sin exceder el budget total. El archivo debería mostrar en tiempo real cuánto budget queda disponible o cuánto se excedió.

También quiero que los archivos enviados a los líderes estén protegidos contra modificación, dejando editable únicamente la columna de ajuste discrecional, y que requieran contraseña para abrirlos.

La población incluye a los líderes, pero ellos no deberían definir su propio salario. En una versión posterior el proceso deberá generar cortes individuales por equipo excluyendo al propio líder y un archivo separado para el CEO con las propuestas de todos los líderes, utilizando un budget específico para ese grupo.

La V3 mantiene además algunos comportamientos detectados durante las pruebas que no eran necesarios para validar el objetivo de esta entrega, por ejemplo el tratamiento visual del budget disponible negativo en un equipo cuyo budget protegido ya fue excedido y la ubicación del flag `BUDGET_INSUFICIENTE`.

## Qué aprendí

El principal aprendizaje fue que una tarea que para una persona de Compensation parece tener reglas conocidas contiene muchas decisiones implícitas que deben convertirse en instrucciones explícitas para que un agente pueda ejecutarla de manera consistente.

La primera versión no falló porque el modelo no pudiera hacer los cálculos, sino porque la especificación todavía dejaba abiertas preguntas importantes: qué referencia de mercado usar después de una promoción, en qué momento medir el compa-ratio, cómo limitar el ajuste de mercado y cómo tratar la precisión y el redondeo.

Trabajar con el mismo dataset en tres corridas permitió ver con claridad el efecto de cada modificación. En lugar de reescribir el prompt completo ante cada problema, fui cambiando una sola parte del contrato, ejecutando nuevamente el mismo caso y comparando los resultados.

También entendí que un output matemáticamente correcto no necesariamente es un output utilizable. Reglas operativas como redondear salarios, limitar decimales y validar el budget después del redondeo son parte de la especificación del entregable y no simples detalles de presentación.

Finalmente, el ejercicio mostró la utilidad de diseñar datos sintéticos con casos límite conocidos. Eso permitió probar el comportamiento del agente sin exponer información salarial real y detectar problemas que probablemente no hubieran aparecido con un ejemplo demasiado simple.
