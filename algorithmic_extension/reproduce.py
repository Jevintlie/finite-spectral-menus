"""Reproduce in a new isolated directory, preserving all distributed records.

verify: replay all saved primary analyses and interval certificates.
smoke: solve a fresh two-preset problem and independently check its certificate.
full: rerun the three timing studies, dictionaries, and all main certificates.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

if not __debug__:
    raise RuntimeError('Verification requires normal Python, without -O or PYTHONOPTIMIZE.')
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--mode',choices=['verify','smoke','full','sparse-full'],default='verify')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
destination=args.output or ROOT/'reproductions'/stamp
longest_relative=max((len(str(p.relative_to(ROOT))) for p in (ROOT/'results').rglob('*')
                      if p.is_file()),default=110)
if args.output is None and os.name=='nt' and len(str(destination/'algorithmic_extension'))+longest_relative+1>=240:
    destination=Path(tempfile.gettempdir())/f'spectral_menu_{stamp}'
    print('Using a shorter Windows reproduction path:',destination,flush=True)
destination.mkdir(parents=True,exist_ok=False)
work=destination/'algorithmic_extension'
work.mkdir()
for path in ROOT.iterdir():
    if path.is_file() and path.suffix in ('.py','.md','.txt'):
        shutil.copy2(path,work/path.name)
if args.mode=='verify':
    shutil.copytree(ROOT/'results',work/'results')
else:
    (work/'results').mkdir()
reference=ROOT.parent/'submission_20261002/code/menu_solver.py'
target=destination/'submission_20261002/code/menu_solver.py'
target.parent.mkdir(parents=True)
shutil.copy2(reference,target)

certificates=[('results/confirmation_v1','results/certificates_v2'),
              ('results/warm_confirmation_v1','results/warm_certificates_v1'),
              ('results/dictionary_comparison_v2','results/dictionary_certificates_v1')]
if args.mode=='verify':
    commands=[['verify_confirmation.py'],['verify_warm_confirmation.py'],
              ['verify_reuse_ablation.py'],['check_interval_arithmetic.py'],
              ['check_structural_example.py'],['check_structural_theory.py']]
    commands += [['check_certificates.py','--source',source,'--certificates',cert]
                 for source,cert in certificates]
    commands += [['check_sparse_backend.py'],['verify_sparse_confirmation_v2.py'],
                 ['verify_sparse_scaling.py']]
    for source,cert in [('results/sparse_confirmation_v2','results/sparse_grid_certificates_v1'),
                        ('results/sparse_scaling_v1','results/sparse_path_certificates_v1')]:
        commands += [['check_sparse_certificates.py','--source',source,'--certificates',cert]]
    commands += [['check_banded_verifier.py'],['check_banded_certificates_v2.py','--workers','6']]
elif args.mode=='smoke':
    commands=[['check_structural_example.py'],['smoke_solver.py']]
elif args.mode=='sparse-full':
    commands=[['check_sparse_backend.py'],['run_sparse_confirmation_v2.py'],
              ['verify_sparse_confirmation_v2.py'],['run_sparse_scaling.py'],
              ['verify_sparse_scaling.py'],
              ['certify_sparse_artifacts.py','--source','results/sparse_confirmation_v2',
               '--output','results/sparse_grid_certificates_v1','--pattern','grid_n128*_sparse.npz'],
              ['check_sparse_certificates.py','--source','results/sparse_confirmation_v2',
               '--certificates','results/sparse_grid_certificates_v1'],
              ['certify_sparse_artifacts.py','--source','results/sparse_scaling_v1',
               '--output','results/sparse_path_certificates_v1','--pattern','path_*.npz','--tridiagonal'],
              ['check_sparse_certificates.py','--source','results/sparse_scaling_v1',
               '--certificates','results/sparse_path_certificates_v1'],
              ['check_banded_verifier.py'],['certify_banded_artifacts_v2.py','--workers','6'],
              ['check_banded_certificates_v2.py','--workers','6']]
else:
    commands=[['run_confirmation.py'],['verify_confirmation.py'],
              ['run_warm_confirmation.py'],['verify_warm_confirmation.py'],
              ['run_reuse_ablation.py'],['verify_reuse_ablation.py'],
              ['compare_dictionaries.py'],['compare_special_case.py'],
              ['check_interval_arithmetic.py'],['check_structural_example.py'],
              ['stress_oracle.py'],['check_structural_theory.py']]
    for source,cert in certificates:
        commands += [['certify_artifacts.py','--source',source,'--output',cert],
                     ['check_certificates.py','--source',source,'--certificates',cert]]
records=[]
try:
    for command in commands:
        print('Running',*command,flush=True)
        start=time.perf_counter()
        result=subprocess.run([sys.executable,*command],cwd=work,capture_output=True,text=True)
        log=work/(command[0].replace('.py','')+f'_{len(records)}.log')
        log.write_text(result.stdout+'\n'+result.stderr,encoding='utf8')
        records.append(dict(command=command,returncode=result.returncode,
                            seconds=time.perf_counter()-start,log=log.name))
        if result.returncode:
            raise RuntimeError(f'{command[0]} failed; see {log}')
    status='PASS'
finally:
    report=dict(status='PASS' if len(records)==len(commands) and all(x['returncode']==0 for x in records) else 'FAIL',
                mode=args.mode,commands=records,python=sys.version,
                original_source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in ROOT.glob('*.py')})
    (destination/'reproduction_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=status,mode=args.mode,report=str(destination/'reproduction_report.json'))),flush=True)
