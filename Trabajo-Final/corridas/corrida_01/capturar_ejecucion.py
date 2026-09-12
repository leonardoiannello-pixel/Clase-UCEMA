"""One-shot evidence capture for the actual generate invocation; no LLM API call.

The Codex agent reads the effective prompts and chooses generate in the current
host session. This helper captures that tool invocation without modifying V4.
"""
import argparse
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

EVIDENCE = Path(__file__).resolve().parent
PACKAGE = EVIDENCE.parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_bytes((json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))


def call(command, env, prefix):
    start = now()
    result = subprocess.run(command, cwd=PACKAGE, env=env, capture_output=True, shell=False)
    end = now()
    (EVIDENCE/(prefix+'_stdout.txt')).write_bytes(result.stdout)
    (EVIDENCE/(prefix+'_stderr.txt')).write_bytes(result.stderr)
    invocation = dict(argv=command,cwd=str(PACKAGE),shell=False,inicio_utc=start,fin_utc=end,
                      exit_code=result.returncode,stdout=prefix+'_stdout.txt',stderr=prefix+'_stderr.txt')
    save(EVIDENCE/(prefix+'_invocacion.json'),invocation)
    return result, invocation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node',required=True)
    args = parser.parse_args()
    record = json.loads((EVIDENCE/'registro.json').read_text(encoding='utf-8'))
    if record['estado'] != 'PENDIENTE_NO_EJECUTADA' or (EVIDENCE/'prompts').exists():
        raise SystemExit('Evidence already exists; do not rerun over this record.')
    (EVIDENCE/'prompts').mkdir()
    (EVIDENCE/'fuentes').mkdir()
    for name in ['system_prompt.md','user_prompt.md']:
        source = PACKAGE/'prompts'/name
        target = EVIDENCE/'prompts'/name
        shutil.copyfile(source,target)
        assert sha(source)==sha(target)
        record[name.removesuffix('.md')] = dict(referencia_plantilla='../../prompts/'+name,
                     archivo_efectivamente_usado='prompts/'+name,sha256=sha(target),
                     modo_uso='Leído por el agente Codex como contrato/solicitud de tarea en la sesión actual; no reemplaza el system prompt del host.')
    for name,source in {'cli.py':PACKAGE/'agente/cli.py',
                        'contrato_herramienta.json':PACKAGE/'agente/contrato_herramienta.json',
                        'inputs_referencias.json':PACKAGE/'inputs/referencias.json',
                        'v4_referencias.json':PACKAGE/'agente/v4_referencias.json'}.items():
        shutil.copyfile(source,EVIDENCE/'fuentes'/name)
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=PACKAGE,text=True).strip()
    host = dict(host='Codex desktop',fuente_host='Contexto de la sesión de la aplicación',
                modo='Agente Codex en conversación existente, con herramienta local de procesos',
                sistema_operativo=platform.system(),python_version=platform.python_version(),
                node_version=subprocess.check_output([args.node,'--version'],text=True).strip(),
                modelo=None,input_tokens=None,cached_tokens=None,output_tokens=None,usage_metadata=None,
                motivo_metricas_null='El contexto/herramientas de esta ejecución no exponen un identificador exacto verificable del modelo ni usage de la respuesta. No se utilizan contadores de salida de herramientas como tokens del modelo.',
                llm_api_adicional_invocada=False,costo_estimado=None)
    save(EVIDENCE/'host_metadata.json',host)
    env = {**os.environ,'SALARY_NODE':args.node,'PYTHONIOENCODING':'utf-8'}
    verify, verify_invocation = call([sys.executable,str(PACKAGE/'agente/cli.py'),'verify'],env,'verificacion')
    if verify.returncode:
        raise SystemExit('Preflight failed; generate was not executed. Record remains pending.')
    # Synthetic sheet-protection password exists only in this process environment.
    # Its plaintext is never serialized, logged or committed.
    password = secrets.token_urlsafe(9)
    env['SALARY_REVIEW_PASSWORD'] = password
    run_name = 'corrida_01_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    execution = PACKAGE/'ejecuciones'/run_name
    command = [sys.executable,str(PACKAGE/'agente/cli.py'),'generate','--output',str(execution),'--synthetic-data']
    result, invocation = call(command,env,'cli')
    report_path = execution/'reporte.json'
    if not report_path.exists():
        record.update(estado='EJECUTADA_CON_FALLO',fecha_utc=invocation['inicio_utc'],
                      tool_invocations=['verificacion_invocacion.json','cli_invocacion.json'],
                      observaciones='Se invocó generate pero no existe reporte; consultar stderr. No hubo consolidación.')
        save(EVIDENCE/'registro.json',record)
        raise SystemExit('generate did not produce a report; preserve the failed invocation.')
    shutil.copytree(execution,EVIDENCE/'ejecucion',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    report = json.loads(report_path.read_text(encoding='utf-8'))
    assert sha(report_path)==sha(EVIDENCE/'ejecucion/reporte.json')
    save(EVIDENCE/'ubicaciones.json',dict(ejecucion_original=str(execution),copia_evidencia='ejecucion',
         criterio='Copias byte a byte. Los paths absolutos emitidos se conservan como evidencia, no se reescriben.',
         excluidos=['__pycache__','*.pyc']))
    inputs = []
    for entry in report['inputs_procesados']:
        staged = Path(entry['copia_utilizada'])
        archived = EVIDENCE/'ejecucion'/staged.relative_to(execution)
        assert sha(archived)==entry['sha256']
        inputs.append({**entry,'archivo_evidencia':archived.relative_to(EVIDENCE).as_posix()})
    outputs=[]
    for entry in report['outputs_generados']:
        archived=EVIDENCE/'ejecucion'/entry['archivo']
        assert sha(archived)==entry['sha256']
        outputs.append({**entry,'archivo_evidencia':archived.relative_to(EVIDENCE).as_posix()})
    record.update(estado=report['estado'],operacion='generate',ejecucion_real=True,datos='SINTETICOS',
        fecha_utc=invocation['inicio_utc'],fin_utc=invocation['fin_utc'],source_commit=revision,
        host='Codex desktop',host_metadata='host_metadata.json',modelo=None,proveedor=None,
        inputs=inputs,tool_invocations=['verificacion_invocacion.json','cli_invocacion.json','ejecucion/tool_invocation.json'],
        salida_del_agente='salida_agente.md',reporte_herramienta='ejecucion/reporte.json',
        archivos_generados=outputs,excepciones=report['excepciones'],budgets=report['budgets'],
        archivos_revision=report['archivos_revision'],estado_aprobacion=report['estado_aprobacion'],
        tokens=dict(input_total=None,input_cached=None,output=None,fuente_medicion=None,
                    motivo='Métricas de modelo no expuestas de manera verificable por este host en la corrida.'),
        costo_por_corrida=None,frecuencia_anual=None,proyeccion_anual=None,
        intervenciones_humanas=[],consolidacion_ejecutada=False,ajustes_humanos_realizados=False,
        observaciones='Ejecución real de generate coordinada por el agente Codex con datos sintéticos. No se enviaron archivos, no hubo devoluciones ni ajustes humanos. Ver OBSERVACIONES.md. El campo llm_invocado=false del CLI describe al subprocess determinístico, no niega la coordinación del agente en el host.')
    save(EVIDENCE/'registro.json',record)
    checked=0
    for path in EVIDENCE.rglob('*'):
        if not path.is_file():
            continue
        assert password.encode() not in path.read_bytes(), 'Plaintext password in evidence'
        checked+=1
        if is_zipfile(path):
            with ZipFile(path) as z:
                for name in z.namelist():
                    assert password.encode() not in z.read(name), 'Plaintext password in ZIP'
    save(EVIDENCE/'control_password.json',dict(fecha_utc=now(),archivos_revisados=checked,
         contrasena_en_claro_detectada=False,metodo='Búsqueda exacta en todos los archivos y partes descomprimidas de ZIP/XLSX antes de descartar el valor efímero.',
         aclaracion='Excel conserva un verificador de protección de hoja, no la contraseña en claro. La protección no es cifrado.'))
    print(json.dumps(dict(estado=report['estado'],inicio_utc=invocation['inicio_utc'],fin_utc=invocation['fin_utc'],
          outputs=outputs,budgets=report['budgets'],excepciones=report['excepciones'],estado_aprobacion=report['estado_aprobacion']),ensure_ascii=False,indent=2))
    return result.returncode


if __name__=='__main__':
    raise SystemExit(main())
