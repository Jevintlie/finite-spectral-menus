"""Wrap immutable archives with the reports/logs that certify their exact bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from verify_publication_bundle import verify

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    tag = args.tag
    if not tag.replace('_', '').isalnum():
        raise ValueError('Invalid tag')
    out = ROOT / 'releases'
    target = out / f'paper2_publication_bundle_{tag}.zip'
    if target.exists():
        raise FileExistsError('Preserve prior bundles; use a new tag')
    payload = {}
    for name in (f'paper2_algorithmic_research_{tag}.zip',
                 f'paper2_algorithmic_arxiv_source_{tag}.zip',
                 f'paper2_journal_source_{tag}.zip'):
        payload['archives/' + name] = (out / name).read_bytes()
    for name in (f'package_{tag}.json', f'release_validation_{tag}.json',
                 f'journal_validation_{tag}.json', f'completion_{tag}.json'):
        payload['validation/' + name] = (out / name).read_bytes()
    report = json.loads(payload[f'validation/release_validation_{tag}.json'])
    for command in report['commands']:
        name = command['log']
        if Path(name).name != name:
            raise ValueError('Unsafe log name')
        payload['validation/logs/' + name] = (ROOT / 'release_checks' / tag / name).read_bytes()
    payload['main.pdf'] = (ROOT / 'manuscript/main.pdf').read_bytes()
    for name in ('REVIEW_BRIEF.pdf', 'REVIEW_BRIEF.tex', 'CLOSEST_PRIOR_RESULTS.md', 'RESPONSE_TEMPLATE.md'):
        payload['review/' + name] = (ROOT / 'submission/independent_review' / name).read_bytes()
    for name in ('LICENSE.md', 'LICENSE_CODE.txt', 'LICENSE_CONTENT.txt', 'verify_publication_bundle.py'):
        payload[name] = (ROOT / name).read_bytes()
    payload['START_HERE.md'] = f'''# Paper 2 publication handoff — {tag}

Author: Jevint Felixciano, Independent researcher.
Start with main.pdf. The three immutable ZIPs in archives/ are the complete
research artifact, arXiv source, and flat journal source. Reports in
validation/ certify those exact ZIPs; command logs are included in logs/.
This outer wrapper closes the missing-report handoff gap. No checksum
claims to certify a ZIP containing its own checksum.

Run: python verify_publication_bundle.py paper2_publication_bundle_{tag}.zip
(Pass the actual path to the original bundle after extracting this verifier.)

The check validates hashes and recorded outcomes. To replay the scientific
checks, extract the research ZIP and follow its REPRODUCIBILITY.md. Timings
are frozen evidence, not a new performance study. See review/ for a focused
request for independent criticism; no independent response is claimed.

Author identity and declarations are supplied. Public GitHub location,
arXiv submission, final author approval and prior/concurrent-submission
confirmation remain separate actions. The manuscript does not invent a
public URL. See submission/PUBLICATION_PLAN.md in the research artifact.
'''.encode('utf8')
    manifest = {'release': tag, 'files': {n: hashlib.sha256(b).hexdigest() for n, b in sorted(payload.items())}}
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            archive.writestr(name, data)
        archive.writestr('BUNDLE_MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    result = verify(target)
    result.update(bundle=target.name, sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (out / f'bundle_validation_{tag}.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
