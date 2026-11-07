"""Extract release archives, check hashes, replay evidence, and build both PDFs."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time
import zipfile

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--tag',default='v1')
args=parser.parse_args()
assert args.tag.replace('_','').isalnum()
base=ROOT/'release_checks'/args.tag
base.mkdir(parents=True,exist_ok=False)
archives={key:ROOT/'releases'/f'paper2_algorithmic_{suffix}_{args.tag}.zip'
          for key,suffix in [('research','research'),('arxiv','arxiv_source')]}
for key,path in archives.items():
    destination=base/key
    destination.mkdir()
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not (destination/name).resolve().is_relative_to(destination.resolve()):
                raise ValueError('Archive path escapes extraction directory.')
        archive.extractall(destination)
research=base/'research/algorithmic_extension'
arxiv=base/'arxiv'
commands=[([sys.executable,'verify_distribution.py'],research),
          ([sys.executable,'reproduce.py','--mode','verify'],research),
          ([sys.executable,'reproduce.py','--mode','smoke'],research),
          ([sys.executable,'manuscript/build.py'],research),
          ([sys.executable,'audit_results.py'],research),
          ([sys.executable,'audit_sparse_results.py'],research),
          ([sys.executable,'audit_banded_results.py'],research)]
commands += [(command,arxiv) for command in [
    ['pdflatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','main.tex'],
    ['bibtex','main'],
    ['pdflatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','main.tex'],
    ['pdflatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','main.tex']]]
records=[]
try:
    for i,(command,cwd) in enumerate(commands):
        start=time.perf_counter()
        print('Validating',cwd.name,*command[1:],flush=True)
        result=subprocess.run(command,cwd=cwd,capture_output=True,text=True)
        log=base/f'command_{i}.log'
        log.write_text(result.stdout+'\n'+result.stderr,encoding='utf8')
        records.append(dict(command=command,cwd=str(cwd.relative_to(base)),
                            returncode=result.returncode,seconds=time.perf_counter()-start,log=log.name))
        if result.returncode:
            raise RuntimeError(f'Release validation failed: {log}')
    for folder in [research/'manuscript',arxiv]:
        log=(folder/'main.log').read_text(errors='replace')
        assert not any(s in log for s in ['Overfull','Underfull','undefined','Fatal error'])
        assert (folder/'main.pdf').stat().st_size>10000
    passed=True
finally:
    report=dict(status='PASS' if locals().get('passed',False) else 'FAIL',
        archives={key:dict(name=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                  for key,path in archives.items()},commands=records,
        scope='Clean extraction and distributed hashes; original 134 menu checks/54 certificate replays; sparse 31 menu checks/8 certificate replays; 14 banded grid certificate replays and both arithmetic paths; structural diagnostics; fresh smoke solve/certificate; both PDF builds. Significance and priority assessed separately.')
    path=ROOT/'releases'/f'release_validation_{args.tag}.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],report=str(path))),flush=True)
