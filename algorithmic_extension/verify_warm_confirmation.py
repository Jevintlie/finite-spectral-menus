"""Independent saved-menu checks and paired analysis; no training or timing."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json
import statistics
import hashlib
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/warm_confirmation_v1'
execution=json.loads((OUT/'execution.json').read_text())
assert execution['recorded_runs']==execution['expected_runs']==198
manifest=json.loads((OUT/'manifest.json').read_text())
assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value
           for name,value in manifest['source_sha256'].items())
rows=[json.loads(line) for line in (OUT/'runs.jsonl').read_text().splitlines()]
failures=[r for r in rows if r['status']!='PASS_EXECUTION']
checks=[]
for path in sorted(OUT.glob('*.npz')):
    with np.load(path) as z:
        a,c,d=z['A'],z['C'],z['d']; rank=int(z['rank']); upper=float(z['upper'])
        bases,segments=z['bases'],z['segments']
    assert segments[0,0]==0. and segments[-1,1]==upper
    assert np.array_equal(segments[:-1,1],segments[1:,0])
    assert all(np.linalg.norm(u.T@u-np.eye(rank))<1e-9 for u in bases)
    intercepts=np.array([-np.trace(u.T@a@u) for u in bases])
    slopes=np.array([min(np.trace(u.T@cost@u)+oh for cost,oh in zip(c,d)) for u in bases])
    prices=[0.,upper]
    for i in range(len(bases)):
        for j in range(i):
            if slopes[i]!=slopes[j]:
                p=(intercepts[j]-intercepts[i])/(slopes[i]-slopes[j])
                if 0<p<upper:
                    prices.append(p)
    def regret(p):
        f=min(np.linalg.eigvalsh(-a+p*cost)[:rank].sum()+p*oh for cost,oh in zip(c,d))
        return float(np.min(intercepts+p*slopes)-f)
    exact=max(regret(p) for p in prices)
    grid=max(regret(p) for p in np.linspace(0.,upper,101))
    stem=path.stem
    expected=next(r for r in rows if f"{r['case']}_K{r['K']}_{r['method']}"==stem and r['repeat']==0)
    assert abs(exact-expected['loss'])<1e-8
    assert grid<=exact+1e-8
    checks.append({'artifact':path.name,'independent_max':exact,'grid_max':grid})
pairs=[]
for case,k in sorted(set((r['case'],r['K']) for r in rows)):
    b=[r for r in rows if r['case']==case and r['K']==k and r['method']=='reused' and r['status']=='PASS_EXECUTION']
    for method in ('warm_brent','hybrid_brent'):
        a=[r for r in rows if r['case']==case and r['K']==k and r['method']==method and r['status']=='PASS_EXECUTION']
        assert len(a)==len(b)==3,(case,k,method)
        gap=max(abs(x['loss']-y['loss']) for x in a for y in b)
        assert gap<5e-6,(case,k,method,gap)
        pairs.append(dict(case=case,K=k,reference=method,loss_difference=gap,
            reference_seconds=statistics.median(x['seconds'] for x in a),
            reused_seconds=statistics.median(x['seconds'] for x in b),
            reference_over_reused=statistics.median(x['seconds'] for x in a)/statistics.median(x['seconds'] for x in b),
            reference_eigen_calls=a[0]['eigen_calls'],reused_eigen_calls=b[0]['eigen_calls'],
            reference_fallbacks=a[0]['brent_fallbacks'],
            reused_retained_bytes=b[0]['spectra_bytes_peak']+b[0]['sample_bytes']))
summaries={}
for method in ('warm_brent','hybrid_brent'):
    cells=[r for r in pairs if r['reference']==method and r['case']!='mirror']
    ratios=[r['reference_over_reused'] for r in cells]
    summaries[method]=dict(cells=len(cells),median=statistics.median(ratios),
        minimum=min(ratios),maximum=max(ratios),losses=[r for r in cells if r['reference_over_reused']<1])
assert len(checks)==66 and not failures
report=dict(status='PASS',runs=len(rows),failures=failures,saved_menu_checks=checks,
    paired_cells=pairs,new_seed_summaries=summaries,
    scope='Declared dense synthetic families, own implementations, repeated timings. Global certificates separate.')
(OUT/'analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],runs=len(rows),saved_menus=len(checks),summaries=summaries)),flush=True)
