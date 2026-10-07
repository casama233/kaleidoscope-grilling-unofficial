"""Exact default-off held client probe on the fully conserved public G91."""
from functools import lru_cache
import hashlib
import json
import g91_source_conservation as previous

ROOT = previous.ROOT
PROJECT = previous.PROJECT
FROZEN_SOURCE_BASE = 'b29737b250544fea2e3ab712bad30c2c04498809'
FROZEN_TREE = '254f367835779c07963efc8ad139c13a41f048bb'
MANIFESTS = previous.MANIFESTS
WRITER_PATH = PROJECT + 'behavior_pack/scripts/bottle_held_visual_runtime.js'
ATTACHABLE_PATH = PROJECT + 'resource_pack/attachables/skewer_plate.attachable.json'
CONTROLLERS_PATH = PROJECT + 'resource_pack/render_controllers/plate_held.render_controllers.json'
QA_GEOMETRY_PATH = PROJECT + 'resource_pack/models/entity/plate_held_qa.geo.json'
QA_CONTROLLERS = ('controller.render.kg_plate_held.qa_probe',
                  'controller.render.kg_plate_held.qa_forced_food')
REVIEWED_PATCH_SHA256 = '47725fb4d7fc39233c6fb1919f23efcca4be2b522e3e10f050f0bb76c2d3ca2e'
REVIEWED_AFTER = {
    WRITER_PATH: 'd956a5bd54071560ab8138e3685dbae7750b8b8f6d3d3887ae2e8785eb2173be',
    ATTACHABLE_PATH: 'ff52e39282ec837cd9321dd95cdb020d780270dcb89b388be7f4c9ca515aa453',
    CONTROLLERS_PATH: '71aea09c3b02bab08fca5487260cb38a6ff5bee0de64fb265179a5332d050181',
    QA_GEOMETRY_PATH: 'd30da28f8eb06bbb55ca72303dd63974060a0be9b2104712f194b9808e720f09',
}
ADDED_PATHS = {QA_GEOMETRY_PATH}
DELTA_PATHS = MANIFESTS | set(REVIEWED_AFTER)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(path):
    return previous.previous.source(FROZEN_SOURCE_BASE, path)


def files():
    return previous.previous.files(FROZEN_SOURCE_BASE)


def metadata():
    data = json.loads((ROOT / 'tools/fixtures/g92-runtime-reviewed-delta.json').read_text())
    assert data['schema'] == 1 and data['release'] == [2, 8, 92]
    assert data['base_commit'] == FROZEN_SOURCE_BASE and data['base_tree'] == FROZEN_TREE
    assert previous.previous.git('rev-parse', FROZEN_SOURCE_BASE + '^{tree}').decode().strip() == FROZEN_TREE
    assert set(data['files']) == DELTA_PATHS, 'Unreviewed G92 runtime path'
    assert data['held_review'] == {'patch_sha256': REVIEWED_PATCH_SHA256,
                                   'after_sha256': REVIEWED_AFTER}, 'Unreviewed held client probe'
    for path, identity in REVIEWED_AFTER.items():
        assert data['files'][path]['after_sha256'] == identity, 'Held probe differs from reviewed bytes: ' + path
    return data


def assert_held_preservation(path, before, after):
    """The reviewed probe preserves every production decoder and controller."""
    if path == ATTACHABLE_PATH:
        old = json.loads(before)
        new = json.loads(after)
        desc = new['minecraft:attachable']['description']
        prior = old['minecraft:attachable']['description']
        assert desc['geometry'].pop('qa_probe') == 'geometry.kg_plate_held.qa_probe'
        assert desc['render_controllers'] == prior['render_controllers'] + list(QA_CONTROLLERS)
        desc['render_controllers'] = desc['render_controllers'][:-2]
        for phase in ('initialize', 'pre_animation'):
            desc['scripts'][phase] = [row for row in desc['scripts'][phase]
                                       if not row.startswith('v.kg_plate_qa_')]
            assert desc['scripts'][phase] == prior['scripts'][phase], 'Production decoder ordering changed'
        assert new == old, 'Attachable changed outside exact QA additions'
    elif path == CONTROLLERS_PATH:
        old = json.loads(before)
        new = json.loads(after)
        prior = old['render_controllers']
        current = new['render_controllers']
        assert len(prior) == 31 and list(current) == list(prior) + list(QA_CONTROLLERS)
        for key in QA_CONTROLLERS:
            current.pop(key)
        assert new == old, 'Production controller changed'
    elif path == QA_GEOMETRY_PATH:
        geometry = json.loads(after)['minecraft:geometry']
        assert len(geometry) == 1 and geometry[0]['description']['identifier'] == 'geometry.kg_plate_held.qa_probe'


def bump_manifest(value):
    if isinstance(value, dict):
        return {key: ([2, 8, 92] if key == 'version' and item == [2, 8, 91]
                      else bump_manifest(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [bump_manifest(item) for item in value]
    return value


def apply_delta(path):
    row = metadata()['files'][path]
    assert (path in ADDED_PATHS) == (path not in files()), 'Unreviewed runtime addition/deletion'
    before = b'' if path in ADDED_PATHS else source(path)
    assert row['before_sha256'] == sha(before), 'Reviewed G92 preimage hash changed'
    text = before.decode('utf-8')
    operations = row['operations']
    assert operations and all(0 <= op['start'] <= op['end'] <= len(text) for op in operations)
    assert all(a['end'] <= b['start'] for a, b in zip(operations, operations[1:])), 'Overlapping G92 reviewed edits'
    for op in reversed(operations):
        assert text[op['start']:op['end']] == op['before'], 'Reviewed G92 edit preimage changed'
        text = text[:op['start']] + op['after'] + text[op['end']:]
    after = text.encode('utf-8')
    assert sha(after) == row['after_sha256'], 'Incomplete reviewed G92 delta'
    if path in MANIFESTS:
        assert json.loads(after) == bump_manifest(json.loads(before)), 'Manifest changed outside paired G92 identity'
    else:
        assert sha(after) == REVIEWED_AFTER[path], 'Held probe differs from exact independently reviewed patch'
        assert_held_preservation(path, before, after)
    return after


@lru_cache(maxsize=None)
def expected_frozen_runtime_bytes(path):
    assert path in set(files()) | ADDED_PATHS, 'Runtime path outside frozen G91 and exact G92 additions'
    return apply_delta(path) if path in DELTA_PATHS else source(path)


def expected_runtime_bytes(path):
    if tuple(json.loads((ROOT / 'baseline.json').read_text())['version']) >= (2, 8, 93):
        from g93_source_conservation import expected_runtime_bytes as expected_next
        return expected_next(path)
    return expected_frozen_runtime_bytes(path)


def verify_snapshot(ref):
    """Validate immutable G92 independently of any later current release."""
    result = previous.verify_snapshot(FROZEN_SOURCE_BASE)
    metadata()
    expected = set(files()) | ADDED_PATHS
    frozen = previous.previous.files(ref)
    assert set(frozen) == expected, 'Frozen G92 missing/extra runtime file'
    for path, identity in frozen.items():
        expected_identity = (previous.previous.blob(expected_frozen_runtime_bytes(path))
                             if path in DELTA_PATHS else files()[path])
        assert identity == expected_identity, 'Frozen G92 source drift: ' + path
    history = json.loads(previous.previous.source(ref, 'release-history.json'))
    for version, row in json.loads(source('release-history.json')).items():
        assert history[version] == row, 'Frozen G91 history drift: ' + version
    return {**result, 'runtime_files': len(frozen), 'reviewed_release': [2, 8, 92],
            'reviewed_paths': len(DELTA_PATHS)}


def verify_current():
    if tuple(json.loads((ROOT / 'baseline.json').read_text())['version']) >= (2, 8, 93):
        from g93_source_conservation import verify_current as verify_next
        return verify_next()
    # Immutable G91 (and its G90 source union) must pass before current admission.
    result = previous.verify_snapshot(FROZEN_SOURCE_BASE)
    metadata()
    expected = set(files()) | ADDED_PATHS
    current = {path.relative_to(ROOT).as_posix(): path
               for side in ('behavior_pack', 'resource_pack')
               for path in (ROOT / PROJECT / side).rglob('*') if path.is_file()}
    assert set(current) == expected, 'Missing/extra G92 runtime file'
    for path, local in current.items():
        if path in DELTA_PATHS:
            assert local.read_bytes() == expected_frozen_runtime_bytes(path), 'Runtime source drift: ' + path
        else:
            assert previous.previous.blob(local.read_bytes()) == files()[path], 'Runtime source drift: ' + path
    history = json.loads((ROOT / 'release-history.json').read_text())
    for version, row in json.loads(source('release-history.json')).items():
        assert history[version] == row, 'G91 history drift: ' + version
    return {**result, 'runtime_files': len(current), 'reviewed_release': [2, 8, 92],
            'reviewed_paths': len(DELTA_PATHS)}
