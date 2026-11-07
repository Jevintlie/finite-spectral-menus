"""Check cached queries against original algorithm, including changing order."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
from pathlib import Path
import json
import time
import hashlib
import numpy as np
from spectral_menu import SpectralModel, mirror_model, random_model
from reused_spectral import as_reused

ROOT = Path(__file__).resolve().parent
rows = []
rng = np.random.default_rng(4250)
for n, rank in ((2, 1), (8, 3), (24, 4)):
    plain = random_model(4251, n, rank)
    cached = as_reused(plain)
    for i in range(25):
        a, b = sorted(rng.uniform(0., 2., 2))
        expected = plain.endpoint(a, b, tol=1e-9)
        result = cached.endpoint(a, b, tol=1e-9)
        assert abs(result.upper-expected.upper) < 2e-9
        assert result.upper-result.lower < 2e-9
    print(f'PASS: cached full oracle, n={n}, rank={rank}, 25 unordered queries.', flush=True)
for name, model in [('mirror', mirror_model()), ('n8_r3_s3', random_model(4200, 8, 3)),
                    ('n24_r4_s3', random_model(4201, 24, 4))]:
    for k in (1, 2, 4):
        cached = as_reused(model)
        start = time.perf_counter()
        result = cached.minimax(k, loss_tol=2e-6, price_tol=2e-8, oracle_tol=1e-9)
        elapsed = time.perf_counter()-start
        previous = json.loads((ROOT/'results/benchmark_development.json').read_text())['rows']
        expected = next(r for r in previous if r['model']==name and r['K']==k and r['method']=='continuous')
        loss = result['continuous_max']['value']
        assert abs(loss-expected['loss']) < 3e-6
        row = {'model':name,'K':k,'loss':loss,'seconds':elapsed,
               'eigen_calls':cached.eigen_calls,'cached_decisions':cached.reuse_decisions,
               'previous_seconds':expected['seconds'], 'previous_eigen_calls':expected['eigen_calls']}
        rows.append(row)
        print(json.dumps(row),flush=True)
out = {'status':'PASS_DEVELOPMENT_REUSE','rows':rows,
       'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                        (ROOT/'spectral_menu.py', ROOT/'reused_spectral.py', Path(__file__))}}
(ROOT/'results/reuse_screen.json').write_text(json.dumps(out,indent=2)+'\n')
