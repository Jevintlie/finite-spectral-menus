"""Check the exact structural proposition, including an SPD shifted version."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json
import numpy as np
from spectral_menu import SpectralModel
from reused_spectral import as_reused
from interval_verifier import IntervalVerifier

rows=[]
for alpha,beta in [(0.,0.),(.5,.5)]:
    a=np.diag([1.,0.])+alpha*np.eye(2)
    for name,costs,target in [('single',[np.diag([2.,0.])],.5),
                              ('multi',[np.diag([2.,2.]),np.diag([4.,0.])],.75)]:
        c=np.array([x+beta*np.eye(2) for x in costs])
        model=as_reused(SpectralModel(a,c,np.zeros(len(c)),upper=1.))
        for p in np.linspace(0,1,129):
            assert abs(model.optimum(p)-(min(-1+2*p,0)-alpha+beta*p))<1e-12
        result=model.minimax(1)
        basis=result['segments'][0]['basis']
        assert abs(result['continuous_max']['value']-target)<1e-9
        verifier=IntervalVerifier(a,c,np.zeros(len(c)),1,1.)
        upper=verifier.menu_upper([basis],np.array([[0.,1.]]))['upper']
        prices=[.5] if name=='single' else [1.,.25]
        lower=verifier.pair_lower(0.,1.,prices)['lower']
        assert lower<=target<=upper and upper-lower<1e-10
        rows.append(dict(model=name,alpha=alpha,beta=beta,expected=target,
                         lower=lower,upper=upper,t=float(basis[0,0]**2)))
report=dict(status='PASS',rows=rows,
            scope='Numerical outward checks support the separate exact algebraic proof; all-global-optima dictionary limitation proved analytically.')
Path(__file__).with_name('results').joinpath('structural_example.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
