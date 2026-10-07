"""G92 default-off source probe and real generated-expression harness.

This is not Bedrock Molang/native-client acceptance. The fixture-only QA pass
isolates client property/decode observations from constant mesh/palette routing.
Numeric log sample order is canary, hand, raw0, floor0, raw5, raw7, count,
desc0, shape0, style0, food0/1/2. No player identity is queried or emitted.
"""
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'development/gameplay_core')]
import build_plate_held as held
from test_eating_observer_projection import node


def load(relative):
    return json.loads((held.RP / relative).read_text())


class PlateClientProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.attach = load('attachables/skewer_plate.attachable.json')['minecraft:attachable']['description']
        cls.controllers = load('render_controllers/plate_held.render_controllers.json')['render_controllers']
        cls.qa = load('models/entity/plate_held_qa.geo.json')['minecraft:geometry'][0]

    def harness(self, source):
        node('const d=' + json.dumps(self.attach) + '; const rc=' + json.dumps(self.controllers) + r''';
const fixture=[8285209,0,0,0,1,57,0,133];
const other=[9+4*214+7*45796,0,0,0,0,57,0,133];
const math={clamp:(n,a,b)=>Math.max(a,Math.min(b,n)),max:Math.max};
function instance(hand='main_hand',word=fixture,options={}){
 const state={main:[...(hand==='main_hand'?word:other)],off:[...(hand==='off_hand'?word:other)],
  mainItem:d.identifier,offItem:d.identifier,...options};
 const owner={has_property:n=>/^kaleidoscope_grilling:bottle_(main|off)_[0-7]$/.test(n),
  property:n=>state[n.includes(':bottle_off_')?'off':'main'][Number(n.slice(-1))],
  is_item_name_any:(slot,...names)=>names.includes(slot==='slot.weapon.offhand'?state.offItem:state.mainItem)};
 const logs=[],v={},c={item_slot:hand,owning_entity:owner};
 const q={life_time:0,delta_time:0,property:()=>{throw Error('Attachable-local property query');},
  log:n=>{if(typeof n!=='number'||!Number.isFinite(n))throw Error('Non-numeric probe log');logs.push(n);return 0;}};
 evaluatePreAnimation(d.scripts.initialize,q,c,math,v);
 const update=(time,delta=0)=>{q.life_time=time;q.delta_time=delta;evaluatePreAnimation(d.scripts.pre_animation,q,c,math,v);};
 const visible=name=>Object.fromEntries(rc['controller.render.kg_plate_held.'+name].part_visibility
  .flatMap(row=>Object.entries(row)).map(([bone,expr])=>[bone,Boolean(new Function('v','return '+expr)(v))]));
 return {state,logs,v,c,q,update,visible};
}
function assert(condition,message){if(!condition)throw Error(message);}
''' + source)

    def test_source_outputs_keep_probe_geometry_separate_and_primary_unchanged(self):
        output = held.build()
        self.assertEqual(len(output), 5)
        for path, data in output.items():
            self.assertTrue(path.is_relative_to(held.RP))
            self.assertEqual(path.read_bytes(), data, str(path))
        primary = load('models/entity/plate_held.geo.json')['minecraft:geometry']
        self.assertEqual(len(primary), 526)
        self.assertFalse(any(g['description']['identifier'].endswith('.qa_probe') for g in primary))
        self.assertEqual(self.attach['geometry']['qa_probe'], 'geometry.kg_plate_held.qa_probe')
        self.assertEqual(load('animations/plate_held.animation.json'), held.animations())
        self.assertEqual(len(self.controllers), 33)
        production = {key: value for key, value in self.controllers.items()
            if not key.startswith('controller.render.kg_plate_held.qa_')}
        self.assertEqual(len(production), 31)
        self.assertNotIn('kg_plate_qa_', json.dumps(production))

    def test_raw_reads_are_independent_owner_scalars_without_floor(self):
        scripts = self.attach['scripts']
        for word in (0, 5, 7):
            raw = f'v.kg_plate_qa_raw_word_{word}'
            self.assertIn(raw + ' = 0;', scripts['initialize'])
            read, = [row for row in scripts['pre_animation'] if row.startswith(raw + ' = ')]
            self.assertNotIn('math.floor', read)
            self.assertNotIn(f'v.kg_plate_word_{word}', read)
            for hand in ('main', 'off'):
                self.assertIn(held.property_read(hand, word), read)
        text = '\n'.join(scripts['pre_animation'])
        self.assertNotIn('q.get_name', text)
        self.assertNotIn('q.get_id', text)
        self.assertNotIn('q.position', text)
        self.assertNotIn('kg_plate_owner_occupied', next(row for row in scripts['pre_animation']
            if row.startswith('v.kg_plate_qa_enabled = ')))

    def test_four_posts_reuse_body_material_texture_and_original_socket(self):
        self.assertEqual(self.qa['description']['texture_width'], 16)
        self.assertEqual(self.qa['description']['texture_height'], 16)
        self.assertEqual(self.qa['bones'][0], {'name': 'grip', 'pivot': [0, 24, 0], 'binding': held.BINDING})
        self.assertEqual(self.qa['bones'][1], {'name': 'plate_pose', 'parent': 'grip', 'pivot': [0, 24, 0]})
        posts = self.qa['bones'][2:]
        self.assertEqual([post['name'] for post in posts], list(held.QA_POST_TESTS))
        self.assertEqual([post['cubes'][0]['size'] for post in posts], [[1, n, 1] for n in (1, 2, 3, 4)])
        self.assertEqual(len({tuple(post['cubes'][0]['origin']) for post in posts}), 4)
        for post in posts:
            self.assertEqual(post['parent'], 'plate_pose')
            self.assertEqual(post['pivot'], [0, 24, 0])
            self.assertEqual(len(post['cubes']), 1)
            self.assertEqual(post['cubes'][0]['origin'][1], 26)
        controller = self.controllers['controller.render.kg_plate_held.qa_probe']
        self.assertEqual(controller['geometry'], 'Geometry.qa_probe')
        self.assertEqual(controller['textures'], ['Texture.body'])
        self.assertEqual(controller['materials'], [{'*': 'Material.default'}])
        self.assertEqual(controller['part_visibility'][0], {'*': 0})
        for row in controller['part_visibility'][1:]:
            bone, expression = next(iter(row.items()))
            self.assertEqual(expression, 'v.kg_plate_qa_enabled == 1 && (' + held.QA_POST_TESTS[bone] + ')')

    def test_forced_state53_golden_apple_uses_constant_existing_aliases(self):
        self.assertEqual(held.COMPLETE_STATES[18], 53)
        controller = self.controllers['controller.render.kg_plate_held.qa_forced_food']
        self.assertEqual(controller, {'geometry': 'Geometry.secret_0_18_1',
            'materials': [{'*': 'Material.default'}], 'textures': ['Texture.food_195_s0'],
            'part_visibility': [{'*': 0}, {'plate_row_0': 'v.kg_plate_qa_enabled == 1'}]})
        self.assertIn('secret_0_18_1', self.attach['geometry'])
        self.assertIn('food_195_s0', self.attach['textures'])
        self.assertNotIn('arrays', controller)
        self.assertNotIn('Array.', json.dumps(controller))

    def test_qa_is_default_off_and_requires_flag_count_and_raw_plate_occupancy(self):
        self.harness(r'''
for(const hand of ['main_hand','off_hand']){
 const fresh=instance(hand);assert(fresh.v.kg_plate_qa_enabled===0,'QA not initialized off');
 for(const flag of [0,2]){
  const w=[...fixture];w[4]=flag;const i=instance(hand,w);i.update(0);
  assert(!i.v.kg_plate_qa_enabled&&i.logs.length===0,'Dormant flag logged');
  assert(!Object.values(i.visible('qa_probe')).some(Boolean)&&!i.visible('qa_forced_food').plate_row_0,'Dormant flag drew QA');
 }
 for(const count of [0,2,5]){
  const w=[...fixture];w[7]=10+count*123;const i=instance(hand,w);i.update(0);
  assert(!i.v.kg_plate_qa_enabled&&i.logs.length===0,'Other count admitted');
 }
 const key=hand==='main_hand'?'mainItem':'offItem';
 const stale=instance(hand,fixture,{[key]:'minecraft:stick'});stale.update(0);
 assert(!stale.v.kg_plate_qa_enabled&&stale.logs.length===0,'Stale hand owner admitted');
 const absent=instance(hand);delete absent.c.owning_entity;absent.update(0);
 assert(!absent.v.kg_plate_qa_enabled&&absent.logs.length===0,'Absent owner admitted');
 const unknown=instance(hand);unknown.c.item_slot='inventory';unknown.update(0);
 assert(!unknown.v.kg_plate_qa_enabled&&unknown.logs.length===0,'Unknown hand admitted');
}
''')

    def test_posts_distinguish_raw_large_small_and_decoded_words_in_each_hand(self):
        self.harness(r'''
for(const hand of ['main_hand','off_hand']){
 const good=instance(hand);good.update(0);
 for(const name of ['qa_a_flag','qa_b_large_word','qa_c_small_words','qa_d_decoded'])assert(good.visible('qa_probe')[name],'Fixture post missing '+name);
 assert(good.visible('qa_forced_food').plate_row_0,'Constant pass disabled');
 const corrupt=[...fixture];corrupt[0]=-1;const large=instance(hand,corrupt);large.update(0);
 assert(!large.v.kg_plate_owner_occupied&&large.v.kg_plate_qa_enabled,'QA borrowed production payload validity');
 const p=large.visible('qa_probe');assert(p.qa_a_flag&&!p.qa_b_large_word&&p.qa_c_small_words&&!p.qa_d_decoded,'Large-word isolation wrong');
 assert(large.visible('qa_forced_food').plate_row_0,'Constant pass borrowed decoded validity');
 const fraction=[...fixture];fraction[0]+=.75;const raw=instance(hand,fraction);raw.update(0);
 assert(raw.v.kg_plate_qa_raw_word_0===8285209.75&&raw.v.kg_plate_word_0===8285209,'Raw scalar was floored');
 assert(!raw.visible('qa_probe').qa_b_large_word&&raw.visible('qa_probe').qa_d_decoded,'Raw and floor observations collapsed');
 const small=[...fixture];small[5]=58;const descriptor=instance(hand,small);descriptor.update(0);
 const s=descriptor.visible('qa_probe');assert(s.qa_a_flag&&s.qa_b_large_word&&!s.qa_c_small_words&&!s.qa_d_decoded,'Small/decode isolation wrong');
}
''')

    def test_generated_numeric_log_samples_are_three_maximum_at_one_second_spacing(self):
        calls = [row for row in self.attach['scripts']['pre_animation'] if 'q.log(' in row]
        self.assertEqual(calls, [f'v.kg_plate_qa_sample_due ? q.log({value}) : 0;'
            for value in (str(held.QA_LOG_CANARY), *held.QA_LOG_FIELDS)])
        self.assertEqual(held.QA_LOG_SAMPLES, 3)
        self.harness(r'''
for(const hand of ['main_hand','off_hand'])for(const lifeSupported of [true,false]){
 const i=instance(hand),sampleTimes=[],update=i.update;
 let before=0;
 for(const time of [0,.25,.5,.75,1,1.25,1.5,1.75,2,2.25,3,10,100]){
  update(lifeSupported?time:0,time-before);before=time;
  const count=i.logs.length/13;
  if(count>sampleTimes.length)sampleTimes.push(time);
 }
 assert(JSON.stringify(sampleTimes)==='[0,1,2]','One-second sample spacing/cap wrong '+sampleTimes);
 const expected=[914000,hand==='main_hand'?1:2,8285209,8285209,57,133,1,57,18,0,199,195,180];
 assert(i.logs.length===39&&i.v.kg_plate_qa_samples===3,'More than three numeric groups');
 for(let sample=0;sample<3;sample++)assert(JSON.stringify(i.logs.slice(sample*13,(sample+1)*13))===JSON.stringify(expected),'Numeric group/hand order wrong');
 // Disable/re-enable, re-entrant frames and a reset life clock cannot reset
 // the per-attachable cap. A new attachable initialization gets its own cap.
 i.state[hand==='main_hand'?'main':'off'][4]=0;i.update(200,100);
 i.state[hand==='main_hand'?'main':'off'][4]=1;i.update(201,1);i.update(0,0);i.update(1000,999);
 assert(i.logs.length===39&&i.v.kg_plate_qa_samples===3,'Flag toggle reset lifetime cap');
 const fresh=instance(hand);fresh.update(0);assert(fresh.logs.length===13&&fresh.v.kg_plate_qa_samples===1,'New attachable did not initialize');
}
// An already old entity starts with a new attachable-local sampling clock.
const old=instance();for(const time of [500,500.5,501,501.5,502,503])old.update(time,0);
assert(old.logs.length===39&&old.v.kg_plate_qa_samples===3,'Owner lifetime origin/cap wrong');
''')


if __name__ == '__main__':
    unittest.main()
