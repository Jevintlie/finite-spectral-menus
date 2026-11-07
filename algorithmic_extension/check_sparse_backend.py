"""Development correctness and adversarial controls for partial spectra."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from fractions import Fraction
import json
import numpy as np
from scipy import sparse
from scipy.linalg import eigh
from sparse_spectral import PartialSpectralModel,sparse_graph_model
from tridiagonal_verifier import TridiagonalVerifier
from interval_verifier import IntervalVerifier


def run():
    rows=[]
    for geometry in ['path','grid']:
        for rank in [2,8]:
            m=sparse_graph_model(6101,64,rank,geometry=geometry)
            reference=PartialSpectralModel(m.A,m.C,m.d,rank,backend='dense_full')
            for p in [0.,.25,1.,2.]:
                for site in range(2):
                    w,u=m.spectrum(p,site);exact,_=reference.spectrum(p,site)
                    error=float(abs(w[:rank+1]-exact[:rank+1]).max())
                    assert error<1e-9
                    rows.append(dict(geometry=geometry,rank=rank,p=p,site=site,error=error))
            actual=m.endpoint(0.,2.,tol=1e-9)
            expected=reference.endpoint(0.,2.,tol=1e-9)
            assert abs(actual.upper-expected.upper)<1e-8
    stress=[]
    # Exact eightfold cutoff collision, high rank and fully repeated spectrum.
    for n,rank in [(32,1),(32,4),(32,31),(32,32)]:
        a=sparse.diags(np.r_[np.ones(8),np.zeros(n-8)])
        c=sparse.diags(np.r_[np.linspace(0.,2.,8),np.ones(n-8)])
        m=PartialSpectralModel(a,[c],[0.],rank)
        reference=PartialSpectralModel(a,[c],[0.],rank,backend='dense_full')
        actual=m.endpoint(0.,2.,tol=1e-9)
        expected=reference.endpoint(0.,2.,tol=1e-9)
        assert abs(actual.upper-expected.upper)<1e-8
        stress.append(dict(n=n,rank=rank,error=abs(actual.upper-expected.upper),**m.storage()))
    m=PartialSpectralModel(sparse.eye(32),[sparse.eye(32)],[0.],2)
    w,u=m.spectrum(.5,0)
    assert abs(w[:2]+.5).max()<1e-10
    stress.append(dict(case='fully_repeated',**m.storage()))
    # Sturm pivot signs checked against exact rational LDL recurrence.
    rng=np.random.default_rng(6102);counts=[]
    for n in [3,9,17]:
        ad=rng.integers(0,8,n).astype(float)
        ae=rng.integers(-2,3,n-1).astype(float)
        a=sparse.diags([ae,ad,ae],[-1,0,1])
        v=TridiagonalVerifier(a,[sparse.eye(n)],[0.],1,2.)
        for shift in [-10.125,-7.125,-3.125,-1.125,.125,.375,1.125,3.125,7.125]:
            piv=[]
            for i in range(n):
                t=-Fraction(float(ad[i]))-Fraction(shift)
                if i:t-=Fraction(float(ae[i-1]))**2/piv[-1]
                piv.append(t)
            exact=sum(x<0 for x in piv)
            observed=v.count(0.,0,shift)
            assert exact==observed
            counts.append(dict(n=n,shift=shift,count=exact))
    # Cross-check the independent sparse verifier against the existing dense one.
    m=sparse_graph_model(6103,24,3)
    tri=TridiagonalVerifier(m.A,m.C,m.d,m.rank,m.upper)
    dense=IntervalVerifier(m.A.toarray(),np.array([x.toarray() for x in m.C]),m.d,m.rank,m.upper)
    enclosures=[]
    for p in [0.,.25,1.,2.]:
        for site in range(2):
            tb=tri.branch(p,site);db=dense.branch(p,site)
            exact=eigh((-m.A+p*m.C[site]).toarray(),eigvals_only=True)[:m.rank].sum()+p*m.d[site]
            assert tb[0]<=exact<=tb[1] and max(tb[0],db[0])<=min(tb[1],db[1])
            u=np.linalg.qr(rng.normal(size=(m.n,m.rank)))[0]
            t=tri.objective(u,p,site);d=dense.objective(u,p,site)
            assert max(t[0],d[0])<=min(t[1],d[1])
            enclosures.append(dict(p=p,site=site,tri=tb,dense=db))
    # Consumed confirmation seed: a narrow avoided crossing defeated price
    # bisection at binary64 resolution in BOTH original backends.
    regression=[]
    for backend in ['dense_partial','sparse']:
        m=sparse_graph_model(6201,128,2,geometry='grid',backend=backend)
        solved=m.minimax(2,loss_tol=2e-6,price_tol=2e-8,oracle_tol=1e-9)
        assert m.endpoint_recoveries>0
        regression.append(dict(backend=backend,loss=float(solved['continuous_max']['value']),
                               recoveries=m.endpoint_recoveries))
    assert abs(regression[0]['loss']-regression[1]['loss'])<5e-8
    zero=TridiagonalVerifier(sparse.csr_matrix((9,9)),[sparse.eye(9)],[0.],4,2.)
    try:zero.count(0.,0,0.)
    except ArithmeticError:pass
    else:raise AssertionError('An unresolved zero pivot must be rejected')
    assert zero.count(0.,0,-1.)==0 and zero.count(0.,0,1.)==9
    lo,hi=zero.branch(0.,0)
    assert lo<=0<=hi and hi-lo<1e-9
    grid=sparse_graph_model(6104,32,2,geometry='grid')
    try:TridiagonalVerifier(grid.A,grid.C,grid.d,grid.rank,grid.upper)
    except ValueError:pass
    else:raise AssertionError('General grid must not enter the tridiagonal verifier')
    result=dict(status='PASS',spectral_checks=rows,stress=stress,avoided_crossing=regression,
                fail_closed_zero_pivot=True,repeated_sturm_eigenvalue=True,nontridiagonal_rejected=True,
                exact_rational_sturm_counts=counts,enclosure_checks=enclosures,
                limitation='Residuals do not certify extremal ordering or complete multiplicity for general sparse inputs.')
    path=Path(__file__).resolve().parent/'results/sparse_development_v2.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],spectral_checks=len(rows),stress=len(stress),
                         rational_counts=len(counts),enclosure_checks=len(enclosures))),flush=True)

if __name__=='__main__':run()
