"""Exact raw client diagnostics over independently conserved public G92."""
from functools import lru_cache
import hashlib
import json
import g92_source_conservation as previous

ROOT = previous.ROOT
PROJECT = previous.PROJECT
FROZEN_SOURCE_BASE = '9d7185abc8ec98a53aa315cc18b13ea51c074786'
FROZEN_TREE = '21e89288ec74cb233aa24185eea7f93d6f6fb6a5'
MANIFESTS = previous.MANIFESTS
ATTACHABLE_PATH = previous.ATTACHABLE_PATH
REVIEWED_PATCH_SHA256 = '3d1453f1048c39303c2171588e3b11c6b95553fd23356c2b58ec235c215f1231'
REVIEWED_AFTER = {ATTACHABLE_PATH: 'a02bac07b403fcd4a2f126b60d23f10ca807b75dcfe846f7f67fd8e3f34b1727'}
DELTA_PATHS = MANIFESTS | set(REVIEWED_AFTER)
ADDED_PATHS = set()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(path):
    return previous.previous.previous.source(FROZEN_SOURCE_BASE, path)


def files():
    return previous.previous.previous.files(FROZEN_SOURCE_BASE)


def metadata():
    data = json.loads((ROOT / 'tools/fixtures/g93-runtime-reviewed-delta.json').read_text())
    assert data['schema'] == 1 and data['release'] == [2, 8, 93]
    assert data['base_commit'] == FROZEN_SOURCE_BASE and data['base_tree'] == FROZEN_TREE
    assert previous.previous.previous.git('rev-parse', FROZEN_SOURCE_BASE + '^{tree}').decode().strip() == FROZEN_TREE
    assert set(data['files']) == DELTA_PATHS, 'Unreviewed G93 runtime path'
    assert data['held_review'] == {'patch_sha256': REVIEWED_PATCH_SHA256,
                                   'after_sha256': REVIEWED_AFTER}, 'Unreviewed raw client diagnostic'
    for path, identity in REVIEWED_AFTER.items():
        assert data['files'][path]['after_sha256'] == identity, 'Raw diagnostic differs from reviewed bytes: ' + path
    return data


def assert_held_preservation(before, after):
    """Only exact reviewed QA statements change; production remains source-exact."""
    old, new = json.loads(before), json.loads(after)
    prior = old['minecraft:attachable']['description']
    desc = new['minecraft:attachable']['description']
    for phase in ('initialize', 'pre_animation'):
        production = lambda rows: [row for row in rows if not row.startswith('v.kg_plate_qa_')]
        assert production(desc['scripts'][phase]) == production(prior['scripts'][phase]), 'Production decoder ordering changed'
    expected = json.loads(before)
    scripts = expected['minecraft:attachable']['description']['scripts']
    variables = [f'v.kg_plate_qa_raw_{hand}_word_{index}' for hand in ('main', 'off') for index in range(8)]
    raw_init = [variable + ' = 0;' for variable in variables]
    index = scripts['initialize'].index('v.kg_plate_qa_raw_word_0 = 0;')
    scripts['initialize'][index:index] = raw_init
    raw_reads = [f"v.kg_plate_qa_raw_{hand}_word_{index} = (c.owning_entity->q.has_property('kaleidoscope_grilling:bottle_{hand}_{index}') ? c.owning_entity->q.property('kaleidoscope_grilling:bottle_{hand}_{index}') : 0);"
                 for hand in ('main', 'off') for index in range(8)]
    rows = scripts['pre_animation']
    rows[0:0] = raw_reads
    for index in (0, 5, 7):
        prefix = f'v.kg_plate_qa_raw_word_{index} = '
        positions = [i for i, row in enumerate(rows) if row.startswith(prefix)]
        assert len(positions) == 1, 'Frozen raw selector changed'
        rows[positions[0]] = f"{prefix}c.item_slot == 'off_hand' ? v.kg_plate_qa_raw_off_word_{index} : v.kg_plate_qa_raw_main_word_{index};"
    positions = [i for i, row in enumerate(rows) if row.startswith('v.kg_plate_qa_enabled = ')]
    assert len(positions) == 1, 'Frozen QA sentinel changed'
    rows[positions[0]] = 'v.kg_plate_qa_enabled = (v.kg_plate_qa_raw_main_word_4 == 1 && v.kg_plate_qa_raw_main_word_7 == 133) || (v.kg_plate_qa_raw_off_word_4 == 1 && v.kg_plate_qa_raw_off_word_7 == 133);'
    sentinel = rows.index('v.kg_plate_qa_sample_due ? q.log(914000) : 0;')
    rows[sentinel] = 'v.kg_plate_qa_sample_due ? q.log(914100) : 0;'
    index = rows.index('v.kg_plate_qa_sample_due ? q.log(v.kg_plate_qa_raw_word_0) : 0;')
    assert rows[index:index + 4] == [f'v.kg_plate_qa_sample_due ? q.log({variable}) : 0;'
        for variable in ('v.kg_plate_qa_raw_word_0', 'v.kg_plate_word_0', 'v.kg_plate_qa_raw_word_5', 'v.kg_plate_qa_raw_word_7')]
    rows[index:index + 4] = [f'v.kg_plate_qa_sample_due ? q.log({variable}) : 0;' for variable in variables]
    index = rows.index('v.kg_plate_qa_next_log = v.kg_plate_qa_sample_due ? v.kg_plate_qa_clock + 1 : v.kg_plate_qa_next_log;')
    rows[index:index] = ['v.kg_plate_qa_sample_due ? q.log(v.kg_plate_owner_occupied == 1 ? 1 : 0) : 0;']
    assert new == expected, 'Attachable changed outside exact raw-client QA statements'
    assert desc['geometry'] == prior['geometry'], 'Production/QA geometry mapping changed'
    assert desc['render_controllers'] == prior['render_controllers'], 'Production/QA controller mapping changed'
    assert desc['animations'] == prior['animations'], 'Production animation mapping changed'


def bump_manifest(value):
    if isinstance(value, dict):
        return {key: ([2, 8, 93] if key == 'version' and item == [2, 8, 92]
                      else bump_manifest(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [bump_manifest(item) for item in value]
    return value


def apply_delta(path):
    row = metadata()['files'][path]
    assert path in files(), 'Unreviewed runtime addition/deletion'
    before = source(path)
    assert row['before_sha256'] == sha(before), 'Reviewed G93 preimage hash changed'
    text = before.decode('utf-8')
    operations = row['operations']
    assert operations and all(0 <= op['start'] <= op['end'] <= len(text) for op in operations)
    assert all(a['end'] <= b['start'] for a, b in zip(operations, operations[1:])), 'Overlapping G93 reviewed edits'
    for op in reversed(operations):
        assert text[op['start']:op['end']] == op['before'], 'Reviewed G93 edit preimage changed'
        text = text[:op['start']] + op['after'] + text[op['end']:]
    after = text.encode('utf-8')
    assert sha(after) == row['after_sha256'], 'Incomplete reviewed G93 delta'
    if path in MANIFESTS:
        assert json.loads(after) == bump_manifest(json.loads(before)), 'Manifest changed outside paired G93 identity'
    else:
        assert sha(after) == REVIEWED_AFTER[path], 'Raw diagnostic differs from exact independently reviewed patch'
        assert_held_preservation(before, after)
    return after


@lru_cache(maxsize=None)
def expected_frozen_runtime_bytes(path):
    assert path in files(), 'Runtime path outside frozen G92'
    return apply_delta(path) if path in DELTA_PATHS else source(path)


def expected_runtime_bytes(path):
    if tuple(json.loads((ROOT / 'baseline.json').read_text())['version']) >= (2, 8, 94):
        from g94_source_conservation import expected_runtime_bytes as expected_next
        return expected_next(path)
    return expected_frozen_runtime_bytes(path)


def verify_snapshot(ref):
    """Validate immutable G93 with its unchanged independently reviewed delta."""
    result = previous.verify_snapshot(FROZEN_SOURCE_BASE)
    metadata()
    frozen = previous.previous.previous.files(ref)
    assert set(frozen) == set(files()), 'Frozen G93 missing/extra runtime file'
    for path, identity in frozen.items():
        expected_identity = (previous.previous.previous.blob(expected_frozen_runtime_bytes(path))
                             if path in DELTA_PATHS else files()[path])
        assert identity == expected_identity, 'Frozen G93 source drift: ' + path
    history = json.loads(previous.previous.previous.source(ref, 'release-history.json'))
    for version, row in json.loads(source('release-history.json')).items():
        assert history[version] == row, 'Frozen G92 history drift: ' + version
    return {**result, 'runtime_files': len(frozen), 'reviewed_release': [2, 8, 93],
            'reviewed_paths': len(DELTA_PATHS)}


def verify_current():
    if tuple(json.loads((ROOT / 'baseline.json').read_text())['version']) >= (2, 8, 94):
        from g94_source_conservation import verify_current as verify_next
        return verify_next()
    # Frozen G92 must pass independently, using its unchanged reviewed metadata.
    result = previous.verify_snapshot(FROZEN_SOURCE_BASE)
    metadata()
    current = {path.relative_to(ROOT).as_posix(): path
               for side in ('behavior_pack', 'resource_pack')
               for path in (ROOT / PROJECT / side).rglob('*') if path.is_file()}
    assert set(current) == set(files()), 'Missing/extra G93 runtime file'
    for path, local in current.items():
        if path in DELTA_PATHS:
            assert local.read_bytes() == expected_frozen_runtime_bytes(path), 'Runtime source drift: ' + path
        else:
            assert previous.previous.previous.blob(local.read_bytes()) == files()[path], 'Runtime source drift: ' + path
    history = json.loads((ROOT / 'release-history.json').read_text())
    for version, row in json.loads(source('release-history.json')).items():
        assert history[version] == row, 'G92 history drift: ' + version
    return {**result, 'runtime_files': len(current), 'reviewed_release': [2, 8, 93],
            'reviewed_paths': len(DELTA_PATHS)}
