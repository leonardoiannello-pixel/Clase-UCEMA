import importlib.util
import json
from pathlib import Path
import unittest

PACKAGE=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('formula_equivalence',PACKAGE/'agente/v41/formula_equivalence.py')
formula=importlib.util.module_from_spec(spec)
spec.loader.exec_module(formula)


class FormulaEquivalenceTests(unittest.TestCase):
    def test_detail_optional_quotes(self):
        self.assertTrue(formula.equivalent_formulas("='Detail'!A1",'=Detail!A1'))

    def test_summary_optional_quotes(self):
        self.assertTrue(formula.equivalent_formulas("='Summary'!B2",'=Summary!B2'))

    def test_changed_address_rejected(self):
        self.assertFalse(formula.equivalent_formulas("='Detail'!A1",'=Detail!A2'))

    def test_changed_operator_rejected(self):
        self.assertFalse(formula.equivalent_formulas("='Detail'!A1+1",'=Detail!A1-1'))

    def test_changed_constant_rejected(self):
        self.assertFalse(formula.equivalent_formulas("='Detail'!A1+1",'=Detail!A1+2'))

    def test_changed_sheet_rejected(self):
        self.assertFalse(formula.equivalent_formulas("='Detail'!A1",'=Summary!A1'))

    def test_required_quotes_preserved(self):
        for name in ['Team Alpha','Team-Alpha',"O''Brien",'2026','A1','Detail.Sheet']:
            value=f"='{name}'!A1"
            self.assertEqual(formula.canonical_formula(value),value)
            self.assertFalse(formula.equivalent_formulas(value,f'={name}!A1'))

    def test_string_literals_and_escaped_quotes_unchanged(self):
        for value in ['="\'Detail\'!A1"', '=IF(A1="say ""\'Summary\'!B2""",1,0)']:
            self.assertEqual(formula.canonical_formula(value),value)
            self.assertFalse(formula.equivalent_formulas(value,value.replace("'Detail'!",'Detail!').replace("'Summary'!",'Summary!')))

    def test_external_structured_and_3d_not_rewritten(self):
        for value in ["='[Book.xlsx]Detail'!A1", "=[Book.xlsx]'Detail'!A1", "=Table['Detail'!A1]", "='Other:Detail'!A1", "=Other:'Detail'!A1"]:
            self.assertEqual(formula.canonical_formula(value),value)

    def test_nonformula_values_not_rewritten(self):
        for v in [None,1,True,"'Detail'!A1"]:
            self.assertEqual(formula.canonical_formula(v),v)
        self.assertFalse(formula.equivalent_formulas("'Detail'!A1",'Detail!A1'))
        self.assertFalse(formula.equivalent_formulas('=1',1))

    def test_case_spaces_and_absolute_address_not_ignored(self):
        for b in ['=detail!A1','=Detail!$A$1','=Detail!A1 ','= Detail!A1']:
            self.assertFalse(formula.equivalent_formulas("='Detail'!A1",b))

    def test_unterminated_atoms_fail_closed(self):
        for s in ['="broken + \'Detail\'!A1', "=['Detail'!A1", "='broken + 'Detail'!A1"]:
            self.assertEqual(formula.canonical_formula(s),s)

    def test_only_two_line_derivation_from_historical_v4(self):
        source=(PACKAGE.parent/'Entrega-2/v4/workflow.py').read_text(encoding='utf-8')
        expected=source.replace('from protection import protect','from protection import protect\nfrom formula_equivalence import equivalent_formulas')
        expected=expected.replace('else (a != b)','else (not equivalent_formulas(a, b))')
        self.assertEqual((PACKAGE/'agente/v41/workflow_v41.py').read_text(encoding='utf-8'),expected)

    def test_recorded_run02_differences_equivalent_read_only(self):
        differences=json.loads((PACKAGE/'corridas/corrida_02/diferencias_protegidas.json').read_text(encoding='utf-8'))
        self.assertEqual(len(differences),13)
        for d in differences:
            self.assertTrue(formula.equivalent_formulas(d['original'],d['reviewed']),d['celda'])
            self.assertNotEqual(d['original'],d['reviewed'])

if __name__=='__main__': unittest.main()
