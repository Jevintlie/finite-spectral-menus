"""Create portable source/evidence and arXiv-source archives; never upload."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--tag',default='v1')
args=parser.parse_args()
assert args.tag.replace('_','').isalnum()
out=ROOT/'releases'
out.mkdir(exist_ok=True)
research=out/f'paper2_algorithmic_research_{args.tag}.zip'
arxiv=out/f'paper2_algorithmic_arxiv_source_{args.tag}.zip'
assert not research.exists() and not arxiv.exists(),'Choose a new tag; preserve existing archives.'
files={}
for path in ROOT.iterdir():
    if path.is_file() and path.suffix in ('.py','.md','.txt'):
        files['algorithmic_extension/'+path.name]=path
for path in (ROOT/'results').rglob('*'):
    if path.is_file() and path.suffix in ('.json','.jsonl','.npz','.md','.py'):
        files['algorithmic_extension/'+path.relative_to(ROOT).as_posix()]=path
for path in (ROOT/'manuscript').rglob('*'):
    if path.is_file() and path.suffix in ('.tex','.bib','.bbl','.pdf','.py','.json') and 'preview' not in path.parts:
        files['algorithmic_extension/'+path.relative_to(ROOT).as_posix()]=path
files['submission_20261002/code/menu_solver.py']=ROOT.parent/'submission_20261002/code/menu_solver.py'
for path in (ROOT/'submission').rglob('*'):
    if path.name in ('CONTACTS_AND_DRAFTS.md', 'author_confirmation.json'):
        continue
    if path.is_file() and path.suffix in ('.tex','.pdf','.md','.txt','.json'):
        files['algorithmic_extension/'+path.relative_to(ROOT).as_posix()]=path
manifest={'files':{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in sorted(files.items())},
          'description':'Finite Menus of Spectral Subspaces: portable research artifact',
          'author_fields':'See manuscript/author_info.tex and submission/AUTHOR_FINALIZATION.md.',
          'licensing':'See LICENSE.md, LICENSE_CODE.txt, and LICENSE_CONTENT.txt. No upload performed.'}
with zipfile.ZipFile(research,'x',zipfile.ZIP_DEFLATED) as archive:
    for name,path in sorted(files.items()):archive.write(path,name)
    archive.writestr('ARTIFACT_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
texfiles=[]
with zipfile.ZipFile(arxiv,'x',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted((ROOT/'manuscript').rglob('*')):
        if not path.is_file() or 'preview' in path.parts:continue
        if path.suffix in ('.tex','.bib','.bbl') or (path.suffix=='.pdf' and path.parent.name=='figures'):
            name=path.relative_to(ROOT/'manuscript').as_posix()
            archive.write(path,name)
            texfiles.append(name)
report={'research_archive':research.name,'research_files':len(files)+1,
        'research_sha256':hashlib.sha256(research.read_bytes()).hexdigest(),
        'arxiv_archive':arxiv.name,'arxiv_inputs':texfiles,
        'arxiv_sha256':hashlib.sha256(arxiv.read_bytes()).hexdigest()}
(out/f'package_{args.tag}.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
