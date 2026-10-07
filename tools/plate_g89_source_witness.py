"""Exact G89 plate-only delta on the frozen G88 native/documentation snapshot."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
DIRECTION_SOURCE_BASE='39e6dd145a84abdf921382aef9c90833061aa955'
PROJECT='projects/grilling/gameplay_core/'
ALLOWED={PROJECT+p for p in (
 'behavior_pack/scripts/plate_visual_core.js','behavior_pack/entities/plate_food_visual.json',
 'resource_pack/entity/plate_food_visual.entity.json','resource_pack/models/entity/plate_food_display.geo.json',
 'resource_pack/render_controllers/plate_food_visual.render_controllers.json')}
NEW={PROJECT+p for p in ('resource_pack/models/entity/plate_food_display.geo.json','resource_pack/render_controllers/plate_food_visual.render_controllers.json')}
def sha(data):return hashlib.sha256(data).hexdigest()
def source(path):return subprocess.check_output(['git','show',DIRECTION_SOURCE_BASE+':'+path],cwd=ROOT)
def metadata():
 d=json.loads((ROOT/'tools/fixtures/g89-plate-runtime-reviewed-delta.json').read_text())
 assert d['schema']==1 and d['release']==[2,8,89] and d['base_commit']==DIRECTION_SOURCE_BASE
 assert set(d['files'])==ALLOWED
 assert {p for p,row in d['files'].items() if row['new']}==NEW
 return d
def expected_current(path, snapshot=None):
 row=metadata()['files'][path]
 if row['new']:
  data=subprocess.check_output(['git','show',snapshot+':'+path],cwd=ROOT) if snapshot else (ROOT/path).read_bytes();assert sha(data)==row['after_sha256'];return data
 before=source(path);assert sha(before)==row['before_sha256']
 text=before.decode();ops=row['operations'];assert ops
 assert all(0<=op['start']<=op['end']<=len(text) for op in ops)
 assert all(a['end']<=b['start'] for a,b in zip(ops,ops[1:]))
 for op in reversed(ops):
  assert text[op['start']:op['end']]==op['before']
  text=text[:op['start']]+op['after']+text[op['end']:]
 after=text.encode();assert sha(after)==row['after_sha256'];return after
def verify_snapshot(ref):
 metadata()
 for side in ('behavior_pack','resource_pack'):
  prefix=PROJECT+side+'/'
  old={line.split('\t',1)[1]:line.split('\t',1)[0].split()[2] for line in subprocess.check_output(['git','ls-tree','-r',DIRECTION_SOURCE_BASE,'--',prefix],cwd=ROOT,text=True).splitlines()}
  frozen={line.split('\t',1)[1]:line.split('\t',1)[0].split()[2] for line in subprocess.check_output(['git','ls-tree','-r',ref,'--',prefix],cwd=ROOT,text=True).splitlines()}
  assert set(frozen)==set(old)|{p for p in NEW if p.startswith(prefix)},'Frozen G89 missing/extra runtime file'
  for path,identity in frozen.items():
   if path.endswith('/manifest.json'):continue
   if path in ALLOWED:
    data=expected_current(path,snapshot=ref)
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==identity,path
   else:assert identity==old[path],path

def verify_current():
 if tuple(json.loads((ROOT/'baseline.json').read_text())['version'])>=(2,8,90):
  from g90_source_conservation import PLATE_SOURCE_BASE,verify_current as verify_union
  verify_snapshot(PLATE_SOURCE_BASE);verify_union();return
 metadata()
 for side in ('behavior_pack','resource_pack'):
  prefix=PROJECT+side+'/'
  old={line.split('\t',1)[1]:line.split('\t',1)[0].split()[2] for line in subprocess.check_output(['git','ls-tree','-r',DIRECTION_SOURCE_BASE,'--',prefix],cwd=ROOT,text=True).splitlines()}
  current={p.relative_to(ROOT).as_posix():p for p in (ROOT/prefix).rglob('*') if p.is_file()}
  assert set(current)==set(old)|{p for p in NEW if p.startswith(prefix)},'G89 missing/extra runtime file'
  for path,p in current.items():
   if path.endswith('/manifest.json'):continue
   if path in ALLOWED:assert p.read_bytes()==expected_current(path),path
   else:
    data=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==old[path],path
