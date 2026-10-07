"""Exact default-off binary QA board over independently conserved public G93."""
from functools import lru_cache
import hashlib
import json
import g93_source_conservation as previous

ROOT = previous.ROOT
PROJECT = previous.PROJECT
HISTORICAL = previous.previous.previous.previous
FROZEN_SOURCE_BASE = '44c5fd8a786addf6cf1881ba5f7d665f0f492b0c'
FROZEN_TREE = 'b555875c13464c377ac8d81adc4d01ca7b0b5a00'
MANIFESTS = previous.MANIFESTS
ATTACHABLE_PATH = previous.ATTACHABLE_PATH
CONTROLLERS_PATH = previous.previous.CONTROLLERS_PATH
QA_GEOMETRY_PATH = PROJECT + 'resource_pack/models/entity/plate_held_binary_qa.geo.json'
QA_CONTROLLER = 'controller.render.kg_plate_held.qa_binary'
REVIEWED_PATCH_SHA256 = '052a29fc9deff0617a15425600f5267c854212cc26b59570fd083e7f8fee553b'
REVIEWED_AFTER = {
    ATTACHABLE_PATH: '4e443d04eddd276d55bac04d98e6b78c68c6eb59d4fa77ee3a97a2c5fcbc102d',
    CONTROLLERS_PATH: '0807c6745eddb2a81cebf60f1467682528e715138cac5de7d78be1a2e64f9330',
    QA_GEOMETRY_PATH: 'd928752c81e08f95e97106872106e6ebdffdcb13a761e87d1591139099c13572',
}
DELTA_PATHS = MANIFESTS | set(REVIEWED_AFTER)
ADDED_PATHS = {QA_GEOMETRY_PATH}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(path):
    return HISTORICAL.source(FROZEN_SOURCE_BASE, path)


def files():
    return HISTORICAL.files(FROZEN_SOURCE_BASE)


def metadata():
    data = json.loads((ROOT / 'tools/fixtures/g94-runtime-reviewed-delta.json').read_text())
    assert data['schema'] == 1 and data['release'] == [2, 8, 94]
    assert data['base_commit'] == FROZEN_SOURCE_BASE and data['base_tree'] == FROZEN_TREE
    assert HISTORICAL.git('rev-parse', FROZEN_SOURCE_BASE + '^{tree}').decode().strip() == FROZEN_TREE
    assert set(data['files']) == DELTA_PATHS, 'Unreviewed G94 runtime path'
    assert data['held_review'] == {'patch_sha256': REVIEWED_PATCH_SHA256,
                                   'after_sha256': REVIEWED_AFTER}, 'Unreviewed binary client diagnostic'
    for path, identity in REVIEWED_AFTER.items():
        assert data['files'][path]['after_sha256'] == identity, 'Binary diagnostic differs from reviewed bytes: ' + path
    return data


def binary_bit(value, bit):
    high = f'math.floor({value}/{2 ** (bit + 1)})'
    return f'math.floor({value}/{2 ** bit}) - {high} - {high}'


def expected_binary_controller():
    raw = 'v.kg_plate_qa_raw_word_0'
    rows = [[binary_bit(raw, bit) for bit in range(top, top - 8, -1)] for top in (23, 15, 7)]
    rows.append([binary_bit('v.kg_plate_count', bit) for bit in (2, 1, 0)] +
        [f'{raw} != math.floor({raw})', f'{raw} - math.floor({raw}) == 0.5', '0', '1', '1'])
    rows.append([f'{raw} < 0'] + [binary_bit('v.kg_plate_desc_0', bit) for bit in range(6, -1, -1)])
    rows += [[binary_bit(f'v.kg_plate_food_0_{slot}', bit) for bit in range(7, -1, -1)] for slot in range(3)]
    visibility = [{'*': 0}, {'qa_binary_frame': 'v.kg_plate_qa_enabled == 1'}]
    for row, expressions in enumerate(rows):
        for col, expression in enumerate(expressions):
            for value in (0, 1):
                visibility.append({f'qa_binary_{row}_{col}_{value}':
                    f'v.kg_plate_qa_enabled == 1 && ({expression}) == {value}'})
    return {'geometry': 'Geometry.qa_binary', 'materials': [{'*': 'Material.default'}],
            'textures': ['Texture.qa_binary'], 'part_visibility': visibility}


def assert_held_preservation(path, before, after):
    """Add the one exact board without touching production or prior raw QA."""
    if path == ATTACHABLE_PATH:
        expected, new = json.loads(before), json.loads(after)
        prior = expected['minecraft:attachable']['description']
        desc = new['minecraft:attachable']['description']
        assert desc['scripts'] == prior['scripts'], 'Production/raw QA decoder or log statements changed'
        assert 'qa_binary' not in prior['textures'] and 'qa_binary' not in prior['geometry']
        prior['textures']['qa_binary'] = 'textures/held/bottle_shell_palette'
        prior['geometry']['qa_binary'] = 'geometry.kg_plate_held.qa_binary'
        prior['render_controllers'].append(QA_CONTROLLER)
        assert new == expected, 'Attachable changed outside exact binary QA references'
    elif path == CONTROLLERS_PATH:
        old, new = json.loads(before), json.loads(after)
        prior, current = old['render_controllers'], new['render_controllers']
        assert len(prior) == 33 and list(current) == list(prior) + [QA_CONTROLLER], 'Binary QA controller scope/order changed'
        for name, controller in prior.items():
            assert current[name] == controller, 'Production/prior QA controller changed: ' + name
        assert current[QA_CONTROLLER] == expected_binary_controller(), 'Binary QA bit layout/gating changed'
        old['render_controllers'][QA_CONTROLLER] = expected_binary_controller()
        assert new == old, 'Controllers changed outside exact binary QA addition'
    elif path == QA_GEOMETRY_PATH:
        assert before == b'', 'Binary QA geometry must be the one reviewed addition'
        new = json.loads(after)
        assert new['format_version'] == '1.21.0' and len(new['minecraft:geometry']) == 1
        geometry = new['minecraft:geometry'][0]
        assert geometry['description']['identifier'] == 'geometry.kg_plate_held.qa_binary'
        assert geometry['description']['texture_width'] == geometry['description']['texture_height'] == 128
        bones = geometry['bones']
        expected_names = ['grip', 'plate_pose', 'qa_binary_frame'] + [
            f'qa_binary_{row}_{col}_{value}' for row in range(8) for col in range(8) for value in (0, 1)]
        assert [bone['name'] for bone in bones] == expected_names, 'Binary QA board bone scope/order changed'
        assert bones[:2] == json.loads(source(PROJECT + 'resource_pack/models/entity/plate_held_qa.geo.json'))['minecraft:geometry'][0]['bones'][:2], 'Binary QA changed original hand rig'
    else:
        raise AssertionError('Unreviewed binary QA path: ' + path)


def bump_manifest(value):
    if isinstance(value, dict):
        return {key: ([2, 8, 94] if key == 'version' and item == [2, 8, 93]
                      else bump_manifest(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [bump_manifest(item) for item in value]
    return value


def apply_delta(path):
    row = metadata()['files'][path]
    assert (path in ADDED_PATHS) == (path not in files()), 'Unreviewed runtime addition/deletion'
    before = b'' if path in ADDED_PATHS else source(path)
    assert row['before_sha256'] == sha(before), 'Reviewed G94 preimage hash changed'
    text = before.decode('utf-8')
    operations = row['operations']
    assert operations and all(0 <= op['start'] <= op['end'] <= len(text) for op in operations)
    assert all(a['end'] <= b['start'] for a, b in zip(operations, operations[1:])), 'Overlapping G94 reviewed edits'
    for op in reversed(operations):
        assert text[op['start']:op['end']] == op['before'], 'Reviewed G94 edit preimage changed'
        text = text[:op['start']] + op['after'] + text[op['end']:]
    after = text.encode('utf-8')
    assert sha(after) == row['after_sha256'], 'Incomplete reviewed G94 delta'
    if path in MANIFESTS:
        assert json.loads(after) == bump_manifest(json.loads(before)), 'Manifest changed outside paired G94 identity'
    else:
        assert sha(after) == REVIEWED_AFTER[path], 'Binary diagnostic differs from exact independently reviewed patch'
        assert_held_preservation(path, before, after)
    return after


@lru_cache(maxsize=None)
def expected_frozen_runtime_bytes(path):
    assert path in set(files()) | ADDED_PATHS, 'Runtime path outside frozen G93 and exact G94 addition'
    return apply_delta(path) if path in DELTA_PATHS else source(path)


def expected_runtime_bytes(path):
    if tuple(json.loads((ROOT / 'baseline.json').read_text())['version']) >= (2, 8, 95):
        from g95_source_conservation import expected_runtime_bytes as expected_next
        return expected_next(path)
    return expected_frozen_runtime_bytes(path)


def verify_snapshot(ref):
    """Validate diagnostic G94 independently of every later current release."""
    result = previous.verify_snapshot(FROZEN_SOURCE_BASE)
    for release in (92, 93):
        path = f'tools/fixtures/g{release}-runtime-reviewed-delta.json'
        assert (ROOT / path).read_bytes() == source(path), 'Frozen reviewed fixture drift: ' + path
    metadata()
    frozen = HISTORICAL.files(ref)
    assert set(frozen) == set(files()) | ADDED_PATHS, 'Frozen G94 missing/extra runtime file'
    for path, identity in frozen.items():
        expected_identity = (HISTORICAL.blob(expected_frozen_runtime_bytes(path))
                             if path in DELTA_PATHS else files()[path])
        assert identity == expected_identity, 'Frozen G94 source drift: ' + path
    path = 'tools/fixtures/g94-runtime-reviewed-delta.json'
    assert (ROOT / path).read_bytes() == HISTORICAL.source(ref, path), 'Frozen reviewed fixture drift: ' + path
    history = json.loads(HISTORICAL.source(ref, 'release-history.json'))
    for version, row in json.loads(source('release-history.json')).items():
        assert history[version] == row, 'Frozen G93 history drift: ' + version
    return {**result, 'runtime_files': len(frozen), 'reviewed_release': [2, 8, 94],
            'reviewed_paths': len(DELTA_PATHS)}


def verify_current():
    if tuple(json.loads((ROOT / 'baseline.json').read_text())['version']) >= (2, 8, 95):
        from g95_source_conservation import verify_current as verify_next
        return verify_next()
    # Immutable G93 passes on unchanged d93/d92 fixtures before G94 admission.
    result = previous.verify_snapshot(FROZEN_SOURCE_BASE)
    for release in (92, 93):
        path = f'tools/fixtures/g{release}-runtime-reviewed-delta.json'
        assert (ROOT / path).read_bytes() == source(path), 'Frozen reviewed fixture drift: ' + path
    metadata()
    current = {path.relative_to(ROOT).as_posix(): path
               for side in ('behavior_pack', 'resource_pack')
               for path in (ROOT / PROJECT / side).rglob('*') if path.is_file()}
    assert set(current) == set(files()) | ADDED_PATHS, 'Missing/extra G94 runtime file'
    for path, local in current.items():
        if path in DELTA_PATHS:
            assert local.read_bytes() == expected_frozen_runtime_bytes(path), 'Runtime source drift: ' + path
        else:
            assert HISTORICAL.blob(local.read_bytes()) == files()[path], 'Runtime source drift: ' + path
    history = json.loads((ROOT / 'release-history.json').read_text())
    for version, row in json.loads(source('release-history.json')).items():
        assert history[version] == row, 'G93 history drift: ' + version
    return {**result, 'runtime_files': len(current), 'reviewed_release': [2, 8, 94],
            'reviewed_paths': len(DELTA_PATHS)}
