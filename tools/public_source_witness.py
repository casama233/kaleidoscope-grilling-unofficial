"""Immutable public repaired-source conservation, not private before/after proof."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SOURCE_BASE = 'a2656e08d97a6b4c31ef3667b2c957e18c80c8fd'
PUBLIC_SOURCE_TREE = '7d2c9c91d9d3be7713d893c76d64aa458b2cb1db'

@lru_cache(maxsize=1)
def witness():
    meta = json.loads((ROOT / 'tools/fixtures/g69-public-source-witness.json').read_text())
    assert meta['schema'] == 1 and meta['commit'] == PUBLIC_SOURCE_BASE
    assert meta['tree'] == PUBLIC_SOURCE_TREE
    actual = subprocess.check_output(['git', 'rev-parse', PUBLIC_SOURCE_BASE + '^{tree}'], cwd=ROOT, text=True).strip()
    assert actual == PUBLIC_SOURCE_TREE, 'Public repaired-source tree mismatch'
    return meta


def public_bytes(relative_path):
    path = Path(relative_path)
    if path.is_absolute():
        path = path.relative_to(ROOT)
    assert '..' not in path.parts, 'Source path must remain inside repository'
    key = path.as_posix()
    meta = witness()
    assert key in meta['files'], 'Public source witness path absent: ' + key
    data = subprocess.check_output(['git', 'show', PUBLIC_SOURCE_BASE + ':' + key], cwd=ROOT)
    assert hashlib.sha256(data).hexdigest() == meta['files'][key], 'Public source bytes mismatch: ' + key
    return data


def public_json(relative_path):
    return json.loads(public_bytes(relative_path))


def assert_public_bytes(testcase, path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    testcase.assertEqual(path.read_bytes(), public_bytes(path), 'Repaired public-source bytes changed: ' + str(path.relative_to(ROOT)))
