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


MAIN_PATH = 'projects/grilling/gameplay_core/behavior_pack/scripts/main.js'


def _main_delta(filename):
    delta = json.loads((ROOT / 'tools/fixtures' / filename).read_text())
    assert delta['schema'] == 1
    return delta


def _apply_main_operations(expected, delta):
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
    return expected


def _local_bottle_main_bytes(expected, version):
    # These are local candidate identities, distinct from published G72/G73.
    for patch_version, filename in (
        (71, 'g71-bottle-main-delta.json'),
        (72, 'g72-bottle-main-delta.json'),
        (73, 'g73-plate-alias-main-delta.json'),
    ):
        if version < (2, 8, patch_version):
            break
        delta = _main_delta(filename)
        assert delta['path'] == MAIN_PATH
        assert delta['release'] == [2, 8, patch_version]
        assert hashlib.sha256(expected).hexdigest() == delta['before_sha256'], 'Reviewed bottle delta has wrong preimage'
        lines = expected.decode('utf-8').splitlines(keepends=True)
        cursor, result = 0, []
        assert delta['edits'], 'Reviewed bottle delta has no edits'
        for edit in delta['edits']:
            start, end = edit['start'], edit['end']
            assert cursor <= start <= end <= len(lines), 'Reviewed bottle edits overlap or exceed source'
            assert ''.join(lines[start:end]) == edit['before'], 'Reviewed bottle edit preimage changed'
            result.extend(lines[cursor:start]); result.append(edit['after']); cursor = end
        result.extend(lines[cursor:])
        expected = ''.join(result).encode('utf-8')
        assert hashlib.sha256(expected).hexdigest() == delta['after_sha256'], 'Reviewed bottle delta is incomplete'
    return expected


def expected_main_bytes(version, *, local_bottles=False, proposal=None):
    """Published G73/G74 and local G71-G73 remain distinct; G75 adds one plate fix."""
    version = tuple(version)
    original = public_bytes(MAIN_PATH)
    if version in [(2,8,75),(2,8,76)]:
        assert proposal in ['plate_alias','seasoning'], 'Conflicting unpublished proposals require an explicit source lineage'
        if proposal=='seasoning':
            return _apply_main_operations(original, _main_delta('g74-main-reviewed-delta.json'))
    if version == (2,8,80):
        assert proposal in ["checkpoint_stop","jar_projection"], "Conflicting G80 proposals require explicit source lineage"
    if version >= (2, 8, 74):
        expected = _apply_main_operations(original, _main_delta('g74-main-reviewed-delta.json'))
        if version >= (2, 8, 77) or proposal=='plate_alias':
            delta = _main_delta('g75-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 75]
            local = _main_delta('g73-plate-alias-main-delta.json')['edits']
            assert len(delta['operations']) == len(local) == 1
            assert [(op['before'], op['after']) for op in delta['operations']] == [(op['before'], op['after']) for op in local]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 81) or (version==(2,8,80) and proposal=="checkpoint_stop"):
            delta = _main_delta('g80-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 80]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 83):
            delta = _main_delta('g83-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 83]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 84):
            delta = _main_delta('g84-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 84]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 85):
            delta = _main_delta('g85-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 85]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 86):
            delta = _main_delta('g86-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 86]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 94):
            delta = _main_delta('g94-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 94]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 100):
            delta = _main_delta('g100-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 100]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 105):
            delta = _main_delta('g105-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 105]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 110):
            delta = _main_delta('g110-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 110]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 111):
            delta = _main_delta('g111-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 111]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 113):
            delta = _main_delta('g113-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 113]
            expected = _apply_main_operations(expected, delta)
        if version >= (2, 8, 114):
            delta = _main_delta('g114-main-reviewed-delta.json')
            assert delta['path'] == MAIN_PATH and delta['release'] == [2, 8, 114]
            expected = _apply_main_operations(expected, delta)
        return expected
    if local_bottles:
        return _local_bottle_main_bytes(original, version)
    if version >= (2, 8, 73):
        return _apply_main_operations(original, _main_delta('g73-main-reviewed-delta.json'))
    return original


def assert_public_bytes(testcase, path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    expected = public_bytes(path)
    if path.relative_to(ROOT).as_posix() == MAIN_PATH:
        version = json.loads((ROOT / 'baseline.json').read_text())['version']
        expected = expected_main_bytes(version)
    testcase.assertEqual(path.read_bytes(), expected, 'Repaired public-source bytes changed outside reviewed scope: ' + str(path.relative_to(ROOT)))


def assert_public_bytes_with_g71_bottles(testcase, path):
    """Conserve local bottle/plate repairs plus the exact published G73/G74 in G75."""
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    relative = path.relative_to(ROOT).as_posix()
    if relative != MAIN_PATH:
        return assert_public_bytes(testcase, path)
    version = json.loads((ROOT / 'baseline.json').read_text())['version']
    expected = expected_main_bytes(version, local_bottles=True)
    testcase.assertEqual(path.read_bytes(), expected, 'Source differs outside exact reviewed bottle, plate-alias and published G73 deltas')
