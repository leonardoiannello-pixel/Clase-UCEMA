"""Extract actual output values and record the agent's observed conclusion."""
import json
from pathlib import Path
import openpyxl

E=Path(__file__).resolve().parent
def read(n):return json.loads((E/n).read_text(encoding='utf-8'))
def save(n,v):(E/n).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

report=read('ejecucion/reporte.json')
w=openpyxl.load_workbook(E/'ejecucion/artifacts/consolidated_final.xlsx',data_only=True)
rows=list(w['Final'].values);w.close()
a001=next(dict(zip(rows[0],r)) for r in rows[1:] if r[0]=='A001')
save('a001_observado.json',a001)
record=read('registro.json')
record.update(a001_observado=a001,tests=dict(invocacion='tests_invocacion.json',cantidad=8,exit_code=read('tests_invocacion.json')['exit_code'],alcance='Sólo lectura/consistencia, sin nuevas ejecuciones de workflow'),
    validaciones=dict(falsos_positivos_corrida02_no_bloquean=True,proposed_intacto=True,ajuste_solo_final=True,budgets_recalculados=True,excesos_reportados_sin_correccion=True,reviewed_mismos_bytes_corrida02=True,aprobacion_pendiente=True,contrasena_en_claro_detectada=False,soporte='test_evidencia.py, logs, control_password.json, control_integridad.json'),
    observaciones='Consolidación real V4.1 con las mismas entradas de Corrida 2. Propuesta preservada; ajuste humano existente aplicado sólo a Final; excesos reportados sin corrección. Ver OBSERVACIONES.md.')
save('registro.json',record)
save('salida_agente.json',dict(tipo='Respuesta estructurada del agente basada en los resultados observados; separada del reporte CLI, no exportación de API',
    estado=report['estado'],workflow_version=report['workflow_version'],inputs_procesados=report['inputs_procesados'],outputs_generados=report['outputs_generados'],
    excepciones=report['excepciones'],budgets=report['budgets'],archivos_revision=report['archivos_revision'],
    a001=a001,estado_aprobacion=report['estado_aprobacion'],proximo_paso_requerido=report['proximo_paso_requerido'],
    conclusion='Las 13 diferencias de comillas ya no bloquean. Mismos reviewed humanos, sin edición por el agente. Proposed conservado; excesos de Alpha y Gamma informados, sin aprobación automática.',
    host='Codex desktop',modelo=None,input_tokens=None,cached_input_tokens=None,output_tokens=None,usage_metadata=None,costo=None))
