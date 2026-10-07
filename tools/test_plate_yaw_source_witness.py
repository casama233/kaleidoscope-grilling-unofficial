"""Exact plate-only yaw rebuild delta; source evidence is not native acceptance."""
from pathlib import Path
import hashlib,json,subprocess,unittest
ROOT=Path(__file__).resolve().parents[1]
from test_g86_source_coherence import HARDENING_SOURCE_BASE,G88_DELTAS,source,apply_runtime_delta
PLATE_YAW_SOURCE_BASE='6e714853d029f93f0186efa2e96e192e87735a74'
PATH='projects/grilling/gameplay_core/behavior_pack/scripts/station_contents_visual_runtime.js'
def reviewed():
 d=json.loads((ROOT/'tools/fixtures/g87-plate-yaw-reviewed-delta.json').read_text())
 assert d['schema']==1 and d['release']==[2,8,87] and d['base_commit']==PLATE_YAW_SOURCE_BASE and d['path']==PATH
 before=subprocess.check_output(['git','show',PLATE_YAW_SOURCE_BASE+':'+PATH],cwd=ROOT)
 assert hashlib.sha256(before).hexdigest()==d['before_sha256']
 text=before.decode();cursor=0;result=[]
 assert len(d['operations'])==2
 for op in d['operations']:
  assert cursor<=op['start']<=op['end']<=len(text)
  assert text[op['start']:op['end']]==op['before']
  result.append(text[cursor:op['start']]);result.append(op['after']);cursor=op['end']
 result.append(text[cursor:]);after=''.join(result).encode()
 assert hashlib.sha256(after).hexdigest()==d['after_sha256']
 return before,after,d
def current_reviewed():
 _,after,_=reviewed()
 if tuple(json.loads((ROOT/'baseline.json').read_text())['version'])>=(2,8,88):
  assert after==source(HARDENING_SOURCE_BASE,PATH)
  after=apply_runtime_delta(after,PATH,G88_DELTAS[PATH],(2,8,88),HARDENING_SOURCE_BASE)
 return after
class PlateYawWitness(unittest.TestCase):
 def test_exact_renderer_delta_and_no_unrelated_runtime_edits(self):
  before,after,d=reviewed();self.assertEqual((ROOT/PATH).read_bytes(),current_reviewed())
  self.assertEqual(d['operations'][0]['before'].count('if(old&&'),1)
  self.assertIn('old.spawnYaw!==-at.angle',d['operations'][0]['after'])
  self.assertIn('spawnYaw:-at.angle',d['operations'][1]['after'])
  start=before.index(b'function renderPlate(');end=before.index(b'export function syncStationContentsVisual(')
  self.assertEqual(before[:start],after[:start]);self.assertEqual(before[end:],after[after.index(b'export function syncStationContentsVisual('):])
 def test_missing_rebuild_or_spawn_basis_and_unrelated_mutations_differ(self):
  _,after,_=reviewed()
  for changed in (after+b'\n',after.replace(b'||old.spawnYaw!==-at.angle',b''),after.replace(b',spawnYaw:-at.angle',b''),after.replace(b'initialRotation:-at.angle',b'initialRotation:0')):
   self.assertNotEqual(after,changed)
 def test_layouts_and_eating_code_are_identical_to_frozen_g86(self):
  for path in ('projects/grilling/gameplay_core/behavior_pack/scripts/plate_visual_core.js','projects/grilling/gameplay_core/behavior_pack/scripts/main.js'):
   original=subprocess.check_output(['git','show',PLATE_YAW_SOURCE_BASE+':'+path],cwd=ROOT)
   if path.endswith('/plate_visual_core.js') and tuple(json.loads((ROOT/'baseline.json').read_text())['version'])>=(2,8,89):
    from plate_g89_source_witness import expected_current,source as frozen_source
    self.assertEqual(frozen_source(path),original);self.assertEqual((ROOT/path).read_bytes(),expected_current(path),path)
   else:self.assertEqual((ROOT/path).read_bytes(),original,path)
if __name__=='__main__':unittest.main()
