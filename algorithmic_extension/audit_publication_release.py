"""Verify current v6 publication-preparation gates after clean release validation.

Mechanical checks bind the separately documented internal proof/literature and
visual reviews to the actual files. They do not prove theorems or originality.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf8'))


def main():
    if not __debug__:
        raise RuntimeError('Run without Python optimization flags.')
    validation = read('releases/release_validation_v6.json')
    journal = read('releases/journal_validation_v6.json')
    package = read('releases/package_v6.json')
    freeze = read('results/publication_audit_v6/frozen_evidence.json')
    review = read('results/publication_audit_v6/review_record.json')
    for report in (validation, journal, freeze):
        assert report['status'] == 'PASS'
    assert len(validation['commands']) == 11
    assert all(c['returncode'] == 0 for c in validation['commands'])
    archive_hashes = {}
    for key in ('research', 'arxiv'):
        path = ROOT / 'releases' / package[f'{key}_archive']
        digest = sha(path)
        assert digest == package[f'{key}_sha256'] == validation['archives'][key]['sha256']
        archive_hashes[path.name] = digest
    path = ROOT / 'releases' / journal['archive']
    assert sha(path) == journal['sha256']
    archive_hashes[path.name] = sha(path)
    assert journal['no_subfolders'] and journal['clean_build']
    assert journal['pdf_text_matches_working_manuscript'] and journal['pages'] == 22
    for name, expected in freeze['hashes'].items():
        assert sha(ROOT / name) == expected, name
    data_now = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'results').rglob('*')
                if p.is_file() and (p.name == 'runs.jsonl' or p.suffix == '.npz')}
    assert data_now == {n for n in freeze['hashes'] if n.startswith('results/')}
    for name, expected in review['hashes'].items():
        assert sha(ROOT / name) == expected, name

    old_package = read('releases/package_v5.json')
    for key in ('research', 'arxiv'):
        assert sha(ROOT / 'releases' / old_package[f'{key}_archive']) == old_package[f'{key}_sha256']
    tex = (ROOT / 'manuscript/main.tex').read_text(encoding='utf8')
    with zipfile.ZipFile(ROOT / 'releases' / old_package['arxiv_archive']) as archive:
        old = archive.read('main.tex').decode().replace('\r\n', '\n')
        old_block = old.split('\\section{Computational study}', 1)[1].split('\\section{Scope and conclusions}', 1)[0].strip()
        new_block = tex.split('\\section{Computational protocols and complete results}\\label{app:experiments}', 1)[1].split('\\section{Outward bounds', 1)[0].strip()
        assert old_block == new_block
        unchanged_inputs = [n for n in archive.namelist() if n.startswith(('tables/', 'figures/')) or n in
                            ('sparse_study.tex', 'sparse_verification.tex', 'sparse_results.tex', 'banded_results.tex')]
        for name in unchanged_inputs:
            assert archive.read(name) == (ROOT / 'manuscript' / name).read_bytes(), name

    with zipfile.ZipFile(ROOT / 'releases' / package['research_archive']) as archive:
        manifest = json.loads(archive.read('ARTIFACT_MANIFEST.json'))
        for name, expected in manifest['files'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected, name
            if name.startswith('algorithmic_extension/'):
                local = ROOT / name.removeprefix('algorithmic_extension/')
                assert sha(local) == expected, name
        assert not any('/resources/' in name or '/.venv/' in name for name in archive.namelist())
        for name in ('submission/cover_letter.tex', 'submission/cover_letter.pdf',
                     'submission/arxiv_metadata.json', 'submission/AUTHOR_FINALIZATION.md',
                     'results/publication_audit_v6/literature_sources.json'):
            assert 'algorithmic_extension/' + name in archive.namelist()

    pdfs = [ROOT / 'manuscript/main.pdf',
            ROOT / 'release_checks/v6/research/algorithmic_extension/manuscript/main.pdf',
            ROOT / 'release_checks/v6/arxiv/main.pdf']
    with tempfile.TemporaryDirectory(prefix='paper2_text_check_') as tmp:
        texts = []
        for i, pdf in enumerate(pdfs):
            target = Path(tmp) / f'{i}.txt'
            subprocess.run(['pdftotext', '-layout', str(pdf), str(target)], check=True, capture_output=True)
            texts.append(target.read_bytes())
        assert texts[0] == texts[1] == texts[2]
    log = (ROOT / 'manuscript/main.log').read_text(errors='replace')
    assert not any(s in log for s in ('Overfull', 'Underfull', 'undefined', 'Fatal error'))
    pages = int(re.search(r'Output written on main.pdf \((\d+) pages?', log)[1])
    assert pages == 22
    abstract = tex.split('\\begin{abstract}')[1].split('\\end{abstract}')[0].strip()
    assert 150 <= len(abstract.split()) <= 250
    metadata = read('submission/arxiv_metadata.json')
    assert metadata['abstract_latex'] == abstract
    assert metadata['suggested_primary_category'] == 'math.OC'
    assert 'placeholder' in (ROOT / 'manuscript/author_info.tex').read_text()
    for field in ('Funding.', 'Competing interests.', 'Author contributions.'):
        assert '\\paragraph{' + field + '} [To be supplied' in tex
    assert 'AI assistance was used' in tex
    aux = (ROOT / 'manuscript/main.aux').read_text()
    theorem_numbers = {}
    for label, number in [('thm:factor', '3'), ('thm:exactness', '4'), ('thm:repair', '6')]:
        match = re.search(r'\\newlabel\{' + re.escape(label) + r'\}\{\{(\d+)\}', aux)
        assert match and match[1] == number
        theorem_numbers[label] = int(number)
    literature = read('results/publication_audit_v6/literature_sources.json')
    assert len(literature['sources']) == 11
    # The research copies are deliberately not distributed. Check them locally
    # when present, without requiring them to reproduce numerical evidence.
    for item in literature['sources']:
        local = ROOT / item['local_research_copy']
        if local.exists():
            assert sha(local) == item['sha256']
    evidence = {key: read('results/' + name) for key, name in
                [('dense', 'completion_evidence.json'), ('sparse', 'sparse_audit.json'), ('banded', 'banded_audit.json')]}
    assert all(item['status'] == 'PASS' for item in evidence.values())
    report = dict(status='PASS', release='v6', checked_on='2026-10-19', pages=pages,
        abstract_whitespace_words=len(abstract.split()), theorem_numbers=theorem_numbers,
        frozen_files_checked=len(freeze['hashes']), benchmark_expansion=False,
        experiment_block_verbatim_from_v5=True, unchanged_experiment_inputs=len(unchanged_inputs),
        previous_v5_archives_unchanged=True, clean_validation_commands=11,
        pdf_text_identical_between_working_research_and_arxiv=True,
        journal_flat_source_validated=True, internal_review_bound_to_current_hashes=True,
        primary_source_records=11, archive_hashes=archive_hashes,
        manuscript_pdf_sha256=sha(pdfs[0]), evidence=evidence,
        scope='Focused proof-and-priority audit and LaTeX publication preparation completed, within the explicit author-placeholder scope. Internal mathematical review, not independent peer review or worldwide novelty certification.',
        ready_for_author_finalization=True, ready_for_upload_without_author_edits=False,
        remaining_human_actions=['True author identity/contact details', 'Human scientific review and responsibility',
                                'Accurate funding, competing-interest and contribution statements',
                                'Cover-letter publication/concurrent-submission declarations',
                                'Public artifact/license and submission account choices'],
        public_submission_performed=False)
    path = ROOT / 'releases/completion_v6.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status='PASS', pages=pages, frozen_files=len(freeze['hashes']),
                         report=str(path), ready_for_upload_without_author_edits=False)))


if __name__ == '__main__':
    main()
