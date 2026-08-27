# Run 1 Observations — V1

## Qué funcionó

- Se procesaron 15 empleados fuera de convenio con `Is_Leader = NO`: 5 por equipo. Se excluyó 1 líder de cada equipo de payroll, budget y outputs. Pieza responsable: **2. Contexto**.
- Los tres workbooks se generaron con las hojas `Detail` y `Summary`, las columnas/campos solicitados y cálculos derivados mediante fórmulas auditables. Pieza responsable: **5. Formato**.
- Team Alpha consumió exactamente su budget de 28% con `X = 10.9701492537%`, payroll actual ARS 9.000.000, payroll protegido ARS 10.050.000 y payroll propuesto ARS 11.520.000. Pieza responsable: **4. Restricciones y reglas de negocio — Budget y cálculo de X**.
- Los límites de los tramos de mercado se aplicaron de manera consistente en Team Alpha: A001 tuvo preliminary compa-ratio 0.700 y Market Weight 2; A002, 0.800 y peso 1; A003, 0.900 y peso 0.5; A004, 1.000 y peso 0. Pieza responsable: **4. Restricciones y reglas de negocio — Mercado**.
- A005 (Team Alpha) fue clasificado como promoción: recibió Promotion Increase, Merit Weight 0 y Market Weight 1. Pieza responsable: **4. Restricciones y reglas de negocio — Movimiento, Mérito y Mercado**.
- Team Beta consumió exactamente su budget de 18% con `X = 4.0966921120%`, payroll actual ARS 9.100.000, payroll protegido ARS 9.933.000 y payroll propuesto ARS 10.738.000. Pieza responsable: **4. Restricciones y reglas de negocio — Budget y cálculo de X**.
- B002 (Team Beta) fue clasificado como progresión: recibió Progression Increase y Merit Weight 0. Pieza responsable: **4. Restricciones y reglas de negocio — Movimiento y Mérito**.
- B004 (Team Beta) tiene `MKT_MISSING`: la referencia y los compa-ratios quedaron vacíos, Market Weight y Market Increase quedaron en 0, y se generó `MARKET_DATA_MISSING`. Pieza responsable: **4. Restricciones y reglas de negocio — Mercado**.
- Team Gamma activó correctamente el caso de budget insuficiente: payroll protegido ARS 9.322.000 frente a máximo ARS 8.800.000; `X = 0`; excepción requerida `YES`; monto adicional ARS 522.000; 6.525 puntos porcentuales adicionales. Pieza responsable: **4. Restricciones y reglas de negocio — Budget insuficiente**.
- No se detectaron errores de fórmula `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?` ni `#N/A` en los outputs. Las hojas fueron renderizadas y revisadas visualmente; títulos, encabezados, cifras y flags resultaron visibles. Pieza responsable: **5. Formato**.

## Qué no funcionó o produjo resultados dudosos

- Los salarios, porcentajes y `X` conservan precisión completa porque V1 no define una regla de redondeo. Esto produce importes con centavos y porcentajes con varios decimales, por ejemplo en A001–A003 y B001–B004. No se corrigió. Pieza responsable: **4. Restricciones y reglas de negocio — Reglas deliberadamente no definidas en V1**.
- El compa-ratio final supera 1.000 para A003 (Team Alpha, 1.129) y B003 (Team Beta, 1.035). V1 prohíbe agregar un tope a 1.00, por lo que no se corrigió. Pieza responsable: **4. Restricciones y reglas de negocio — Reglas deliberadamente no definidas en V1**.
- En Team Gamma, `Budget_Available_For_Merit_And_Market` aparece como ARS -522.000. El contrato pide informar ese campo y define el exceso, pero no especifica si “available” debe truncarse a cero cuando el budget protegido ya fue excedido. Se mantuvo la diferencia aritmética verificable. Pieza responsable: **5. Formato**, en interacción con **4. Budget insuficiente**.
- `BUDGET_INSUFICIENTE` se muestra en el `Flag` de los cinco empleados de Team Gamma (C001, C002, C003, C004 y C005). El contrato exige generar el flag y provee una columna `Flag`, pero no define si una excepción de equipo debe marcar cada fila o sólo el resumen. Se mantuvo el flag a nivel de cada fila elegible. Pieza responsable: **5. Formato**, en interacción con **4. Budget insuficiente**.

No se creó una V2 ni se modificaron las reglas para resolver estos hallazgos.
