"""Partial-source state selection/owner gates; native pixels remain separate."""
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'projects/grilling/gameplay_core/resource_pack';sys.path.insert(0,str(ROOT/'tools'))
from secret_skewer_assets import model,pinned,ASSET,PARTIAL_STATES,partial_geometries
from test_eating_observer_projection import node
class PartialSkewerHeld(unittest.TestCase):
 def test_original_unfinished_display_and_shaft_match_existing_secret(self):
  partial=json.loads(pinned(ASSET+'models/item/unfinished_skewer.json'));secret=json.loads(pinned(ASSET+'models/item/secret_skewer.json'))
  self.assertEqual(partial['display'],secret['display']);self.assertEqual(partial['elements'],secret['elements'])
  self.assertEqual(len(partial_geometries()),21)
 def test_partial_attachable_has_no_eating_or_raw_helper(self):
  d=json.loads((RP/'attachables/unfinished_skewer.attachable.json').read_text())['minecraft:attachable']['description']
  self.assertEqual(set(d['animations']),{'fp_right','fp_left','tp_right','tp_left','fp_idle_calibrated_right','fp_idle_calibrated_left'})
  self.assertNotIn('java_secret_piece',d['geometry']);self.assertNotIn('controller.render.kg_secret_held.piece',d['render_controllers'])
  self.assertEqual(len(d['render_controllers']),3)
  self.assertFalse(any(k.startswith(('eat_','fp_eat_'))for k in d['animations']));self.assertNotIn('v.kg_secret_piece_',json.dumps(d))
 def test_zero_one_two_counts_select_exact_joint_states_in_both_hands(self):
  d=json.loads((RP/'attachables/unfinished_skewer.attachable.json').read_text())['minecraft:attachable']['description']
  controllers=json.loads((RP/'render_controllers/secret_held.render_controllers.json').read_text())['render_controllers']
  node('const d='+json.dumps(d)+';const controllers='+json.dumps(controllers)+r''';
for(const hand of ['main_hand','off_hand'])for(const count of [0,1,2])for(let a=1;a<=3;a++)for(let b=1;b<=3;b++){
 let held=d.identifier;const encoded=[count?174+256*(a-1+3*count):0,count===2?180+256*(b-1+3*count):0,0];
 const owner={has_property:()=>true,property:n=>encoded[Number(n.slice(-1))]??0,
 is_item_name_any:(slot,...ids)=>slot===(hand==='main_hand'?'slot.weapon.mainhand':'slot.weapon.offhand')&&ids.includes(held)};
 const v={};evaluatePreAnimation(d.scripts.pre_animation,{}, {item_slot:hand,owning_entity:owner},{clamp:(n,a,b)=>Math.max(a,Math.min(b,n)),max:Math.max},v);
 const state=count===0?0:a*16+(count===2?b*4:0);if(v.kg_secret_partial_state!==state||v.kg_bite_stage!==0)throw Error('Partial count/state mismatch');
 for(const slot of [0,1]){
 const row=controllers['controller.render.kg_partial_held.'+slot],geometry=row.arrays.geometries['Array.states'][encoded[slot]===0?0:state];
 const expected=slot<count?'Geometry.partial_state_'+state+'_'+slot:'Geometry.part_'+slot+'_0';if(geometry!==expected)throw Error('Wrong exact partial geometry');
 if(row.textures[0]!=='Array.food[v.kg_secret_food_'+slot+']')throw Error('Partial got cooking glaze');
 }
 held='minecraft:stick';evaluatePreAnimation(d.scripts.pre_animation,{}, {item_slot:hand,owning_entity:owner},{clamp:(n,a,b)=>Math.max(a,Math.min(b,n)),max:Math.max},v);
 if(v.kg_secret_owner_occupied)throw Error('Partial owner predicate leaked to ordinary stick');
}
''')
if __name__=='__main__':unittest.main()
