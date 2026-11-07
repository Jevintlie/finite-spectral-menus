"""Development correctness and screening for stronger Brent references."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
from pathlib import Path
import json
import time
import numpy as np
from spectral_menu import random_model, mirror_model, SpectralModel
from reused_spectral import as_reused
from warm_brent import as_warm_brent, as_hybrid_brent

rows = []
rng = np.random.default_rng(5300)
for n, rank, sites in [(2,1,2),(8,3,3),(16,8,2)]:
    original = random_model(5300, n, rank, sites)
    candidates = [as_warm_brent(original), as_hybrid_brent(original)]
    for _ in range(15):
        a, b = sorted(rng.uniform(0, 2, 2))
        ref = original.endpoint(a, b)
        for candidate in candidates:
            out = candidate.endpoint(a, b)
            assert abs(ref.upper-out.upper) < 3e-8
            assert out.upper-out.lower < 3e-8
            assert np.linalg.norm(out.basis.T@out.basis-np.eye(rank)) < 1e-10

collision = SpectralModel(np.diag([1.,0.]), [np.diag([1.,0.])], [0.])
cases = [('mirror', mirror_model()), ('collision', collision),
         ('n24_r4_s3', random_model(5301,24,4)),
         ('n64_r8_s3', random_model(5302,64,8))]
for name, original in cases:
    for k in ((1,) if name == 'collision' else (1,2,4)):
        losses = []
        for method, wrapper in [('reused',as_reused),('warm_brent',as_warm_brent),
                                ('hybrid_brent',as_hybrid_brent)]:
            model = wrapper(original)
            start = time.perf_counter()
            result = model.minimax(k, loss_tol=2e-6, price_tol=2e-8, oracle_tol=1e-9)
            row = dict(case=name, K=k, method=method, seconds=time.perf_counter()-start,
                       loss=result['continuous_max']['value'], eigen_calls=model.eigen_calls,
                       fallbacks=getattr(model,'brent_fallbacks',0))
            losses.append(row['loss'])
            rows.append(row)
            print(json.dumps(row), flush=True)
        assert max(losses)-min(losses) < 5e-6
        if name == 'collision':
            assert max(abs(x-.5) for x in losses) < 1e-9
out = Path(__file__).with_name('results')/'warm_brent_screen.json'
out.write_text(json.dumps(dict(status='PASS_DEVELOPMENT',endpoint_checks=90,rows=rows),indent=2)+'\n')
