"""Development comparison against published Brent strategy, same outer search."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json
import time
from spectral_menu import mirror_model,random_model
from reused_spectral import as_reused
from brent_reference import as_brent

rows=[]
for name,factory in [('mirror',mirror_model),('n24_r4_s3',lambda:random_model(4201,24,4)),
                     ('n64_r8_s3',lambda:random_model(4202,64,8))]:
    for k in (1,2,4):
        losses=[]
        for method,wrapper in [('brent',as_brent),('reused',as_reused)]:
            model=wrapper(factory())
            start=time.perf_counter()
            result=model.minimax(k,loss_tol=2e-6,price_tol=2e-8,oracle_tol=1e-9)
            elapsed=time.perf_counter()-start
            row={'model':name,'K':k,'method':method,'loss':result['continuous_max']['value'],
                 'seconds':elapsed,'eigen_calls':model.eigen_calls,
                 'brent_fallbacks':getattr(model,'brent_fallbacks',None)}
            rows.append(row)
            losses.append(row['loss'])
            print(json.dumps(row),flush=True)
        assert abs(losses[0]-losses[1])<3e-6
Path(__file__).with_name('results').joinpath('brent_development.json').write_text(
    json.dumps({'status':'PASS_DEVELOPMENT_COMPARISON','rows':rows},indent=2)+'\n')
