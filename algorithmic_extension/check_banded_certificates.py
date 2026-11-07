"""Standalone certificate replay: does not import the menu or ARPACK solver."""
from pathlib import Path
import argparse,hashlib,json,sys,time
from banded_certificate_support import verify_records


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=6);args=parser.parse_args()
    root=Path(__file__).resolve().parent;out=root/'results/banded_certificates_v1'
    original=json.loads((out/'summary.json').read_text())
    assert original['status']=='PASS' and original['cases']==len(original['rows'])==14
    start=time.perf_counter();checked=verify_records(root,original['rows'],workers=args.workers)
    for a,b in zip(original['rows'],checked):
        assert a['artifact']==b['artifact'] and b['upper']<=a['upper'] and b['gap']<=a['gap']
    assert 'spectral_menu' not in sys.modules and 'sparse_spectral' not in sys.modules
    report=dict(status='PASS_STANDALONE_BANDED_VERIFICATION',cases=len(checked),
        rows=[{k:r[k] for k in ['artifact','lower','upper','gap','min_exclusion_margin','n','half_bandwidth']} for r in checked],
        seconds=time.perf_counter()-start,workers=args.workers,solver_imported=False,
        source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in
                       ['check_banded_certificates.py','banded_certificate_support.py','banded_verifier.py','interval_verifier.py','sparse_artifacts.py']})
    (out/'standalone_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['rows','source_sha256']}),flush=True)

if __name__=='__main__':main()
