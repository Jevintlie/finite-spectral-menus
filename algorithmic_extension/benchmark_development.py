"""Small development comparison; preserve all outcomes, no superiority gate."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
from pathlib import Path
import hashlib
import json
import time
from spectral_menu import mirror_model, random_model
from baselines import sampled_dictionary, adaptive_tangents

ROOT = Path(__file__).resolve().parent


def run():
    factories = [('mirror', mirror_model),
                 ('n8_r3_s3', lambda: random_model(4200, 8, 3)),
                 ('n24_r4_s3', lambda: random_model(4201, 24, 4))]
    rows = []
    path = ROOT/'results/benchmark_development.json'
    for name, factory in factories:
        for k in (1, 2, 4):
            for method in ('continuous', 'adaptive_global', 'global_129', 'allsite_129', 'allsite_1025'):
                model = factory()
                start = time.perf_counter()
                if method == 'continuous':
                    result = model.minimax(k, loss_tol=2e-6, price_tol=2e-8, oracle_tol=1e-9)
                elif method == 'adaptive_global':
                    result = adaptive_tangents(model, k)
                else:
                    count = int(method.split('_')[1])
                    result = sampled_dictionary(model, count, method.startswith('allsite')).minimax(k)
                seconds = time.perf_counter()-start
                row = {'model': name, 'n': model.n, 'rank': model.rank, 'sites': len(model.d),
                       'K': k, 'method': method, 'loss': result['continuous_max']['value'],
                       'seconds': seconds, 'eigen_calls': model.eigen_calls,
                       'cached_spectra_peak': model.cache_peak}
                if method == 'continuous':
                    epsilon = max(0., row['loss']-2e-5)
                    packing = model.packing(epsilon, k, step=2e-6, oracle_tol=1e-9)
                    row['packing'] = packing
                    row['packing_seconds'] = time.perf_counter()-start-seconds
                rows.append(row)
                print(json.dumps(row), flush=True)
                path.parent.mkdir(exist_ok=True)
                path.write_text(json.dumps({'scope':'Development instances; timings are single runs.',
                                            'rows': rows}, indent=2)+'\n')
    data = json.loads(path.read_text())
    data['status'] = 'COMPLETE_DEVELOPMENT_COMPARISON'
    data['source_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [ROOT/'spectral_menu.py', ROOT/'baselines.py', Path(__file__)]}
    path.write_text(json.dumps(data, indent=2)+'\n')


if __name__ == '__main__':
    run()
