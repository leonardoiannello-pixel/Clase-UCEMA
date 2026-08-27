# Run 2 Observations — V2

## 1. Problema que V2 intentaba corregir

En V1, la banda y el peso de mercado se determinaban a partir de `Preliminary_Compa_Ratio`, después de componentes protegidos pero antes del mérito. Por eso el componente de mercado podía continuar asignándose aunque el mérito ya hubiese cerrado o superado el gap contra mercado. A003 y B003 terminaron por encima de compa-ratio 1 con una porción de aumento de mercado que ya no era necesaria.

V2 evalúa la banda después del mérito y limita el aumento de mercado al gap individual que todavía existe en ese momento.

## 2. Única pieza modificada

La única pieza del contrato modificada fue **4. Restricciones y reglas de negocio**, específicamente **Mercado** y la adaptación indispensable del **cálculo de X** para considerar bandas posteriores al mérito y caps individuales. Rol, Contexto general, Tarea, Formato y Ejemplos se mantuvieron, salvo referencias textuales mínimas para hacer inequívoca la nueva regla.

## 3. Significado de Market_Job_Code

V2 aclara explícitamente que `Market_Job_Code` representa la posición destino/post-ciclo correspondiente a `New_Rank` y `New_Grade`. Los valores existentes se interpretaron como Target Market Job Code. Todos los compa-ratios de decisión se calcularon contra esa referencia destino.

## 4. Inputs sin modificaciones

Se reutilizaron exactamente los mismos archivos y valores de V1. No se renombró ni modificó ningún input.

- `Employees_Input.xlsx` — SHA-256 `FFBE3DE403520874924BD4A696E3A78A5A76DFBC46790AB668248E03C64AF628`
- `Market_Data.xlsx` — SHA-256 `8C49C32E823ED0A788421CC7D535845CF1EFE8A688B3B2D9B0E202EFEBF56079`
- `Parameters.xlsx` — SHA-256 `CADE3214D9A53198C81B760CA19023F1F07ED30F5329BAF235825D5E2110DF54`

## 5–7. Comparación individual

Para hacer comparable V1, `Compa_Ratio_Before_Market` se reconstruyó como salario después de componentes protegidos y mérito, dividido por la referencia WTW. En V2 es el compa-ratio que determina la banda de mercado.

| Employee / versión | Merit Increase % | Market Increase % | Compa Ratio Before Market | Final Compa Ratio |
|---|---:|---:|---:|---:|
| A003 — V1 | 21.9402985075% | 5.4850746269% | 1.082835821 | 1.128544776 |
| A003 — V2 | 23.5199999998% | 0.0000000000% | 1.096000000 | 1.096000000 |
| B003 — V1 | 8.1933842239% | 2.0483460560% | 1.016692112 | 1.034615140 |
| B003 — V2 | 8.6559139783% | 0.0000000000% | 1.020739247 | 1.020739247 |

### A003 — Team Alpha

V2 eliminó el aumento de mercado porque el mérito ya llevaba el compa-ratio antes de mercado a 1.096. El empleado sigue por encima de 1 exclusivamente por mérito, comportamiento permitido expresamente por V2. El compa-ratio final bajó de 1.128545 a 1.096000.

### B003 — Team Beta

V2 eliminó el aumento de mercado porque el mérito ya llevaba el compa-ratio antes de mercado a 1.020739. El empleado sigue por encima de 1 exclusivamente por mérito, comportamiento permitido expresamente por V2. El compa-ratio final bajó de 1.034615 a 1.020739.

## 8. X por equipo

| Team | X V1 | X V2 | Cambio |
|---|---:|---:|---:|
| Team Alpha | 10.9701492537% | 11.7599999999% | +0.7898507462 pp |
| Team Beta | 4.0966921120% | 4.3279569891% | +0.2312648772 pp |
| Team Gamma | 0.0000000000% | 0.0000000000% | 0.0000000000 pp |

La búsqueda de V2 dividió el dominio de `X` por los puntos de cruce de bandas de cada empleado y aplicó búsqueda binaria dentro de cada tramo continuo. El valor final se desplazó `1e-12` hacia abajo para evitar que la aritmética de punto flotante superara técnicamente el maximum payroll; esto no constituye una regla de redondeo.

## 9. Payroll final por equipo

| Team | Payroll final V1 | Payroll final V2 | Maximum Payroll |
|---|---:|---:|---:|
| Team Alpha | ARS 11,520,000.00 | ARS 11,519,999.999987502 | ARS 11,520,000.00 |
| Team Beta | ARS 10,738,000.00 | ARS 10,737,999.999981401 | ARS 10,738,000.00 |
| Team Gamma | ARS 9,322,000.00 | ARS 9,322,000.00 | ARS 8,800,000.00 |

## 10. Validación de budgets

- Team Alpha: budget respetado; queda un remanente técnico de ARS 0.000012498.
- Team Beta: budget respetado; queda un remanente técnico de ARS 0.000018599.
- Team Gamma: el budget no puede respetarse porque los componentes protegidos exceden el máximo por ARS 522,000. Esto ya ocurría en V1; V2 mantiene `X = 0`, no reduce componentes protegidos y conserva `BUDGET_INSUFICIENTE` y la excepción requerida.

Por lo tanto, todos los equipos con budget factible respetan su máximo. Gamma continúa como excepción protegida, sin cambio frente a V1.

## 11. Consecuencias inesperadas o emergentes

- Al limitar el mercado individual, parte del budget dejó de consumirse en A003 y B003. Como el objetivo sigue siendo maximizar `X`, ese espacio se redistribuyó mediante un `X` mayor para todo el equipo. Este efecto es una consecuencia directa y verificable de la nueva regla no lineal.
- A003 y B003 siguen por encima de compa-ratio 1, pero ahora exclusivamente por mérito. No se corrigió porque V2 lo permite expresamente.
- B005 continúa con compa-ratio final 1.125 sin aumento de mercado ni mérito; el nivel ya resulta del salario protegido frente a su referencia. No es causado por la nueva regla de mercado.
- El comportamiento de Team Gamma, el valor negativo de `Budget_Available_For_Merit_And_Market`, la ubicación de `BUDGET_INSUFICIENTE`, la precisión sin redondeo y los demás puntos fuera de alcance permanecieron como en V1.

No se creó una V3.
