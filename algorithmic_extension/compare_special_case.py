"""Matched-tolerance comparison with the original analytic mirror solver."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import importlib.util
import sys
import json
import time
import math
import hashlib
import statistics
import numpy as np
from spectral_menu import mirror_model
from reused_spectral import as_reused

ROOT=Path(__file__).resolve().parent
source=ROOT.parent/'submission_20261002/code/menu_solver.py'
spec=importlib.util.spec_from_file_location('old_mirror_reference',source)
old=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=old
spec.loader.exec_module(old)

class MatchedMirror(old.MirrorModel):
    # Original analytic formulas; reduce its defaults to the general solver's
    # requested price resolution so extra precision does not penalize it.
    def furthest(self,left,epsilon,iterations=27):
        return super().furthest(left,epsilon,iterations)

rows=[]
for k in (1,2,4):
    for repeat in range(3):
        methods=['analytic','reused'] if repeat%2==0 else ['reused','analytic']
        for method in methods:
            model=MatchedMirror() if method=='analytic' else as_reused(mirror_model())
            start=time.perf_counter()
            if method=='analytic':
                result=model.minimax(k,iterations=19)
                loss=model.continuous_max(result['angles'])['value']
            else:
                result=model.minimax(k,loss_tol=2e-6,price_tol=2e-8,oracle_tol=1e-9)
                loss=result['continuous_max']['value']
            row=dict(K=k,repeat=repeat,method=method,seconds=time.perf_counter()-start,loss=loss)
            if method=='analytic':
                bases=[np.array([[math.cos(x)],[math.sin(x)]]) for x in result['angles']]
                check=mirror_model().continuous_max(bases)['value']
                assert abs(check-loss)<1e-12
            rows.append(row)
            print(json.dumps(row),flush=True)
pairs=[]
for k in (1,2,4):
    a=[x for x in rows if x['K']==k and x['method']=='analytic']
    b=[x for x in rows if x['K']==k and x['method']=='reused']
    assert max(abs(x['loss']-y['loss']) for x in a for y in b)<5e-6
    pairs.append(dict(K=k,analytic_seconds=statistics.median(x['seconds'] for x in a),
                     reused_seconds=statistics.median(x['seconds'] for x in b)))
report=dict(status='PASS',rows=rows,pairs=pairs,
            old_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            scope='Special two-dimensional analytic competitor, three repetitions, matched stopping resolution; no general-rank applicability.')
(ROOT/'results/special_case_comparison.json').write_text(json.dumps(report,indent=2)+'\n')
