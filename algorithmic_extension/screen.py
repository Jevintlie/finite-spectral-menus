"""Development correctness screen; no speed or novelty confirmation claim."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
from pathlib import Path
import hashlib
import importlib.util
import json
import platform
import time
import numpy as np
from scipy.linalg import eigvalsh
from scipy.optimize import minimize_scalar
from spectral_menu import SpectralModel, mirror_model, random_model

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('old_solver', ROOT.parent/'submission_20261002/code/menu_solver.py')
old = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = old
spec.loader.exec_module(old)


def independent_dual(model, a, b):
    def val(p, site):
        return float(eigvalsh(-model.A+p*model.C[site])[:model.rank].sum()+p*model.d[site])
    fa = min(val(a, s) for s in range(len(model.d)))
    fb = min(val(b, s) for s in range(len(model.d)))
    vals = []
    for site in range(len(model.d)):
        def neg(p):
            return -(val(p, site)-fa-(p-a)*(fb-fa)/(b-a))
        opt = minimize_scalar(neg, bounds=(a, b), method='bounded', options={'xatol': 1e-13})
        vals.append(max(-opt.fun, -neg(a), -neg(b)))
    return min(vals)


def run():
    results = {'scope': 'Development screen; double precision, no interval certification.',
               'random_cases': [], 'collisions': [], 'mirror_endpoints': [], 'menus': []}
    for n, rank in [(2, 1), (3, 1), (4, 2), (8, 3), (16, 4), (8, 8)]:
        for seed in range(4100, 4105):
            model = random_model(seed, n, rank)
            a, b = .13, 1.83
            out = model.endpoint(a, b, tol=1e-9)
            ref = independent_dual(model, a, b)
            ortho = np.linalg.norm(out.basis.T@out.basis-np.eye(rank))
            ai, bi, _ = model.line(out.basis)
            primal = max(ai+a*bi-model.optimum(a), ai+b*bi-model.optimum(b))
            assert ortho < 1e-10
            assert out.upper-out.lower < 2e-9
            assert abs(out.lower-ref) < 2e-7, (n, rank, seed, out.lower, ref)
            assert primal <= out.upper+1e-10
            results['random_cases'].append({'n': n, 'rank': rank, 'seed': seed,
                'lower': out.lower, 'upper': out.upper, 'reference': ref,
                'orthogonality_error': ortho, 'actual_primal': primal})
    print('PASS: 30 random endpoint cases including full-rank projections.', flush=True)
    fixtures = [
        ('rank1_crossing', np.diag([2., 1.]), np.diag([2., 0.]), 1, .5),
        ('rank2_crossing', np.diag([3., 2., 1., 0.]), np.diag([0., 2., 0., 0.]), 2, .5),
        ('fourfold_tie', np.diag([4., 3., 2., 1.]), np.diag([6., 4., 2., 0.]), 2, 2.),
    ]
    for name, a, c, rank, expected in fixtures:
        model = SpectralModel(a, [c], [0.], rank, upper=1.)
        out = model.endpoint(0., 1., tol=1e-10)
        assert abs(out.lower-expected) < 1e-10
        assert abs(out.upper-expected) < 1e-10
        assert np.linalg.norm(out.basis.T@out.basis-np.eye(rank)) < 1e-10
        results['collisions'].append({'name': name, 'lower': out.lower,
                                     'upper': out.upper, 'basis': out.basis.tolist()})
    print('PASS: three eigenvalue-collision fixtures with recovered subspaces.', flush=True)
    rng = np.random.default_rng(4170)
    mirror = old.MirrorModel()
    general = mirror_model()
    for _ in range(30):
        a, b = sorted(rng.uniform(0., 2., 2))
        out = general.endpoint(a, b, tol=1e-10)
        assert mirror.endpoint_witness(a, b, out.upper+1e-8) is not None
        if out.lower > 1e-8:
            assert mirror.endpoint_witness(a, b, out.lower-1e-8) is None
        results['mirror_endpoints'].append({'a': a, 'b': b, 'lower': out.lower, 'upper': out.upper})
    print('PASS: 30 endpoint comparisons with old independent angle oracle.', flush=True)
    for k in (1, 2, 4):
        model = mirror_model()
        start = time.perf_counter()
        result = model.minimax(k, loss_tol=2e-6, price_tol=2e-8, oracle_tol=1e-9)
        elapsed = time.perf_counter()-start
        ref = mirror.minimax(k, iterations=30)
        loss = result['continuous_max']['value']
        assert abs(loss-ref['numerical_feasible_epsilon']) < 3e-6
        witness = model.packing(max(0., loss-1e-5), k, step=1e-5, oracle_tol=1e-9)
        assert witness is not None
        results['menus'].append({'K': k, 'loss': loss, 'old_reference': ref['numerical_feasible_epsilon'],
            'seconds': elapsed, 'eigen_calls': result['eigen_calls'], 'packing': witness})
        print(f'PASS: mirror K={k}, loss={loss:.9g}, {elapsed:.2f}s, lower witness gap 1e-5.', flush=True)
    results['status'] = 'PASS_DEVELOPMENT_SCREEN'
    results['environment'] = {'python': platform.python_version(), 'numpy': np.__version__}
    results['source_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [ROOT/'spectral_menu.py', Path(__file__)]}
    path = ROOT/'results/development_screen.json'
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(results, indent=2)+'\n')


if __name__ == '__main__':
    run()
