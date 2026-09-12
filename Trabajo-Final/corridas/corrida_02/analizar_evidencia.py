"""Read-only analysis of input workbooks and failed consolidation artifacts."""
import json
from pathlib import Path
import openpyxl
from capturar_ejecucion import E, ORIGINAL, save

def main():
    m=json.loads((ORIGINAL/'manifest.json').read_text(encoding='utf-8'))
    report=json.loads((E/'ejecucion/reporte.json').read_text(encoding='utf-8'))
    differences=[]
    proposed=[]
    strings=[]
    cached=[]
    for n,info in m['files'].items():
        w=openpyxl.load_workbook(E/'reviewed'/n,data_only=False)
        for s,expected in m['snapshots'][n].items():
            actual={c.coordinate:c.value for row in w[s] for c in row if c.value is not None}
            editable={'R'+str(i) for i in range(2,len(info['employee_ids'])+2)} if s=='Detail' else set()
            for c in set(expected)|set(actual):
                a,b=expected.get(c),actual.get(c)
                if c not in editable and a!=b:
                    only_quotes=isinstance(a,str) and isinstance(b,str) and a.replace("'Summary'!",'Summary!').replace("'Detail'!",'Detail!')==b
                    differences.append(dict(archivo=n,celda=s+'!'+c,original=a,reviewed=b,solo_comillas_referencia_hoja=only_quotes))
        for i,p in enumerate(m['proposals'][info['group']],2):
            proposed.append(dict(archivo=n,employee_id=p['Employee_ID'],salario_sin_cambio=w['Detail'][f'Q{i}'].value==p['New_Salary'],aumento_sin_cambio=w['Detail'][f'P{i}'].value==p['Total_Increase_Pct'],compa_original=p['Final_Compa_Ratio'],nota_compa='No hay columna Proposed Compa Ratio separada en reviewed; manifest original intacto, no se produjo consolidado para compararla.'))
        orig=openpyxl.load_workbook(ORIGINAL/n,data_only=False)
        old={c.value for s in orig for row in s for c in row if isinstance(c.value,str) and not c.value.startswith('=')}
        new={c.value for s in w for row in s for c in row if isinstance(c.value,str) and not c.value.startswith('=')}
        strings.append(dict(archivo=n,nuevos_textos_no_formula=sorted(new-old),dataset=w['Summary']['B2'].value))
        orig.close();w.close()
        w=openpyxl.load_workbook(E/'reviewed'/n,data_only=True)
        summary={r[0]:r[1] for r in w['Summary'].values}
        rows=list(w['Detail'].values)
        cached.append(dict(archivo=n,fuente='Valores cacheados del archivo reviewed guardado por Excel; no resultado de consolidación ni validación del agente',summary=summary,a001=next((dict(zip(rows[0],r)) for r in rows[1:] if r[0]=='A001'),None)))
        w.close()
    save(E/'diferencias_protegidas.json',sorted(differences,key=lambda x:(x['archivo'],x['celda'])))
    save(E/'validacion_proposed.json',proposed)
    save(E/'observaciones_cache_excel.json',cached)
    save(E/'control_datos_sinteticos.json',dict(procedencia='Mismos master, manifest e inputs sintéticos de corrida_01; tres reviewed idénticos y uno con ajuste humano y cambios de serialización de fórmulas.',archivos=strings,
        datos_salariales_reales_detectados=False,alcance='Verificación de procedencia, etiquetas y ausencia de nuevos textos de negocio en celdas. No constituye un detector universal de confidencialidad.',
        metadata='El archivo guardado en Excel contiene metadatos de autor/última modificación. Se preservan en la copia exacta; no se usan para autenticar al revisor ni atribuir L-A a una identidad real.'))
    r=json.loads((E/'registro.json').read_text(encoding='utf-8'))
    r.update(validaciones=dict(proposed_reviewed_conservado=all(x['salario_sin_cambio'] and x['aumento_sin_cambio'] for x in proposed),campos_protegidos_sin_cambios=False,diferencias_protegidas=len(differences),consolidado_generado=False,final_validado=None,budgets_recalculados_por_consolidacion=False,motivo='REJECTED antes de calcular Final y budgets; observaciones de cache Excel se registran por separado.'),
        observaciones_cache_excel='observaciones_cache_excel.json',archivos_evidencia_herramienta=[dict(archivo='ejecucion/'+p.relative_to(E/'ejecucion').as_posix()) for p in sorted((E/'ejecucion').rglob('*')) if p.is_file()])
    save(E/'registro.json',r)

if __name__=='__main__':
    main()
