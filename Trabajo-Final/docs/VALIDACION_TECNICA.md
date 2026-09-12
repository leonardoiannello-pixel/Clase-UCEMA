# Validación técnica del paquete académico

Validaciones realizadas el 2026-09-12 con datos exclusivamente sintéticos y el runtime local disponible. Son pruebas de software, **no tres corridas instrumentadas del agente final**. No se registró uso de LLM en estas pruebas ni costo por tokens.

| Suite | Comando desde Trabajo-Final | Resultado registrado |
|---|---|---|
| V4 original, sin edición | `python -m unittest discover -s ../Entrega-2/v4/tests -v` | 20 tests aprobados |
| Interfaz académica | `python -m unittest discover -s agente/tests -v` | 10 tests aprobados |

Logs: [V4](validacion/v4_tests.txt) e [interfaz](validacion/interfaz_tests.txt). Se sustituyeron únicamente prefijos de directorios temporales locales por un marcador en el log de V4; no se alteraron resultados ni se agregaron métricas. Los logs originales del repositorio V4 no se tocaron.

## Cobertura relevante

La suite V4 conserva regresión contra los archivos históricos V3, protección de hojas, única columna editable, separación de líderes, floor, cap tras redondeo, budgets inválidos, hash de Parameters, semántica Proposed/Final, rechazo de manipulación y recálculo de Excel con Artifact Tool.

La suite de la interfaz comprueba:

- JSON CLI verificable y ausencia de invocación LLM;
- generación con payrolls sintéticos iguales a la demo;
- copias de código e inputs idénticas byte a byte;
- consolidación de ajuste cero que permanece pendiente de aprobación;
- rechazo de un salario protegido manipulado;
- rechazo de directorio existente y escritura en evidencia histórica;
- declaración de datos sintéticos y contraseña por entorno;
- contraseña ausente de reportes/logs;
- uso efectivo de un input sintético alternativo con hash distinto.

| Pool | Payroll propuesto y final en prueba de ajuste cero (ARS) |
|---|---:|
| Team Alpha | 11.520.000 |
| Team Beta | 10.736.500 |
| Team Gamma | 9.322.000 |
| Leadership | 14.038.500 |

Gamma continúa con exceso de 522.000; B004 conserva referencia de mercado faltante. La prueba con archivos originales como devolución está rotulada como técnica, no como intervención humana. Las salidas temporales de tests no se agregan a la evidencia histórica.

## Alcance de las conclusiones

Estas pruebas acreditan los caminos cubiertos y la reproducción del dataset sintético, no calidad universal de inputs, confidencialidad, identidad, aprobación salarial ni uso productivo. El renderer se probó mediante Artifact Tool; no se afirma validación en Microsoft Excel de escritorio.

La revisión del paquete verifica además links locales, plantillas de corridas sin resultados ficticios, catálogos de procedencia y que el diff sólo agregue archivos bajo `Trabajo-Final/`. V1–V4, README previos y outputs existentes permanecen intactos.
