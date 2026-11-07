"""Resumable, hash-bound sequential confirmation run. See protocol."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
from pathlib import Path
import hashlib
import json
import platform
import time
import traceback
import numpy as np
import scipy
from spectral_menu import mirror_model,random_model
from reused_spectral import as_reused
from warm_brent import as_warm_brent, as_hybrid_brent

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/warm_confirmation_v1'
OUT.mkdir(parents=True,exist_ok=True)
sources=['spectral_menu.py','reused_spectral.py','brent_reference.py',
         'warm_brent.py','run_warm_confirmation.py','WARM_CONFIRMATION_PROTOCOL.md']
hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sources}
manifest=OUT/'manifest.json'
if manifest.exists():
    assert json.loads(manifest.read_text())['source_sha256']==hashes,'Changed source: use a new version.'
else:
    manifest.write_text(json.dumps({'source_sha256':hashes,'python':platform.python_version(),
        'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),
        'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},indent=2)+'\n')
raw=OUT/'runs.jsonl'
done=set()
if raw.exists():
    done={tuple(json.loads(line)[k] for k in ('case','K','repeat','method'))
          for line in raw.read_text().splitlines()}
cases=[('mirror',mirror_model)]
for n,r,s in [(8,1,1),(16,4,3),(32,8,6),(64,4,3),(64,16,3)]:
    for seed in (5400,5401):
        cases.append((f'n{n}_r{r}_s{s}_seed{seed}',
                      lambda n=n,r=r,s=s,seed=seed:random_model(seed,n,r,s)))
for index,(name,factory) in enumerate(cases):
    for k in (2,4):
        for repeat in range(3):
            methods=[('reused',as_reused),('warm_brent',as_warm_brent),('hybrid_brent',as_hybrid_brent)]
            offset=(repeat+index)%3
            methods=methods[offset:]+methods[:offset]
            for method,wrapper in methods:
                key=(name,k,repeat,method)
                if key in done:
                    continue
                model=wrapper(factory())
                row={'case':name,'K':k,'repeat':repeat,'method':method,
                     'n':model.n,'rank':model.rank,'sites':len(model.d)}
                start=time.perf_counter()
                try:
                    result=model.minimax(k,loss_tol=2e-6,price_tol=2e-8,oracle_tol=1e-9)
                    row.update(status='PASS_EXECUTION',seconds=time.perf_counter()-start,
                               loss=result['continuous_max']['value'],
                               eigen_calls=model.eigen_calls,endpoint_calls=model.endpoint_calls,
                               cached_spectra_peak=model.cache_peak,
                               spectra_bytes_peak=model.cache_peak*8*(model.n**2+model.n),
                               brent_fallbacks=getattr(model,'brent_fallbacks',0),
                               reuse_decisions=getattr(model,'reuse_decisions',0))
                    if hasattr(model,'samples'):
                        row['sample_bytes']=sum(x.array.nbytes+sum(u.nbytes for u in x.bases)
                                                for x in model.samples)
                    else:
                        row['sample_bytes']=0
                    if repeat==0:
                        bases=np.array([s['basis'] for s in result['segments']])
                        np.savez_compressed(OUT/f'{name}_K{k}_{method}.npz',
                            A=model.A,C=model.C,d=model.d,rank=model.rank,upper=model.upper,
                            bases=bases,segments=np.array([[s['left'],s['right']] for s in result['segments']]))
                except Exception as exc:
                    row.update(status='FAIL_EXECUTION',seconds=time.perf_counter()-start,
                               error=repr(exc),traceback=traceback.format_exc())
                with raw.open('a',encoding='utf8') as f:
                    f.write(json.dumps(row)+'\n')
                    f.flush()
                done.add(key)
                print(json.dumps({k:row[k] for k in ('case','K','repeat','method','status','seconds')}),flush=True)
summary={'status':'RUN_TERMINAL','expected_runs':len(cases)*2*3*3,'recorded_runs':len(done),
         'ended_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
         'scope':'Execution complete; independent analysis and failure review remain.'}
(OUT/'execution.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary),flush=True)
