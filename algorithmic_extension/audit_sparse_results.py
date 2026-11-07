"""Check sparse-study provenance, counts, independent analyses and certificates."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads((ROOT/p).read_text())
summary=read('results/sparse_summary.json')
assert summary['status']=='PASS' and summary['runs']==72 and summary['saved_menus']==24
assert summary['scaling_runs']==7 and summary['certificate_artifacts']==8
assert summary['max_loss_crosscheck_error']<5e-8
for folder,expected in [('sparse_confirmation_v2',72),('sparse_scaling_v1',7)]:
    prefix='results/'+folder+'/'
    manifest=read(prefix+'manifest.json')
    for p,h in manifest['source_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    rows=list(map(json.loads,(ROOT/(prefix+'runs.jsonl')).read_text().splitlines()))
    assert len(rows)==expected and all(r['status']=='PASS_EXECUTION' for r in rows)
    assert read(prefix+'analysis.json')['status']=='PASS'
    execution=read(prefix+'execution.json')
    assert execution['runs']==execution['expected']==expected and execution['failures']==0
for folder,count in [('sparse_grid_certificates_v1',4),('sparse_path_certificates_v1',4)]:
    prefix='results/'+folder+'/'
    cert=read(prefix+'summary.json');replay=read(prefix+'standalone_verification.json')
    assert cert['status']=='PASS' and replay['status']=='PASS_STANDALONE_INTERVAL_VERIFICATION'
    assert cert['cases']==replay['cases']==count
    for p,h in cert['source_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    for row in cert['rows']:
        path=ROOT/cert['source']/row['artifact']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['artifact_sha256']
        assert 0<=row['gap']<=1.0001e-5 and row['min_exclusion_margin']>0
dev=read('results/sparse_development_v2.json')
assert dev['status']=='PASS' and len(dev['exact_rational_sturm_counts'])==27
assert len(dev['avoided_crossing'])==2 and all(r['recoveries']>0 for r in dev['avoided_crossing'])
old=read('results/sparse_confirmation_v1/execution.json')
assert old['recorded_runs']==18 and old['failures']==6
old_manifest=read('results/sparse_confirmation_v1/manifest.json')
for p,h in old_manifest['source_sha256'].items():
    assert hashlib.sha256((ROOT/'results/sparse_confirmation_v1/source_snapshot'/p).read_bytes()).hexdigest()==h
text=(ROOT/'manuscript/main.tex').read_text()
assert '\\input{sparse_study}' in text and '\\input{sparse_verification}' in text
report=dict(status='PASS',**{k:v for k,v in summary.items() if k!='status'},
            retained_failed_v1_runs=6,scope='Provenance, completed study checks, saved certificates and manuscript inputs; no universal sparse claim.')
(ROOT/'results/sparse_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
