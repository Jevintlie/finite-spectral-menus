"""Descriptive larger sparse screen, declared in SPARSE_SCALING_PROTOCOL.md."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
import hashlib,json,time,traceback,platform
import numpy as np
import scipy
from sparse_spectral import sparse_graph_model
from sparse_artifacts import save

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/sparse_scaling_v1';OUT.mkdir(exist_ok=True)
sources=['spectral_menu.py','reused_spectral.py','sparse_spectral.py','sparse_artifacts.py',
         'run_sparse_scaling.py','SPARSE_SCALING_PROTOCOL.md']
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}
manifest=OUT/'manifest.json'
if manifest.exists():assert json.loads(manifest.read_text())['source_sha256']==hashes
else:manifest.write_text(json.dumps(dict(source_sha256=hashes,python=platform.python_version(),
                                        numpy=np.__version__,scipy=scipy.__version__),indent=2)+'\n')
raw=OUT/'runs.jsonl'
done=set()
if raw.exists():done={r['artifact'] for r in map(json.loads,raw.read_text().splitlines())}
for geometry,seed in [('path',6300),('grid',6500)]:
    for n in [1024,4096]:
        methods=['sparse','tridiagonal'] if geometry=='path' else (['dense_partial','sparse'] if n==1024 else ['sparse'])
        for method in methods:
            name=f'{geometry}_n{n}_r2_s2_seed{seed}_{method}.npz'
            if name in done:continue
            start=time.perf_counter()
            model=sparse_graph_model(seed,n,2,geometry=geometry,backend=method)
            row=dict(artifact=name,n=n,rank=2,seed=seed,K=2,geometry=geometry,method=method,
                     setup_seconds=time.perf_counter()-start)
            start=time.perf_counter()
            try:
                result=model.minimax(2,loss_tol=2e-6,price_tol=2e-8,oracle_tol=1e-9)
                row.update(status='PASS_EXECUTION',seconds=time.perf_counter()-start,
                           loss=float(result['continuous_max']['value']),**model.storage())
                save(OUT/name,model,result)
            except Exception as exc:
                row.update(status='FAIL_EXECUTION',seconds=time.perf_counter()-start,error=repr(exc),
                           traceback=traceback.format_exc(),**model.storage())
            with raw.open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps(row),flush=True)
rows=list(map(json.loads,raw.read_text().splitlines()))
(OUT/'execution.json').write_text(json.dumps(dict(status='RUN_TERMINAL',expected=7,runs=len(rows),
    failures=sum(r['status']!='PASS_EXECUTION' for r in rows)),indent=2)+'\n')
