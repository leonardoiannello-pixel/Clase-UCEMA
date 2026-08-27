# User Prompt V2 — Instrucción de corrida

Ejecutá la Corrida 2 — V2 usando exactamente los mismos inputs de V1: `Employees_Input.xlsx`, `Market_Data.xlsx` y `Parameters.xlsx`.

No modifiques esos archivos ni sus valores. Procesá únicamente empleados con `Population_Type = Fuera de convenio` e `Is_Leader = NO`.

Aplicá exactamente las reglas definidas en `system_prompt_v2.md`. Interpretá los valores existentes de `Market_Job_Code` como Target Market Job Code de la posición destino/post-ciclo. No incorpores reglas nuevas ni corrijas los comportamientos que permanecen fuera de alcance.

Generá:

- `Team_Alpha_Salary_Review_V2.xlsx`
- `Team_Beta_Salary_Review_V2.xlsx`
- `Team_Gamma_Salary_Review_V2.xlsx`

Guardá los outputs dentro de `Entrega-2/runs/run_2_v2/outputs/`.

No generes una V3.
