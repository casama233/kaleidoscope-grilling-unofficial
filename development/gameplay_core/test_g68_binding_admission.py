"""Fail-closed G68 bindings; source tests do not certify native visuals."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from verify_a287 import expression,idle_pose_alias,secret_helper_binding_gate,animation_entries,plate_binding_gate
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
def load(path):return json.loads(path.read_text())
class G68BindingAdmission(unittest.TestCase):
 def idle_dispatch(self,d):
  for first in (0,1):
   for slot,hand in [('main_hand','right'),('off_hand','left')]:
    for bone in (hand+'item',hand+'Item','custom_'+hand+'_grip'):
     matches=[key for row in d['scripts']['animate']for key,expr in row.items()if expression(expr,first,slot,bone)]
     self.assertEqual(matches,[idle_pose_alias((2,8,68),d['identifier'],first,hand)])
 def test_owned_idle_calibration_is_required_and_historical_alias_stays_unchanged(self):
  for name in ('secret_skewer','unfinished_skewer'):
   d=load(RP/f'attachables/{name}.attachable.json')['minecraft:attachable']['description'];self.idle_dispatch(d)
   broken=deepcopy(d);broken['scripts']['animate']=[r for r in broken['scripts']['animate']if not any(k.startswith('fp_idle_calibrated_')for k in r)]
   with self.assertRaises(AssertionError):self.idle_dispatch(broken)
  self.assertEqual(idle_pose_alias((2,8,67),'kaleidoscope_grilling:secret_skewer',1,'right'),'fp_right')
  self.assertEqual(idle_pose_alias((2,8,68),'kaleidoscope_grilling:beef_skewer',1,'right'),'fp_right')
 def test_helper_requires_opposite_hand_and_exact_owner(self):
  d=load(RP/'attachables/secret_skewer.attachable.json')['minecraft:attachable']['description']
  g=next(g for g in load(RP/'models/entity/secret_held.geo.json')['minecraft:geometry']if g['description']['identifier']=='geometry.kg_secret_held.piece');ref=g['description']['identifier']
  secret_helper_binding_gate('fixture',d,ref,g)
  for binding in ('q.item_slot_to_bone_name(context.item_slot)',"'rightItem'","'leftItem'"):
   broken=deepcopy(g);broken['bones'][0]['binding']=binding
   with self.assertRaises(AssertionError):secret_helper_binding_gate('fixture',d,ref,broken)
  broken=deepcopy(d);broken['identifier']='kaleidoscope_grilling:beef_skewer'
  with self.assertRaises(AssertionError):secret_helper_binding_gate('fixture',broken,ref,g)
class BindingAnimationEntries(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.description=json.loads((RP/'attachables/skewer_plate.attachable.json').read_text())['minecraft:attachable']['description']
  cls.geometries={g['description']['identifier']:g for g in json.loads((RP/'models/entity/plate_held.geo.json').read_text())['minecraft:geometry']}
  cls.animations=json.loads((RP/'animations/plate_held.animation.json').read_text())['animations']

 def test_supported_string_and_map_entries_are_not_skipped(self):
  self.assertEqual(list(animation_entries([{'fp_right':'c.is_first_person == 1'},'layout'])),[('fp_right','c.is_first_person == 1'),('layout','1')])
  for rows in [[],[''],[None],[3],[{}],[{'layout':True}],[['layout']]]:
   with self.assertRaises(AssertionError):list(animation_entries(rows))

 def dispatch(self,description):
  entries=list(animation_entries(description['scripts']['animate']))
  for first in (0,1):
   for slot,hand in [('main_hand','right'),('off_hand','left')]:
    for bone in (hand+'item',hand+'Item','custom_'+hand+'_grip'):
     for using in (False,True):
      matches=[key for key,condition in entries if expression(condition,first,slot,bone,using)]
      self.assertEqual(matches,[('fp_' if first else 'tp_')+hand,'layout'])

 def test_unconditional_layout_retains_all_camera_slot_and_bone_checks(self):
  self.dispatch(self.description)
  broken=deepcopy(self.description);broken['scripts']['animate'][0]['fp_right']="c.is_first_person == 1 && c.item_slot == 'off_hand'"
  with self.assertRaises(AssertionError):self.dispatch(broken)
  broken=deepcopy(self.description);broken['scripts']['animate'].remove('layout')
  with self.assertRaises(AssertionError):self.dispatch(broken)
  with self.assertRaises(AssertionError):expression('c.unrecognized_owner == 1',1,'main_hand','rightitem')

 def test_plate_geometry_and_animation_hierarchy_remain_strict(self):
  refs=['geometry.kg_plate_held.body','geometry.kg_plate_held.empty_0']
  for ref in refs:plate_binding_gate('fixture',self.description,ref,self.geometries[ref],self.animations)
  ref=refs[1];original=self.geometries[ref]
  mutations=[lambda g:g['bones'][0].update(binding="'rightItem'"),
             lambda g:g['bones'][0].update(parent='plate_pose'),
             lambda g:g['bones'][1].update(binding='q.item_slot_to_bone_name(context.item_slot)'),
             lambda g:g['bones'][3].update(parent='plate_pose'),
             lambda g:g['bones'][4].update(pivot=[0,0,0])]
  for mutate in mutations:
   broken=deepcopy(original);mutate(broken)
   with self.assertRaises(AssertionError):plate_binding_gate('fixture',self.description,ref,broken,self.animations)
  animations=deepcopy(self.animations);animations['animation.kg_plate_held.layout']['bones'].pop('plate_fixed_4')
  with self.assertRaises(AssertionError):plate_binding_gate('fixture',self.description,ref,original,animations)


if __name__=='__main__':unittest.main()
