"""Generate checkable upper menus and lower packing witnesses from saved menus."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import hashlib
import json
import time
import traceback
import numpy as np
from scipy.optimize import minimize_scalar
from sparse_spectral import PartialSpectralModel
from sparse_artifacts import load
from tridiagonal_verifier import TridiagonalVerifier
from interval_verifier import IntervalVerifier

ROOT=Path(__file__).resolve().parent
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--source',required=True)
parser.add_argument('--output',required=True)
parser.add_argument('--pattern',default='*_sparse.npz')
parser.add_argument('--tridiagonal',action='store_true')
args=parser.parse_args()
SOURCE=ROOT/args.source
OUT=ROOT/args.output
OUT.mkdir(parents=True,exist_ok=True)
assert not (OUT/'summary.json').exists(),'Preserve prior results; choose a new output directory.' 
rows=[]
for path in sorted(SOURCE.glob(args.pattern)):
    start=time.perf_counter()
    row={'artifact':path.name,'artifact_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    try:
        model_args,bases,segments=load(path)
        model=PartialSpectralModel(**model_args,backend='tridiagonal' if args.tridiagonal else 'dense_partial')
        if args.tridiagonal:
            verifier=TridiagonalVerifier(model.A,model.C,model.d,model.rank,model.upper)
        else:
            verifier=IntervalVerifier(model.A,np.array(model.C),model.d,model.rank,model.upper)
        row['verifier']='tridiagonal' if args.tridiagonal else 'dense'
        upper=verifier.menu_upper(bases,segments)
        epsilon=max(0.,upper['upper']-1e-5)
        witness=model.packing(epsilon,len(bases),step=1e-6,oracle_tol=1e-9)
        if witness is None:
            raise ArithmeticError('No numerical packing at the requested gap; no certificate claimed.')
        pair_records=[]
        for a,b in zip(witness['points'][:-1],witness['points'][1:]):
            fa,fb=model.optimum(a),model.optimum(b)
            # A reused primal basis can originate outside [a,b]; its source
            # price is not a valid dual witness. Independently optimize the
            # scalar dual over this pair instead. The verifier trusts neither
            # this optimizer nor its value, only its proposed in-range price.
            prices=[]
            for site in range(len(model.d)):
                def phi(p):
                    return model.branch(p,site)-fa-(p-a)*(fb-fa)/(b-a)
                opt=minimize_scalar(lambda p:-phi(p),bounds=(a,b),method='bounded',
                                    options={'xatol':1e-13})
                prices.append(max((a,float(opt.x),b),key=phi))
            checked=verifier.pair_lower(a,b,prices)
            assert checked['lower']>epsilon,(checked['lower'],epsilon)
            pair_records.append({'left':a,'right':b,'dual_prices':prices,**checked})
        row.update(status='PASS_OUTWARD_BOUNDS',upper=upper['upper'],lower=epsilon,
                   gap=upper['upper']-epsilon,upper_segments=upper['segments'],
                   witness_points=witness['points'],pairs=pair_records,
                   min_exclusion_margin=min(p['lower']-epsilon for p in pair_records))
    except Exception as exc:
        row.update(status='FAILED_TO_CERTIFY',error=repr(exc),traceback=traceback.format_exc())
    row['seconds']=time.perf_counter()-start
    rows.append(row)
    (OUT/path.with_suffix('.json').name).write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps({k:row[k] for k in ('artifact','status','seconds')}),flush=True)
report={'status':'PASS' if rows and all(r['status']=='PASS_OUTWARD_BOUNDS' for r in rows) else 'FAILURES_PRESENT',
        'cases':len(rows),'rows':rows,'source':args.source,
        'arithmetic_contract':'Exact binary64 input matrices; IEEE-754 outward elementary interval arithmetic; see CERTIFICATE_DERIVATION.md.',
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         (Path(__file__),ROOT/'interval_verifier.py',ROOT/'CERTIFICATE_DERIVATION.md',ROOT/'tridiagonal_verifier.py',ROOT/'SPARSE_VERIFICATION.md')}}
(OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
