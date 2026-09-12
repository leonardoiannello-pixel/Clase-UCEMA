# Inputs del ciclo

El catálogo [referencias.json](referencias.json) identifica los tres Excel sintéticos y su SHA256. No se duplican los binarios: la interfaz los encuentra automáticamente desde este catálogo en el mismo clon del repositorio.

| Entrada | Archivo original | Contenido necesario |
|---|---|---|
| Employees | [Employees_Input.xlsx](../../Entrega-2/inputs/Employees_Input.xlsx) | IDs, equipo, líder asignado, población, moneda, salario junio, posiciones actual/destino, rating y código de mercado destino |
| Market | [Market_Data.xlsx](../../Entrega-2/inputs/Market_Data.xlsx) | Código de mercado, referencia salarial sintética y moneda |
| Parameters | [Parameters.xlsx de V4](../../Entrega-2/v4/inputs/Parameters.xlsx) | General, Promotion, Progression, alcance, budgets por equipo, límites discrecionales y budget Leadership |

La demo contiene 18 personas sintéticas: 15 empleados y 3 líderes. `CEO001` es un identificador sintético de routing; no acredita identidad ni autoridad real. Los límites -5%/+5% y el budget Leadership 20% son valores DEMO ya existentes, pendientes de ratificación de negocio.

La interfaz admite rutas alternativas mediante `--employees`, `--market` y `--parameters`, siempre con la misma estructura V4 y declaración `--synthetic-data`. Copia los bytes recibidos al área de ejecución, registra su origen y hash y no edita parámetros. La declaración de datos sintéticos no es un detector de información confidencial.

Para evaluación se recomienda usar el catálogo sin cambios. Para otro caso sintético, crear archivos nuevos fuera de la evidencia histórica. No subir salarios reales a este repositorio público.
