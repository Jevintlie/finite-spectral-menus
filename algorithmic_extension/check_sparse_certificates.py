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
from tridiagonal_verifier import TridiagonalVerifier
from sparse_artifacts import load

ROOT=Path(__file__).resolve().parent
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--source',required=True)
parser.add_argument('--certificates',required=True)
args=parser.parse_args()
OUT=ROOT/args.certificates
records=json.loads((OUT/'summary.json').read_text())
assert records['status']=='PASS' and records['rows']
rows=[]
for certificate in records['rows']:
    start=time.perf_counter()
    assert certificate['status']=='PASS_OUTWARD_BOUNDS'
    path=ROOT/args.source/certificate['artifact']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==certificate['artifact_sha256']
    model_args,bases,segments=load(path)
    a=model_args['task'];c=model_args['costs'];d=model_args['overheads']
    rank=model_args['rank'];limit=model_args['upper']
    if certificate['verifier']=='tridiagonal':
        verifier=TridiagonalVerifier(a,c,d,rank,limit)
    else:
        assert certificate['verifier']=='dense'
        verifier=IntervalVerifier(a.toarray(),np.array([x.toarray() for x in c]),d,rank,limit)
    upper=verifier.menu_upper(bases,segments)['upper']
    k=len(bases)
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
            (Path(__file__),ROOT/'interval_verifier.py',ROOT/'tridiagonal_verifier.py')},
        'scope':'Continuous-price global bounds under the documented IEEE-754/input contract; not a novelty assessment.'}
(OUT/'standalone_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'}),flush=True)
