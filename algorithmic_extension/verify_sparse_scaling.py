"""Independent ordered LAPACK evaluation; no menu or ARPACK solver imported."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
import hashlib,json,time
import numpy as np
from scipy.linalg import eigvalsh,eigh_tridiagonal,eigvals_banded
from sparse_artifacts import load

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/sparse_scaling_v1'
manifest=json.loads((OUT/'manifest.json').read_text())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in manifest['source_sha256'].items())
rows=list(map(json.loads,(OUT/'runs.jsonl').read_text().splitlines()))
assert len(rows)==7
checks=[]
for record in rows:
    if record['status']!='PASS_EXECUTION':continue
    start=time.perf_counter()
    args,bases,segments=load(OUT/record['artifact'])
    a=args['task'];cs=args['costs'];d=args['overheads'];rank=args['rank'];upper=args['upper'];n=a.shape[0]
    assert len(bases)==2 and np.max(abs(bases.transpose(0,2,1)@bases-np.eye(rank)))<1e-8
    assert segments[0,0]==0 and segments[-1,1]==upper and np.array_equal(segments[:-1,1],segments[1:,0])
    lines=np.array([[-np.sum(u*(a@u)),min(np.sum(u*(c@u))+o for c,o in zip(cs,d))] for u in bases])
    prices=[0.,upper]
    for i,(ai,bi) in enumerate(lines):
        for aj,bj in lines[i+1:]:
            if bi!=bj:
                p=(aj-ai)/(bi-bj)
                if 0<p<upper:prices.append(float(p))
    cache={}
    def optimum(p):
        if p in cache:return cache[p]
        values=[]
        for c,o in zip(cs,d):
            h=-a+p*c
            if record['geometry']=='path':
                w=eigh_tridiagonal(h.diagonal(),h.diagonal(1),eigvals_only=True,select='i',select_range=(0,rank-1))
            elif n==1024:
                w=eigvalsh(h.toarray(),check_finite=False)[:rank]
            else:
                coo=h.tocoo();width=int(max(abs(coo.row-coo.col)))
                ab=np.zeros((width+1,n))
                for k in range(width+1):ab[k,:n-k]=h.diagonal(-k)
                w=eigvals_banded(ab,lower=True,select='i',select_range=(0,rank-1),check_finite=False)
            values.append(float(w.sum()+p*o))
        cache[p]=min(values);return cache[p]
    loss=max(float(np.min(lines[:,0]+p*lines[:,1])-optimum(p)) for p in prices)
    endpoint=max(float(ai+p*bi-optimum(p)) for (ai,bi),(left,right) in zip(lines,segments) for p in [left,right])
    assert abs(loss-record['loss'])<5e-8,(record['artifact'],loss,record['loss'])
    assert endpoint<=record['loss']+5e-6
    checks.append(dict(artifact=record['artifact'],loss=loss,endpoint_upper=endpoint,
                       reported_difference=abs(loss-record['loss']),seconds=time.perf_counter()-start,
                       reference='tridiagonal' if record['geometry']=='path' else ('dense_full' if n==1024 else 'banded')))
    print(json.dumps(checks[-1]),flush=True)
report=dict(status='PASS' if len(checks)==7 else 'FAILURES_PRESENT',checks=checks,
            scope='Independent ordered LAPACK numerical cross-checks; outward certificates are separate.')
(OUT/'analysis.json').write_text(json.dumps(report,indent=2)+'\n')
