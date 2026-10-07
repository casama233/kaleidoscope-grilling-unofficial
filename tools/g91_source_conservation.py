"""One exact Cloud input repair on the independently conserved frozen G90."""
from functools import lru_cache
import hashlib,json
from pathlib import Path
import g90_source_conservation as previous

ROOT=previous.ROOT
PROJECT=previous.PROJECT
FROZEN_SOURCE_BASE='6fbc56f9b49d033f5df106123311096ee39f8702'
FROZEN_TREE='b262b2c3095b9ef2c106740c22239f8f24eb71d1'
CLOUD_PATH=PROJECT+'resource_pack/particles/feedback_cloud.json'
MANIFESTS=previous.MANIFESTS
HELD_WRITER_PATH=PROJECT+'behavior_pack/scripts/bottle_held_visual_runtime.js'
HELD_FRAME_PATH=PROJECT+'resource_pack/animations/plate_held.animation.json'
HELD_PATCH_SHA256='eb4a1d985e6ea47556ef61a10fe580450abd8ec8e8394852a85349a9c3d308ce'
HELD_REVIEWED_AFTER={
 HELD_WRITER_PATH:'72b0e69d561ae2a12ca9c2d7f27c335837bdb7d11c6749a40ab6679e8168a224',
 HELD_FRAME_PATH:'802a8391a37bde12f6846b83429c37afb43ae09e6d74c1d662e1d8b3da642d89',
}
DELTA_PATHS={CLOUD_PATH}|MANIFESTS|set(HELD_REVIEWED_AFTER)

def source(path):return previous.source(FROZEN_SOURCE_BASE,path)
def sha(data):return hashlib.sha256(data).hexdigest()

def corrected_cloud(before):
    text=before.decode('utf-8')
    for axis in 'xyz':
        old='((variable.kg_velocity.'+axis+' ?? 0)/20)'
        assert text.count(old)==1,'Frozen Cloud input changed: '+axis
        text=text.replace(old,'(variable.kg_velocity.'+axis+'/20)')
    return text.encode('utf-8')

def metadata():
    d=json.loads((ROOT/'tools/fixtures/g91-cloud-reviewed-delta.json').read_text())
    assert d['schema']==1 and d['release']==[2,8,91]
    assert d['base_commit']==FROZEN_SOURCE_BASE and d['base_tree']==FROZEN_TREE
    assert previous.git('rev-parse',FROZEN_SOURCE_BASE+'^{tree}').decode().strip()==FROZEN_TREE
    assert set(d['files'])==DELTA_PATHS,'Unreviewed G91 runtime path'
    assert d['held_review']=={'patch_sha256':HELD_PATCH_SHA256,'after_sha256':HELD_REVIEWED_AFTER}
    for path,identity in HELD_REVIEWED_AFTER.items():assert d['files'][path]['after_sha256']==identity,'Unreviewed held diagnostic/frame delta'
    return d

def apply_delta(path):
    d=metadata()['files'][path];before=source(path)
    assert d['before_sha256']==sha(before)
    text=before.decode('utf-8');ops=d['operations']
    assert ops and all(0<=op['start']<=op['end']<=len(text) for op in ops)
    assert all(a['end']<=b['start'] for a,b in zip(ops,ops[1:]))
    for op in reversed(ops):
        assert text[op['start']:op['end']]==op['before'],'Reviewed G91 preimage changed'
        text=text[:op['start']]+op['after']+text[op['end']:]
    after=text.encode('utf-8');assert sha(after)==d['after_sha256'],'Incomplete G91 delta'
    if path==CLOUD_PATH:
        assert after==corrected_cloud(before),'Cloud changed outside its three supported vector reads'
    elif path in HELD_REVIEWED_AFTER:
        assert sha(after)==HELD_REVIEWED_AFTER[path],'Held source differs from exact independently reviewed patch'
        if path==HELD_FRAME_PATH:
            old=json.loads(before);new=json.loads(after)
            assert set(new['animations'])==set(old['animations'])
            for key,clip in old['animations'].items():
                current=new['animations'][key]
                if key in ['animation.kg_plate_held.fp_right','animation.kg_plate_held.fp_left']:
                    current=json.loads(json.dumps(current));current['bones']['plate_pose']['position']=clip['bones']['plate_pose']['position']
                assert current==clip,'Held frame changed outside two FP position vectors'
    else:
        def bump(value):
            if isinstance(value,dict):return {key:([2,8,91] if key=='version' and item==[2,8,90] else bump(item)) for key,item in value.items()}
            if isinstance(value,list):return [bump(item) for item in value]
            return value
        assert json.loads(after)==bump(json.loads(before)),'Manifest changed outside paired G91 identity'
    return after

@lru_cache(maxsize=None)
def expected_frozen_runtime_bytes(path):
    assert path in previous.files(FROZEN_SOURCE_BASE),'Runtime path outside frozen G90'
    return apply_delta(path) if path in DELTA_PATHS else source(path)

def expected_runtime_bytes(path):
    if tuple(json.loads((ROOT/'baseline.json').read_text())['version']) >= (2,8,92):
        from g92_source_conservation import expected_runtime_bytes as expected_next
        return expected_next(path)
    return expected_frozen_runtime_bytes(path)


def verify_snapshot(ref):
    """Retain all G91 assertions on an immutable public runtime snapshot."""
    result=previous.verify_snapshot(FROZEN_SOURCE_BASE)
    metadata();expected=previous.files(FROZEN_SOURCE_BASE);frozen=previous.files(ref)
    assert set(frozen)==set(expected),'Frozen G91 missing/extra runtime file'
    for path,identity in expected.items():
        if path in DELTA_PATHS:identity=previous.blob(expected_frozen_runtime_bytes(path))
        assert frozen[path]==identity,'Frozen G91 source drift: '+path
    history=json.loads(previous.source(ref,'release-history.json'))
    for version,row in json.loads(source('release-history.json')).items():
        assert history[version]==row,'Frozen G90 history drift: '+version
    return {**result,'reviewed_release':[2,8,91],'reviewed_paths':len(DELTA_PATHS)}


def verify_current():
    if tuple(json.loads((ROOT/'baseline.json').read_text())['version']) >= (2,8,92):
        from g92_source_conservation import verify_current as verify_next
        return verify_next()
    # Validate frozen G90's full original source union before inspecting G91.
    result=previous.verify_snapshot(FROZEN_SOURCE_BASE)
    metadata();expected=previous.files(FROZEN_SOURCE_BASE)
    current={p.relative_to(ROOT).as_posix():p for side in ('behavior_pack','resource_pack')
             for p in (ROOT/PROJECT/side).rglob('*') if p.is_file()}
    assert set(current)==set(expected),'Missing/extra G91 runtime file'
    for path,p in current.items():
        if path in DELTA_PATHS:assert p.read_bytes()==expected_frozen_runtime_bytes(path),'Runtime source drift: '+path
        else:assert previous.blob(p.read_bytes())==expected[path],'Runtime source drift: '+path
    current_history=json.loads((ROOT/'release-history.json').read_text())
    for version,row in json.loads(source('release-history.json')).items():
        assert current_history[version]==row,'G90 history drift: '+version
    return {**result,'reviewed_release':[2,8,91],'reviewed_paths':len(DELTA_PATHS)}
