"""Exact main/plate/held source union; no inherited native acceptance."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
COMMON_SOURCE_BASE = 'c85cb34f591079c0b06878b8e565e7f262833e49'
MERGED_MAIN_SOURCE_BASE = 'fe99c0ca3d25ffe5140ed699e89a470ee6abbc63'
COOKERY_DAMAGE_SOURCE_BASE = '0a3f55be6dad72ad50b9a9c485dc195b9c7b1930'
PLATE_SOURCE_BASE = 'fdc9892edcb714c22e1b014943b4ce86c4a2570d'
# Set only after the final held error-path repair is independently reviewed.
HELD_SOURCE_BASE = '05c7ad49e8aa43f813e826905106020c8e803a46'
PROJECT = 'projects/grilling/gameplay_core/'
MAIN_PATH = PROJECT + 'behavior_pack/scripts/main.js'
MANIFESTS = {PROJECT + side + '/manifest.json' for side in ('behavior_pack', 'resource_pack')}
DELTA_PATHS = {MAIN_PATH} | MANIFESTS
COLLISIONS = {'2.8.83', '2.8.84'}
SNAPSHOTS = {
 'development/gameplay_core/verify_a2883.py', 'development/gameplay_core/verify_a2884.py',
 'docs/STATUS-A2.8.83.md', 'docs/STATUS-A2.8.84.md',
 'tools/fixtures/g83-main-reviewed-delta.json', 'tools/fixtures/g84-main-reviewed-delta.json',
 'tools/public_source_witness.py',
}

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def source(ref, path):
    assert ref and not Path(path).is_absolute() and '..' not in Path(path).parts
    return git('show', ref + ':' + path)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

@lru_cache(maxsize=None)
def files(ref, prefix=PROJECT):
    return {row.split('\t', 1)[1]: row.split('\t', 1)[0].split()[2]
            for row in git('ls-tree', '-r', ref, '--', prefix).decode().splitlines()
            if row.split('\t',1)[1].startswith((PROJECT+'behavior_pack/',PROJECT+'resource_pack/'))}

def verify_lineages():
    meta = json.loads((ROOT/'tools/fixtures/g90-source-lineages.json').read_text())
    assert meta['schema'] == 1
    assert meta['main_commit'] == MERGED_MAIN_SOURCE_BASE and meta['plate_commit'] == PLATE_SOURCE_BASE
    for label, ref in [('main', MERGED_MAIN_SOURCE_BASE), ('plate', PLATE_SOURCE_BASE)]:
        assert git('rev-parse', ref+'^{tree}').decode().strip() == meta[label+'_tree'], label+' source tree changed'
    assert set(meta['collisions']) == COLLISIONS
    assert set(meta['main_snapshots']) == SNAPSHOTS
    for path, row in meta['main_snapshots'].items():
        expected = source(MERGED_MAIN_SOURCE_BASE, path)
        assert sha(expected) == row['sha256'], path+' snapshot identity changed'
        assert (ROOT/row['snapshot']).read_bytes() == expected, path+' snapshot bytes changed'
    for version in COLLISIONS:
        fixture = 'tools/fixtures/g'+version.split('.')[-1]+'-main-reviewed-delta.json'
        assert (ROOT/fixture).read_bytes() == source(PLATE_SOURCE_BASE,fixture), 'Plate historical delta changed: '+version
        for label, ref in [('main', MERGED_MAIN_SOURCE_BASE), ('plate', PLATE_SOURCE_BASE)]:
            history = json.loads(source(ref, 'release-history.json'))
            assert meta['collisions'][version][label] == history[version], version+' '+label+' collision changed'
        assert meta['collisions'][version]['main'] != meta['collisions'][version]['plate']
        path = 'docs/STATUS-A'+version+'.md'
        assert (ROOT/'docs/plate-lineage'/Path(path).name).read_bytes() == source(PLATE_SOURCE_BASE, path)
    return meta

def assert_history(testcase, current, ref):
    """Both collisions stay exact in their ledger; current main keeps its labels."""
    meta = verify_lineages()
    prior = json.loads(source(ref, 'release-history.json'))
    for version, row in prior.items():
        if version in COLLISIONS:
            testcase.assertEqual(meta['collisions'][version]['plate'], row, version+' plate history')
            testcase.assertEqual(current[version], meta['collisions'][version]['main'], version+' canonical main history')
        else:
            testcase.assertEqual(current[version], row, version)


def metadata():
    assert HELD_SOURCE_BASE, 'Final held source is not yet admitted'
    d = json.loads((ROOT/'tools/fixtures/g90-runtime-reviewed-delta.json').read_text())
    assert d['schema'] == 1 and d['release'] == [2,8,90]
    assert d['sources'] == {'common':COMMON_SOURCE_BASE, 'main':MERGED_MAIN_SOURCE_BASE,
                            'plate':PLATE_SOURCE_BASE, 'held':HELD_SOURCE_BASE}
    assert set(d['files']) == DELTA_PATHS, 'Unreviewed G90 runtime delta path'
    for label, ref in d['sources'].items():
        assert git('rev-parse', ref+'^{tree}').decode().strip() == d['trees'][label], label+' tree drift'
    return d


def apply_delta(before, path):
    row = metadata()['files'][path]
    assert row['base_commit'] == PLATE_SOURCE_BASE and sha(before) == row['before_sha256']
    text = before.decode('utf-8'); ops = row['operations']
    assert ops and all(0 <= op['start'] <= op['end'] <= len(text) for op in ops)
    assert all(a['end'] <= b['start'] for a,b in zip(ops, ops[1:])), 'Overlapping reviewed edits'
    for op in reversed(ops):
        assert text[op['start']:op['end']] == op['before'], 'Reviewed edit preimage changed'
        text = text[:op['start']] + op['after'] + text[op['end']:]
    result = text.encode('utf-8')
    assert sha(result) == row['after_sha256'], 'Incomplete reviewed G90 delta'
    return result


def merge_bytes(ours, base, theirs):
    """Derive expected text only; never modify canonical or packaged files."""
    with tempfile.TemporaryDirectory() as directory:
        paths = [Path(directory)/name for name in ('ours','base','theirs')]
        for path,data in zip(paths,(ours,base,theirs)):
            path.write_bytes(data)
        result = subprocess.run(['git','merge-file','--stdout',*[str(p) for p in paths]],
                                cwd=ROOT, capture_output=True)
    assert result.returncode == 0, 'Source composition needs explicit conflict review: '+result.stderr.decode(errors='replace')
    return result.stdout

@lru_cache(maxsize=1)
def union_sources():
    metadata()
    common, main, plate, held = [files(ref) for ref in (COMMON_SOURCE_BASE,MERGED_MAIN_SOURCE_BASE,PLATE_SOURCE_BASE,HELD_SOURCE_BASE)]
    expected = {}
    for path in set(main)|set(plate):
        if path in DELTA_PATHS:
            expected[path] = None
            continue
        a,b,p = main.get(path),common.get(path),plate.get(path)
        if a == p:
            ref = MERGED_MAIN_SOURCE_BASE
        elif a == b:
            ref = PLATE_SOURCE_BASE
        elif p == b:
            ref = MERGED_MAIN_SOURCE_BASE
        else:
            raise AssertionError('Unreviewed main/plate conflict: '+path)
        assert files(ref).get(path), 'Unreviewed runtime deletion: '+path
        expected[path] = ref
    for path in set(plate)|set(held):
        if path in DELTA_PATHS:
            continue
        if held.get(path) != plate.get(path):
            assert held.get(path), 'Held source deletes existing runtime: '+path
            assert path not in expected or expected[path] == PLATE_SOURCE_BASE or main.get(path) == plate.get(path), 'Unreviewed held/main conflict: '+path
            expected[path] = HELD_SOURCE_BASE
    return expected

@lru_cache(maxsize=None)
def expected_frozen_runtime_bytes(path):
    ref = union_sources().get(path, 'missing')
    assert ref != 'missing', 'Runtime path outside exact G90 union: '+path
    if path in DELTA_PATHS:
        result = apply_delta(source(PLATE_SOURCE_BASE,path), path)
        if path in MANIFESTS:
            original=json.loads(source(PLATE_SOURCE_BASE,path))
            def bump(value):
                if isinstance(value,dict):
                    return {key:([2,8,90] if key=='version' and item==[2,8,89] else bump(item)) for key,item in value.items()}
                if isinstance(value,list):return [bump(item) for item in value]
                return value
            assert json.loads(result)==bump(original), 'Manifest changed outside fresh paired release identity: '+path
        if path == MAIN_PATH:
            merged = merge_bytes(source(PLATE_SOURCE_BASE,path), source(COMMON_SOURCE_BASE,path), source(MERGED_MAIN_SOURCE_BASE,path))
            merged = merge_bytes(merged, source(PLATE_SOURCE_BASE,path), source(HELD_SOURCE_BASE,path))
            assert result == merged, 'Reviewed main delta differs from exact three-source merge'
        return result
    return source(ref,path)


@lru_cache(maxsize=None)
def expected_runtime_bytes(path):
    if tuple(json.loads((ROOT/'baseline.json').read_text())['version']) >= (2,8,91):
        from g91_source_conservation import expected_runtime_bytes as expected_next
        return expected_next(path)
    return expected_frozen_runtime_bytes(path)


def verify_snapshot(ref):
    """Retain every exact G90 assertion on its immutable public pack snapshot."""
    verify_lineages();metadata()
    expected=union_sources();frozen=files(ref)
    assert set(frozen)==set(expected),'Frozen G90 missing/extra runtime file'
    for path,origin in expected.items():
        identity=blob(expected_frozen_runtime_bytes(path)) if origin is None else files(origin)[path]
        assert frozen[path]==identity,'Frozen G90 source drift: '+path
    history=json.loads(source(ref,'release-history.json'))
    for version,row in json.loads(source(MERGED_MAIN_SOURCE_BASE,'release-history.json')).items():
        assert history[version]==row,'Frozen canonical main history drift: '+version
    for version,row in json.loads(source(PLATE_SOURCE_BASE,'release-history.json')).items():
        if version not in COLLISIONS:assert history[version]==row,'Frozen plate history drift: '+version
    return {'runtime_files':len(frozen),'sources':3,'collision_labels':len(COLLISIONS)}


def verify_current():
    if tuple(json.loads((ROOT/'baseline.json').read_text())['version']) >= (2,8,91):
        from g91_source_conservation import verify_current as verify_next
        return verify_next()
    verify_lineages(); metadata()
    expected = union_sources()
    current = {p.relative_to(ROOT).as_posix():p for side in ('behavior_pack','resource_pack')
               for p in (ROOT/PROJECT/side).rglob('*') if p.is_file()}
    assert set(current) == set(expected), 'Missing/extra G90 runtime file'
    for path,p in current.items():
        ref = expected[path]
        if ref is None:
            assert p.read_bytes() == expected_runtime_bytes(path), 'Runtime source drift: '+path
        else:
            assert blob(p.read_bytes()) == files(ref)[path], 'Runtime source drift: '+path
    history = json.loads((ROOT/'release-history.json').read_text())
    for version,row in json.loads(source(MERGED_MAIN_SOURCE_BASE,'release-history.json')).items():
        assert history[version] == row, 'Canonical main history drift: '+version
    for version,row in json.loads(source(PLATE_SOURCE_BASE,'release-history.json')).items():
        if version not in COLLISIONS:
            assert history[version] == row, 'Plate history drift: '+version
    return {'runtime_files':len(current),'sources':3,'collision_labels':len(COLLISIONS)}
