"""Declared fresh-seed comparison of dense partial and CSR/ARPACK backends."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
from pathlib import Path
import hashlib,json,platform,time,traceback
import numpy as np
import scipy
from sparse_spectral import sparse_graph_model
from sparse_artifacts import save

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/sparse_confirmation_v1';OUT.mkdir(exist_ok=True)
sources=['spectral_menu.py','reused_spectral.py','sparse_spectral.py','sparse_artifacts.py',
         'run_sparse_confirmation.py','SPARSE_STUDY_PROTOCOL.md']
hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sources}
manifest=OUT/'manifest.json'
if manifest.exists():
    assert json.loads(manifest.read_text())['source_sha256']==hashes
else:
    manifest.write_text(json.dumps(dict(source_sha256=hashes,python=platform.python_version(),
        numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform()),indent=2)+'\n')
raw=OUT/'runs.jsonl'
done=set()
if raw.exists():done={(r['case'],r['repeat'],r['method']) for r in map(json.loads,raw.read_text().splitlines())}
index=0
for n in [128,256,512]:
    for rank in [2,8]:
        for seed in [6200,6201]:
            name=f'grid_n{n}_r{rank}_s2_seed{seed}'
            for repeat in range(3):
                methods=['dense_partial','sparse']
                if (index+repeat)%2:methods.reverse()
                for method in methods:
                    if (name,repeat,method) in done:continue
                    setup=time.perf_counter()
                    m=sparse_graph_model(seed,n,rank,geometry='grid',backend=method)
                    row=dict(case=name,n=n,rank=rank,seed=seed,K=2,repeat=repeat,method=method,
                             setup_seconds=time.perf_counter()-setup)
                    start=time.perf_counter()
                    try:
                        result=m.minimax(2,loss_tol=2e-6,price_tol=2e-8,oracle_tol=1e-9)
                        row.update(status='PASS_EXECUTION',seconds=time.perf_counter()-start,
                                   loss=float(result['continuous_max']['value']),**m.storage())
                        if repeat==0:save(OUT/f'{name}_{method}.npz',m,result)
                    except Exception as exc:
                        row.update(status='FAIL_EXECUTION',seconds=time.perf_counter()-start,
                                   error=repr(exc),traceback=traceback.format_exc(),**m.storage())
                    with raw.open('a',encoding='utf8') as f:f.write(json.dumps(row)+'\n')
                    print(json.dumps({k:row[k] for k in ['case','repeat','method','status','seconds']}),flush=True)
            index+=1
rows=[json.loads(x) for x in raw.read_text().splitlines()]
(OUT/'execution.json').write_text(json.dumps(dict(status='RUN_TERMINAL',expected=72,
    runs=len(rows),failures=sum(r['status']!='PASS_EXECUTION' for r in rows)),indent=2)+'\n')
