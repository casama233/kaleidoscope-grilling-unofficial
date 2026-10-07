"""Exact count-only midpoint repair over independently conserved public G95.

All predecessor snapshots and reviewed fixtures are checked before admission.
The final independently reviewed patch and generator/test identities are required.
"""
import hashlib
import json
import g95_source_conservation as previous

ROOT = previous.ROOT
PROJECT = previous.PROJECT
HISTORICAL = previous.HISTORICAL
FROZEN_SOURCE_BASE = 'ca6a2d0777066b4bcdce278d1d0f501a39fbc2c5'
FROZEN_TREE = '25e5d0aee047092302f9973c5420bd789a090c3d'
MANIFESTS = previous.MANIFESTS
ATTACHABLE_PATH = previous.previous.ATTACHABLE_PATH
COUNT_BEFORE = 'v.kg_plate_count = math.floor((v.kg_plate_word_7 - 10)/123);'
COUNT_AFTER = 'v.kg_plate_count = math.floor((v.kg_plate_word_7 - 10 + 0.5)/123);'
REVIEWED_PATCH_SHA256 = '158d7046d64e11e536cddb49181507f5e03328f100b3710a002f1ab5345ef3ec'
REVIEWED_AFTER = {'projects/grilling/gameplay_core/resource_pack/attachables/skewer_plate.attachable.json': '0f9203656d395bd6c969b63b1429c485e45fdddb0ea8b47f683593fa1d74f608'}
REVIEWED_SOURCE_AFTER = {'tools/build_plate_held.py': 'dbcf25054a28bb0e3d868257058595f3349ad173b5071a34fe3b17cf299d7f1a', 'tools/test_plate_client_probe.py': '77ac579a8b8580074fb550b1428cfd334b3c75231e20a05b002a8f3aed6e74ab'}
ADDED_PATHS = set()
DELTA_PATHS = MANIFESTS | {ATTACHABLE_PATH}
FROZEN_FIXTURES = ('tools/fixtures/g90-source-lineages.json',
    'tools/fixtures/g90-runtime-reviewed-delta.json', 'tools/fixtures/g91-cloud-reviewed-delta.json') + tuple(
    f'tools/fixtures/g{release}-runtime-reviewed-delta.json' for release in (92, 93, 94, 95))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(path):
    return HISTORICAL.source(FROZEN_SOURCE_BASE, path)


def files():
    return HISTORICAL.files(FROZEN_SOURCE_BASE)


def verify_frozen_foundation():
    """Retain every predecessor assertion before inspecting any G96 metadata."""
    assert HISTORICAL.git('rev-parse', FROZEN_SOURCE_BASE + '^{tree}').decode().strip() == FROZEN_TREE, 'Diagnostic G95 tree drift'
    result = previous.verify_snapshot(FROZEN_SOURCE_BASE)
    for path in FROZEN_FIXTURES:
        assert (ROOT / path).read_bytes() == source(path), 'Frozen reviewed fixture drift: ' + path
    return result


def metadata():
    assert REVIEWED_PATCH_SHA256 and COUNT_AFTER and REVIEWED_AFTER and REVIEWED_SOURCE_AFTER, 'Final reviewed G96 patch is not yet admitted'
    data = json.loads((ROOT / 'tools/fixtures/g96-runtime-reviewed-delta.json').read_text())
    assert data['schema'] == 1 and data['release'] == [2, 8, 96]
    assert data['base_commit'] == FROZEN_SOURCE_BASE and data['base_tree'] == FROZEN_TREE
    assert HISTORICAL.git('rev-parse', FROZEN_SOURCE_BASE + '^{tree}').decode().strip() == FROZEN_TREE
    assert set(data['files']) == DELTA_PATHS, 'Unreviewed G96 runtime path'
    assert set(REVIEWED_AFTER) == {ATTACHABLE_PATH}, 'Unreviewed count midpoint runtime scope'
    assert set(REVIEWED_SOURCE_AFTER) == {'tools/build_plate_held.py', 'tools/test_plate_client_probe.py'}, 'Unreviewed count midpoint source scope'
    assert data['held_review'] == {'patch_sha256': REVIEWED_PATCH_SHA256,
                                   'after_sha256': REVIEWED_AFTER,
                                   'source_after_sha256': REVIEWED_SOURCE_AFTER}, 'Unreviewed count midpoint repair'
    assert data['files'][ATTACHABLE_PATH]['after_sha256'] == REVIEWED_AFTER[ATTACHABLE_PATH], 'Count midpoint repair differs from reviewed bytes'
    for path, identity in REVIEWED_SOURCE_AFTER.items():
        assert sha((ROOT / path).read_bytes()) == identity, 'Reviewed count midpoint source drift: ' + path
    return data


def assert_held_preservation(path, before, after):
    """Change one exact count statement, conserving every other byte."""
    assert path == ATTACHABLE_PATH, 'Unreviewed count midpoint path: ' + path
    old = COUNT_BEFORE.encode('utf-8'); new = COUNT_AFTER.encode('utf-8')
    assert before.count(old) == 1 and before.count(new) == 0, 'Frozen count statement changed'
    assert after == before.replace(old, new, 1), 'Attachable changed outside exact count midpoint statement'
    prior = json.loads(before)['minecraft:attachable']['description']['scripts']['pre_animation']
    current = json.loads(after)['minecraft:attachable']['description']['scripts']['pre_animation']
    assert prior.count(COUNT_BEFORE) == 1 and current.count(COUNT_AFTER) == 1
    assert [COUNT_AFTER if row == COUNT_BEFORE else row for row in prior] == current, 'Count decoder ordering changed'


def bump_manifest(value):
    if isinstance(value, dict):
        return {key: ([2, 8, 96] if key == 'version' and item == [2, 8, 95]
                      else bump_manifest(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [bump_manifest(item) for item in value]
    return value


def apply_delta(path):
    row = metadata()['files'][path]
    assert path in files(), 'Unreviewed runtime addition/deletion'
    before = source(path)
    assert row['before_sha256'] == sha(before), 'Reviewed G96 preimage hash changed'
    text = before.decode('utf-8')
    operations = row['operations']
    assert operations and all(0 <= op['start'] <= op['end'] <= len(text) for op in operations)
    assert all(a['end'] <= b['start'] for a, b in zip(operations, operations[1:])), 'Overlapping G96 reviewed edits'
    for op in reversed(operations):
        assert text[op['start']:op['end']] == op['before'], 'Reviewed G96 edit preimage changed'
        text = text[:op['start']] + op['after'] + text[op['end']:]
    after = text.encode('utf-8')
    assert sha(after) == row['after_sha256'], 'Incomplete reviewed G96 delta'
    if path in MANIFESTS:
        assert json.loads(after) == bump_manifest(json.loads(before)), 'Manifest changed outside paired G96 identity'
    else:
        assert sha(after) == REVIEWED_AFTER[path], 'Count repair differs from exact independently reviewed patch'
        assert_held_preservation(path, before, after)
    return after


def expected_runtime_bytes(path):
    assert path in files(), 'Runtime path outside frozen diagnostic G95'
    metadata()
    return apply_delta(path) if path in DELTA_PATHS else source(path)


def verify_current():
    result = verify_frozen_foundation()
    metadata()
    assert json.loads((ROOT / 'baseline.json').read_text())['version'] == [2, 8, 96], 'Current identity is not G96'
    current = {path.relative_to(ROOT).as_posix(): path
               for side in ('behavior_pack', 'resource_pack')
               for path in (ROOT / PROJECT / side).rglob('*') if path.is_file()}
    assert set(current) == set(files()), 'Missing/extra G96 runtime file'
    for path, local in current.items():
        if path in DELTA_PATHS:
            assert local.read_bytes() == expected_runtime_bytes(path), 'Runtime source drift: ' + path
        else:
            assert HISTORICAL.blob(local.read_bytes()) == files()[path], 'Runtime source drift: ' + path
    history = json.loads((ROOT / 'release-history.json').read_text())
    for version, row in json.loads(source('release-history.json')).items():
        assert history[version] == row, 'Diagnostic G95 history drift: ' + version
    return {**result, 'runtime_files': len(current), 'reviewed_release': [2, 8, 96],
            'reviewed_paths': len(DELTA_PATHS)}
