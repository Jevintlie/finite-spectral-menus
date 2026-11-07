"""Verify a self-contained release handoff; standard library only, no execution."""
import argparse
import hashlib
import io
import json
from pathlib import PurePosixPath
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_names(archive):
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValueError('Duplicate ZIP entries')
    for name in names:
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
            raise ValueError('Unsafe ZIP member: ' + name)
    return set(names)


def verify(path):
    with zipfile.ZipFile(path) as outer:
        names = safe_names(outer)
        manifest = json.loads(outer.read('BUNDLE_MANIFEST.json'))
        if names != set(manifest['files']) | {'BUNDLE_MANIFEST.json'}:
            raise ValueError('Bundle manifest does not cover exactly all files')
        for name, expected in manifest['files'].items():
            if digest(outer.read(name)) != expected:
                raise ValueError('Bundle hash mismatch: ' + name)
        tag = manifest['release']
        report = json.loads(outer.read(f'validation/release_validation_{tag}.json'))
        journal = json.loads(outer.read(f'validation/journal_validation_{tag}.json'))
        completion = json.loads(outer.read(f'validation/completion_{tag}.json'))
        if any(r['status'] != 'PASS' for r in (report, journal, completion)):
            raise ValueError('Release gate did not pass')
        for item in list(report['archives'].values()) + [journal]:
            name = item.get('name', item.get('archive'))
            if digest(outer.read('archives/' + name)) != item['sha256']:
                raise ValueError('Report/archive mismatch: ' + name)
        for name, expected in completion['archive_hashes'].items():
            if digest(outer.read('archives/' + name)) != expected:
                raise ValueError('Completion/archive mismatch: ' + name)
        for command in report['commands']:
            if command['returncode'] or 'validation/logs/' + command['log'] not in names:
                raise ValueError('Missing or failed recorded validation command')
        research = outer.read('archives/' + report['archives']['research']['name'])
        with zipfile.ZipFile(io.BytesIO(research)) as inner:
            inner_names = safe_names(inner)
            inner_manifest = json.loads(inner.read('ARTIFACT_MANIFEST.json'))
            if inner_names != set(inner_manifest['files']) | {'ARTIFACT_MANIFEST.json'}:
                raise ValueError('Research manifest coverage mismatch')
            for name, expected in inner_manifest['files'].items():
                if digest(inner.read(name)) != expected:
                    raise ValueError('Research member mismatch: ' + name)
            if outer.read('main.pdf') != inner.read('algorithmic_extension/manuscript/main.pdf'):
                raise ValueError('Convenience PDF differs from research PDF')
        for kind in ('arxiv',):
            with zipfile.ZipFile(io.BytesIO(outer.read('archives/' + report['archives'][kind]['name']))) as src:
                safe_names(src)
        with zipfile.ZipFile(io.BytesIO(outer.read('archives/' + journal['archive']))) as src:
            safe_names(src)
            if set(src.namelist()) != set(journal['files']):
                raise ValueError('Journal manifest coverage mismatch')
            for name, expected in journal['files'].items():
                if digest(src.read(name)) != expected:
                    raise ValueError('Journal member mismatch: ' + name)
    return {'status': 'PASS', 'release': tag, 'bundle_files': len(names),
            'research_files_checked': len(inner_manifest['files']),
            'recorded_validation_commands': len(report['commands']),
            'scope': 'Hashes and recorded gates, not new benchmark runs or independent proof review'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle')
    print(json.dumps(verify(parser.parse_args().bundle), indent=2))
