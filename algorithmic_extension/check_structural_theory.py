"""Targeted checks of the new structural statements, not proofs of them.

The kappa-family bounds use the optimizer-independent interval verifier.
Other checks are numerical diagnostics, explicitly not interval certificates.
No frozen timing inputs or solver implementation are modified.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
from pathlib import Path
from fractions import Fraction
import json
import numpy as np
from scipy.optimize import minimize_scalar
from spectral_menu import SpectralModel, random_model
from reused_spectral import as_reused
from interval_verifier import IntervalVerifier
from baselines import DictionarySolver

ROOT = Path(__file__).resolve().parent


def relaxed_endpoint(model, a, b):
    fa, fb = model.optimum(a), model.optimum(b)
    s = (fb-fa)/(b-a)
    objective = lambda p: model.optimum(p)-fa-(p-a)*s
    opt = minimize_scalar(lambda p: -objective(p), bounds=(a,b),
                          method='bounded', options={'xatol': 1e-13})
    return max(0., objective(a), objective(b), objective(opt.x))


def run():
    family = []
    for kappa in [2+2**-8, 2.25, 3., 4., 16., 256.]:
        for shift in [0., 1.]:
            a = np.diag([1.,0.])+shift*np.eye(2)
            c = np.array([2*np.eye(2),np.diag([kappa,0.])])+shift*np.eye(2)
            model = SpectralModel(a,c,np.zeros(2),upper=1.)
            result = model.endpoint(0.,1.,tol=1e-10)
            t = 1/kappa
            basis = np.array([[np.sqrt(t)],[np.sqrt(1-t)]])
            verifier = IntervalVerifier(a,c,np.zeros(2),1,1.)
            lower = verifier.pair_lower(0.,1.,[1.,1/kappa])['lower']
            upper = verifier.menu_upper([basis],np.array([[0.,1.]]))['upper']
            expected = 1-1/kappa
            exact = 1-Fraction(1,1)/Fraction.from_float(kappa)
            assert Fraction.from_float(lower) <= exact <= Fraction.from_float(upper)
            assert upper-lower < 1e-10
            assert abs(result.upper-expected) < 1e-9
            family.append(dict(kappa=kappa,shift=shift,exact_loss=expected,exact_fraction=str(exact),
                               lower=lower,upper=upper,solver_upper=result.upper,
                               supported_loss=1.,relaxed_loss=.5))

    rng = np.random.default_rng(5700)
    endpoint_checks = []
    for sites in [1,3]:
        for n, rank in [(2,1),(6,2),(8,4)]:
            for seed in [5701,5702,5703]:
                model = random_model(seed,n,rank,sites)
                for _ in range(3):
                    a,b = sorted(rng.uniform(0.,model.upper,2))
                    actual = model.endpoint(a,b,tol=1e-9)
                    relaxed = relaxed_endpoint(model,a,b)
                    u = model.optimal_basis((a+b)/2)
                    intercept,cost,_ = model.line(u)
                    midpoint_upper = max(intercept+p*cost-model.optimum(p) for p in [a,b])
                    assert relaxed <= actual.upper+2e-8
                    assert actual.lower <= midpoint_upper+2e-8
                    assert midpoint_upper <= 2*relaxed+2e-8
                    if sites == 1:
                        assert abs(actual.upper-relaxed) < 2e-8
                    endpoint_checks.append(dict(n=n,rank=rank,sites=sites,seed=seed,
                        a=a,b=b,actual=actual.upper,relaxed=relaxed,midpoint=midpoint_upper))

    # A corner can have a complete supported slope interval: one-site tie.
    single = SpectralModel(np.diag([1.,0.]),[np.diag([2.,0.])],[0.],upper=1.)
    complete = single.endpoint(0.,1.,tol=1e-10)
    assert abs(complete.upper-.5) < 1e-10
    assert abs(single.line(complete.basis)[1]-1.) < 1e-10

    # At p=1, two active sites supply [1,2] and [0,1], filling the corner.
    filled = SpectralModel(np.diag([2.,1.,0.]),
        [np.diag([2.,1.,4.]),np.diag([6.,1.,0.])],[0.,0.],upper=2.)
    # Changing one entry leaves a slope gap (1,2), but the full-domain
    # chord slope 1 remains available. Necessity concerns EVERY subinterval.
    gapped = SpectralModel(np.diag([2.,1.,0.]),
        [np.diag([2.,3.,4.]),np.diag([6.,1.,0.])],[0.,0.],upper=2.)
    active_face_cases = []
    for name,model in [('filled',filled),('gapped',gapped)]:
        full = model.endpoint(0.,2.,tol=1e-10).upper
        local_actual = model.endpoint(.5,7/6,tol=1e-10).upper
        local_relaxed = relaxed_endpoint(model,.5,7/6)
        assert abs(full-1.) < 1e-9
        if name == 'filled':
            assert abs(local_actual-local_relaxed) < 1e-8
        else:
            assert local_actual-local_relaxed > .01
        active_face_cases.append(dict(case=name,full_domain=full,
            local_actual=local_actual,local_relaxed=local_relaxed))

    # A slope gap need not imply that supported presets are suboptimal.
    multi = SpectralModel(np.diag([1.,0.]),[2*np.eye(2),np.diag([4.,0.])],[0.,0.],upper=1.)
    local = []
    for h in [.125,.0625,.015625]:
        a,b = .5-h,.5+h
        result = multi.endpoint(a,b,tol=1e-10)
        relaxed = relaxed_endpoint(multi,a,b)
        assert abs(result.upper-2*h) < 1e-9 and abs(relaxed-h) < 1e-9
        local.append(dict(h=h,actual=result.upper,supported=2*h,relaxed=relaxed))

    # Two distinct slope gaps. The optimal relaxed two-cover splits at 2/3.
    c = np.full((3,3),8.)
    np.fill_diagonal(c,[3.,1.,0.])
    model = as_reused(SpectralModel(np.diag([2.,1.,0.]),[np.diag(x) for x in c],
                                   np.zeros(3),upper=2.))
    basis = [np.eye(3)[:,i:i+1] for i in range(3)]
    restricted = DictionarySolver(model,basis).minimax(2,loss_tol=1e-7)
    actual = model.minimax(2,loss_tol=1e-7,price_tol=1e-9,oracle_tol=1e-10)
    left,right = relaxed_endpoint(model,0.,2/3),relaxed_endpoint(model,2/3,2.)
    assert abs(left-.25) < 1e-8 and abs(right-.25) < 1e-8
    assert abs(restricted['continuous_max']['value']-1/3) < 3e-7
    assert abs(model.continuous_max(basis)['value']) < 1e-10
    two_gaps = dict(relaxed_two_menu=.25,restricted_two_menu=restricted['continuous_max']['value'],
                    actual_two_menu=float(actual['continuous_max']['value']),repaired_three_menu=0.,
                    gap_prices=[.5,1.],relaxed_partition=[0.,2/3,2.])
    out = dict(status='PASS',interpretation='Diagnostics support, but do not prove, the theorems.',
               interval_certified_kappa_cases=family,numerical_endpoint_checks=endpoint_checks,
               complete_corner_loss=complete.upper,active_face_cases=active_face_cases,
               local_distinction=local,two_gaps=two_gaps)
    path = ROOT/'results/structural_theory_v1.json'
    path.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k not in ['interval_certified_kappa_cases','numerical_endpoint_checks']},indent=2))
    print('Interval cases:',len(family),'Numerical endpoint checks:',len(endpoint_checks))


if __name__ == '__main__':
    run()
