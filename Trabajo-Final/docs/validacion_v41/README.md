# Validación técnica V4.1

Ejecutada después de implementar la corrección del falso positivo de Corrida 2. Son pruebas técnicas con fixtures temporales; no constituyen Corrida 3, una nueva devolución humana ni un reintento de Corrida 2.

| Suite | Resultado |
|---|---|
| Workflow V4 histórico, sin editar sus tests | 20/20 aprobados |
| Interfaz académica y equivalencia V4.1 | 26/26 aprobados (10 anteriores + 16 nuevos) |
| Los mismos 20 tests históricos contra el workflow V4.1 | 20/20 aprobados |

Total: **66 ejecuciones de tests aprobadas**, incluidas repeticiones de la suite histórica contra ambas versiones. Los 16 nuevos tests son 14 pruebas unitarias/de derivación/lectura de evidencia y 2 integraciones; una integración recorre cuatro alteraciones de fórmula manteniendo el cache anterior. La manipulación se rechaza aunque su cache no cambie.

Se verifican equivalencia Detail/Summary, rechazos por referencias, operadores, constantes y hojas distintas, comillas necesarias, strings y escapes, referencias externas/estructuradas/3D, valores no fórmula y sintaxis incompleta. La derivación del workflow se compara automáticamente con V4: sólo importación del comparador y reemplazo de la comparación no numérica.

El runner `agente/tests/run_historical_suite_v41.py` carga la variante como `workflow` y apunta ROOT al directorio histórico sólo para localizar fixtures y renderer; no escribe fuentes históricas. Las integraciones de `test_interface.py` prueban la invocación real a través del CLI y el runtime aislado V4.1.

`invocaciones.json` y los archivos stdout/stderr conservan comandos y resultados reales. `control_integridad.json` verifica SHA256 de todos los archivos versionados fuera del paquete y de todas las corridas, más los cuatro reviewed originales de trabajo. Corrida 3 conserva `PENDIENTE_NO_EJECUTADA`. No se modifica ni reinterpreta el rechazo histórico de Corrida 2.
