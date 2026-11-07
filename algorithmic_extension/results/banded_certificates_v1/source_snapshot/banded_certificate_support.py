"""Solver-independent parallel branch checks and finite witness replay."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import hashlib,time
import numpy as np
from banded_verifier import BandedVerifier
from sparse_artifacts import load


def make_verifier(path):
    args,bases,segments=load(path)
    return BandedVerifier(args['task'],args['costs'],args['overheads'],args['rank'],args['upper']),bases,segments


def branch_job(item):
    path,p,site=item
    verifier,_,_=make_verifier(path)
    start=time.perf_counter();bound=verifier.branch(p,site)
    return dict(path=path,p=p,site=site,bound=bound,seconds=time.perf_counter()-start,**verifier.storage())


def verify_records(root,records,workers=6):
    """Precompute independently checked branches in CPU processes, then replay."""
    root=Path(root);jobs=[];contexts={};bounds={}
    for row in records:
        path=root/row['artifact']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['artifact_sha256']
        verifier,bases,segments=make_verifier(path)
        points=row['witness_points'];k=len(bases)
        assert len(points)==k+1 and len(row['pairs'])==k
        assert all(0<=a<b<=verifier.upper for a,b in zip(points[:-1],points[1:]))
        assert np.isfinite(row['lower']) and row['lower']>=0
        prices=set(float(p) for p in segments.ravel())|set(points)
        for i,pair in enumerate(row['pairs']):
            assert pair['left']==points[i] and pair['right']==points[i+1]
            assert len(pair['dual_prices'])==len(verifier.d)
            assert all(pair['left']<=p<=pair['right'] for p in pair['dual_prices'])
        queries={(p,site) for p in prices for site in range(len(verifier.d))}
        queries|={(float(p),site) for pair in row['pairs'] for site,p in enumerate(pair['dual_prices'])}
        jobs.extend((str(path),p,site) for p,site in sorted(queries))
        contexts[str(path)]=(row,verifier,bases,segments)
        bounds[str(path)]=[]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(branch_job,job):job for job in jobs}
        for future in as_completed(futures):
            result=future.result();path=result['path']
            contexts[path][1].eigen_cache[(result['p'],result['site'])]=tuple(result['bound'])
            bounds[path].append(result)
    checked=[]
    for path,(row,verifier,bases,segments) in contexts.items():
        before=len(verifier.eigen_cache)
        upper=verifier.menu_upper(bases,segments)
        pairs=[dict(left=p['left'],right=p['right'],dual_prices=p['dual_prices'],
                    **verifier.pair_lower(p['left'],p['right'],p['dual_prices'])) for p in row['pairs']]
        assert len(verifier.eigen_cache)==before,'All branch work must use independent precomputed bounds'
        margin=min(p['lower']-row['lower'] for p in pairs)
        # Outward subtraction also bounds the width itself.
        gap=float(np.nextafter(upper['upper']-row['lower'],np.inf))
        assert margin>0,(path,'Nonpositive exclusion margin',margin)
        assert 0<=gap<1.01e-5,(path,'Global gap too wide',gap)
        statistics=verifier.storage()
        for key in ['successful_counts','rejected_counts','bracket_expansions']:
            statistics[key]=sum(b[key] for b in bounds[path])
        checked.append(dict(artifact=row['artifact'],artifact_sha256=row['artifact_sha256'],
                            status='PASS_OUTWARD_BOUNDS',lower=row['lower'],upper=upper['upper'],
                            gap=gap,upper_segments=upper['segments'],witness_points=row['witness_points'],
                            pairs=pairs,min_exclusion_margin=margin,branches=bounds[path],**statistics))
    return checked
