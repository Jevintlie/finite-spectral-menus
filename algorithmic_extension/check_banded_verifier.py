"""Exact rational inertia, enclosure, reduction and fail-closed controls."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
from fractions import Fraction as F
import json
import numpy as np
from scipy import sparse
from scipy.linalg import eigvalsh
from banded_verifier import BandedVerifier,tree_sum
from interval_verifier import IntervalVerifier
from tridiagonal_verifier import TridiagonalVerifier
from sparse_spectral import sparse_graph_model


def exact_count(h,shift):
    a=[[F(float(x)) for x in row] for row in h]
    for i in range(len(a)):a[i][i]-=F(shift)
    negative=0
    for k in range(len(a)):
        pivot=a[k][k]
        if not pivot:raise ArithmeticError('Exact zero pivot')
        negative+=pivot<0
        for i in range(k+1,len(a)):
            for j in range(k+1,i+1):
                a[i][j]-=a[i][k]*a[j][k]/pivot
                a[j][i]=a[i][j]
    return negative


def run():
    rng=np.random.default_rng(6600);counts=[]
    for n,b in [(1,0),(5,0),(7,1),(9,3),(12,7),(15,14)]:
        for case in range(4):
            h=np.diag(rng.integers(-5,6,n).astype(float))
            for k in range(1,b+1):
                d=rng.integers(-2,3,n-k).astype(float)
                h+=np.diag(d,k)+np.diag(d,-k)
            verifier=BandedVerifier(-h,[sparse.eye(n)],[0.],min(n,3),2.)
            for shift in [-10.125,-3.375,-.125,.375,4.125,12.375]:
                expected=exact_count(h,shift)
                observed=verifier.count(0.,0,shift)
                assert observed==expected,(n,b,shift,observed,expected)
                assert verifier.count_decimal(0.,0,shift)==expected
                counts.append(dict(n=n,bandwidth=b,case=case,shift=shift,count=observed))
    sums=[]
    for n in [0,1,2,3,17,101,4096]:
        values=rng.normal(size=n)*np.exp2(rng.integers(-50,50,n))
        exact=sum((F(float(x)) for x in values),F(0))
        lo,hi=tree_sum((values,values))
        assert F(float(lo))<=exact<=F(float(hi))
        sums.append(dict(n=n,width=hi-lo))
    enclosures=[]
    for geometry in ['path','grid']:
        model=sparse_graph_model(6601,25,3,geometry=geometry)
        verifier=BandedVerifier(model.A,model.C,model.d,model.rank,model.upper)
        dense=IntervalVerifier(model.A.toarray(),np.array([x.toarray() for x in model.C]),model.d,3,2.)
        tri=TridiagonalVerifier(model.A,model.C,model.d,3,2.) if geometry=='path' else None
        for p in [0.,.3,1.,2.]:
            for site in range(2):
                b=verifier.branch(p,site);d=dense.branch(p,site)
                exact=eigvalsh((-model.A+p*model.C[site]).toarray())[:3].sum()+p*model.d[site]
                assert b[0]<=exact<=b[1] and max(b[0],d[0])<=min(b[1],d[1])
                if tri:
                    t=tri.branch(p,site);assert max(b[0],t[0])<=min(b[1],t[1])
                u=np.linalg.qr(rng.normal(size=(25,3)))[0]
                u[:,0]*=1+1e-7  # Exercise the exact polar correction.
                bo=verifier.objective(u,p,site);do=dense.objective(u,p,site)
                assert max(bo[0],do[0])<=min(bo[1],do[1])
                enclosures.append(dict(geometry=geometry,p=p,site=site,band=b,dense=d))
    zero=BandedVerifier(sparse.csr_matrix((8,8)),[sparse.eye(8)],[0.],3,2.)
    try:zero.count(0.,0,0.)
    except ArithmeticError:pass
    else:raise AssertionError('Zero pivot must fail closed')
    lo,hi=zero.branch(0.,0);assert lo<=0<=hi
    # Nonsingular indefinite matrix whose unpivoted first pivot is zero.
    indefinite=BandedVerifier([[0.,-1.],[-1.,0.]],[np.zeros((2,2))],[0.],1,2.)
    try:indefinite.count(0.,0,0.)
    except ArithmeticError:pass
    else:raise AssertionError('No-pivot method must reject this valid nonsingular input')
    try:BandedVerifier(np.ones((8,8)),[np.eye(8)],[0.],1,2.,max_bandwidth=2)
    except ValueError:pass
    else:raise AssertionError('Bandwidth cap must be enforced')
    report=dict(status='PASS',exact_counts=counts,decimal_exact_count_cases=len(counts),exact_sum_checks=sums,enclosures=enclosures,
                zero_pivot_rejected=True,nonsingular_zero_pivot_rejected=True,
                repeated_eigenvalues_enclosed=True,bandwidth_limit_enforced=True)
    target=Path(__file__).resolve().parent/'results/banded_development_v2.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',exact_counts=len(counts),sum_checks=len(sums),enclosures=len(enclosures))))

if __name__=='__main__':run()
