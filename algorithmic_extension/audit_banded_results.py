"""Audit new outward grid evidence without changing frozen optimization studies."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parent
folder=ROOT/'results/banded_certificates_v2'
manifest=json.loads((folder/'manifest.json').read_text())
for name,digest in manifest['source_sha256'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
summary=json.loads((folder/'summary.json').read_text())
replay=json.loads((folder/'standalone_verification.json').read_text())
assert summary['status']=='PASS' and replay['status']=='PASS_STANDALONE_BANDED_VERIFICATION'
assert summary['cases']==replay['cases']==14 and not replay['solver_imported']
for name,digest in replay['source_sha256'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
assert len({r['artifact'] for r in summary['rows']})==14
for row in summary['rows']:
    assert row['status']=='PASS_OUTWARD_BOUNDS' and row['min_exclusion_margin']>0
    assert 0<=row['gap']<1.01e-5
    assert hashlib.sha256((ROOT/row['artifact']).read_bytes()).hexdigest()==row['artifact_sha256']
    assert row['half_bandwidth']==int(row['n']**.5)
    assert len(row['witness_points'])==3 and len(row['pairs'])==2
old=ROOT/'results/banded_certificates_v1'
assert 'Nonpositive exclusion margin' in json.loads((old/'verification_failure.json').read_text())['error']
for name,digest in json.loads((old/'manifest.json').read_text())['source_sha256'].items():
    assert hashlib.sha256((old/'source_snapshot'/name).read_bytes()).hexdigest()==digest,name
dev=json.loads((ROOT/'results/banded_development_v2.json').read_text())
assert dev['status']=='PASS' and len(dev['exact_counts'])==dev['decimal_exact_count_cases']==144
assert len(dev['exact_sum_checks'])==7 and len(dev['enclosures'])==16
assert dev['nonsingular_zero_pivot_rejected'] and dev['bandwidth_limit_enforced']
assert '\\input{banded_results}' in (ROOT/'manuscript/sparse_study.tex').read_text()
report=dict(status='PASS',grid_certificate_artifacts=14,max_n=max(r['n'] for r in summary['rows']),
    max_gap=max(r['gap'] for r in summary['rows']),
    decimal_counts=sum(r['decimal_counts'] for r in summary['rows']),
    binary64_only_large_cases=all(r['decimal_counts']==0 for r in summary['rows'] if r['n']>=1024),
    exact_count_checks_per_arithmetic=144,retained_failure=True)
(ROOT/'results/banded_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
