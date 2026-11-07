"""Check v7 packaging and unchanged science; not an external-review certificate."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf8'))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    old = read('releases/completion_v6.json')
    for name, expected in old['archive_hashes'].items():
        check(sha(ROOT / 'releases' / name) == expected, 'Changed v6 archive: ' + name)
    frozen = read('results/publication_audit_v6/frozen_evidence.json')
    for name, expected in frozen['hashes'].items():
        check(sha(ROOT / name) == expected, 'Changed frozen evidence: ' + name)
    tex = (ROOT / 'manuscript/main.tex').read_text(encoding='utf8')
    with zipfile.ZipFile(ROOT / 'releases/paper2_algorithmic_arxiv_source_v6.zip') as archive:
        before = archive.read('main.tex').decode().replace('\r\n', '\n')
        check(tex.split('\\section*{Statements and declarations}')[0] == before.split('\\section*{Statements and declarations}')[0], 'Changed scientific main text')
        check(tex.split('\\appendix', 1)[1] == before.split('\\appendix', 1)[1], 'Changed appendices')
        for name in archive.namelist():
            if name not in ('main.tex', 'author_info.tex', 'main.bbl'):
                check((ROOT / 'manuscript' / name).read_bytes() == archive.read(name), 'Changed scientific input: ' + name)
    author = (ROOT / 'manuscript/author_info.tex').read_text()
    for value in ('Jevint Felixciano', 'Independent researcher', 'jevintfelixciano@protonmail.com'):
        check(value in author, 'Missing author field')
    check('placeholder' not in author.lower() and '[To be supplied' not in tex, 'Unresolved author placeholder')
    check('AI assistance was used' in tex, 'AI disclosure missing')
    check('no external funding' in tex and 'no competing interests' in tex, 'Confirmed declaration missing')
    metadata = read('submission/arxiv_metadata.json')
    check(metadata['authors'] == 'Jevint Felixciano' and metadata['license'] == 'CC BY 4.0', 'Metadata mismatch')
    check(metadata['abstract_latex'] == tex.split('\\begin{abstract}')[1].split('\\end{abstract}')[0].strip(), 'Abstract mismatch')
    validation = read('releases/release_validation_v7.json')
    journal = read('releases/journal_validation_v7.json')
    check(validation['status'] == journal['status'] == 'PASS', 'Validation failed')
    check(len(validation['commands']) == 11 and all(c['returncode'] == 0 for c in validation['commands']), 'Incomplete clean checks')
    hashes = {}
    for item in list(validation['archives'].values()) + [journal]:
        name = item.get('name', item.get('archive'))
        check(sha(ROOT / 'releases' / name) == item['sha256'], 'Archive/report mismatch')
        hashes[name] = item['sha256']
    check(journal['clean_build'] and journal['pdf_text_matches_working_manuscript'], 'Journal build mismatch')
    log = (ROOT / 'manuscript/main.log').read_text(errors='replace')
    check(not any(s in log for s in ('Overfull', 'Underfull', 'undefined', 'Fatal error')), 'LaTeX warning')
    pages = int(re.search(r'Output written on main.pdf \((\d+) pages?', log)[1])
    with zipfile.ZipFile(ROOT / 'releases/paper2_algorithmic_research_v7.zip') as archive:
        check(not any('CONTACTS_AND_DRAFTS' in n or '/resources/' in n or '/.venv/' in n for n in archive.namelist()), 'Excluded preparation/private material packaged')
        manifest = json.loads(archive.read('ARTIFACT_MANIFEST.json'))
        for name, expected in manifest['files'].items():
            check(hashlib.sha256(archive.read(name)).hexdigest() == expected, 'Research member mismatch')
    result = {'status': 'PASS', 'release': 'v7', 'checked_on': '2026-11-07',
              'pages': pages, 'archive_hashes': hashes,
              'manuscript_pdf_sha256': sha(ROOT / 'manuscript/main.pdf'),
              'frozen_files_checked': len(frozen['hashes']),
              'scientific_text_and_inputs_unchanged_from_v6': True,
              'v6_archives_unchanged': True, 'clean_validation_commands': 11,
              'author_fields_supplied': True, 'licenses_authorized': True,
              'new_performance_benchmarks': False,
              'independent_review': 'Prepared; no reviewer contacted or response received',
              'public_artifact_url': None, 'arxiv_submission': 'Not performed',
              'submission_ready': False,
              'pending': ['Final author approval', 'Prior/concurrent submission confirmation',
                          'Live GitHub artifact URL and manuscript update', 'Independent criticism',
                          'arXiv account/endorsement/upload'],
              'scope': 'PASS is a technical preparation gate, not proof, priority, peer review, or public submission.'}
    (ROOT / 'releases/completion_v7.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
