# Run 3 Observations — V3

## 1. Problema de precisión detectado en V2

V2 era matemáticamente correcta, pero almacenaba `X`, porcentajes, salarios y payrolls con numerosos decimales. Alpha y Beta mostraban remanentes técnicos de budget del orden de fracciones mínimas de peso. Ese nivel de precisión no era utilizable en un proceso real de Compensation.

## 2. Única pieza modificada

La única pieza conceptual modificada fue **4. Restricciones y reglas de negocio**, mediante la nueva subsección **Redondeo y precisión**. Se mantuvieron sin cambios las reglas V2 de movimientos, componentes protegidos, mérito, referencia destino/post-ciclo, bandas y cap de mercado, budget, líderes y estructura principal de los outputs.

Los inputs y sus valores no fueron modificados:

- `Employees_Input.xlsx` — SHA-256 `FFBE3DE403520874924BD4A696E3A78A5A76DFBC46790AB668248E03C64AF628`
- `Market_Data.xlsx` — SHA-256 `8C49C32E823ED0A788421CC7D535845CF1EFE8A688B3B2D9B0E202EFEBF56079`
- `Parameters.xlsx` — SHA-256 `CADE3214D9A53198C81B760CA19023F1F07ED30F5329BAF235825D5E2110DF54`

## 3. X por equipo — V2 vs V3

| Team | X V2 | X V3 | Ajuste posterior al redondeo |
|---|---:|---:|---|
| Team Alpha | 11.7599999999% | 11.76% | Ninguno |
| Team Beta | 4.3279569891% | 4.32% | El 4.33% inicial excedía el budget; se redujo 0.01 pp |
| Team Gamma | 0.0000000000% | 0.00% | Ninguno; budget insuficiente protegido |

## 4. Payroll final — V2 vs V3

| Team | Payroll V2 | Payroll V3 | Maximum Payroll | Remanente/exceso V3 |
|---|---:|---:|---:|---:|
| Team Alpha | ARS 11,519,999.999987502 | ARS 11,520,000 | ARS 11,520,000 | ARS 0 |
| Team Beta | ARS 10,737,999.999981401 | ARS 10,736,500 | ARS 10,738,000 | ARS 1,500 |
| Team Gamma | ARS 9,322,000 | ARS 9,322,000 | ARS 8,800,000 | ARS -522,000 |

## 5. Control New_Salary MOD 100

Se incorporó un bloque explícito de control en cada hoja `Summary`:

| Team | Control_New_Salary_MOD_100 | Employees_Failing_MOD_100 |
|---|---|---:|
| Team Alpha | PASS | 0 |
| Team Beta | PASS | 0 |
| Team Gamma | PASS | 0 |

La fórmula controla cada empleado mediante `MOD(New_Salary,100)`. Los 15 `New_Salary` son múltiplos exactos de ARS 100 y no contienen centavos.

## 6. Control de porcentajes

Todos los porcentajes visibles y almacenados en los outputs V3 tienen como máximo dos decimales: General, Promotion, Progression, Protected, X, Merit, Market, Total Increase efectivo, Team Budget, Proposed Payroll Increase y Additional Budget Required en puntos porcentuales.

Los compa-ratios conservan tres decimales de formato, según lo solicitado, y `Final_Compa_Ratio` utiliza el salario final redondeado.

## 7. Budgets después del redondeo

- Alpha: factible y respetado exactamente; payroll ARS 11,520,000 = máximo ARS 11,520,000.
- Beta: factible y respetado; payroll ARS 10,736,500 < máximo ARS 10,738,000.
- Gamma: continúa la excepción preexistente. Los componentes protegidos generan ARS 9,322,000 frente a un máximo de ARS 8,800,000. Se mantuvieron `X = 0`, Merit = 0, Market = 0 y `BUDGET_INSUFICIENTE`.

Todos los budgets factibles respetan el máximo utilizando los salarios finales redondeados, no los salarios teóricos.

## 8. Reducción de X por efecto del redondeo

Sólo Team Beta requirió reducción. El máximo continuo de V2 redondeaba convencionalmente a 4.33%, pero ese valor hacía que el payroll de salarios finales redondeados superara el máximo. Se redujo un paso de 0.01 puntos porcentuales hasta `X = 4.32%`, dejando ARS 1,500 de budget disponible.

Alpha aceptó directamente `X = 11.76%`. Gamma permaneció en cero por budget insuficiente.

## 9. Market Increase redondeado hacia abajo por cap

Ningún empleado requirió redondeo hacia abajo de `Market_Increase_Pct` para respetar su `Market_Gap_Pct`. En todos los casos con aumento de mercado, el valor redondeado convencionalmente quedó por debajo del gap individual. La fórmula conserva la protección mediante el menor entre el aumento convencional y el gap redondeado hacia abajo.

## 10. A003 y B003

| Employee | X V3 | Merit Increase V3 | Market Increase V3 | Compa Ratio Before Market | Final Compa Ratio |
|---|---:|---:|---:|---:|---:|
| A003 — Team Alpha | 11.76% | 23.52% | 0.00% | 1.096 | 1.096 |
| B003 — Team Beta | 4.32% | 8.64% | 0.00% | 1.021 | 1.021 |

A003 y B003 continúan sin recibir aumento de mercado porque ya están por encima de compa-ratio 1 después del mérito. La leve diferencia entre compa-ratio antes de mercado y final se debe exclusivamente al redondeo del salario a ARS 100, no a un componente de mercado.

## 11. Consecuencias inesperadas

- La granularidad discreta de `X` y salarios impidió utilizar exactamente todo el budget de Beta: quedó un remanente de ARS 1,500. No se ajustaron salarios individuales para consumirlo.
- El `Proposed_Payroll_Increase_Pct` de Beta pasó a 17.98%, aunque el budget máximo continúa siendo 18.00%.
- En Gamma, el aumento efectivo de payroll se almacena como 16.52% y el budget adicional requerido como 6.53 puntos porcentuales por la política de dos decimales. Los importes monetarios autoritativos permanecen ARS 9,322,000 y ARS 522,000.
- No aparecieron violaciones del cap de mercado, salarios con centavos ni diferencias técnicas de budget por punto flotante.

No se creó una V4, no se agregaron funcionalidades fuera de alcance y no se realizaron cambios ni push en GitHub.
