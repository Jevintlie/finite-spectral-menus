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
from spectral_menu import SpectralModel
from reused_spectral import as_reused
from interval_verifier import IntervalVerifier

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'results/confirmation_v1'
OUT=ROOT/'results/certificates_v2'
OUT.mkdir(exist_ok=True)
rows=[]
for path in sorted(SOURCE.glob('*_reused.npz')):
    start=time.perf_counter()
    row={'artifact':path.name,'artifact_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    try:
        with np.load(path) as z:
            model=as_reused(SpectralModel(z['A'],z['C'],z['d'],int(z['rank']),float(z['upper'])))
            bases=z['bases']; segments=z['segments']
        verifier=IntervalVerifier(model.A,model.C,model.d,model.rank,model.upper)
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
report={'status':'PASS' if all(r['status']=='PASS_OUTWARD_BOUNDS' for r in rows) else 'FAILURES_PRESENT',
        'cases':len(rows),'rows':rows,
        'arithmetic_contract':'Exact binary64 input matrices; IEEE-754 outward elementary interval arithmetic; see CERTIFICATE_DERIVATION.md.',
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         (Path(__file__),ROOT/'interval_verifier.py',ROOT/'CERTIFICATE_DERIVATION.md')}}
(OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
