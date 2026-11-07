"""Test enclosure arithmetic against exact fractions and 80-digit eigenvalues."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from fractions import Fraction
from pathlib import Path
import json
import hashlib
import numpy as np
import mpmath as mp
from interval_verifier import point,add,sub,mul,divide_positive,matmul,IntervalVerifier
from spectral_menu import random_model

F=Fraction.from_float
rng=np.random.default_rng(4400)
counts={'scalar_operations':0,'matrix_entries':0,'eigenvalues':0,'objectives':0}
for scale in (1e-100,1e-10,1.,1e10,1e100):
    for _ in range(30):
        a,b=rng.normal(size=2)*scale
        for fn,exact in ((add,F(float(a))+F(float(b))),
                         (sub,F(float(a))-F(float(b))),
                         (mul,F(float(a))*F(float(b)))):
            lo,hi=fn(point(a),point(b))
            assert F(float(lo))<=exact<=F(float(hi))
            counts['scalar_operations']+=1
        positive=abs(b)
        lo,hi=divide_positive(point(a),point(positive))
        exact=F(float(a))/F(float(positive))
        assert F(float(lo))<=exact<=F(float(hi))
        counts['scalar_operations']+=1
for m,n,k in ((2,3,4),(5,8,3),(8,8,8)):
    a=rng.normal(size=(m,n)); b=rng.normal(size=(n,k))
    lo,hi=matmul(point(a),point(b))
    for i in range(m):
        for j in range(k):
            exact=sum((F(float(a[i,t]))*F(float(b[t,j])) for t in range(n)),Fraction(0))
            assert F(float(lo[i,j]))<=exact<=F(float(hi[i,j]))
            counts['matrix_entries']+=1
mp.mp.dps=80
for n,r in ((2,1),(4,2),(8,3)):
    model=random_model(4401,n,r,sites=2)
    verifier=IntervalVerifier(model.A,model.C,model.d,r,model.upper)
    for p in (0.,.23,1.91):
        for site in range(2):
            a=mp.matrix(model.A.tolist()); c=mp.matrix(model.C[site].tolist())
            w=mp.eigsy(-a+mp.mpf(p)*c,eigvals_only=True)
            exact=sum(w[i] for i in range(r))+mp.mpf(p)*mp.mpf(float(model.d[site]))
            lo,hi=verifier.branch(p,site)
            assert mp.mpf(lo)<=exact<=mp.mpf(hi),(n,p,site,lo,exact,hi)
            counts['eigenvalues']+=n
            # Deliberately perturb orthonormality to exercise the polar bound.
            u=model.optimal_basis(p)*(1.+1e-7)
            um=mp.matrix(u.tolist()); gram=um.T*um
            wg,vg=mp.eigsy(gram)
            invsqrt=vg*mp.diag([1/mp.sqrt(x) for x in wg])*vg.T
            q=um*invsqrt
            product=q.T*(-a+mp.mpf(p)*c)*q
            actual=sum(product[j,j] for j in range(r))+mp.mpf(p)*mp.mpf(float(model.d[site]))
            lo,hi=verifier.objective(u,p,site)
            assert mp.mpf(float(lo))<=actual<=mp.mpf(float(hi))
            counts['objectives']+=1
out={'status':'PASS_ENCLOSURE_DEVELOPMENT_TESTS','counts':counts,
     'scope':'Exact rational basic arithmetic checks and high-precision reference checks; not a formal software proof.',
     'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                     (Path(__file__),Path(__file__).with_name('interval_verifier.py'))}}
Path(__file__).with_name('results').joinpath('interval_arithmetic_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out),flush=True)
