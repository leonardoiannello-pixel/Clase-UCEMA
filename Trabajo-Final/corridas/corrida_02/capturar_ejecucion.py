"""Capture one actual consolidation; never edit reviewed workbooks or source evidence."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import secrets
import shutil
import subprocess
import sys
from zipfile import ZipFile, is_zipfile
import openpyxl

E = Path(__file__).resolve().parent
P = E.parents[1]
R = P.parent
ORIGINAL = P/'corridas/corrida_01/ejecucion/artifacts'
REVIEWED = P/'ejecuciones/corrida_02_devoluciones_20260912T221754742175Z'
NAMES = ['team_L-A.xlsx','team_L-B.xlsx','team_L-C.xlsx','leadership_review.xlsx']

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p,v):
    Path(p).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))

def now():
    return datetime.now(timezone.utc).isoformat()

def main():
    record=json.loads((E/'registro.json').read_text(encoding='utf-8'))
    if record['estado']!='PENDIENTE_NO_EJECUTADA' or (E/'reviewed').exists():
        raise SystemExit('Existing evidence; refusing to overwrite or rerun')
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0')
    baseline={n:sha(R/n) for n in tracked if n and not n.startswith('Trabajo-Final/corridas/corrida_02/')}
    save(E/'fuentes_intactas_antes.json',baseline)
    shutil.copyfile(P/'prompts/system_prompt.md',E/'prompts/system_prompt.md')
    (E/'fuentes').mkdir()
    for n,p in {'cli.py':P/'agente/cli.py','contrato_herramienta.json':P/'agente/contrato_herramienta.json','v4_referencias.json':P/'agente/v4_referencias.json','inputs_referencias.json':P/'inputs/referencias.json'}.items():
        shutil.copyfile(p,E/'fuentes'/n)
    (E/'reviewed').mkdir()
    inputs=[]
    observations=[]
    for n in NAMES:
        src=REVIEWED/n
        shutil.copyfile(src,E/'reviewed'/n)
        assert src.read_bytes()==(E/'reviewed'/n).read_bytes()
        inputs.append(dict(archivo=n,origen=str(src),copia='reviewed/'+n,sha256=sha(src),original_sha256=sha(ORIGINAL/n),bytes_distintos_del_original=src.read_bytes()!=(ORIGINAL/n).read_bytes()))
        w=openpyxl.load_workbook(src,data_only=False)
        rows=list(w['Detail'].values)
        for row in rows[1:]:
            d=dict(zip(rows[0],row))
            observations.append(dict(archivo=n,employee_id=d['Employee_ID'],valor_observado=d['Discretionary Adjustment %']))
        w.close()
    save(E/'reviewed_inputs.json',inputs)
    save(E/'ajustes_observados.json',observations)
    human=dict(intervencion_humana_real=True,fuente_declaracion='Mensaje del usuario en esta conversación',
        archivo='team_L-A.xlsx',employee_id='A001',campo='Discretionary Adjustment %',
        valor_observado=next(x['valor_observado'] for x in observations if x['employee_id']=='A001'),
        unidad_almacenada='fracción; multiplicar por 100 para puntos porcentuales',
        origen='Edición manual en Excel fuera del agente, según declaración del usuario',
        decidida_por_agente=False,identidad_real=None,
        aclaracion='La declaración humana y el valor observado son evidencias distintas. reviewer_id es routing sintético, no autenticación ni identidad real.')
    save(E/'intervencion_humana.json',human)
    originals=[dict(archivo=n,origen=str(ORIGINAL/n),referencia='../corrida_01/ejecucion/artifacts/'+n,sha256=sha(ORIGINAL/n)) for n in ['master_proposal.xlsx','manifest.json']]
    save(E/'original_confiable.json',originals)
    node=sys.argv[1]
    host=dict(host='Codex desktop',fuente='Contexto de la aplicación en esta sesión',
        sistema_operativo=platform.system(),python_version=platform.python_version(),
        node_version=subprocess.check_output([node,'--version'],text=True).strip(),
        modelo=None,input_tokens=None,cached_input_tokens=None,output_tokens=None,usage_metadata=None,costo=None,
        motivo_null='El host no expuso modelo exacto ni métricas de uso de manera verificable para esta corrida. No se estiman costos.',
        modo_prompts='Leídos como instrucciones de tarea en la conversación existente; no sustituyen el system prompt del host. No se efectuó una nueva llamada API LLM.')
    save(E/'host_metadata.json',host)
    password=secrets.token_urlsafe(18)
    env={**os.environ,'SALARY_REVIEW_PASSWORD':password,'SALARY_NODE':node,'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1'}
    output=P/'ejecuciones'/('corrida_02_consolidacion_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    command=[sys.executable,str(P/'agente/cli.py'),'consolidate','--original',str(ORIGINAL),'--reviewed',str(REVIEWED),'--output',str(output),'--synthetic-data']
    invocation=dict(argv=command,cwd=str(P),shell=False,inicio_utc=now(),password_source='environment; value not recorded')
    child=subprocess.run(command,cwd=P,env=env,capture_output=True)
    invocation.update(fin_utc=now(),exit_code=child.returncode)
    for n,b in [('cli_stdout.txt',child.stdout),('cli_stderr.txt',child.stderr)]:
        assert password.encode() not in b
        (E/n).write_bytes(b)
    save(E/'cli_invocacion.json',invocation)
    record.update(estado='EJECUTADA_CON_FALLO',ejecucion_real=True,operacion='consolidate',fecha_utc=invocation['inicio_utc'],fin_utc=invocation['fin_utc'])
    save(E/'registro.json',record)
    if not (output/'reporte.json').exists():
        raise SystemExit('Invocation occurred but no report exists; preserve failure evidence')
    shutil.copytree(output,E/'ejecucion',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    save(E/'ubicaciones.json',dict(ejecucion_original=str(output),copia_evidencia='ejecucion',reviewed_utilizado=str(REVIEWED),original_utilizado=str(ORIGINAL),criterio='Copias byte a byte; paths emitidos conservados sin reescritura.'))
    report=json.loads((E/'ejecucion/reporte.json').read_text(encoding='utf-8'))
    record.update(estado=report['estado'],source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
        host=host['host'],modelo=None,proveedor=None,host_metadata='host_metadata.json',datos='SINTETICOS',
        system_prompt=dict(archivo_efectivamente_usado='prompts/system_prompt.md',sha256=sha(E/'prompts/system_prompt.md')),
        user_prompt=dict(archivo_efectivamente_usado='prompts/user_prompt.md',sha256=sha(E/'prompts/user_prompt.md')),
        inputs=report['inputs_procesados'],original_confiable=originals,reviewed=inputs,
        tool_invocations=['cli_invocacion.json','ejecucion/tool_invocation.json'],salida_del_agente='salida_agente.json',
        reporte_herramienta='ejecucion/reporte.json',archivos_generados=report['outputs_generados'],
        excepciones=report['excepciones'],budgets=report['budgets'],estado_aprobacion=report['estado_aprobacion'],
        tokens=dict(input_total=None,input_cached=None,output=None,usage_metadata=None,fuente_medicion=None,motivo=host['motivo_null']),
        intervenciones_humanas=[human],observaciones='Consolidación real de datos sintéticos con devolución humana preservada. Ver OBSERVACIONES.md; no se aprueban salarios.')
    save(E/'registro.json',record)
    assert all(sha(R/n)==h for n,h in baseline.items())
    assert all(sha(REVIEWED/x['archivo'])==x['sha256']==sha(E/x['copia']) for x in inputs)
    save(E/'control_integridad.json',dict(archivos_previos_verificados=len(baseline),fuentes_intactas=True,reviewed_preservados=True,metodo='SHA256 antes/después de todos los archivos versionados fuera de corrida_02 y de los cuatro reviewed.'))
    count=0
    for p in E.rglob('*'):
        if p.is_file():
            assert password.encode() not in p.read_bytes()
            count+=1
            if is_zipfile(p):
                with ZipFile(p) as z:
                    assert all(password.encode() not in z.read(n) for n in z.namelist())
    save(E/'control_password.json',dict(fecha_utc=now(),archivos_revisados=count,contrasena_en_claro_detectada=False,metodo='Búsqueda exacta del valor efímero en archivos y partes ZIP/XLSX antes de descartarlo. El verificador de protección no es contraseña en claro ni cifrado.'))
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
