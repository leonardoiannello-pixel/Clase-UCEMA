"""Consistency tests only: no execution, editing, saving workbooks or decisions."""
import hashlib
import json
from pathlib import Path
import unittest
import openpyxl

E=Path(__file__).resolve().parent
R=E.parents[2]
def read(n): return json.loads((E/n).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

class EvidenceTests(unittest.TestCase):
    def test_real_rejection(self):
        r=read('registro.json'); report=read('ejecucion/reporte.json')
        self.assertTrue(r['ejecucion_real']);self.assertEqual(r['estado'],'REJECTED')
        self.assertEqual(r['estado'],report['estado'])
        self.assertEqual(read('cli_invocacion.json')['exit_code'],1)
        self.assertEqual(read('cli_stdout.txt'),report)

    def test_no_false_final_or_budget(self):
        self.assertFalse((E/'ejecucion/artifacts/consolidated_final.xlsx').exists())
        self.assertEqual(read('ejecucion/reporte.json')['budgets'],[])
        self.assertFalse(read('registro.json')['validaciones']['budgets_recalculados_por_consolidacion'])

    def test_original_hashes(self):
        for x in read('original_confiable.json'):
            self.assertEqual(sha(E/x['referencia']),x['sha256'])
        m=read('../corrida_01/ejecucion/artifacts/manifest.json')
        self.assertEqual(m['master_sha256'],sha(E/'../corrida_01/ejecucion/artifacts/master_proposal.xlsx'))

    def test_preserved_reviewed(self):
        for x in read('reviewed_inputs.json'):
            self.assertEqual(sha(E/x['copia']),x['sha256'])
            self.assertEqual(sha(Path(x['origen'])),x['sha256'])
            self.assertEqual(x['bytes_distintos_del_original'],x['archivo']=='team_L-A.xlsx')

    def test_human_adjustment(self):
        w=openpyxl.load_workbook(E/'reviewed/team_L-A.xlsx',data_only=False)
        self.assertEqual(w['Detail']['A2'].value,'A001');self.assertEqual(w['Detail']['R2'].value,0.01);w.close()
        a=read('ajustes_observados.json')
        self.assertEqual([x['employee_id'] for x in a if x['valor_observado']!=0],['A001'])
        h=read('intervencion_humana.json');self.assertFalse(h['decidida_por_agente']);self.assertIsNone(h['identidad_real'])

    def test_protected_rejection_explained(self):
        d=read('diferencias_protegidas.json');log=read('ejecucion/artifacts/validation_exceptions.json')
        self.assertEqual(len(d),13)
        self.assertTrue(all(x['solo_comillas_referencia_hoja'] for x in d))
        self.assertEqual({(x['archivo'],x['celda']) for x in d},{(x['file'],x['cell']) for x in log['errors']})
        self.assertTrue(all(x['error']=='PROTECTED_FIELD_CHANGED' for x in log['errors']))

    def test_proposed_preserved(self):
        self.assertTrue(all(x['salario_sin_cambio'] and x['aumento_sin_cambio'] for x in read('validacion_proposed.json')))

    def test_approval_metrics(self):
        r=read('registro.json');self.assertEqual(r['estado_aprobacion'],'PENDING_HUMAN_APPROVAL')
        h=read('host_metadata.json')
        for k in ['modelo','input_tokens','cached_input_tokens','output_tokens','usage_metadata','costo']:self.assertIsNone(h[k])

    def test_prompt_hashes(self):
        r=read('registro.json')
        for k in ['system_prompt','user_prompt']:self.assertEqual(sha(E/r[k]['archivo_efectivamente_usado']),r[k]['sha256'])
        self.assertEqual((E/'prompts/system_prompt.md').read_bytes(),(E/'../../prompts/system_prompt.md').read_bytes())

    def test_untouched_sources(self):
        for n,h in read('fuentes_intactas_antes.json').items():self.assertEqual(sha(R/n),h,n)

    def test_synthetic_provenance(self):
        for x in read('control_datos_sinteticos.json')['archivos']:
            self.assertEqual(x['dataset'],'SYNTHETIC DEMO');self.assertEqual(x['nuevos_textos_no_formula'],[])

    def test_cache_separate_from_results(self):
        a=next(x for x in read('observaciones_cache_excel.json') if x['archivo']=='team_L-A.xlsx')
        self.assertEqual(a['a001']['Discretionary Adjustment %'],0.01)
        self.assertEqual(a['a001']['Final Salary'],1937600)
        self.assertEqual(a['summary']['Final Payroll'],11534000)
        self.assertEqual(a['summary']['Budget Status'],'EXCEEDED')
        self.assertEqual(a['summary']['Budget Remaining'],-14000)
        self.assertIn('no resultado de consolidación',a['fuente'])

    def test_password_control(self):
        self.assertFalse(read('control_password.json')['contrasena_en_claro_detectada'])
        self.assertNotIn('--password',read('cli_invocacion.json')['argv'])

if __name__=='__main__': unittest.main()
