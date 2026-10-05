"""Source-pose calibration admission, separate from native rendering acceptance."""
from pathlib import Path
from copy import deepcopy
import json,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'projects/grilling/gameplay_core/resource_pack';sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'development/gameplay_core'))
from held_pose_frames import point
from secret_active_calibration import calibrated_target,PROFILE_IDS
import java_dual_eating_frames as dual
import java_active_eating_frames as active
from test_eating_observer_projection import node
BASE='1457df933ba801511c02783fe7fd3d4a3550e830'
def old(p):return json.loads(subprocess.check_output(['git','show',BASE+':'+str(p.relative_to(ROOT))],cwd=ROOT))
class SecretActiveCalibration(unittest.TestCase):
 def test_each_native_pose_matrix_preserves_orientation_and_only_changes_world_origin(self):
  for profile in PROFILE_IDS:
   for hand in (-1,1):
    for t in (0,.1,.95833,2.16667,2.33333,3.5,3.54167,4.20833,4.5,5):
     targets=[dual.native_arm_target(profile,t,hand,a)for a in (True,False)]if profile=='THREE'else[active.native_arm_target(profile,t,hand)]
     for target in targets:
      result=calibrated_target(target)
      for row in range(4):self.assertEqual(result[row][:3],target[row][:3])
      for axis,(a,b)in enumerate(zip(point(target,[0,0,0]),point(result,[0,0,0]))):self.assertAlmostEqual(b-a,3.41 if axis==1 else 0,places=10)
 def test_only_four_profile_clips_arm_y_channels_get_exact_owned_hand_guard(self):
  p=RP/'animations/java_eating_player.animation.json';before=old(p)['animations'];after=json.loads(p.read_text())['animations'];expected=deepcopy(before);cases=[]
  for profile,id in PROFILE_IDS.items():
   for hand in ('right','left'):
    name='animation.kg_java_eating.player.'+profile.lower()+'.'+hand;slot='slot.weapon.mainhand'if hand=='right'else'slot.weapon.offhand';bones=('rightarm','leftarm')if profile=='THREE'else(hand+'arm',)
    suffix=" + (q.is_item_name_any('"+slot+"','"+id+"') ? 3.41 : 0)"
    for bone in bones:
     for time,value in expected[name]['bones'][bone]['position'].items():
      original=value[1];value[1]+=suffix;cases.append({'id':id,'slot':slot,'old':original,'new':value[1]})
  self.assertEqual(set(after),set(expected))
  for name in expected:self.assertTrue(after[name]==expected[name],name)
  node('const cases='+json.dumps(cases)+r''';
for(const row of cases)for(const held of [row.id,'minecraft:apple','kaleidoscope_grilling:grilled_ender_pearl_skewer','kaleidoscope_grilling:unfinished_skewer'])for(const slot of [row.slot,row.slot==='slot.weapon.mainhand'?'slot.weapon.offhand':'slot.weapon.mainhand']){
 const q={get_default_bone_pivot:()=>22,is_item_name_any:(s,...ids)=>s===slot&&ids.includes(held)};
 const value=x=>new Function('q','return '+x)(q),delta=value(row.new)-value(row.old),expected=held===row.id&&slot===row.slot?3.41:0;
 if(Math.abs(delta-expected)>1e-9)throw Error('Wrong active calibration scope');
}
''')
 def test_item_child_helper_timing_scale_and_calibrated_active_animation_are_preserved(self):
  p=RP/'animations/java_eating_projection.animation.json';self.assertEqual(json.loads(p.read_text()),old(p))
  changed=subprocess.check_output(['git','diff','--name-only',BASE,'--',str((RP/'animations').relative_to(ROOT))],cwd=ROOT,text=True).splitlines();self.assertEqual(changed,[str((RP/'animations/java_eating_player.animation.json').relative_to(ROOT))])
if __name__=='__main__':unittest.main()
