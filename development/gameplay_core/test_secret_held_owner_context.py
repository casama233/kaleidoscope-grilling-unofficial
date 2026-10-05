"""Pinned mesh and owner dispatch regressions, separate from engine acceptance."""
from pathlib import Path
import json,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'projects/grilling/gameplay_core/resource_pack';BP=ROOT/'projects/grilling/gameplay_core/behavior_pack'
sys.path.insert(0,str(ROOT/'tools'))
from secret_idle_calibration import apply_idle_calibration
from secret_terminal_visibility import STAGE as TERMINAL_STAGE
from secret_skewer_assets import held_geometries,partial_geometries,slot_cubes,shaft_cubes,ATLAS_WIDTH,ATLAS_HEIGHT
BASE='4bacfc5d549ecf101b7478a0aaa40e789e4f9939'
def load(p):return json.loads(p.read_text())
def old(p):return json.loads(subprocess.check_output(['git','show',BASE+':'+str(p.relative_to(ROOT))],cwd=ROOT))
class SecretHeldOwnerContextTests(unittest.TestCase):
 def test_exact_nine_source_volumes_and_shaft_are_preserved(self):
  doc=load(RP/'models/entity/secret_held.geo.json');self.assertEqual(doc,{'format_version':'1.21.0','minecraft:geometry':held_geometries()+partial_geometries()})
  self.assertEqual([[len(slot_cubes(slot,shape))for slot in range(3)]for shape in range(1,4)],[[12,18,18],[18,18,18],[12,24,26]])
  self.assertEqual(shaft_cubes(True)[0]['size'],[.5,.5,12.5]);self.assertEqual(len(doc['minecraft:geometry']),107)
 def test_owner_properties_decode_locally_and_player_count_does_not_expand(self):
  props=load(BP/'entities/player.json')['minecraft:entity']['description']['properties'];self.assertEqual(len(props),32)
  for name in ('secret_skewer','secret_skewer_java_three_alt'):
   d=load(RP/f'attachables/{name}.attachable.json')['minecraft:attachable']['description'];scripts=d['scripts'];reads=[s for s in scripts['pre_animation']if s.startswith('v.kg_secret_')]
   self.assertEqual(reads[0],"v.kg_secret_off_hand = c.item_slot == 'off_hand';");self.assertEqual(len(reads),34)
   for i in range(3):
    statement=next(s for s in reads if s.startswith(f'v.kg_secret_ingredient_{i} = '));self.assertIn('c.owning_entity->q.has_property',statement);self.assertIn(', 0, 5333)',statement)
    for hand in ('main','off'):self.assertEqual(props[f'kaleidoscope_grilling:secret_{hand}_{i}']['range'],[0,5333])
   self.assertEqual(props['kaleidoscope_grilling:secret_main_piece']['range'],[0,255])
 def test_passes_are_owned_and_slots_choose_real_shapes_and_palette_stages(self):
  controllers=load(RP/'render_controllers/secret_held.render_controllers.json')['render_controllers'];self.assertNotIn('q.property',json.dumps(controllers));self.assertNotIn('c.item_slot',json.dumps(controllers))
  for i in range(3):
   row=controllers[f'controller.render.kg_secret_held.{i}'];self.assertEqual(row['geometry'],f'Array.states[v.kg_secret_food_{i} == 0 ? 0 : v.kg_secret_state]')
   self.assertEqual(len(row['arrays']['geometries']['Array.states']),64);self.assertEqual(len(row['arrays']['textures']['Array.food']),214*7)
   self.assertEqual(row['part_visibility'],[{'*':0},{'skewer_model':f'v.kg_secret_owner_occupied == 1 && v.kg_bite_stage < {3-i}'}])
  self.assertEqual(controllers['controller.render.kg_secret_held.piece']['textures'],['Array.food[v.kg_secret_piece_index]'])
 def test_animations_socket_helper_and_nonsecret_owner_dispatch_are_unchanged(self):
  for name in ('secret_skewer','secret_skewer_java_three_alt'):
   path=RP/f'attachables/{name}.attachable.json';actual=load(path)['minecraft:attachable']['description'];before=apply_idle_calibration(old(path)['minecraft:attachable']['description'])
   for field in ('identifier','materials','animations'):self.assertEqual(actual[field],before[field])
   self.assertEqual(actual['scripts']['animate'],before['scripts']['animate'])
   self.assertEqual([s for s in actual['scripts']['pre_animation']if not s.startswith('v.kg_secret_') and s!=TERMINAL_STAGE],[s for s in before['scripts']['pre_animation']if not s.startswith('v.kg_secret_')])
   self.assertEqual({k:v for k,v in actual['textures'].items()if k.startswith('food_')and '_s'not in k},{k:v for k,v in before['textures'].items()if k.startswith('food_')})
   self.assertEqual(actual['textures']['stick'],'textures/secret_skewer_stick')
if __name__=='__main__':unittest.main()
