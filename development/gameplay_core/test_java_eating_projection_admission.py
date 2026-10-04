"""Exact native item/profile/renderer admission; no rendered-client claim."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import build_java_eating_projection as generator
from test_eating_observer_projection import node


class ProjectionAdmission(unittest.TestCase):
    def test_canonical_random_and_dynamic_secret_do_not_borrow_alt_renderer(self):
        items=generator.projection_items()
        self.assertTrue(items['THREE_ALT'])
        self.assertTrue(all(identifier.endswith(generator.ALT_SUFFIX) for identifier in items['THREE_ALT']))
        self.assertEqual(items['ONE'],['kaleidoscope_grilling:grilled_fish_skewer'])
        self.assertEqual(items['THREE'],['kaleidoscope_grilling:grilled_ender_pearl_skewer'])
        admitted={identifier for rows in items.values() for identifier in rows}
        for identifier in ('kaleidoscope_grilling:grilled_gluten_skewer',
                           'kaleidoscope_grilling:secret_skewer',
                           'kaleidoscope_grilling:secret_skewer_java_three_alt'):
            self.assertNotIn(identifier,admitted)

    def test_an_actual_alt_with_another_food_geometry_is_rejected(self):
        path=generator.RP/'attachables/grilled_gluten_skewer_java_three_alt.attachable.json'
        wrong=json.loads(path.read_text())
        desc=wrong['minecraft:attachable']['description']
        self.assertTrue(generator.fixed_geometry(desc))
        desc['geometry']['stage0']='geometry.kg_a287.kg_a22.raw_gluten_skewer.stage0'
        self.assertFalse(generator.fixed_geometry(desc))
        self.assertNotIn(desc['identifier'],generator.projection_items({path:wrong})['THREE_ALT'])
        wrong=copy.deepcopy(wrong);wrong['minecraft:attachable']['description']['geometry']={}
        self.assertNotIn(desc['identifier'],generator.projection_items({path:wrong})['THREE_ALT'])

    def test_wrong_native_duration_fails_closed_for_actual_alt(self):
        identifier=generator.projection_items()['THREE_ALT'][0]
        path=generator.BP/'items'/(identifier.split(':')[1]+'.json')
        wrong=json.loads(path.read_text())
        wrong['minecraft:item']['components']['minecraft:use_modifiers']['use_duration']=5.0
        self.assertNotIn(identifier,generator.projection_items({path:wrong})['THREE_ALT'])

    def test_generated_script_player_and_attachable_admit_the_same_actual_identity(self):
        items=generator.projection_items()
        descriptions=[]
        for profile,identifiers in items.items():
            for identifier in identifiers:
                path=generator.RP/'attachables'/(identifier.split(':')[1]+'.attachable.json')
                desc=json.loads(path.read_text())['minecraft:attachable']['description']
                descriptions.append({'id':identifier,'profile':profile,'description':desc})
        players=json.loads((generator.RP/'animations/java_eating_player.animation.json').read_text())['animations']
        module=generator.BP/'scripts/java_eating_projection_items.js'
        node('import {supportsJavaEatingProjection} from '+json.dumps(module.as_uri())+';'+'''
const rows='''+json.dumps(descriptions)+''',players='''+json.dumps(players)+''';
for(const {id,profile,description:d} of rows)for(const hand of ['right','left']){
 let held=id,p={eat_projection:1,eat_profile:{ONE:1,TWO:2,THREE:3,THREE_ALT:4,FOUR:5}[profile],eat_hand:hand==='right'?1:2};
 const slot=hand==='right'?'slot.weapon.mainhand':'slot.weapon.offhand';
 const q={is_using_item:true,is_sneaking:0,is_swimming:0,is_gliding:0,is_riding:0,is_item_equipped:()=>0,
 property:name=>p[name.split(':')[1]],is_item_name_any:(s,...ids)=>s===slot&&ids.includes(held)};
 const c={is_first_person:1,item_slot:hand==='right'?'main_hand':'off_hand'},variable={is_first_person:1};
 const item=d.scripts.animate.find(row=>row['fp_eat_'+hand])['fp_eat_'+hand];
 const player=players['animation.kg_java_eating.player.'+profile.toLowerCase()+'.'+hand].blend_weight;
 const active=expression=>Boolean(new Function('q','c','variable','return '+expression)(q,c,variable));
 if(!supportsJavaEatingProjection(id,profile)||!active(item)||!active(player))throw Error('Actual renderer missing '+id);
 for(const other of ['minecraft:apple','kaleidoscope_grilling:secret_skewer_java_three_alt',id.replace('_java_three_alt','')]){
  if(other===id)continue;held=other;
  if(active(item)||active(player))throw Error('Actual identity gate leaked '+id+' -> '+other);
 }
 const peer=rows.find(row=>row.profile===profile&&row.id!==id);
 if(peer){held=peer.id;if(active(item))throw Error('Attachable borrowed another actual item');if(!active(player))throw Error('Player lost another admitted same-profile item');}
 held=id;p.eat_profile=0;if(active(item)||active(player))throw Error('Stale profile leaked');
}
for(const id of ['kaleidoscope_grilling:grilled_gluten_skewer','kaleidoscope_grilling:secret_skewer_java_three_alt'])
 for(const profile of ['ONE','TWO','THREE','THREE_ALT','FOUR'])if(supportsJavaEatingProjection(id,profile))throw Error('Missing exact renderer admitted');
''')

    def test_canonical_random_legacy_hold_and_hidden_alt_clock_are_both_preserved(self):
        from native_eating_clock import ASSIGNMENT
        for name in ('grilled_gluten_skewer','ordinary_skewer'):
            canonical=json.loads((generator.RP/'attachables'/(name+'.attachable.json')).read_text())['minecraft:attachable']['description']
            alt=json.loads((generator.RP/'attachables'/(name+generator.ALT_SUFFIX+'.attachable.json')).read_text())['minecraft:attachable']['description']
            self.assertFalse(any(key.startswith('fp_eat_') for key in canonical['animations']))
            self.assertEqual(canonical['geometry'],alt['geometry'])
            self.assertEqual(canonical['textures'],alt['textures'])
            self.assertEqual(alt['scripts']['pre_animation'][0],ASSIGNMENT)
            self.assertNotIn('q.item_in_use_duration',' '.join(alt['scripts']['pre_animation']))
            for hand,slot in [('right','main_hand'),('left','off_hand')]:
                row=next(row for row in canonical['scripts']['animate'] if 'fp_'+hand in row)
                self.assertEqual(row['fp_'+hand],"c.is_first_person == 1 && c.item_slot == '"+slot+"'")
                self.assertEqual(alt['animations']['fp_eat_'+hand],generator.item_animation_id('THREE_ALT',hand))


if __name__=='__main__':unittest.main()
