"""Independent dense full-spectrum evaluation of saved sparse-study menus."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.linalg import eigvalsh
from sparse_artifacts import load

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/sparse_confirmation_v2'
rows=[json.loads(x) for x in (OUT/'runs.jsonl').read_text().splitlines()]
manifest=json.loads((OUT/'manifest.json').read_text())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in manifest['source_sha256'].items())
assert len(rows)==72
checks=[];failures=[]
for path in sorted(OUT.glob('*.npz')):
    args,bases,segments=load(path)
    a=args['task'].toarray();cs=[x.toarray() for x in args['costs']]
    d=args['overheads'];rank=args['rank'];upper=args['upper']
    assert len(bases)==2 and np.max(abs(bases.transpose(0,2,1)@bases-np.eye(rank)))<1e-8
    assert segments[0,0]==0 and segments[-1,1]==upper and np.array_equal(segments[:-1,1],segments[1:,0])
    lines=np.array([[-np.sum(u*(a@u)),min(np.sum(u*(c@u))+o for c,o in zip(cs,d))] for u in bases])
    prices=[0.,upper]
    for i,(ai,bi) in enumerate(lines):
        for aj,bj in lines[i+1:]:
            if bi!=bj:
                p=(aj-ai)/(bi-bj)
                if 0<p<upper:prices.append(float(p))
    def optimum(p):return min(eigvalsh(-a+p*c,check_finite=False)[:rank].sum()+p*o for c,o in zip(cs,d))
    loss=max(float(np.min(lines[:,0]+p*lines[:,1])-optimum(p)) for p in prices)
    endpoint=max(float(intercept+p*cost-optimum(p)) for (intercept,cost),(left,right) in zip(lines,segments) for p in [left,right])
    record=next(r for r in rows if path.stem==r['case']+'_'+r['method'] and r['repeat']==0)
    assert abs(loss-record['loss'])<5e-8
    assert endpoint<=record['loss']+5e-6
    checks.append(dict(artifact=path.name,loss=loss,endpoint_upper=endpoint,
                       reported_difference=abs(loss-record['loss'])))
cells=[]
for case in sorted({r['case'] for r in rows}):
    group=[r for r in rows if r['case']==case]
    if any(r['status']!='PASS_EXECUTION' for r in group):
        failures.append(case);continue
    med={m:float(np.median([r['seconds'] for r in group if r['method']==m])) for m in ['dense_partial','sparse']}
    spread=max(r['loss'] for r in group)-min(r['loss'] for r in group)
    assert spread<5e-6
    cells.append(dict(case=case,n=group[0]['n'],rank=group[0]['rank'],times=med,
        dense_to_sparse_ratio=med['dense_partial']/med['sparse'],loss_spread=spread,
        max_retained_bytes={m:max(r['input_bytes']+r['spectrum_bytes_peak']+r['sample_bytes'] for r in group if r['method']==m) for m in med},
        fallbacks={m:sum(r['fallback_count'] for r in group if r['method']==m) for m in med}))
report=dict(status='PASS' if not failures and len(checks)==24 else 'FAILURES_PRESENT',
            runs=len(rows),saved_menu_checks=checks,cells=cells,failures=failures,
            median_ratio=float(np.median([c['dense_to_sparse_ratio'] for c in cells])),
            scope='Numerical full-spectrum continuous-price cross-checks, not outward certificates or a universal speed claim.')
(OUT/'analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['saved_menu_checks','cells']},indent=2))
for cell in cells:print(cell['case'],cell['dense_to_sparse_ratio'])
