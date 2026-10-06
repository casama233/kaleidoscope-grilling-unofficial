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


def assert_public_bytes_with_g71_bottles(testcase, path):
    """Allow only exact reviewed bottle deltas; conserve every other byte."""
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    relative = path.relative_to(ROOT).as_posix()
    if relative != 'projects/grilling/gameplay_core/behavior_pack/scripts/main.js':
        return assert_public_bytes(testcase, path)
    version = json.loads((ROOT / 'baseline.json').read_text())['version']
    if tuple(version) < (2, 8, 71):
        return assert_public_bytes(testcase, path)
    fixtures=[(71,'g71-bottle-main-delta.json')]
    if tuple(version) >= (2, 8, 72):
        fixtures.append((72,'g72-bottle-main-delta.json'))
    expected = public_bytes(path)
    for patch_version, filename in fixtures:
        delta = json.loads((ROOT / 'tools/fixtures' / filename).read_text())
        testcase.assertEqual(delta['path'], relative)
        testcase.assertEqual(delta['release'], [2, 8, patch_version])
        testcase.assertEqual(hashlib.sha256(expected).hexdigest(), delta['before_sha256'])
        lines = expected.decode('utf-8').splitlines(keepends=True)
        cursor, result = 0, []
        for edit in delta['edits']:
            start, end = edit['start'], edit['end']
            testcase.assertTrue(cursor <= start <= end <= len(lines))
            testcase.assertEqual(''.join(lines[start:end]), edit['before'])
            result.extend(lines[cursor:start]); result.append(edit['after']); cursor = end
        result.extend(lines[cursor:])
        expected = ''.join(result).encode('utf-8')
        testcase.assertEqual(hashlib.sha256(expected).hexdigest(), delta['after_sha256'])
    testcase.assertEqual(path.read_bytes(), expected, 'Source differs outside exact reviewed bottle deltas')
