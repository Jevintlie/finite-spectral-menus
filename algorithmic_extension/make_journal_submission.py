"""Build and check a flat journal source package; no upload or benchmark run."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent


def run(command, folder):
    result = subprocess.run(command, cwd=folder, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout[-5000:] + result.stderr[-2000:])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    if not args.tag.replace('_', '').isalnum():
        raise ValueError('Invalid tag')
    out = ROOT / 'releases'
    out.mkdir(exist_ok=True)
    target = out / f'paper2_journal_source_{args.tag}.zip'
    if target.exists():
        raise FileExistsError('Preserve old archives; choose a new tag.')
    source = ROOT / 'manuscript'
    payload = {}
    mapping = {}
    for path in sorted(source.rglob('*')):
        if not path.is_file() or 'preview' in path.parts:
            continue
        if path.suffix in ('.tex', '.bib', '.bbl') or (
                path.suffix == '.pdf' and path.parent.name == 'figures'):
            name = 'Fig1.pdf' if path.name == 'structural.pdf' else path.name
            if name in payload:
                raise ValueError(f'Flattened filename collision: {name}')
            mapping[path.relative_to(source).as_posix()] = name
            payload[name] = path.read_bytes()
    for name, data in list(payload.items()):
        if name.endswith('.tex'):
            text = data.decode('utf8')
            for old, new in mapping.items():
                if old != new:
                    text = text.replace('{' + old + '}', '{' + new + '}')
            payload[name] = text.encode('utf8')
    with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            archive.writestr(name, data)
    # Build from the actual archive, not the pre-packaging files.
    with tempfile.TemporaryDirectory(prefix='paper2_journal_') as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(target) as archive:
            assert all('/' not in n and '\\' not in n for n in archive.namelist())
            archive.extractall(tmp)
        for command in [
                ['pdflatex', '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'],
                ['bibtex', 'main'],
                ['pdflatex', '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'],
                ['pdflatex', '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', 'main.tex']]:
            run(command, tmp)
        log = (tmp / 'main.log').read_text(errors='replace')
        assert not any(s in log for s in ('Overfull', 'Underfull', 'undefined', 'Fatal error'))
        for pdf, txt in [(source / 'main.pdf', tmp / 'working.txt'),
                         (tmp / 'main.pdf', tmp / 'flat.txt')]:
            run(['pdftotext', '-layout', str(pdf), str(txt)], tmp)
        assert (tmp / 'working.txt').read_bytes() == (tmp / 'flat.txt').read_bytes()
        report = {
            'status': 'PASS', 'archive': target.name,
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'files': {n: hashlib.sha256(d).hexdigest() for n, d in sorted(payload.items())},
            'path_mapping': mapping, 'no_subfolders': True,
            'clean_build': True, 'pdf_text_matches_working_manuscript': True,
            'pages': int(re.search(r'Output written on main.pdf \((\d+) pages?', log)[1]),
            'author_fields': 'See author_info.tex; submission readiness is tracked separately',
        }
    (out / f'journal_validation_{args.tag}.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('files', 'path_mapping')}))


if __name__ == '__main__':
    main()
