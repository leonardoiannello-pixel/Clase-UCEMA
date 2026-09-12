"""Local tool interface. It does not call an LLM or change V4 salary rules."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parents[1]
REPOSITORY = PACKAGE.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def references(catalog):
    data = json.loads((PACKAGE/catalog).read_text(encoding='utf-8'))
    result = {}
    for key, entry in data['files'].items():
        path = (PACKAGE/entry['path']).resolve()
        content = path.read_bytes()
        checked = content.replace(b'\r\n', b'\n') if entry['hash_mode']=='lf_for_text' else content
        if hashlib.sha256(checked).hexdigest() != entry['sha256']:
            raise ValueError('REFERENCE_CHANGED: ' + key)
        result[key] = path
    return result


def verify():
    code = references('agente/v4_referencias.json')
    inputs = references('inputs/referencias.json')
    variant = references('agente/v41_referencias.json')
    return {'estado':'REFERENCES_VERIFIED', 'referencias':list(code)+list(inputs),
            'variante_consolidacion':'V4.1', 'referencias_v41':list(variant),
            'python_openpyxl_disponible':importlib.util.find_spec('openpyxl') is not None,
            'node_executable':shutil.which(os.environ.get('SALARY_NODE','node')),
            'artifact_tool':'Requiere resolución desde un node_modules ancestro del directorio de ejecución.',
            'llm_invocado':False, 'estado_aprobacion':'PENDING_HUMAN_APPROVAL'}


def ensure_new_output(path):
    path = Path(path).resolve()
    if path == REPOSITORY or path in REPOSITORY.parents:
        raise ValueError('OUTPUT_OVERLAPS_SOURCE')
    if path.is_relative_to(REPOSITORY) and not path.is_relative_to(PACKAGE/'ejecuciones'):
        raise ValueError('OUTPUT_MUST_USE_EJECUCIONES: source/evidence are read-only')
    if path.exists():
        raise ValueError('OUTPUT_ALREADY_EXISTS: choose a new execution directory')
    return path


def summary(artifacts, operation, original=None):
    import openpyxl
    exceptions, budgets, reviews = [], [], []
    mapping = [('Team Payroll June','payroll_june'),('Maximum Payroll / Budget','maximum_payroll'),
               ('Proposed Payroll','proposed_payroll'),('Final Payroll','final_payroll'),
               ('Budget Remaining','budget_remaining'),('Budget Status','budget_status')]
    if operation == 'generate':
        manifest = json.loads((artifacts/'manifest.json').read_text(encoding='utf-8'))
        exceptions = json.loads((artifacts/'generation_validation.json').read_text(encoding='utf-8'))['events']
        for name, info in manifest['files'].items():
            workbook = openpyxl.load_workbook(artifacts/name, data_only=True)
            values = {r[0]:r[1] for r in workbook['Summary'].values}
            workbook.close()
            budgets.append({'pool':info['group'], **{out:values[label] for label,out in mapping}})
            reviews.append({'archivo':name,'pool':info['group'],'reviewer_id':values['Reviewer_ID'],'enviado':False})
    else:
        log = json.loads((artifacts/'validation_exceptions.json').read_text(encoding='utf-8'))
        exceptions = log.get('errors',[]) + [r for r in log.get('reviewed_files',[]) if 'flag' in r]
        manifest = json.loads((Path(original)/'manifest.json').read_text(encoding='utf-8'))
        exceptions += [{'employee_id':e['Employee_ID'],'flag':e['Flag']} for es in manifest['proposals'].values() for e in es if e['Flag']]
        workbook = openpyxl.load_workbook(artifacts/'consolidated_final.xlsx', data_only=True)
        all_rows = list(workbook['Budgets'].values)
        workbook.close()
        for row in all_rows[1:]:
            values = dict(zip(all_rows[0],row))
            budgets.append({'pool':values['Pool'], **{out:values[label] for label,out in mapping}})
        reviews = [{'archivo':r['file'],'reviewer_id':r['reviewer_id'],'sha256':r['sha256']} for r in log['reviewed_files'] if 'file' in r]
    return exceptions, budgets, reviews


def execute(operation, output, *, synthetic_data=False, employees=None, market=None,
            parameters=None, original=None, reviewed=None):
    """The synthetic-data flag is a declaration, not a confidentiality detector."""
    report = {'estado':'NOT_EXECUTED','operacion':operation,'tipo_ejecucion':'WORKFLOW_DETERMINISTICO',
              'fecha_utc':datetime.now(timezone.utc).isoformat(),'inputs_procesados':[],
              'outputs_generados':[],'excepciones':[],'budgets':[],'archivos_revision':[],
              'estado_aprobacion':'PENDING_HUMAN_APPROVAL','proximo_paso_requerido':None,
              'llm_invocado':False,'modelo':None,'tokens':None,'costo_llm':None,
              'datos_declarados_sinteticos':synthetic_data,'confidencialidad_verificada_automaticamente':False}
    execution = None
    try:
        if operation not in ('generate','consolidate'):
            raise ValueError('UNKNOWN_OPERATION')
        if not synthetic_data:
            raise ValueError('SYNTHETIC_DATA_DECLARATION_REQUIRED')
        password = os.environ.get('SALARY_REVIEW_PASSWORD')
        if not password:
            raise ValueError('SALARY_REVIEW_PASSWORD_REQUIRED')
        code = references('agente/v4_referencias.json')
        variant = references('agente/v41_referencias.json') if operation == 'consolidate' else {}
        output = ensure_new_output(output)
        if operation == 'generate':
            defaults = references('inputs/referencias.json')
            sources = {k:Path(v).resolve() if v else defaults[k] for k,v in
                       [('employees',employees),('market',market),('parameters',parameters)]}
            for path in sources.values():
                if not path.is_file():
                    raise ValueError('INPUT_NOT_FOUND: ' + str(path))
            # Capture all input bytes before staging, including alternative synthetic inputs.
            contents = {k:p.read_bytes() for k,p in sources.items()}
        else:
            if original is None or reviewed is None:
                raise ValueError('ORIGINAL_AND_REVIEWED_REQUIRED')
            original, reviewed = Path(original).resolve(), Path(reviewed).resolve()
            if not original.is_dir() or not reviewed.is_dir():
                raise ValueError('REVIEW_DIRECTORY_NOT_FOUND')
            if not (original/'manifest.json').is_file() or not (original/'master_proposal.xlsx').is_file():
                raise ValueError('TRUSTED_ORIGINAL_MISSING')
            sources = {'original_manifest':original/'manifest.json','original_master':original/'master_proposal.xlsx'}
            sources.update({'reviewed/'+p.name:p for p in reviewed.glob('*.xlsx')})
            if any(output.is_relative_to(p) or p.is_relative_to(output) for p in [original,reviewed]):
                raise ValueError('OUTPUT_OVERLAPS_REVIEW_INPUTS')
        output.mkdir(parents=True, exist_ok=False)
        execution = output
        runtime = output/'runtime/v4'
        runtime.mkdir(parents=True)
        copied = {}
        for name,path in code.items():
            shutil.copyfile(path,runtime/name)
            if sha(path)!=sha(runtime/name):
                raise ValueError('RUNTIME_COPY_MISMATCH')
            copied[name] = {'source':str(path),'sha256':sha(runtime/name)}
        variant_copies = {}
        for name,path in variant.items():
            shutil.copyfile(path,runtime/name)
            if sha(path)!=sha(runtime/name):
                raise ValueError('RUNTIME_COPY_MISMATCH')
            variant_copies[name] = {'source':str(path),'sha256':sha(runtime/name)}
        artifacts = output/'artifacts'
        entrypoint = 'workflow_v41.py' if operation == 'consolidate' else 'workflow.py'
        command = [sys.executable,str(runtime/entrypoint),operation,'--output',str(artifacts)]
        if operation == 'generate':
            input_dir = output/'runtime/inputs'
            input_dir.mkdir()
            filenames = {'employees':'Employees_Input.xlsx','market':'Market_Data.xlsx','parameters':'Parameters.xlsx'}
            for key,content in contents.items():
                staged = input_dir/filenames[key]
                staged.write_bytes(content)
                report['inputs_procesados'].append({'tipo':key,'origen':str(sources[key]),'copia_utilizada':str(staged),'sha256':sha(staged)})
            command += ['--parameters',str(input_dir/'Parameters.xlsx')]
        else:
            report['inputs_procesados'] = [{'tipo':key,'origen':str(path),'sha256':sha(path)} for key,path in sources.items()]
            command += ['--original',str(original),'--reviewed',str(reviewed)]
        invocation = {'command':command,'shell':False,'password_source':'environment; value not recorded',
                      'v4_copies':copied,'v41_copies':variant_copies,
                      'workflow_version':'V4.1' if variant else 'V4','llm_invoked':False}
        report['workflow_version'] = invocation['workflow_version']
        write_json(output/'tool_invocation.json',invocation)
        child = subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',
                               env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        (output/'tool_stdout.txt').write_text(child.stdout.replace(password,'<redacted>'),encoding='utf-8')
        (output/'tool_stderr.txt').write_text(child.stderr.replace(password,'<redacted>'),encoding='utf-8')
        report['tool_exit_code'] = child.returncode
        if child.returncode:
            log = artifacts/'validation_exceptions.json'
            report['estado'] = 'REJECTED' if log.exists() else 'FAILED'
            if log.exists():
                report['excepciones'] = json.loads(log.read_text(encoding='utf-8')).get('errors',[])
            if not report['excepciones']:
                report['excepciones'] = [{'error':'WORKFLOW_FAILED','detalle':'Consultar tool_stderr.txt; no tratar archivos parciales como válidos.'}]
            report['proximo_paso_requerido'] = 'Responsable de Compensation/coordinador: revisar logs y corregir la causa en una ejecución nueva.'
        else:
            exceptions,budgets,reviews = summary(artifacts,operation,original)
            report.update(excepciones=exceptions,budgets=budgets,archivos_revision=reviews)
            report['estado'] = ('GENERATED' if operation=='generate' else 'CONSOLIDATED') + ('_WITH_EXCEPTIONS' if exceptions else '')
            report['outputs_generados'] = [{'archivo':str(f.relative_to(output)),'sha256':sha(f)} for f in sorted(artifacts.iterdir()) if f.suffix in ('.xlsx','.json')]
            report['proximo_paso_requerido'] = ('Compensation: resolver excepciones y verificar destinatarios; revisores: revisar archivos.' if operation=='generate'
                                              else 'Responsable de Compensation / autoridad autorizada: validar budgets y resolver la aprobación final.')
    except Exception as exc:
        report['estado'] = 'REJECTED'
        report['excepciones'].append({'error':str(exc)})
        report['proximo_paso_requerido'] = 'Coordinador: resolver la causa indicada; no se ha aprobado ningún salario.'
    if execution is not None:
        write_json(execution/'reporte.json',report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='operation',required=True)
    commands.add_parser('verify')
    for name in ['generate','consolidate']:
        cmd=commands.add_parser(name)
        cmd.add_argument('--output',required=True,type=Path)
        cmd.add_argument('--synthetic-data',action='store_true')
        if name=='generate':
            for option in ['employees','market','parameters']:
                cmd.add_argument('--'+option,type=Path)
        else:
            cmd.add_argument('--original',required=True,type=Path)
            cmd.add_argument('--reviewed',required=True,type=Path)
    args=vars(parser.parse_args())
    if args['operation']=='verify':
        try:
            report=verify()
        except Exception as exc:
            report={'estado':'REJECTED','excepciones':[{'error':str(exc)}]}
    else:
        report=execute(**args)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if report['estado'] in ('REJECTED','FAILED','NOT_EXECUTED') else 0


if __name__=='__main__':
    raise SystemExit(main())
