"""Accuracy-matched competitor screen with a generous external loss target."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import hashlib
import json
import time
import numpy as np
from spectral_menu import SpectralModel,mirror_model,random_model
from reused_spectral import as_reused
from baselines import AdaptiveDictionary,sampled_dictionary
from interval_verifier import IntervalVerifier

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/dictionary_comparison_v2'
OUT.mkdir(exist_ok=True)
assert not (OUT/'runs.jsonl').exists(),'Preserve existing run; use a new version.'
files=['spectral_menu.py','reused_spectral.py','baselines.py','interval_verifier.py',
       'compare_dictionaries.py','DICTIONARY_PROTOCOL.md']
(OUT/'manifest.json').write_text(json.dumps({'source_sha256':{
    f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}},indent=2)+'\n')
cases=[('mirror',mirror_model,(1,2,4))]
for n,r,s in ((16,4,3),(32,8,6),(64,4,3)):
    cases.append((f'n{n}_r{r}_s{s}_seed5200',lambda n=n,r=r,s=s:random_model(5200,n,r,s),(2,4)))
cases.append(('commuting_collision',lambda:SpectralModel(np.diag([2.,1.]),[np.diag([2.,0.])],[0.],upper=1.),(1,)))
all_rows=[]
def record(row):
    row=json.loads(json.dumps(row,default=lambda value:value.item()))
    all_rows.append(row)
    with (OUT/'runs.jsonl').open('a') as f:
        f.write(json.dumps(row)+'\n')
    print(json.dumps(row),flush=True)

for name,factory,ks in cases:
    for k in ks:
        model=as_reused(factory())
        start=time.perf_counter()
        ref=model.minimax(k,loss_tol=2e-6,price_tol=2e-8,oracle_tol=1e-9)
        elapsed=time.perf_counter()-start
        target=ref['continuous_max']['value']+1e-5
        bases=[s['basis'] for s in ref['segments']]
        seg=np.array([[s['left'],s['right']] for s in ref['segments']])
        verifier=IntervalVerifier(model.A,model.C,model.d,model.rank,model.upper)
        upper=verifier.menu_upper(bases,seg)['upper']
        np.savez_compressed(OUT/f'{name}_K{k}_reused.npz',A=model.A,C=model.C,d=model.d,
                           rank=model.rank,upper=model.upper,bases=bases,segments=seg)
        record({'case':name,'K':k,'method':'reused','loss':ref['continuous_max']['value'],
                'verified_upper':upper,'seconds':elapsed,'target':target,'eigen_calls':model.eigen_calls})
        for method in ('uniform','adaptive'):
            model=factory()
            start=time.perf_counter()
            adaptive=AdaptiveDictionary(model) if method=='adaptive' else None
            for stage in (range(20) if adaptive else (129,513,2049,8193)):
                result=adaptive.step(k) if adaptive else sampled_dictionary(model,stage,True).minimax(k)
                elapsed=time.perf_counter()-start
                loss=result['continuous_max']['value']
                row={'case':name,'K':k,'method':method,'stage':stage,'loss':loss,
                     'cumulative_seconds':elapsed,'candidates':result['candidate_count'],
                     'target':target,'target_met':loss<=target,'eigen_calls':model.eigen_calls}
                record(row)
                if loss<=target or stage==(19 if adaptive else 8193):
                    verifier=IntervalVerifier(model.A,model.C,model.d,model.rank,model.upper)
                    vb=verifier.menu_upper(result['bases'],np.array(result['segments']))['upper']
                    np.savez_compressed(OUT/f'{name}_K{k}_{method}.npz',A=model.A,C=model.C,d=model.d,
                            rank=model.rank,upper=model.upper,bases=result['bases'],segments=result['segments'])
                    record({'case':name,'K':k,'method':method,'stage':'final_verification',
                            'verified_upper':vb,'target':target,'target_met':vb<=target})
                    break
(OUT/'execution.json').write_text(json.dumps({'status':'RUN_TERMINAL','rows':len(all_rows)},indent=2)+'\n')
