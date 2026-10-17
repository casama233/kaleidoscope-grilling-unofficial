"""Fail-closed G68 bindings; source tests do not certify native visuals."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from verify_a287 import expression,idle_pose_alias,secret_helper_binding_gate
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
if __name__=='__main__':unittest.main()
