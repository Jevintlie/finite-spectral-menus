"""Check v9 citation refinements, packaging and preserved proofs/evidence; not an external-review certificate."""
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
    previous = read('releases/completion_v7.json')
    for name, expected in previous['archive_hashes'].items():
        check(sha(ROOT / 'releases' / name) == expected, 'Changed v7 archive: ' + name)
    previous_v8 = read('releases/completion_v8.json')
    for name, expected in previous_v8['archive_hashes'].items():
        check(sha(ROOT / 'releases' / name) == expected, 'Changed v8 archive: ' + name)
    published = read('releases/github_publication_v8.json')
    check(published['status'] == 'PASS' and published['public_download_hashes_verified'], 'Unverified public artifact')
    frozen = read('results/publication_audit_v6/frozen_evidence.json')
    for name, expected in frozen['hashes'].items():
        check(sha(ROOT / name) == expected, 'Changed frozen evidence: ' + name)
    tex = (ROOT / 'manuscript/main.tex').read_text(encoding='utf8')
    with zipfile.ZipFile(ROOT / 'releases/paper2_algorithmic_arxiv_source_v8.zip') as archive:
        for name in archive.namelist():
            if name not in ('references.bib', 'prior_art_comparison.tex', 'main.bbl'):
                check((ROOT / 'manuscript' / name).read_bytes() == archive.read(name), 'Changed proof/scientific input: ' + name)
        before = archive.read('prior_art_comparison.tex').decode().replace('\r\n', '\n')
        expected = before.replace('uncertainty set, within a bounded integer-recourse setting. Here the',
            'uncertainty set, within a bounded integer-recourse setting and under\n'
            'continuity assumptions in the uncertainty and recourse decision. The\n'
            'approximation bound additionally assumes Lipschitz continuity in the\n'
            'recourse decision. Here the')
        check(expected != before, 'Expected prior-art edit missing from baseline')
        check((ROOT / 'manuscript/prior_art_comparison.tex').read_text(encoding='utf8') == expected, 'Unexpected prior-art change')
        old_bib = archive.read('references.bib').decode().replace('\r\n', '\n')
        new_bib = (ROOT / 'manuscript/references.bib').read_text(encoding='utf8')
        def entries(text):
            return {part.split(',', 1)[0].split('{', 1)[1]: part.strip() for part in text.split('@')[1:]}
        old_entries, new_entries = entries(old_bib), entries(new_bib)
        check(old_entries.keys() == new_entries.keys(), 'Changed bibliography keys')
        changed = {key for key in old_entries if old_entries[key] != new_entries[key]}
        check(changed == {'shen2026', 'diakonikolas2008', 'scipyeigsh'}, 'Unexpected bibliography edits: ' + str(changed))
        check('Article~17' in new_entries['shen2026'] and 'pages={17}' not in new_entries['shen2026'], 'Article number error')
        check('https://www.iliasdiakonikolas.org/papers/convex-pareto-soda.pdf' in new_entries['diakonikolas2008'], 'Missing author PDF')
        check('SciPy 1.18.0 reference documentation' in new_entries['scipyeigsh'] and 'Implementation used: SciPy 1.18.1' in new_entries['scipyeigsh'], 'SciPy versions conflated')
        old_keys = re.findall(r'\\bibitem\{([^}]+)\}', archive.read('main.bbl').decode())
        new_keys = re.findall(r'\\bibitem\{([^}]+)\}', (ROOT / 'manuscript/main.bbl').read_text())
        check(old_keys == new_keys and len(new_keys) == 20, 'Changed cited references')
    check('https://github.com/Jevintlie/finite-spectral-menus/releases/tag/v7' in tex, 'Missing public artifact URL')
    author = (ROOT / 'manuscript/author_info.tex').read_text()
    for value in ('Jevint Felixciano', 'Independent researcher', 'jevintfelixciano@protonmail.com'):
        check(value in author, 'Missing author field')
    check('placeholder' not in author.lower() and '[To be supplied' not in tex, 'Unresolved author placeholder')
    check('AI assistance was used' in tex, 'AI disclosure missing')
    check('no external funding' in tex and 'no competing interests' in tex, 'Confirmed declaration missing')
    metadata = read('submission/arxiv_metadata.json')
    check(metadata['authors'] == 'Jevint Felixciano' and metadata['license'] == 'CC BY 4.0', 'Metadata mismatch')
    check(metadata['abstract_latex'] == tex.split('\\begin{abstract}')[1].split('\\end{abstract}')[0].strip(), 'Abstract mismatch')
    validation = read('releases/release_validation_v9.json')
    journal = read('releases/journal_validation_v9.json')
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
    with zipfile.ZipFile(ROOT / 'releases/paper2_algorithmic_research_v9.zip') as archive:
        check(not any('CONTACTS_AND_DRAFTS' in n or '/resources/' in n or '/.venv/' in n for n in archive.namelist()), 'Excluded preparation/private material packaged')
        manifest = json.loads(archive.read('ARTIFACT_MANIFEST.json'))
        for name, expected in manifest['files'].items():
            check(hashlib.sha256(archive.read(name)).hexdigest() == expected, 'Research member mismatch')
    result = {'status': 'PASS', 'release': 'v9', 'checked_on': '2026-11-08',
              'pages': pages, 'archive_hashes': hashes,
              'manuscript_pdf_sha256': sha(ROOT / 'manuscript/main.pdf'),
              'frozen_files_checked': len(frozen['hashes']),
              'proofs_algorithms_and_frozen_evidence_unchanged_from_v8': True,
              'changes': 'Four citation/assumption refinements and submission documentation',
              'cited_references': 20, 'v7_v8_archives_unchanged': True,
              'v6_archives_unchanged': True, 'clean_validation_commands': 11,
              'prior_concurrent_status_confirmed': True,
              'author_fields_supplied': True, 'licenses_authorized': True,
              'new_performance_benchmarks': False,
              'independent_review': 'Prepared; no reviewer contacted or response received',
              'public_artifact_url': 'https://github.com/Jevintlie/finite-spectral-menus/releases/tag/v7', 'arxiv_submission': 'Not performed',
              'technically_ready_for_author_upload': True,
              'pending': ['arXiv account/endorsement if required/upload',
                          'Author inspection of arXiv-generated PDF and final submission'],
              'scope': 'PASS is a technical preparation gate, not proof, priority, peer review, or public submission.'}
    (ROOT / 'releases/completion_v9.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
