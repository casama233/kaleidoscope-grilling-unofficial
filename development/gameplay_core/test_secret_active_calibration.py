"""Source-pose calibration admission, separate from native rendering acceptance."""
from pathlib import Path
from copy import deepcopy
import json,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'projects/grilling/gameplay_core/resource_pack';sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'development/gameplay_core'))
from held_pose_frames import point
from secret_active_calibration import calibrated_target,PROFILE_IDS
from public_source_witness import PUBLIC_SOURCE_BASE,public_json,assert_public_bytes
import java_dual_eating_frames as dual
import java_active_eating_frames as active
from test_eating_observer_projection import node
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
  p=RP/'animations/java_eating_player.animation.json';before=public_json(p.relative_to(ROOT))['animations'];after=json.loads(p.read_text())['animations'];uncalibrated=deepcopy(before);cases=[]
  # The public witness already includes the repair. Reconstruct the source
  # counterfactual only by removing each verified, exact owned Y suffix.
  # This is source conservation, not proof of an unavailable older revision.
  for profile,id in PROFILE_IDS.items():
   for hand in ('right','left'):
    name='animation.kg_java_eating.player.'+profile.lower()+'.'+hand;slot='slot.weapon.mainhand'if hand=='right'else'slot.weapon.offhand';bones=('rightarm','leftarm')if profile=='THREE'else(hand+'arm',)
    suffix=" + (q.is_item_name_any('"+slot+"','"+id+"') ? 3.41 : 0)"
    for bone in bones:
     for time,value in uncalibrated[name]['bones'][bone]['position'].items():
      repaired=value[1];self.assertTrue(repaired.endswith(suffix),(name,bone,time));self.assertEqual(repaired.count(suffix),1)
      value[1]=repaired[:-len(suffix)];cases.append({'id':id,'slot':slot,'old':value[1],'new':repaired,'clip':name,'bone':bone,'time':time,'suffix':suffix})
  self.assertNotIn('? 3.41 : 0',json.dumps(uncalibrated))
  expected=deepcopy(uncalibrated)
  for case in cases:expected[case['clip']]['bones'][case['bone']]['position'][case['time']][1]+=case['suffix']
  self.assertEqual(set(after),set(expected))
  for name in expected:self.assertTrue(after[name]==expected[name],name)
  assert_public_bytes(self,p)
  node('const cases='+json.dumps(cases)+r''';
for(const row of cases)for(const held of [row.id,'minecraft:apple','kaleidoscope_grilling:grilled_ender_pearl_skewer','kaleidoscope_grilling:unfinished_skewer'])for(const slot of [row.slot,row.slot==='slot.weapon.mainhand'?'slot.weapon.offhand':'slot.weapon.mainhand']){
 const q={get_default_bone_pivot:()=>22,is_item_name_any:(s,...ids)=>s===slot&&ids.includes(held)};
 const value=x=>new Function('q','return '+x)(q),delta=value(row.new)-value(row.old),expected=held===row.id&&slot===row.slot?3.41:0;
 if(Math.abs(delta-expected)>1e-9)throw Error('Wrong active calibration scope');
}
''')
 def test_item_child_helper_timing_scale_and_calibrated_active_animation_are_preserved(self):
  p=RP/'animations/java_eating_projection.animation.json';assert_public_bytes(self,p)
  changed=subprocess.check_output(['git','diff','--name-only',PUBLIC_SOURCE_BASE,'--',str((RP/'animations').relative_to(ROOT))],cwd=ROOT,text=True).splitlines()
  # New station-only files do not replace or loosen the byte equality of any
  # pre-existing eating/helper clip. Each exception must be absent at the
  # public calibration baseline and own exactly its one station clip key.
  station_clips={
   'rack_tool_visual.animation.json':'animation.kg_station.rack_tool',
   'plate_food_visual.animation.json':'animation.kg_station.plate_food',
  }
  allowed=set()
  for filename,clip in station_clips.items():
   path=RP/'animations'/filename
   if not path.exists():continue
   relative=str(path.relative_to(ROOT));allowed.add(relative)
   old=subprocess.run(['git','cat-file','-e',PUBLIC_SOURCE_BASE+':'+relative],cwd=ROOT,capture_output=True)
   self.assertNotEqual(old.returncode,0,'station exception must only admit a new file')
   self.assertEqual(set(json.loads(path.read_text())['animations']),{clip})
  version=tuple(json.loads((ROOT/'baseline.json').read_text())['version'])
  if version >= (2,8,90):
   # This additional held-only clip must be new and exactly source-admitted;
   # all existing eating/helper byte guards above remain unchanged.
   path=RP/'animations/plate_held.animation.json';relative=path.relative_to(ROOT).as_posix()
   old=subprocess.run(['git','cat-file','-e',PUBLIC_SOURCE_BASE+':'+relative],cwd=ROOT,capture_output=True)
   self.assertNotEqual(old.returncode,0)
   if version >= (2,8,91):
    from g91_source_conservation import expected_runtime_bytes
   else:
    from g90_source_conservation import expected_runtime_bytes
   self.assertEqual(path.read_bytes(),expected_runtime_bytes(relative))
   self.assertEqual(set(json.loads(path.read_text())['animations']),{f'animation.kg_plate_held.{key}' for key in ('fp_right','fp_left','tp_right','tp_left','layout')})
   allowed.add(relative)
  self.assertEqual(set(changed)-allowed,set())
if __name__=='__main__':unittest.main()
