"""Generate and consolidate synthetic salary reviews without modifying V1-V3."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from decimal import Decimal

import openpyxl  # Read-only; workbooks are authored by the JS renderer.
from engine import D, prepare, calculate_group, human_result, salary
from protection import protect

ROOT = Path(__file__).resolve().parent
HEADERS = ['Employee_ID', 'Team', 'Current Rank', 'Current Grade', 'New Rank', 'New Grade',
           'Performance Rating', 'June Salary', 'Market Reference', 'Initial Compa Ratio',
           'General %', 'Promotion %', 'Progression %', 'Merit %', 'Market %',
           'Proposed Increase %', 'Proposed Salary', 'Discretionary Adjustment %',
           'Final Increase %', 'Final Salary', 'Final Compa Ratio', 'Flags',
           'Protected Increase %', 'Protected Salary', 'Original Flags', 'Reviewer_ID', 'Human Modified']
KEYS = ['Employee_ID', 'Team', 'Current_Rank', 'Current_Grade', 'New_Rank', 'New_Grade',
        'Performance_Rating', 'June_Base_Salary', 'WTW_Reference_Salary', 'Initial_Compa_Ratio',
        'General_Increase_Pct', 'Promotion_Increase_Pct', 'Progression_Increase_Pct',
        'Merit_Increase_Pct', 'Market_Increase_Pct', 'Total_Increase_Pct', 'New_Salary']


def serial(value):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(type(value).__name__)


def write_json(path, data):
    Path(path).write_text(json.dumps(data, default=serial, indent=2, ensure_ascii=False), encoding='utf-8')


def rows(path, sheet):
    w = openpyxl.load_workbook(path, data_only=True)
    values = list(w[sheet].values)
    w.close()
    return [dict(zip(values[0], row)) for row in values[1:] if row[0] is not None]


def load_inputs(parameters):
    p = {r['Parameter']: r['Value'] for r in rows(parameters, 'Global_Parameters')}
    for key in ['Discretionary_Min_Pct', 'Discretionary_Max_Pct', 'Leadership_Budget_Pct']:
        if key not in p or not D(p[key]).is_finite():
            raise ValueError('Missing/invalid parameter: ' + key)
    if not D(p['Discretionary_Min_Pct']) <= 0 <= D(p['Discretionary_Max_Pct']):
        raise ValueError('Discretionary interval must include zero')
    budgets = {r['Team']: D(r['Team_Budget_Pct']) for r in rows(parameters, 'Team_Budgets')}
    market = {r['Market_Job_Code']: r['WTW_Reference_Salary'] for r in rows(ROOT.parent / 'inputs/Market_Data.xlsx', 'Market_Data')}
    source = rows(ROOT.parent / 'inputs/Employees_Input.xlsx', 'Employees')
    ids = [r['Employee_ID'] for r in source]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate Employee_ID')
    leaders = {r['Employee_ID']: r for r in source if r['Is_Leader'] == 'YES'}
    groups = {}
    for raw in source:
        if raw['Population_Type'] != p['Population_Scope']:
            continue
        if raw['Is_Leader'] not in ['YES', 'NO']:
            raise ValueError('Invalid Is_Leader')
        reviewer = raw['Leader_Employee_ID']
        if not reviewer or reviewer == raw['Employee_ID']:
            raise ValueError('Missing reviewer or self-review')
        if raw['Is_Leader'] == 'NO':
            if reviewer not in leaders or leaders[reviewer]['Team'] != raw['Team']:
                raise ValueError('Invalid team reviewer mapping')
            name = raw['Team']
        else:
            name = 'Leadership'
        groups.setdefault(name, []).append(prepare(raw, market, p))
    for name, records in groups.items():
        if len({e['Leader_Employee_ID'] for e in records}) != 1:
            raise ValueError('Multiple reviewers per budget pool need an explicit allocation decision: ' + name)
    budgets['Leadership'] = D(p['Leadership_Budget_Pct'])
    return p, budgets, groups


def build_sheet(name, records, adjustments=None, editable=False):
    data = [HEADERS]
    formulas = {}
    for i, e in enumerate(records, 2):
        adj = (adjustments or {}).get(e['Employee_ID'], 0)
        data.append([e[k] for k in KEYS] + [adj, None, None, None, None,
                    e['Protected_Increase_Pct'], salary(e['Protected_Salary']), e['Flag'], e['Leader_Employee_ID'], None])
        valid = f'AND(ISNUMBER(R{i}),R{i}>=\'Summary\'!$B$13,R{i}<=\'Summary\'!$B$14,ROUND(R{i},4)=R{i},ROUND(P{i}+R{i},4)>=W{i},ROUND(H{i}*(1+ROUND(P{i}+R{i},4)),-2)>=X{i})'
        formulas.update({f'S{i}': f'=IF({valid},ROUND(P{i}+R{i},4),NA())',
                         f'T{i}': f'=ROUND(H{i}*(1+S{i}),-2)',
                         f'U{i}': f'=IF(I{i}="","",T{i}/I{i})',
                         f'V{i}': f'=Y{i}&IF({valid},"",";INVALID_ADJUSTMENT")',
                         f'AA{i}': f'=R{i}<>0'})
    return dict(name=name, rows=data, formulas=formulas, editable=editable, review=True)


def review_spec(name, records, budget, parameters, adjustments=None, editable=True):
    n = len(records) + 1
    summary = [['Salary review V4', name], ['Dataset', 'SYNTHETIC DEMO'],
               ['Reviewer_ID', records[0]['Leader_Employee_ID']],
               ['Team Payroll June', None], ['Maximum Payroll / Budget', None],
               ['Proposed Payroll', None], ['Discretionary Adjustment Amount', None],
               ['Final Payroll', None], ['Budget Remaining', None],
               ['Budget Utilization %', None], ['Budget Status', None], ['Budget %', budget],
               ['Discretionary_Min_Pct', parameters['Discretionary_Min_Pct']],
               ['Discretionary_Max_Pct', parameters['Discretionary_Max_Pct']],
               ['Final approval', 'PENDING_HUMAN_APPROVAL'],
               ['Instructions', 'Edit only yellow Discretionary Adjustment % cells.'],
               ['Protection', 'Prevents accidental edits. No encryption or access control.'],
               ['Parameters', 'DEMO limits and leadership budget require business approval.'],
               ['Budget utilization definition', 'Final Payroll / Maximum Payroll'],
               ['Invalid adjustments', 'Invalid input blocks final amounts until corrected.']]
    formulas = {'B4': f"=SUM('Detail'!H2:H{n})", 'B5': '=B4*(1+B12)',
                'B6': f"=SUM('Detail'!Q2:Q{n})", 'B7': '=B8-B6',
                'B8': f"=SUM('Detail'!T2:T{n})", 'B9': '=B5-B8',
                'B10': '=B8/B5', 'B11': '=IF(ISERROR(B8),"INVALID",IF(B8>B5,"EXCEEDED","OK"))'}
    return {'sheets': [dict(name='Summary', rows=summary, formulas=formulas),
                       build_sheet('Detail', records, adjustments, editable)]}


def render(specs, folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / '_render_spec.json'
    write_json(path, specs)
    try:
        subprocess.run([os.environ.get('SALARY_NODE', 'node'), str(ROOT / 'render.mjs'), str(path), str(folder)], check=True)
    finally:
        path.unlink(missing_ok=True)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot(path):
    w = openpyxl.load_workbook(path, data_only=False)
    result = {}
    for s in w:
        result[s.title] = {c.coordinate: c.value for row in s for c in row if c.value is not None}
    w.close()
    return result


def generate(output, parameters, password):
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory must be empty; preserve previous cycles')
    p, budgets, groups = load_inputs(parameters)
    proposals = {name: calculate_group(es, budgets[name]) for name, es in groups.items()}
    specs, files, all_records = {}, {}, []
    for name, es in proposals.items():
        filename = 'leadership_review.xlsx' if name == 'Leadership' else 'team_' + es[0]['Leader_Employee_ID'] + '.xlsx'
        if Path(filename).name != filename or '/' in filename or '\\' in filename:
            raise ValueError('Unsafe reviewer identifier')
        specs[filename] = review_spec(name, es, budgets[name], p)
        files[filename] = dict(group=name, employee_ids=[e['Employee_ID'] for e in es])
        all_records.extend(es)
    # Master preserves the whole agent result including X, weights and protected values.
    master_headers = list(all_records[0])
    specs['master_proposal.xlsx'] = {'sheets': [dict(name='Proposal', rows=[master_headers] + [[e.get(k) for k in master_headers] for e in all_records], formulas={})]}
    render(specs, output)
    for filename in specs:
        protect(output / filename, password, editable=filename in files)
    original_files = list((ROOT.parent / 'inputs').glob('*.xlsx')) + list((ROOT.parent / 'runs/run_3_v3/outputs').glob('*.xlsx'))
    manifest = dict(schema=1, parameters=p, budgets=budgets, proposals=proposals, files=files,
                    master_sha256=digest(output / 'master_proposal.xlsx'),
                    sources={str(f.relative_to(ROOT.parent)): digest(f) for f in original_files},
                    snapshots={filename: snapshot(output / filename) for filename in files})
    write_json(output / 'manifest.json', manifest)
    events = [{'group': name, 'employee_id': e['Employee_ID'], 'flag': e['Flag']} for name, es in proposals.items() for e in es if e['Flag']]
    for e in all_records:
        if salary(D(e['June_Base_Salary'])*(1+e['Total_Increase_Pct'])) != e['New_Salary']:
            events.append({'employee_id': e['Employee_ID'], 'flag': 'PROPOSAL_RATE_ROUNDTRIP_REVIEW_REQUIRED'})
    write_json(output / 'generation_validation.json', {'events': events, 'state': 'PENDING_HUMAN_REVIEW', 'synthetic': True})
    return manifest


def consolidate(original, reviewed, output, password):
    original, reviewed, output = map(Path, [original, reviewed, output])
    if output.exists() and any(output.iterdir()):
        raise ValueError('Consolidation output must be empty')
    output.mkdir(parents=True, exist_ok=True)
    # Original master and manifest must remain in the coordinator's trusted location.
    m = json.loads((original / 'manifest.json').read_text(encoding='utf-8'), parse_float=Decimal)
    errors, adjustments, events = [], {}, []
    if digest(original / 'master_proposal.xlsx') != m['master_sha256']:
        errors.append({'error': 'MASTER_CHANGED'})
    expected_files = set(m['files'])
    extra = {f.name for f in reviewed.glob('*.xlsx')} - expected_files - {'master_proposal.xlsx'}
    if extra:
        errors.append({'error': 'UNEXPECTED_FILES', 'files': sorted(extra)})
    for filename, info in m['files'].items():
        path = reviewed / filename
        if not path.exists():
            errors.append({'file': filename, 'error': 'MISSING_FILE'})
            continue
        try:
            actual = snapshot(path)
            expected = m['snapshots'][filename]
            if set(actual) != set(expected):
                raise ValueError('SHEETS_CHANGED')
            editable = {'R' + str(i) for i in range(2, len(info['employee_ids']) + 2)}
            for sheet in expected:
                for cell in set(actual[sheet]) | set(expected[sheet]):
                    if sheet == 'Detail' and cell in editable:
                        continue
                    a, b = actual[sheet].get(cell), expected[sheet].get(cell)
                    numeric = not isinstance(a, bool) and not isinstance(b, bool) and isinstance(a, (int, float, Decimal)) and isinstance(b, (int, float, Decimal))
                    changed = (D(a) != D(b)) if numeric else (a != b)
                    if changed:
                        errors.append({'file': filename, 'cell': sheet + '!' + cell, 'error': 'PROTECTED_FIELD_CHANGED'})
            for i, e in enumerate(m['proposals'][info['group']], 2):
                adj = actual['Detail'].get('R' + str(i))
                try:
                    human_result(e, adj, m['parameters']['Discretionary_Min_Pct'], m['parameters']['Discretionary_Max_Pct'])
                    adjustments[e['Employee_ID']] = adj
                except (ValueError, ArithmeticError) as exc:
                    errors.append({'file': filename, 'employee_id': e['Employee_ID'], 'error': str(exc)})
            events.append({'file': filename, 'sha256': digest(path), 'reviewer_id': m['proposals'][info['group']][0]['Leader_Employee_ID']})
        except Exception as exc:
            errors.append({'file': filename, 'error': str(exc)})
    if errors:
        write_json(output / 'validation_exceptions.json', {'state': 'REJECTED', 'errors': errors, 'reviewed_files': events})
        raise ValueError('Consolidation rejected; see validation_exceptions.json')
    final_rows, budget_rows = [], []
    for group, records in m['proposals'].items():
        final_payroll = 0
        for e in records:
            human = human_result(e, adjustments[e['Employee_ID']], m['parameters']['Discretionary_Min_Pct'], m['parameters']['Discretionary_Max_Pct'])
            final_payroll += human['Final_Salary']
            # Preserve original Final_Compa_Ratio under its original key too.
            final_rows.append({**e, **{('Human_' + k if k == 'Final_Compa_Ratio' else k): v for k, v in human.items()}, 'Reviewer_ID': e['Leader_Employee_ID'], 'Approval_Status': 'PENDING_HUMAN_APPROVAL'})
        june = sum(D(e['June_Base_Salary']) for e in records)
        maximum = june * (1 + m['budgets'][group])
        proposed = sum(e['New_Salary'] for e in records)
        status = 'EXCEEDED' if final_payroll > maximum else 'OK'
        budget_rows.append([group, june, maximum, proposed, final_payroll-proposed, final_payroll, maximum-final_payroll, D(final_payroll)/maximum, status, 'PENDING_HUMAN_APPROVAL'])
        if status == 'EXCEEDED':
            events.append({'group': group, 'flag': 'BUDGET_EXCEEDED', 'amount': final_payroll-maximum})
    headers = list(final_rows[0])
    render({'consolidated_final.xlsx': {'sheets': [dict(name='Final', rows=[headers] + [[e.get(k) for k in headers] for e in final_rows], formulas={}),
            dict(name='Budgets', rows=[['Pool', 'Team Payroll June', 'Maximum Payroll / Budget', 'Proposed Payroll', 'Discretionary Adjustment Amount', 'Final Payroll', 'Budget Remaining', 'Budget Utilization %', 'Budget Status', 'Approval Status']] + budget_rows, formulas={})]}}, output)
    protect(output / 'consolidated_final.xlsx', password, editable=False)
    write_json(output / 'validation_exceptions.json', dict(state='PENDING_HUMAN_APPROVAL', errors=[], reviewed_files=events,
              manifest_sha256=digest(original/'manifest.json'), final_sha256=digest(output/'consolidated_final.xlsx')))
    return final_rows, budget_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['generate', 'consolidate'])
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--parameters', type=Path, default=ROOT/'inputs/Parameters.xlsx')
    parser.add_argument('--original', type=Path)
    parser.add_argument('--reviewed', type=Path)
    parser.add_argument('--password', default=os.environ.get('SALARY_REVIEW_PASSWORD'))
    args = parser.parse_args()
    if not args.password:
        parser.error('Set SALARY_REVIEW_PASSWORD or --password (sheet protection, not encryption)')
    if args.command == 'generate':
        generate(args.output, args.parameters, args.password)
    else:
        if not args.original or not args.reviewed:
            parser.error('consolidate requires --original and --reviewed')
        consolidate(args.original, args.reviewed, args.output, args.password)


if __name__ == '__main__':
    main()
