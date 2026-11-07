"""Audit the manuscript's declared result counts, provenance, and bounds."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np

ROOT=Path(__file__).resolve().parent
studies=[]
for name,runs,menus in [('confirmation_v1',132,44),('warm_confirmation_v1',198,66),
                       ('reuse_ablation_v1',72,24)]:
    folder=ROOT/'results'/name
    execution=json.loads((folder/'execution.json').read_text())
    analysis=json.loads((folder/'analysis.json').read_text())
    manifest=json.loads((folder/'manifest.json').read_text())
    rows=[json.loads(s) for s in (folder/'runs.jsonl').read_text().splitlines()]
    assert execution['recorded_runs']==execution['expected_runs']==len(rows)==runs
    assert analysis['status']=='PASS' and not analysis['failures']
    assert all(x['status']=='PASS_EXECUTION' for x in rows)
    assert len({(x['case'],x['K'],x['repeat'],x['method']) for x in rows})==runs
    for file,digest in manifest['source_sha256'].items():
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest
    paths=list(folder.glob('*.npz'))
    assert len(paths)==len(analysis['saved_menu_checks'])==menus
    for path in paths:
        budget=int(re.search(r'_K(\d+)_',path.name).group(1))
        with np.load(path) as z:assert len(z['bases'])==budget
    studies.append(dict(study=name,runs=runs,menus=menus,status='PASS'))

certificates=[]
for name,count in [('certificates_v2',22),('warm_certificates_v1',22),('dictionary_certificates_v1',10)]:
    folder=ROOT/'results'/name
    report=json.loads((folder/'summary.json').read_text())
    replay=json.loads((folder/'standalone_verification.json').read_text())
    assert report['status']=='PASS' and len(report['rows'])==report['cases']==count
    assert replay['status']=='PASS_STANDALONE_INTERVAL_VERIFICATION' and replay['cases']==count
    assert replay['solver_imported'] is False
    for row in report['rows']:
        assert row['status']=='PASS_OUTWARD_BOUNDS' and row['gap']<=1.0001e-5
    for file,digest in report['source_sha256'].items():
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,(name,file)
    certificates.append(dict(collection=name,artifacts=count,max_gap=max(x['gap'] for x in report['rows'])))

dictionary=[json.loads(s) for s in (ROOT/'results/dictionary_comparison_v2/runs.jsonl').read_text().splitlines()]
refs=[x for x in dictionary if x['method']=='reused']
assert len(refs)==10
lower={x['artifact'].replace('_reused.npz',''):x['lower'] for x in json.loads(
    (ROOT/'results/dictionary_certificates_v1/summary.json').read_text())['rows']}
success={method:[x for x in dictionary if x['method']==method and x.get('stage')=='final_verification' and x['target_met']]
         for method in ('uniform','adaptive')}
assert len(success['uniform'])==1 and len(success['adaptive'])==6
gaps=[x['verified_upper']-lower[f"{x['case']}_K{x['K']}"] for xs in success.values() for x in xs]
assert max(gaps)<1.94e-5
special=json.loads((ROOT/'results/special_case_comparison.json').read_text())
assert special['status']=='PASS' and len(special['rows'])==18
assert hashlib.sha256((ROOT.parent/'submission_20261002/code/menu_solver.py').read_bytes()).hexdigest()==special['old_source_sha256']
for k in (1,2,4):
    values=[x['loss'] for x in special['rows'] if x['K']==k]
    assert max(values)-min(values)<5e-6
tex=(ROOT/'manuscript/main.tex').read_text()
structural=json.loads((ROOT/'results/structural_theory_v1.json').read_text())
assert structural['status']=='PASS'
assert len(structural['interval_certified_kappa_cases'])==12
assert len(structural['numerical_endpoint_checks'])==54
assert len(structural['active_face_cases'])==2
assert len(structural['local_distinction'])==3
for row in structural['interval_certified_kappa_cases']:
    from fractions import Fraction
    assert Fraction(row['lower'])<=Fraction(row['exact_fraction'])<=Fraction(row['upper'])
    assert row['upper']-row['lower']<1e-10
assert '\\input{structural_theory}' in tex
structural_tex=(ROOT/'manuscript/structural_theory.tex').read_text()
assert all(x in structural_tex for x in ['thm:factor','thm:exactness','thm:repair','eq:unionfaces'])
for term in ('1.367','4.220','2.810','1.94','54','optimal\\_inaccurate'):
    assert term in tex,term
log=(ROOT/'manuscript/main.log').read_text(errors='replace')
assert 'Output written on main.pdf' in log
assert not any(x in log for x in ('Overfull','Underfull','undefined','Fatal error'))
report=dict(status='PASS',studies=studies,total_timing_runs=sum(x['runs'] for x in studies),
    total_checked_menus=sum(x['menus'] for x in studies),certificate_collections=certificates,
    total_certificate_artifacts=sum(x['artifacts'] for x in certificates),
    dictionary_target_counts={x:len(y) for x,y in success.items()},
    special_case_runs=len(special['rows']),
    structural_checks=dict(interval_cases=12,numerical_endpoint_cases=54,
                           active_face_cases=2,local_distinctions=3,two_gap_example=True),
    max_successful_dictionary_global_gap=max(gaps),
    manuscript_sha256=hashlib.sha256((ROOT/'manuscript/main.pdf').read_bytes()).hexdigest(),
    scope='Counts, source provenance, saved verification evidence, and typesetting; mathematical claim audit is separate.')
(ROOT/'results/completion_evidence.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
