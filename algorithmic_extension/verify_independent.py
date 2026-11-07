"""Independent SDP values, orthogonal invariance, collisions, and sampled failure."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
from pathlib import Path
import hashlib
import json
import numpy as np
import cvxpy as cp
from spectral_menu import SpectralModel, random_model
from reused_spectral import as_reused
from baselines import sampled_dictionary

ROOT = Path(__file__).resolve().parent
rows = []
for n, rank in ((2,1),(4,2),(8,3),(12,7)):
    for seed in range(4300,4303):
        model = random_model(seed,n,rank,sites=2)
        a,b=.2,1.7
        result = as_reused(model).endpoint(a,b,tol=1e-9)
        # Fresh independent eigenvalue calls for the comparison's reference F.
        def f(p):
            return min(np.linalg.eigvalsh(-model.A+p*c)[:rank].sum()+p*d
                       for c,d in zip(model.C,model.d))
        fa,fb=f(a),f(b)
        bounds=[]
        statuses=[]
        for site in range(2):
            x=cp.Variable((n,n),symmetric=True)
            t=cp.Variable()
            con=[x >> 0,np.eye(n)-x >> 0,cp.trace(x)==rank]
            con += [cp.trace((-model.A+p*model.C[site])@x)+p*model.d[site]-fp<=t
                    for p,fp in ((a,fa),(b,fb))]
            prob=cp.Problem(cp.Minimize(t),con)
            prob.solve(solver='CLARABEL',tol_gap_abs=1e-10,tol_gap_rel=1e-10,tol_feas=1e-10)
            assert prob.status in ('optimal','optimal_inaccurate'),prob.status
            bounds.append(float(prob.value))
            statuses.append(prob.status)
        error=abs(result.upper-min(bounds))
        assert error < 2e-7,(n,rank,seed,error)
        q=np.linalg.qr(np.random.default_rng(seed+1).normal(size=(n,n)))[0]
        rotated=SpectralModel(q@model.A@q.T,[q@c@q.T for c in model.C],model.d,rank)
        r=as_reused(rotated).endpoint(a,b,tol=1e-9)
        assert abs(r.upper-result.upper)<2e-9
        rows.append({'n':n,'rank':rank,'seed':seed,'primal':result.upper,'dual':result.lower,
                     'sdp':min(bounds),'sdp_statuses':statuses,'sdp_error':error,
                     'rotation_error':abs(r.upper-result.upper)})
print('PASS: 24 SDP site solves and 12 rotated endpoint comparisons.',flush=True)

# Exact fixture: F(p)=min(-2+2p,-1), p in [0,1]. The best rank-one preset
# has squared coordinates (1/2,1/2), loss 1/2. A library containing only e1,e2
# has one-preset loss 1, regardless of how densely prices were sampled.
model=SpectralModel(np.diag([2.,1.]),[np.diag([2.,0.])],[0.],upper=1.)
exact=as_reused(model).minimax(1)
sampled=sampled_dictionary(model,4097,True).minimax(1)
assert abs(exact['continuous_max']['value']-.5)<1e-9
assert abs(sampled['continuous_max']['value']-1.)<1e-9
collision={'continuous':exact['continuous_max']['value'],
           'sampled_4097':sampled['continuous_max']['value'],
           'scope':'Fails for the returned coordinate eigenbases, not all possible choices within the tied eigenspace.'}
print('PASS: exact sampled-eigenbasis limitation, loss 1 versus optimal 0.5.',flush=True)
out={'status':'PASS_INDEPENDENT_SDP_AND_ROTATIONS','rows':rows,'collision':collision,
     'cvxpy_version':cp.__version__,
     'scope':'SDP is numerically solved by a separate package, not interval-certified.',
     'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                     (Path(__file__),ROOT/'spectral_menu.py',ROOT/'reused_spectral.py',ROOT/'baselines.py')}}
(ROOT/'results/independent_verification.json').write_text(json.dumps(out,indent=2)+'\n')
