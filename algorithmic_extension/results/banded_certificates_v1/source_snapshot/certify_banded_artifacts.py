"""Generate numerical proposals, then independently check every grid certificate."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,hashlib,json,time,traceback
import numpy as np
from scipy.optimize import minimize_scalar
from sparse_artifacts import load
from sparse_spectral import PartialSpectralModel
from banded_certificate_support import verify_records

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/banded_certificates_v1'


def propose(name):
    start=time.perf_counter();path=ROOT/name
    args,bases,segments=load(path)
    old=ROOT/'results/sparse_grid_certificates_v1'/path.with_suffix('.json').name
    if old.exists():
        oldrow=json.loads(old.read_text())
        assert oldrow['status']=='PASS_OUTWARD_BOUNDS'
        row={k:oldrow[k] for k in ['lower','witness_points','pairs']}
        row['proposal_source']='existing_v4_witness'
    else:
        model=PartialSpectralModel(**args,backend='dense_partial' if args['task'].shape[0]<=256 else 'sparse')
        upper=-np.inf
        for u,(a,b) in zip(bases,segments):
            intercept=-float(np.sum(u*(model.A@u)))
            costs=[float(np.sum(u*(c@u)))+d for c,d in zip(model.C,model.d)]
            fa,fb=model.optimum(a),model.optimum(b)
            upper=max(upper,min(max(intercept+a*c-fa,intercept+b*c-fb) for c in costs))
        epsilon=max(0.,float(np.nextafter(upper-1e-5,np.inf)))
        witness=model.packing(epsilon,len(bases),step=2e-6,oracle_tol=1e-9)
        if witness is None:raise ArithmeticError('No packing proposal at requested tolerance')
        pairs=[]
        for a,b in zip(witness['points'][:-1],witness['points'][1:]):
            fa,fb=model.optimum(a),model.optimum(b);prices=[]
            for site in range(len(model.d)):
                def phi(p):return model.branch(p,site)-fa-(p-a)*(fb-fa)/(b-a)
                opt=minimize_scalar(lambda p:-phi(p),bounds=(a,b),method='bounded',options={'xatol':1e-13})
                prices.append(float(max((a,float(opt.x),b),key=phi)))
            pairs.append(dict(left=a,right=b,dual_prices=prices))
        row=dict(lower=epsilon,witness_points=witness['points'],pairs=pairs,proposal_source=model.backend)
    row.update(artifact=name,artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
               proposal_seconds=time.perf_counter()-start)
    return row


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=6);args=parser.parse_args()
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'summary.json').exists(),'Preserve the prior attempt; select a new version for changes'
    sources=['banded_verifier.py','banded_certificate_support.py','certify_banded_artifacts.py',
             'interval_verifier.py','sparse_artifacts.py','sparse_spectral.py','BANDED_VERIFICATION_PROTOCOL.md']
    manifest=dict(source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},workers=args.workers)
    mf=OUT/'manifest.json'
    if mf.exists():assert json.loads(mf.read_text())['source_sha256']==manifest['source_sha256']
    else:mf.write_text(json.dumps(manifest,indent=2)+'\n')
    paths=sorted((ROOT/'results/sparse_confirmation_v2').glob('*_sparse.npz'))
    paths+=sorted((ROOT/'results/sparse_scaling_v1').glob('grid_*_sparse.npz'))
    assert len(paths)==14
    rows=[];failures=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        tasks={}
        for p in paths:
            target=OUT/(p.stem+'_proposal.json')
            if target.exists():rows.append(json.loads(target.read_text()))
            else:tasks[pool.submit(propose,p.relative_to(ROOT).as_posix())]=target
        for future in as_completed(tasks):
            try:
                row=future.result();rows.append(row)
                tasks[future].write_text(json.dumps(row,indent=2)+'\n')
                print('Proposal ready:',row['artifact'],flush=True)
            except Exception as exc:failures.append(dict(target=str(tasks[future]),error=repr(exc),traceback=traceback.format_exc()))
    if failures:
        (OUT/'proposal_failures.json').write_text(json.dumps(failures,indent=2)+'\n')
        raise RuntimeError('Proposal failures retained')
    start=time.perf_counter()
    try:checked=verify_records(ROOT,sorted(rows,key=lambda r:r['artifact']),workers=args.workers)
    except Exception as exc:
        (OUT/'verification_failure.json').write_text(json.dumps(dict(error=repr(exc),traceback=traceback.format_exc()),indent=2)+'\n')
        raise
    report=dict(status='PASS',cases=len(checked),rows=checked,parallel_verification_seconds=time.perf_counter()-start,
                workers=args.workers,scope='Outward band LDL and exact-polar menu/packing bounds; exact binary64 arithmetic contract.')
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',cases=len(checked),seconds=report['parallel_verification_seconds'],max_gap=max(r['gap'] for r in checked))),flush=True)

if __name__=='__main__':main()
