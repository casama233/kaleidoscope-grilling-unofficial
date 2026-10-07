"""Fail-closed QA-render admission over the immutable diagnostic G94 lineage.

The canonical-main G94 label belongs to a different source lineage. This module
uses the complete diagnostic commit and tree identities, never a version alias.
Final reviewed patch identities must be supplied before current G95 admission.
"""
import hashlib
import json
import g94_source_conservation as previous

ROOT = previous.ROOT
PROJECT = previous.PROJECT
HISTORICAL = previous.HISTORICAL
FROZEN_SOURCE_BASE = '4014645d132ec676791b2aa39752db37d84abb2e'
FROZEN_TREE = 'd641b145893e802265751229df9f415a3a6e2d27'
REVIEWED_SOURCE_BASE = 'ca6a2d0777066b4bcdce278d1d0f501a39fbc2c5'
REVIEWED_SOURCE_TREE = '25e5d0aee047092302f9973c5420bd789a090c3d'
MANIFESTS = previous.MANIFESTS
QA_GEOMETRY_PATH = previous.QA_GEOMETRY_PATH
REVIEWED_PATCH_SHA256 = '0804e8cb0a6619246a17ba0c6f93b7b795ba2af4504e53c6c8ff1a927ed1f94b'
REVIEWED_AFTER = {
    QA_GEOMETRY_PATH: '5d4a5a3261d3d665b86327a05512fe82634ab01a8f2ed1e62bfa432cd23e5bfc',
}
REVIEWED_SOURCE_AFTER = {
    'tools/build_plate_held.py': '60622ae69751633968ca823f9c2f523c4a3d1a9903a48d0c4c13071207bb2d6f',
    'tools/test_plate_client_probe.py': '33124346d563f2a66973fcf8be1059aa7e73aa50bcdbdbd1afa9a3cde654454f',
}
ADDED_PATHS = set()
DELTA_PATHS = MANIFESTS | set(REVIEWED_AFTER)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(path):
    return HISTORICAL.source(FROZEN_SOURCE_BASE, path)


def files():
    return HISTORICAL.files(FROZEN_SOURCE_BASE)


def verify_frozen_foundation():
    """Retain every predecessor assertion before inspecting any G95 metadata."""
    assert HISTORICAL.git('rev-parse', FROZEN_SOURCE_BASE + '^{tree}').decode().strip() == FROZEN_TREE, 'Diagnostic G94 tree drift'
    result = previous.verify_snapshot(FROZEN_SOURCE_BASE)
    for release in (92, 93, 94):
        path = f'tools/fixtures/g{release}-runtime-reviewed-delta.json'
        assert (ROOT / path).read_bytes() == source(path), 'Frozen reviewed fixture drift: ' + path
    return result


def metadata(*, frozen=False):
    assert REVIEWED_PATCH_SHA256 and REVIEWED_AFTER, 'Final reviewed G95 patch is not yet admitted'
    data = json.loads((ROOT / 'tools/fixtures/g95-runtime-reviewed-delta.json').read_text())
    assert data['schema'] == 1 and data['release'] == [2, 8, 95]
    assert data['base_commit'] == FROZEN_SOURCE_BASE and data['base_tree'] == FROZEN_TREE
    assert HISTORICAL.git('rev-parse', FROZEN_SOURCE_BASE + '^{tree}').decode().strip() == FROZEN_TREE
    assert set(data['files']) == DELTA_PATHS, 'Unreviewed G95 runtime path'
    assert data['held_review'] == {'patch_sha256': REVIEWED_PATCH_SHA256,
                                   'after_sha256': REVIEWED_AFTER,
                                   'source_after_sha256': REVIEWED_SOURCE_AFTER}, 'Unreviewed QA-render diagnostic'
    for path, identity in REVIEWED_AFTER.items():
        assert data['files'][path]['after_sha256'] == identity, 'QA-render diagnostic differs from reviewed bytes: ' + path
    frozen_sources = frozen or tuple(json.loads((ROOT / 'baseline.json').read_text())['version']) >= (2, 8, 96)
    if frozen_sources:
        assert HISTORICAL.git('rev-parse', REVIEWED_SOURCE_BASE + '^{tree}').decode().strip() == REVIEWED_SOURCE_TREE, 'Reviewed diagnostic G95 source tree drift'
    for path, identity in REVIEWED_SOURCE_AFTER.items():
        data_source = HISTORICAL.source(REVIEWED_SOURCE_BASE, path) if frozen_sources else (ROOT / path).read_bytes()
        assert sha(data_source) == identity, 'Reviewed QA-render source drift: ' + path
    return data


def assert_held_preservation(path, before, after):
    """Only existing binary QA cube placement and atlas sampling may change."""
    assert path == QA_GEOMETRY_PATH, 'Unreviewed QA-render path: ' + path
    old, new = json.loads(before), json.loads(after)
    assert len(new['minecraft:geometry']) == len(old['minecraft:geometry']) == 1
    prior, current = old['minecraft:geometry'][0], new['minecraft:geometry'][0]
    assert current['description'] == prior['description'], 'Binary QA geometry identity/bounds changed'
    assert [bone['name'] for bone in current['bones']] == [bone['name'] for bone in prior['bones']], 'Binary QA bone scope/order changed'
    assert current['bones'][:2] == prior['bones'][:2], 'Binary QA original hand rig changed'
    for a, b in zip(prior['bones'][2:], current['bones'][2:]):
        assert {key: value for key, value in a.items() if key != 'cubes'} == {
            key: value for key, value in b.items() if key != 'cubes'}, 'Binary QA bone contract changed'
        a['cubes'] = b['cubes']
    assert new == old, 'Binary QA changed outside existing QA cube layers'
    panel = current['bones'][2]['cubes'][0]
    faces = ('north', 'east', 'south', 'west', 'up', 'down')
    assert panel == {'origin': [-7.2, 24.8, -10.2], 'size': [13.15, 9.9, .6],
        'uv': {face: {'uv': [123, 40], 'uv_size': [1, 1]} for face in faces}}, 'Binary QA backing panel changed'
    for bone in current['bones'][2:]:
        cubes = bone['cubes'][1:] if bone['name'] == 'qa_binary_frame' else bone['cubes']
        front = [cube for cube in cubes if cube['origin'][2] == -11.22]
        back = [cube for cube in cubes if cube['origin'][2] == -8.6]
        assert front and len(front) == len(back) and len(cubes) == len(front) + len(back), 'Binary QA text-plane scope changed'
        for a, b in zip(front, back):
            assert set(a) == set(b) == {'origin', 'size', 'uv'} and a['size'][2] == b['size'][2] == .02, 'Binary QA text depth/shape changed'
            assert all(value > 0 for value in a['size']) and b['size'] == a['size']
            assert set(a['uv']) == {'north'} and set(b['uv']) == {'south'}, 'Binary QA text outward faces changed'
            assert a['uv']['north'] in ({'uv': [8, 40], 'uv_size': [1, 1]},
                                       {'uv': [123, 40], 'uv_size': [1, 1]}), 'Binary QA interior atlas sampling changed'
            assert b['uv'] == {'south': a['uv']['north']}, 'Binary QA rear sampling changed'
            assert b['origin'] == [round(-1.25 - a['origin'][0] - a['size'][0], 5), a['origin'][1], -8.6], 'Binary QA mirrored rear layout changed'


def bump_manifest(value):
    if isinstance(value, dict):
        return {key: ([2, 8, 95] if key == 'version' and item == [2, 8, 94]
                      else bump_manifest(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [bump_manifest(item) for item in value]
    return value


def apply_delta(path, *, frozen=False):
    row = metadata(frozen=frozen)['files'][path]
    assert (path in ADDED_PATHS) == (path not in files()), 'Unreviewed runtime addition/deletion'
    before = b'' if path in ADDED_PATHS else source(path)
    assert row['before_sha256'] == sha(before), 'Reviewed G95 preimage hash changed'
    text = before.decode('utf-8')
    operations = row['operations']
    assert operations and all(0 <= op['start'] <= op['end'] <= len(text) for op in operations)
    assert all(a['end'] <= b['start'] for a, b in zip(operations, operations[1:])), 'Overlapping G95 reviewed edits'
    for op in reversed(operations):
        assert text[op['start']:op['end']] == op['before'], 'Reviewed G95 edit preimage changed'
        text = text[:op['start']] + op['after'] + text[op['end']:]
    after = text.encode('utf-8')
    assert sha(after) == row['after_sha256'], 'Incomplete reviewed G95 delta'
    if path in MANIFESTS:
        assert json.loads(after) == bump_manifest(json.loads(before)), 'Manifest changed outside paired G95 identity'
    else:
        assert sha(after) == REVIEWED_AFTER[path], 'QA-render diagnostic differs from exact independently reviewed patch'
        assert_held_preservation(path, before, after)
    return after


def expected_frozen_runtime_bytes(path):
    assert path in set(files()) | ADDED_PATHS, 'Runtime path outside frozen diagnostic G94 and exact G95 additions'
    metadata(frozen=True)
    return apply_delta(path, frozen=True) if path in DELTA_PATHS else source(path)


def expected_runtime_bytes(path):
    if tuple(json.loads((ROOT / 'baseline.json').read_text())['version']) >= (2, 8, 96):
        from g96_source_conservation import expected_runtime_bytes as expected_next
        return expected_next(path)
    return expected_frozen_runtime_bytes(path)


def verify_snapshot(ref):
    """Validate diagnostic G95 without consulting later current expectations."""
    result = verify_frozen_foundation()
    metadata(frozen=True)
    frozen = HISTORICAL.files(ref)
    assert set(frozen) == set(files()) | ADDED_PATHS, 'Frozen G95 missing/extra runtime file'
    for path, identity in frozen.items():
        expected_identity = (HISTORICAL.blob(expected_frozen_runtime_bytes(path))
                             if path in DELTA_PATHS else files()[path])
        assert identity == expected_identity, 'Frozen G95 source drift: ' + path
    path = 'tools/fixtures/g95-runtime-reviewed-delta.json'
    assert (ROOT / path).read_bytes() == HISTORICAL.source(ref, path), 'Frozen reviewed fixture drift: ' + path
    history = json.loads(HISTORICAL.source(ref, 'release-history.json'))
    for version, row in json.loads(source('release-history.json')).items():
        assert history[version] == row, 'Frozen diagnostic G94 history drift: ' + version
    return {**result, 'runtime_files': len(frozen), 'reviewed_release': [2, 8, 95],
            'reviewed_paths': len(DELTA_PATHS)}


def verify_current():
    if tuple(json.loads((ROOT / 'baseline.json').read_text())['version']) >= (2, 8, 96):
        from g96_source_conservation import verify_current as verify_next
        return verify_next()
    result = verify_frozen_foundation()
    metadata()
    assert json.loads((ROOT / 'baseline.json').read_text())['version'] == [2, 8, 95], 'Current identity is not G95'
    current = {path.relative_to(ROOT).as_posix(): path
               for side in ('behavior_pack', 'resource_pack')
               for path in (ROOT / PROJECT / side).rglob('*') if path.is_file()}
    assert set(current) == set(files()) | ADDED_PATHS, 'Missing/extra G95 runtime file'
    for path, local in current.items():
        if path in DELTA_PATHS:
            assert local.read_bytes() == expected_runtime_bytes(path), 'Runtime source drift: ' + path
        else:
            assert HISTORICAL.blob(local.read_bytes()) == files()[path], 'Runtime source drift: ' + path
    history = json.loads((ROOT / 'release-history.json').read_text())
    for version, row in json.loads(source('release-history.json')).items():
        assert history[version] == row, 'Diagnostic G94 history drift: ' + version
    return {**result, 'runtime_files': len(current), 'reviewed_release': [2, 8, 95],
            'reviewed_paths': len(DELTA_PATHS)}
