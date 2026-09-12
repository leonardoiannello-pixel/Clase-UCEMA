"""Read-only checks of this actual run; no workflow executions or workbook writes."""
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import unittest
import openpyxl

E=Path(__file__).resolve().parent
R=E.parents[2]
def read(n): return json.loads((E/n).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p,sheet):
    w=openpyxl.load_workbook(p,data_only=True)
    values=list(w[sheet].values);w.close()
    return [dict(zip(values[0],r)) for r in values[1:] if r[0] is not None]

class RunEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=read('ejecucion/reporte.json')
        cls.final=rows(E/'ejecucion/artifacts/consolidated_final.xlsx','Final')
        cls.manifest=read('../corrida_01/ejecucion/artifacts/manifest.json')

    def test_real_execution_version_and_outputs(self):
        self.assertEqual(read('cli_invocacion.json')['exit_code'],0)
        self.assertEqual(self.report['estado'],'CONSOLIDATED_WITH_EXCEPTIONS')
        self.assertEqual(self.report['workflow_version'],'V4.1')
        self.assertEqual(read('cli_stdout.txt'),self.report)
        inv=read('ejecucion/tool_invocation.json')
        self.assertTrue(inv['command'][1].endswith('workflow_v41.py'))
        for group in ['v4_copies','v41_copies']:
            for n,info in inv[group].items():
                self.assertEqual(sha(E/'ejecucion/runtime/v4'/n),info['sha256'])
                self.assertEqual(sha(Path(info['source'])),info['sha256'])
        for out in self.report['outputs_generados']:
            self.assertEqual(sha(E/'ejecucion'/out['archivo']),out['sha256'])

    def test_same_original_and_reviewed_bytes(self):
        for entry in read('original_confiable.json'):
            self.assertEqual(sha(E/entry['referencia']),entry['sha256'])
        self.assertEqual(read('original_confiable.json'),read('../corrida_02/original_confiable.json'))
        for x in read('reviewed_inputs.json'):
            a=(E/x['copia']).read_bytes()
            self.assertEqual(a,(E/x['referencia_corrida02']).read_bytes())
            self.assertEqual(a,Path(x['origen']).read_bytes())
            self.assertEqual(hashlib.sha256(a).hexdigest(),x['sha256'])

    def test_quote_false_positives_no_longer_block(self):
        old=read('../corrida_02/ejecucion/artifacts/validation_exceptions.json')
        self.assertEqual(len(old['errors']),13)
        new=read('ejecucion/artifacts/validation_exceptions.json')
        self.assertEqual(new['errors'],[])
        self.assertFalse(any(e.get('error')=='PROTECTED_FIELD_CHANGED' for e in self.report['excepciones']))

    def test_proposal_and_protected_components_preserved(self):
        original={e['Employee_ID']:e for group in self.manifest['proposals'].values() for e in group}
        renamed={'New_Salary':'Proposed Salary','Total_Increase_Pct':'Proposed Increase %','Final_Compa_Ratio':'Proposed Compa Ratio'}
        for f in self.final:
            for key,value in original[f['Employee_ID']].items():
                actual=f[renamed.get(key,key)]
                if value=='' and actual is None:continue  # Empty XLSX cell.
                if isinstance(value,(int,float)) and not isinstance(value,bool):
                    self.assertAlmostEqual(actual,value,places=9,msg=f'{f["Employee_ID"]} {key}')
                else:self.assertEqual(actual,value)

    def test_only_observed_adjustment_affects_final(self):
        adjustments={x['employee_id']:x['valor_observado'] for x in read('ajustes_observados.json')}
        self.assertEqual({k:v for k,v in adjustments.items() if v!=0},{'A001':0.01})
        for f in self.final:
            adj=adjustments[f['Employee_ID']]
            self.assertEqual(f['Discretionary Adjustment %'],adj)
            increase=Decimal(str(f['Proposed Increase %']))+Decimal(str(adj))
            salary=int((Decimal(str(f['June_Base_Salary']))*(1+increase)/100).quantize(Decimal('1'),rounding=ROUND_HALF_UP)*100)
            self.assertAlmostEqual(f['Final Increase %'],float(increase))
            self.assertEqual(f['Final Salary'],salary)
            if f['WTW_Reference_Salary']:
                self.assertAlmostEqual(f['Final Compa Ratio'],salary/f['WTW_Reference_Salary'])
            else:self.assertIsNone(f['Final Compa Ratio'])
            self.assertEqual(f['Human_Modified'],adj!=0)
            if adj==0:self.assertEqual(f['Final Salary'],f['Proposed Salary'])

    def test_budget_recalculated_excess_reported_without_reduction(self):
        original_pool={e['Employee_ID']:pool for pool,es in self.manifest['proposals'].items() for e in es}
        for b in self.report['budgets']:
            payroll=sum(e['Final Salary'] for e in self.final if original_pool[e['Employee_ID']]==b['pool'])
            self.assertEqual(b['final_payroll'],payroll)
            self.assertEqual(b['budget_remaining'],b['maximum_payroll']-payroll)
            self.assertEqual(b['budget_status'],'EXCEEDED' if payroll>b['maximum_payroll'] else 'OK')
            if payroll>b['maximum_payroll']:
                self.assertTrue(any(x.get('group')==b['pool'] and x.get('flag')=='BUDGET_EXCEEDED' and x['amount']==payroll-b['maximum_payroll'] for x in self.report['excepciones']))
        alpha=next(b for b in self.report['budgets'] if b['pool']=='Team Alpha')
        self.assertGreater(alpha['final_payroll'],alpha['maximum_payroll'])

    def test_approval_and_metadata(self):
        self.assertEqual(self.report['estado_aprobacion'],'PENDING_HUMAN_APPROVAL')
        self.assertTrue(all(x['Approval_Status']=='PENDING_HUMAN_APPROVAL' for x in self.final))
        h=read('host_metadata.json')
        for k in ['modelo','input_tokens','cached_input_tokens','output_tokens','usage_metadata','costo']:self.assertIsNone(h[k])
        self.assertFalse(read('control_password.json')['contrasena_en_claro_detectada'])
        self.assertNotIn('--password',read('cli_invocacion.json')['argv'])

    def test_sources_and_prompts_preserved(self):
        for n,h in read('fuentes_intactas_antes.json').items():self.assertEqual(sha(R/n),h,n)
        r=read('registro.json')
        for key in ['system_prompt','user_prompt']:
            self.assertEqual(sha(E/r[key]['archivo_efectivamente_usado']),r[key]['sha256'])
        self.assertTrue(self.report['datos_declarados_sinteticos'])
        self.assertEqual(read('host_metadata.json')['host'],'Codex desktop')

if __name__=='__main__':unittest.main()
