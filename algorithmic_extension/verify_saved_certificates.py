"""Check saved certificates without importing or executing the menu solver."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import hashlib
import json
import time
import numpy as np
from interval_verifier import IntervalVerifier

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/certificates_v2'
records=json.loads((OUT/'summary.json').read_text())
rows=[]
for certificate in records['rows']:
    start=time.perf_counter()
    assert certificate['status']=='PASS_OUTWARD_BOUNDS'
    path=ROOT/'results/confirmation_v1'/certificate['artifact']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==certificate['artifact_sha256']
    with np.load(path) as z:
        verifier=IntervalVerifier(z['A'],z['C'],z['d'],int(z['rank']),float(z['upper']))
        upper=verifier.menu_upper(z['bases'],z['segments'])['upper']
        k=len(z['bases'])
    assert upper<=certificate['upper']
    points=certificate['witness_points']
    assert len(points)==k+1
    assert all(0<=a<b<=verifier.upper for a,b in zip(points[:-1],points[1:]))
    assert len(certificate['pairs'])==k
    margins=[]
    for i,pair in enumerate(certificate['pairs']):
        assert pair['left']==points[i] and pair['right']==points[i+1]
        checked=verifier.pair_lower(pair['left'],pair['right'],pair['dual_prices'])
        assert checked['lower']>certificate['lower']
        margins.append(checked['lower']-certificate['lower'])
    assert upper-certificate['lower']<=1.0001e-5
    rows.append({'artifact':path.name,'lower':certificate['lower'],'upper':upper,
                 'gap':upper-certificate['lower'],'min_exclusion_margin':min(margins),
                 'seconds':time.perf_counter()-start})
report={'status':'PASS_STANDALONE_INTERVAL_VERIFICATION','cases':len(rows),'rows':rows,
        'solver_imported':False,'source_sha256':{
            p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (Path(__file__),ROOT/'interval_verifier.py')},
        'scope':'Continuous-price global bounds under the documented IEEE-754/input contract; not a novelty assessment.'}
(OUT/'standalone_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'}),flush=True)
