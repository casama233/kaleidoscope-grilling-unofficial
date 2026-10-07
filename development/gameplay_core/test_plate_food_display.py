"""Plate-only ordinary mesh conservation and calibrated facing math."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_plate_food_display import build,ordinary_world_geometry,BP,RP,NS,PLATE_CONTROLLER,ORDINARY_GEOMETRY
from plate_facing_oracle import runtime_poses,JAVA_LAYOUTS,shaft_errors

def read(path):return json.loads(path.read_text())

class PlateFoodDisplay(unittest.TestCase):
 def test_checked_in_assets_are_exact_generator_output(self):
  for path,data in build().items():self.assertEqual(path.read_bytes(),data,str(path))

 def test_ordinary_preserves_every_cube_uv_rotation_and_parent(self):
  source=read(RP/'models/entity/a22_bites/ordinary_skewer_stage0.geo.json')['minecraft:geometry'][0]
  actual=ordinary_world_geometry();self.assertEqual(actual['description']['identifier'],ORDINARY_GEOMETRY)
  original={b['name']:b for b in source['bones']if b['name']!='display'}
  self.assertEqual(len(actual['bones']),len(original));self.assertEqual(sum(len(b.get('cubes',[]))for b in actual['bones']),19)
  for bone in actual['bones']:
   before=deepcopy(original[bone['name']]);before.pop('binding',None)
   self.assertNotIn('binding',bone)
   if bone['name']!='root':
    if before.get('parent')=='display':before['parent']='root'
    if 'pivot'in before:before['pivot'][1]-=1
    for cube in before.get('cubes',[]):
     cube['origin'][1]-=1
     if 'pivot'in cube:cube['pivot'][1]-=1
   self.assertEqual(bone,before,bone['name'])

 def test_model115_is_plate_only_and_has_no_held_eating_properties(self):
  server=read(BP/'entities/plate_food_visual.json')['minecraft:entity'];client=read(RP/'entity/plate_food_visual.entity.json')['minecraft:client_entity']['description']
  props=server['description']['properties'];self.assertEqual(props[NS+'model']['range'],[0,115])
  self.assertEqual(set(props),{NS+k for k in ['ready','model','secret_0','secret_1','secret_2']})
  self.assertNotIn('minecraft:inventory',server['components']);self.assertNotIn('enable_attachables',client)
  self.assertEqual(client['geometry']['s115'],ORDINARY_GEOMETRY);self.assertEqual(client['textures']['s115'],'textures/a22_bites/ordinary_skewer_stage0')
  self.assertNotIn('eat_',json.dumps(client['scripts']));self.assertNotIn('item_slot',json.dumps(client['scripts']))
  self.assertEqual(read(BP/'entities/grill_food_visual.json')['minecraft:entity']['description']['properties'][NS+'model']['range'],[0,114])
  grill=read(RP/'render_controllers/grill_food_visual.render_controllers.json')['render_controllers']['controller.render.kg_station.grill']
  plate=read(RP/'render_controllers/plate_food_visual.render_controllers.json')['render_controllers'][PLATE_CONTROLLER]
  for group,key,alias in [('geometries','Array.models','Geometry.s115'),('textures','Array.stages','Texture.s115')]:
   self.assertEqual(plate['arrays'][group][key],grill['arrays'][group][key]+[alias])
  self.assertEqual(client['render_controllers'][0],{PLATE_CONTROLLER:"q.property('kaleidoscope_grilling:ready')"})

 def test_production_pose_matches_independent_calibrated_mesh_corner_oracle(self):
  poses=runtime_poses();self.assertEqual(poses['layouts'],JAVA_LAYOUTS)
  fixed=read(ROOT/'projects/grilling/reports/java_display_transforms/beef_raw.json')['java_display']['fixed']
  ordinary_fixed=read(ROOT/'projects/grilling/reports/java_display_transforms/ordinary_full.json')['java_display']['fixed'];self.assertEqual(ordinary_fixed,fixed)
  geos=read(RP/'models/entity/grill_display.geo.json')['minecraft:geometry']
  beef=next(g for g in geos if g['description']['identifier'].endswith('.raw_beef_skewer'))
  clip=read(RP/'animations/plate_food_visual.animation.json')['animations']['animation.kg_station.plate_food']['bones']['root']
  self.assertEqual(clip['position'],[0,"q.property('kaleidoscope_grilling:model') == 114 ? -1.8 : -0.6",1.8])
  static_clip={'scale':clip['scale'],'position':[0,-.6,clip['position'][2]]}
  for geo in [beef,ordinary_world_geometry()]:
   errors=shaft_errors(geo,fixed,poses['rows'],static_clip);self.assertEqual(len(errors),480);self.assertLess(max(errors),1e-8)
  secret=next(g for g in geos if g['description']['identifier'].endswith('.secret_stick'))
  errors=shaft_errors(secret,fixed,poses['rows'],{'scale':clip['scale'],'position':[0,-1.8,clip['position'][2]]},mesh_y_shift=0)
  self.assertEqual(len(errors),480);self.assertLess(max(errors),1e-8)
  old=shaft_errors(beef,fixed,poses['rows'],static_clip,yaw_override=lambda F,t:t-F)
  wrong_sign=shaft_errors(beef,fixed,poses['rows'],static_clip,yaw_override=lambda F,t:180+F+t)
  self.assertGreater(max(old),15);self.assertGreater(max(wrong_sign),11)

if __name__=='__main__':unittest.main()
