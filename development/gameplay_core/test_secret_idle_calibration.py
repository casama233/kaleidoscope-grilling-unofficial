"""Bounded idle alias admission; native mouth/transition acceptance is separate."""
from pathlib import Path
from copy import deepcopy
import json,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'projects/grilling/gameplay_core/resource_pack';sys.path.insert(0,str(ROOT/'tools'))
import secret_idle_calibration as calibration
from build_secret_held import owner_occupancy
from secret_terminal_visibility import apply as apply_terminal_visibility
from test_eating_observer_projection import node
BASE='f64bcbd0a1f9e350c17aa7db1b05aa5d5430c236'
def load(p):return json.loads(p.read_text())
def old(p):return json.loads(subprocess.check_output(['git','show',BASE+':'+str(p.relative_to(ROOT))],cwd=ROOT))
class SecretIdleCalibration(unittest.TestCase):
 def test_exact6710_displacement_preserves_source_rotation_scale_and_shared_files(self):
  current=load(calibration.TARGET);self.assertEqual(current,calibration.animation_document())
  shared_path=RP/'animations/a287_skewer_held.animation.json';self.assertEqual(load(shared_path),old(shared_path));source=load(shared_path)['animations']
  for hand in ('right','left'):
   clip=deepcopy(current['animations'][calibration.clip_id(hand)]);clip['bones']['skewer_pose']['position']=source['animation.kg_a287.skewer_fp_'+hand]['bones']['skewer_pose']['position']
   self.assertEqual(clip,source['animation.kg_a287.skewer_fp_'+hand])
 def test_exact_three_owned_attachables_get_idempotent_idle_aliases_only(self):
  for identifier in calibration.OWNED:
   path=RP/'attachables'/(identifier.split(':')[1]+'.attachable.json');before=old(path)['minecraft:attachable']['description'];expected=calibration.apply_idle_calibration(deepcopy(before));actual=load(path)['minecraft:attachable']['description']
   expected['scripts']['pre_animation']=[owner_occupancy(identifier)if row.startswith('v.kg_secret_owner_occupied = ')else row for row in expected['scripts']['pre_animation']]
   apply_terminal_visibility(expected)
   self.assertEqual(actual,expected);self.assertEqual(calibration.apply_idle_calibration(deepcopy(actual)),actual)
   for key,value in before['animations'].items():self.assertEqual(actual['animations'][key],value)
   self.assertEqual(len(actual['animations']),len(before['animations'])+2)
  for path in (RP/'attachables').glob('*.json'):
   d=load(path)['minecraft:attachable']['description']
   if d['identifier']not in calibration.OWNED:self.assertNotIn('fp_idle_calibrated_',json.dumps(d))
 def test_idle_active_and_completion_repairs_are_only_reviewed_owned_runtime_deltas(self):
  changes=subprocess.check_output(['git','diff','--name-only',BASE,'--','projects/grilling/gameplay_core'],cwd=ROOT,text=True).splitlines()
  expected=[str((RP/'attachables'/(identifier.split(':')[1]+'.attachable.json')).relative_to(ROOT))for identifier in calibration.OWNED]
  # Private 6712 subsequently aligns the active origin; its strict channel
  # conservation and exact item guards are checked by SecretActiveCalibration.
  expected.append(str((RP/'animations/java_eating_player.animation.json').relative_to(ROOT)))
  expected.extend('projects/grilling/gameplay_core/behavior_pack/scripts/'+name for name in ('main.js','secret_held_runtime.js'))
  # The new calibrated animation is untracked before commit, tracked after it.
  self.assertEqual(set(changes)-{str(calibration.TARGET.relative_to(ROOT))},set(expected))
 def test_idle_and_active_base_are_exclusive_without_changing_eating_helper_admission(self):
  rows=[{'before':old(RP/'attachables'/(id.split(':')[1]+'.attachable.json'))['minecraft:attachable']['description'],'after':load(RP/'attachables'/(id.split(':')[1]+'.attachable.json'))['minecraft:attachable']['description']}for id in calibration.OWNED]
  node('const rows='+json.dumps(rows)+r''';
for(const {before,after}of rows)for(const hand of ['right','left'])for(const projection of [0,1])for(const using of [false,true]){
 const slot=hand==='right'?'main_hand':'off_hand',weapon=hand==='right'?'slot.weapon.mainhand':'slot.weapon.offhand',handCode=hand==='right'?1:2;
 const profile=after.identifier.endsWith('_java_three_alt')?4:3;
 const q={is_using_item:using,is_sneaking:0,is_swimming:0,is_gliding:0,is_riding:0,is_item_equipped:()=>0,
 property:n=>({eat_hand:handCode,eat_profile:profile,eat_projection:projection})[n.split(':')[1]],is_item_name_any:(s,...ids)=>s===weapon&&ids.includes(after.identifier)};
 const c={is_first_person:1,item_slot:slot},v={kg_secret_owner_occupied:1,kg_secret_piece_index:176};
 const active=(d,alias)=>{const r=d.scripts.animate.find(r=>alias in r);return r?Boolean(new Function('q','c','return '+r[alias])(q,c)):false};
 const idle=active(after,'fp_idle_calibrated_'+hand),base=active(after,'fp_'+hand);
 if(idle===using)throw Error('Idle calibration entered active own-hand use');
 if(using&&base!==active(before,'fp_'+hand))throw Error('Active legacy base admission changed');
 if(!using&&base)throw Error('Idle drew old and new base together');
 for(const alias of ['eat_'+hand,'eat_alt_'+hand,'fp_eat_'+hand,'tp_'+hand])if(active(before,alias)!==active(after,alias))throw Error('Eating/TP alias changed '+alias);
 c.is_first_person=0;if(active(after,'fp_idle_calibrated_'+hand))throw Error('Idle calibration leaked to third person');
}
''')
if __name__=='__main__':unittest.main()
