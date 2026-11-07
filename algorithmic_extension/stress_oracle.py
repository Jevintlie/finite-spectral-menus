"""Adversarial endpoint screen; preserve every failure for diagnosis."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json
import hashlib
import traceback
import numpy as np
from spectral_menu import SpectralModel
from reused_spectral import as_reused

ROOT=Path(__file__).resolve().parent
cases=[]
for scale in (1e-6,1.,1e6):
    for cross in (0.,1e-12,1e-8,1e-4,.1):
        a=scale*np.array([[2.,cross],[cross,1.]])
        c=scale*np.diag([2.,0.])
        model=SpectralModel(a,[c],[0.],upper=1.)
        # Symmetry about p=1/2 makes the dual optimum exact there.
        expected=scale*(np.hypot(.5,cross)-cross)
        cases.append((f'cross_{cross}_scale_{scale}',model,expected,1e-9*scale))
for rank in (1,3,7,8):
    a=np.diag(np.arange(8.,0.,-1))
    c=2*(a-np.eye(8))
    model=SpectralModel(a,[c,c],[0.,.3],rank,upper=1.)
    # F0(0)+F0(1) can be computed exactly from integer diagonal entries.
    fa=-sum(range(9-rank,9))
    fb=sum(range(-1,rank-1))
    expected=-rank-(fa+fb)/2
    cases.append((f'eightfold_rank_{rank}',model,float(expected),1e-9))
cases.append(('dimension_one',SpectralModel([[2.]],[[[3.]],[[1.]]],[0.,1.],upper=1.),0.,1e-9))
rows=[]
for name,model,expected,tol in cases:
    row={'case':name,'expected':expected,'tol':tol}
    try:
        cached=as_reused(model)
        out=cached.endpoint(0.,1.,tol=tol)
        error=max(abs(out.lower-expected),abs(out.upper-expected))
        assert error<=max(5*tol,1e-13),error
        row.update(status='PASS',lower=out.lower,upper=out.upper,error=error)
    except Exception as exc:
        row.update(status='FAIL',error=repr(exc),traceback=traceback.format_exc())
    rows.append(row)
    print(json.dumps(row),flush=True)
report={'status':'PASS' if all(r['status']=='PASS' for r in rows) else 'FAILURES_PRESENT',
        'rows':rows,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                  (Path(__file__),ROOT/'spectral_menu.py',ROOT/'reused_spectral.py')}}
(ROOT/'results/stress_oracle.json').write_text(json.dumps(report,indent=2)+'\n')
