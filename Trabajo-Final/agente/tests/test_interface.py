import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

PACKAGE=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('academic_cli',PACKAGE/'agente/cli.py')
cli=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


def tamper(path):
    with ZipFile(path) as z:
        data={n:z.read(n) for n in z.namelist()}
    name='xl/worksheets/sheet2.xml'
    root=ET.fromstring(data[name])
    ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    cell=next(c for c in root.iter(ns+'c') if c.get('r')=='H2')
    cell.find(ns+'v').text='999999'
    data[name]=ET.tostring(root,encoding='utf-8')
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        for n,value in data.items():
            z.writestr(n,value)


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (PACKAGE/'ejecuciones').mkdir(exist_ok=True)
        cls.temp=tempfile.TemporaryDirectory(dir=PACKAGE/'ejecuciones')
        cls.base=Path(cls.temp.name)
        cls.env=patch.dict(os.environ,{'SALARY_REVIEW_PASSWORD':'DEMO-only'})
        cls.env.start()
        cls.generated=cls.base/'generated'
        cls.result=cli.execute('generate',cls.generated,synthetic_data=True)
        if cls.result['estado']!='GENERATED_WITH_EXCEPTIONS':
            raise AssertionError(cls.result)

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        cls.temp.cleanup()

    def test_verify_cli_json(self):
        result=subprocess.run([sys.executable,str(PACKAGE/'agente/cli.py'),'verify'],capture_output=True,text=True,check=True)
        report=json.loads(result.stdout)
        self.assertEqual(report['estado'],'REFERENCES_VERIFIED')
        self.assertFalse(report['llm_invocado'])
        self.assertEqual(len(report['referencias']),8)

    def test_report_truthful_and_payrolls(self):
        self.assertFalse(self.result['llm_invocado'])
        for field in ['modelo','tokens','costo_llm']:
            self.assertIsNone(self.result[field])
        self.assertEqual(self.result['estado_aprobacion'],'PENDING_HUMAN_APPROVAL')
        self.assertEqual({r['pool']:r['final_payroll'] for r in self.result['budgets']},
                         {'Team Alpha':11520000,'Team Beta':10736500,'Team Gamma':9322000,'Leadership':14038500})
        self.assertEqual(len(self.result['archivos_revision']),4)
        self.assertTrue(all(not r['enviado'] for r in self.result['archivos_revision']))
        self.assertTrue(any(e['flag']=='MARKET_DATA_MISSING' for e in self.result['excepciones']))

    def test_runtime_copies_exact_bytes(self):
        for name,source in cli.references('agente/v4_referencias.json').items():
            self.assertEqual(source.read_bytes(),(self.generated/'runtime/v4'/name).read_bytes())
        for entry in self.result['inputs_procesados']:
            self.assertEqual(Path(entry['origen']).read_bytes(),Path(entry['copia_utilizada']).read_bytes())
            self.assertEqual(entry['sha256'],cli.sha(entry['copia_utilizada']))

    def test_consolidation_zero_adjustment_is_not_human_approval(self):
        result=cli.execute('consolidate',self.base/'consolidated',synthetic_data=True,
                           original=self.generated/'artifacts',reviewed=self.generated/'artifacts')
        self.assertEqual(result['estado'],'CONSOLIDATED_WITH_EXCEPTIONS')
        self.assertEqual(result['estado_aprobacion'],'PENDING_HUMAN_APPROVAL')
        self.assertEqual({r['pool']:r['final_payroll'] for r in result['budgets']},
                         {r['pool']:r['final_payroll'] for r in self.result['budgets']})

    def test_tampered_review_rejected(self):
        reviewed=self.base/'tampered'
        reviewed.mkdir()
        for name in ['team_L-A.xlsx','team_L-B.xlsx','team_L-C.xlsx','leadership_review.xlsx']:
            shutil.copyfile(self.generated/'artifacts'/name,reviewed/name)
        tamper(reviewed/'team_L-A.xlsx')
        result=cli.execute('consolidate',self.base/'tampered-output',synthetic_data=True,
                           original=self.generated/'artifacts',reviewed=reviewed)
        self.assertEqual(result['estado'],'REJECTED')
        self.assertTrue(any(e['error']=='PROTECTED_FIELD_CHANGED' for e in result['excepciones']))
        self.assertEqual(result['outputs_generados'],[])

    def test_existing_output_not_overwritten(self):
        before=cli.sha(self.generated/'reporte.json')
        result=cli.execute('generate',self.generated,synthetic_data=True)
        self.assertEqual(result['estado'],'REJECTED')
        self.assertEqual(before,cli.sha(self.generated/'reporte.json'))

    def test_historical_output_path_rejected(self):
        target=PACKAGE.parent/'Entrega-2/v4/demo/forbidden-new-output'
        result=cli.execute('generate',target,synthetic_data=True)
        self.assertEqual(result['estado'],'REJECTED')
        self.assertFalse(target.exists())

    def test_synthetic_declaration_required(self):
        result=cli.execute('generate',self.base/'undeclared')
        self.assertEqual(result['estado'],'REJECTED')
        self.assertIn('SYNTHETIC_DATA',result['excepciones'][0]['error'])

    def test_password_required_and_not_logged(self):
        with patch.dict(os.environ,{'SALARY_REVIEW_PASSWORD':''}):
            result=cli.execute('generate',self.base/'no-password',synthetic_data=True)
        self.assertEqual(result['estado'],'REJECTED')
        for name in ['reporte.json','tool_invocation.json','tool_stdout.txt','tool_stderr.txt']:
            self.assertNotIn('DEMO-only',(self.generated/name).read_text(encoding='utf-8'))

    def test_alternative_synthetic_input_is_used(self):
        source=cli.references('inputs/referencias.json')['employees']
        custom=self.base/'Employees_custom.xlsx'
        shutil.copyfile(source,custom)
        with ZipFile(custom,'a') as z:
            z.comment=b'SYNTHETIC alternative input test, unchanged employee values'
        result=cli.execute('generate',self.base/'alternative',synthetic_data=True,employees=custom)
        self.assertEqual(result['estado'],'GENERATED_WITH_EXCEPTIONS')
        entry=next(r for r in result['inputs_procesados'] if r['tipo']=='employees')
        self.assertEqual(entry['sha256'],cli.sha(custom))
        self.assertNotEqual(entry['sha256'],cli.sha(source))
        self.assertEqual(Path(entry['copia_utilizada']).read_bytes(),custom.read_bytes())


if __name__=='__main__':
    unittest.main()
