"""Check every distributed file against the archive-root manifest."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent.parent
manifest=json.loads((ROOT/'ARTIFACT_MANIFEST.json').read_text())
for name,expected in manifest['files'].items():
    path=(ROOT/name).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError('Manifest path escapes distribution.')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        raise ValueError(f'Hash mismatch: {name}')
print(json.dumps({'status':'PASS_DISTRIBUTION_HASHES','files':len(manifest['files'])}))
