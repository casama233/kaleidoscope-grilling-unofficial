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
    expected = public_bytes(path)
    version = tuple(json.loads((ROOT / 'baseline.json').read_text())['version'])
    if version >= (2, 8, 73) and path.relative_to(ROOT).as_posix() == 'projects/grilling/gameplay_core/behavior_pack/scripts/main.js':
        filename = 'g74-main-reviewed-delta.json' if version >= (2, 8, 74) else 'g73-main-reviewed-delta.json'
        delta = json.loads((ROOT / 'tools/fixtures' / filename).read_text())
        assert delta['schema'] == 1
        assert hashlib.sha256(expected).hexdigest() == delta['before_sha256'], 'Reviewed main delta has wrong public preimage'
        text = expected.decode('utf-8')
        operations = delta['operations']
        assert operations and all(0 <= op['start'] <= op['end'] <= len(text) for op in operations)
        assert all(a['end'] <= b['start'] for a, b in zip(operations, operations[1:])), 'Reviewed edits overlap'
        for op in reversed(operations):
            assert text[op['start']:op['end']] == op['before'], 'Reviewed edit preimage changed'
            text = text[:op['start']] + op['after'] + text[op['end']:]
        expected = text.encode('utf-8')
        assert hashlib.sha256(expected).hexdigest() == delta['after_sha256'], 'Reviewed main delta is incomplete'
    testcase.assertEqual(path.read_bytes(), expected, 'Repaired public-source bytes changed outside reviewed scope: ' + str(path.relative_to(ROOT)))

# Historical G71 tests use this name. The current combined admission still
# conserves every byte outside the exact registered G74/G73 edits.
assert_public_bytes_with_g71_bottles = assert_public_bytes
