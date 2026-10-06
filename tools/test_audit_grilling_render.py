"""Mutation guards for exact threaded G68+ audit contracts; static evidence only."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('render_audit',ROOT/'tools/audit_grilling_render.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
class ThreadedAuditContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.geometries=audit.collect_geometries([]);cls.animations=audit.collect_animations()
 def check(self,change=None,geometry=None,animation=None,version=None,food=False,bottle=None):
  loader=audit.load_json
  def modified(path):
   d=loader(path)
   if path.name=='secret_skewer.attachable.json' and change:change(d['minecraft:attachable']['description'])
   if path.name=='pending_seasoning_f8.attachable.json' and bottle:bottle(d['minecraft:attachable']['description'])
   if path.name=='manifest.json' and path.parent==audit.BP and version:d['header']['version']=version
   if path.name=='unfinished_skewer.json' and food:d['minecraft:item']['components']['minecraft:food']={'nutrition':1,'saturation_modifier':.1}
   return d
  geos=deepcopy(self.geometries);anims=deepcopy(self.animations)
  if geometry:geometry(geos)
  if animation:animation(anims)
  findings=[]
  with patch.object(audit,'load_json',modified):audit.check_current_display_contracts(findings,geos,anims)
  return {r['code']for r in findings if r['severity']=='error'}
 def test_current(self):self.assertEqual(self.check(),set())
 def test_unknown_fill_id_cannot_replace_an_expected_proxy_at_same_count(self):
  self.assertIn('held_inventory_contract',self.check(bottle=lambda d:d.update(identifier='kaleidoscope_grilling:pending_seasoning_f9')))
 def test_wrong_helper_hand(self):
  def mutate(geos):geos['geometry.kg_secret_held.piece_1']['geo']['bones'][0]['binding']='q.item_slot_to_bone_name(context.item_slot)'
  self.assertIn('held_binding_contract',self.check(geometry=mutate))
 def test_missing_idle_calibration(self):
  self.assertIn('held_pose_selectors',self.check(change=lambda d:d['animations'].pop('fp_idle_calibrated_right')))
 def test_wrong_idle_hand_selector(self):
  def mutate(d):
   for row in d['scripts']['animate']:
    if 'fp_idle_calibrated_right' in row:row['fp_idle_calibrated_right']=row['fp_idle_calibrated_right'].replace("c.item_slot == 'main_hand'","c.item_slot == 'off_hand'")
  self.assertIn('held_pose_selectors',self.check(change=mutate))
 def test_drifted_calibration_clip(self):
  def mutate(anims):anims['animation.kg_secret_held.fp_idle_calibrated_1_26_52_3_right']['body']['bones']['skewer_pose']['position'][0]+=1
  self.assertIn('held_pose_frame_drift',self.check(animation=mutate))
 def test_nonsecret_helper_owner(self):
  self.assertIn('held_binding_contract',self.check(change=lambda d:d.update(identifier='kaleidoscope_grilling:raw_beef_skewer')))
 def test_unfinished_cannot_become_food(self):self.assertIn('held_partial_contract',self.check(food=True))
 def test_historical_versions_do_not_inherit_new_exemptions(self):self.assertIn('held_pose_selectors',self.check(version=[2,8,67]))
if __name__=='__main__':unittest.main()
