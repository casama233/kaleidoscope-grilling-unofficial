"""Default-off raw-owner source probe and generated-expression harness.

This is not Bedrock Molang/native-client acceptance. The fixture-only QA pass
isolates client property/decode observations from constant mesh/palette routing.
Numeric sample order is canary, hand, main raw0..7, off raw0..7, selected
count/desc0/shape0/style0/food0/1/2/owner occupied: 26 values, no identity.
"""
from pathlib import Path
import json
import re
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
        cls.binary = load('models/entity/plate_held_binary_qa.geo.json')['minecraft:geometry'][0]

    def harness(self, source):
        node('const d=' + json.dumps(self.attach) + '; const rc=' + json.dumps(self.controllers) + r''';
const fixture=[8285209,0,0,0,1,57,0,133];
const other=[9+4*214+7*45796,0,0,0,0,57,0,133];
const math={clamp:(n,a,b)=>Math.max(a,Math.min(b,n)),max:Math.max,floor:Math.floor};
function instance(hand='main_hand',word=fixture,options={}){
 const state={main:[...(hand!=='off_hand'?word:other)],off:[...(hand==='off_hand'?word:other)],
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
  .flatMap(row=>Object.entries(row)).map(([bone,expr])=>[bone,Boolean(new Function('v','math','return '+expr)(v,math))]));
 return {state,logs,v,c,q,update,visible};
}
function assert(condition,message){if(!condition)throw Error(message);}
''' + source)

    def test_source_outputs_keep_probe_geometry_separate_and_primary_unchanged(self):
        output = held.build()
        self.assertEqual(len(output), 6)
        for path, data in output.items():
            self.assertTrue(path.is_relative_to(held.RP))
            self.assertEqual(path.read_bytes(), data, str(path))
        primary = load('models/entity/plate_held.geo.json')['minecraft:geometry']
        self.assertEqual(len(primary), 526)
        self.assertFalse(any(g['description']['identifier'].endswith('.qa_probe') for g in primary))
        self.assertEqual(self.attach['geometry']['qa_probe'], 'geometry.kg_plate_held.qa_probe')
        self.assertEqual(load('animations/plate_held.animation.json'), held.animations())
        self.assertEqual(len(self.controllers), 34)
        production = {key: value for key, value in self.controllers.items()
            if not key.startswith('controller.render.kg_plate_held.qa_')}
        self.assertEqual(len(production), 31)
        self.assertNotIn('kg_plate_qa_', json.dumps(production))

    def test_binary_board_uses_power_of_two_bits_and_explicit_zero_one_glyphs(self):
        rows = held.qa_binary_rows()
        self.assertEqual([label for label, _ in rows], ['H', 'M', 'L', 'C', 'D', '0', '1', '2'])
        self.assertTrue(all(len(expressions) == 8 for _, expressions in rows))
        for row in (0, 1, 2, 4, 5, 6, 7):
            for expression in rows[row][1]:
                for divisor in re.findall(r'/([0-9]+)', expression):
                    value = int(divisor)
                    self.assertGreater(value, 0)
                    self.assertEqual(value & (value-1), 0)
                self.assertNotIn('/123', expression)
                self.assertNotIn('8285209', expression)
        self.assertEqual(rows[3][1][-3:], ['0', '1', '1'])
        self.assertEqual(rows[4][1][0], 'v.kg_plate_qa_raw_word_0 < 0')
        bones = {bone['name']: bone for bone in self.binary['bones']}
        self.assertEqual(len(bones), 131)
        self.assertEqual(bones['grip'], {'name': 'grip', 'pivot': [0, 24, 0], 'binding': held.BINDING})
        self.assertEqual(bones['plate_pose'], {'name': 'plate_pose', 'parent': 'grip', 'pivot': [0, 24, 0]})
        self.assertTrue(bones['qa_binary_frame']['cubes'])
        for row in range(8):
            for col in range(8):
                zero, one = [bones[f'qa_binary_{row}_{col}_{value}'] for value in (0, 1)]
                self.assertTrue(zero['cubes'])
                self.assertTrue(one['cubes'])
                self.assertNotEqual(zero['cubes'], one['cubes'])
                self.assertEqual(zero['parent'], 'plate_pose')
                self.assertEqual(one['parent'], 'plate_pose')
                for glyph in (zero, one):
                    self.assertTrue(all(cube['size'][2] == .02 for cube in glyph['cubes']))
                    self.assertTrue(all(cube['origin'][2] == -10.17 for cube in glyph['cubes']))
                    width = max(cube['origin'][0]+cube['size'][0] for cube in glyph['cubes']) - min(cube['origin'][0] for cube in glyph['cubes'])
                    self.assertAlmostEqual(width, .9)
        controller = self.controllers['controller.render.kg_plate_held.qa_binary']
        self.assertEqual(controller['geometry'], 'Geometry.qa_binary')
        self.assertEqual(controller['textures'], ['Texture.qa_binary'])
        self.assertNotIn('arrays', controller)
        self.assertNotIn('q.', json.dumps(controller))
        self.assertEqual(self.attach['textures']['qa_binary'], held.QA_BINARY_TEXTURE)
        self.assertEqual(self.attach['geometry']['qa_binary'], 'geometry.kg_plate_held.qa_binary')

    def test_binary_board_expected_fixture_grid_both_hands_and_fractional_raw(self):
        self.harness(r'''
function grid(i){
 const p=i.visible('qa_binary');assert(p.qa_binary_frame,'Binary reference frame missing');
 return Array.from({length:8},(_,row)=>Array.from({length:8},(_,col)=>{
  const zero=p['qa_binary_'+row+'_'+col+'_0'],one=p['qa_binary_'+row+'_'+col+'_1'];
  assert(zero!==one,'Missing or ambiguous zero/one cell '+row+'/'+col);return one?'1':'0';
 }).join(''));
}
const expected=['01111110','01101100','00011001','00100011','00111001','11000111','11000011','10110100'];
for(const hand of ['main_hand','off_hand']){
 const i=instance(hand);i.update(0);assert(JSON.stringify(grid(i))===JSON.stringify(expected),'Expected full binary grid wrong');
 // Shared raw QA gate activates both plate boards, but each reads its own
 // selected raw bank. The opposite bank is not replaced with fixture values.
 const cross=instance(hand,fixture,{main:[...fixture],off:[...other]});cross.update(0);
 const word=hand==='main_hand'?8285209:other[0],raw=word.toString(2).padStart(24,'0');
 assert(grid(cross).slice(0,3).join('')===raw,'Binary bank crossed hands');
 const half=[...fixture];half[0]=8285208.5;const h=instance(hand,half);h.update(0);
 assert(grid(h).slice(0,3).join('')==='011111100110110000011000','Fractional raw silently rounded upward');
 assert(grid(h)[3].slice(3,5)==='11','Fraction/half controls absent');
 const quarter=[...fixture];quarter[0]=8285208.25;const q=instance(hand,quarter);q.update(0);
 assert(grid(q)[3].slice(3,5)==='10','Fraction/half controls conflated');
 const signed=[...fixture];signed[0]=8285209-2**24;const n=instance(hand,signed);n.update(0);
 assert(grid(n).slice(0,3).join('')==='011111100110110000011001'&&grid(n)[4][0]==='1','Signed raw pattern/negative control ambiguous');
 i.v.kg_plate_count=0;assert(grid(i)[3]==='00000011','Decoded count zero suppressed binary board');
 i.v.kg_plate_owner_occupied=0;assert(grid(i)[0]===expected[0],'Production owner validity suppressed board');
}
const off=instance();off.state.main[4]=0;off.update(0);
assert(!Object.values(off.visible('qa_binary')).some(Boolean),'Default-off binary board leaked');
''')

    def test_raw_reads_are_independent_owner_scalars_without_floor(self):
        scripts = self.attach['scripts']
        for hand in ('main', 'off'):
            for word in range(8):
                raw = f'v.kg_plate_qa_raw_{hand}_word_{word}'
                self.assertIn(raw + ' = 0;', scripts['initialize'])
                read, = [row for row in scripts['pre_animation'] if row.startswith(raw + ' = ')]
                self.assertEqual(read, raw + ' = ' + held.property_read(hand, word) + ';')
                self.assertNotIn('math.floor', read)
                self.assertNotIn('c.item_slot', read)
                self.assertNotIn('v.kg_plate_word_', read)
        for word in (0, 5, 7):
            raw = f'v.kg_plate_qa_raw_word_{word}'
            self.assertIn(raw + ' = 0;', scripts['initialize'])
            read, = [row for row in scripts['pre_animation'] if row.startswith(raw + ' = ')]
            self.assertNotIn('math.floor', read)
            self.assertNotIn(f'v.kg_plate_word_{word}', read)
            for hand in ('main', 'off'):
                self.assertIn(f'v.kg_plate_qa_raw_{hand}_word_{word}', read)
        text = '\n'.join(scripts['pre_animation'])
        self.assertNotIn('q.get_name', text)
        self.assertNotIn('q.get_id', text)
        self.assertNotIn('q.position', text)
        enabled, = [row for row in scripts['pre_animation'] if row.startswith('v.kg_plate_qa_enabled = ')]
        self.assertEqual(enabled, 'v.kg_plate_qa_enabled = (v.kg_plate_qa_raw_main_word_4 == 1 && v.kg_plate_qa_raw_main_word_7 == 133) || (v.kg_plate_qa_raw_off_word_4 == 1 && v.kg_plate_qa_raw_off_word_7 == 133);')

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

    def test_qa_is_default_off_without_either_raw_flag(self):
        self.harness(r'''
for(const hand of ['main_hand','off_hand','inventory']){
 const fresh=instance(hand);assert(fresh.v.kg_plate_qa_enabled===0,'QA not initialized off');
 for(const mainFlag of [0,2,1.5])for(const offFlag of [0,2,1.5]){
  const main=[...fixture],off=[...fixture];main[4]=mainFlag;off[4]=offFlag;
  const i=instance(hand,fixture,{main,off});i.update(0);
  assert(!i.v.kg_plate_qa_enabled&&i.logs.length===0,'Dormant flag logged');
  assert(!Object.values(i.visible('qa_probe')).some(Boolean)&&!i.visible('qa_forced_food').plate_row_0,'Dormant flag drew QA');
 }
 const absent=instance(hand);delete absent.c.owning_entity;absent.update(0);
 assert(!absent.v.kg_plate_qa_enabled&&absent.logs.length===0,'Absent owner admitted');
}
''')

    def test_raw_flag_bypasses_count_occupancy_and_unknown_hand_gates(self):
        self.harness(r'''
for(const hand of ['main_hand','off_hand','inventory'])for(const flagBank of ['main','off']){
 for(const marker of [133]){
  const main=[...fixture],off=[...fixture];main[4]=0;off[4]=0;main[7]=marker;off[7]=marker;
  const i=instance(hand,fixture,{main,off,mainItem:'minecraft:stick',offItem:'minecraft:air'});
  i.state[flagBank][4]=1;i.update(0);
  assert(i.v.kg_plate_qa_enabled&&i.logs.length===26,'Raw flag still depends on count/hand/item occupancy');
  assert(!i.v.kg_plate_owner_occupied,'Production occupancy gate changed');
  assert(i.visible('qa_probe').qa_a_flag&&i.visible('qa_forced_food').plate_row_0,'Existing constant passes not activated');
  assert(i.logs[1]===(hand==='main_hand'?1:hand==='off_hand'?2:0),'Unknown hand code wrong');
 }
}
''')

    def test_bottle_and_count5_word4_one_cannot_enable_plate_probe(self):
        self.harness(r'''
for(const hand of ['main_hand','off_hand','inventory'])for(const bank of ['main','off']){
 for(const marker of [0,1,4,9,10,256,625,626,664,747,748,1000]){
  // A held plate without the tag may share a flagged bottle or a legitimate
  // count5 plate whose fifth row has paletteword1 (secret descriptor39=664).
  const main=[...fixture],off=[...fixture];main[4]=0;off[4]=0;
  const i=instance(hand,fixture,{main,off});i.state[bank][4]=1;i.state[bank][7]=marker;i.update(0);
  assert(!i.v.kg_plate_qa_enabled&&i.logs.length===0,'Nonfixture marker enabled probe '+bank+'/'+marker);
  assert(!Object.values(i.visible('qa_probe')).some(Boolean)&&!i.visible('qa_forced_food').plate_row_0,'Bottle/count5 word4 drew QA');
 }
 // A valid raw plate flag remains visible beside a normal flagged bottle.
 const i=instance(hand,fixture,{main:[...fixture],off:[...fixture]});
 i.state[bank][7]=9;i.update(0);assert(i.v.kg_plate_qa_enabled,'Bottle marker masked other valid plate flag');
}
''')

    def test_both_raw_banks_are_read_without_floor_or_selected_hand_borrow(self):
        self.harness(r'''
const main=[101.25,102.25,103.25,104.25,1,106.25,107.25,133];
const off=[201.75,202.75,203.75,204.75,0,206.75,207.75,208.75];
for(const hand of ['main_hand','off_hand','inventory']){
 const i=instance(hand,fixture,{main:[...main],off:[...off]});i.update(0);
 assert(i.v.kg_plate_qa_enabled,'Opposite-hand raw flag omitted');
 for(const [bank,expected] of [['main',main],['off',off]])for(let word=0;word<8;word++)
  assert(i.v['kg_plate_qa_raw_'+bank+'_word_'+word]===expected[word],'Raw bank floored/borrowed '+bank+'/'+word);
 assert(JSON.stringify(i.logs.slice(2,10))===JSON.stringify(main),'Main raw log order wrong');
 assert(JSON.stringify(i.logs.slice(10,18))===JSON.stringify(off),'Off raw log order wrong');
}
''')

    def test_raw_marker133_logs_when_modeled_float32_reciprocal_count_is_zero(self):
        # A source/harness discriminator, not proof of native arithmetic:
        # inject only the hypothesized decoder result before running the real
        # unchanged QA gate/log statements. Production division is untouched.
        self.harness(r'''
const qaStart=d.scripts.pre_animation.findIndex(row=>row.startsWith('v.kg_plate_qa_enabled = '));
assert(d.scripts.pre_animation.includes('v.kg_plate_count = math.floor((v.kg_plate_word_7 - 10)/123);'),'Production division changed');
for(const hand of ['main_hand','off_hand'])for(const [marker,expectedCount] of [[133,0]]){
 const word=[...fixture];word[7]=marker;const i=instance(hand,word);
 evaluatePreAnimation(d.scripts.pre_animation.slice(0,qaStart),i.q,i.c,math,i.v);
 i.v.kg_plate_count=Math.floor(Math.fround(Math.fround(marker-10)*Math.fround(1/123)));
 assert(i.v.kg_plate_count===expectedCount,'Float32 reciprocal hypothesis result changed');
 evaluatePreAnimation(d.scripts.pre_animation.slice(qaStart),i.q,i.c,math,i.v);
 assert(i.v.kg_plate_qa_enabled&&i.logs.length===26,'Modeled count failure suppressed probe');
 assert(i.logs[hand==='main_hand'?9:17]===marker&&i.logs[18]===expectedCount,'Raw marker/decoded count not distinguished');
 assert(i.visible('qa_probe').qa_a_flag&&!i.visible('qa_probe').qa_d_decoded,'Count-failure post legend wrong');
 assert(i.visible('qa_forced_food').plate_row_0,'Modeled count failure suppressed constant control');
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
for(const hand of ['main_hand','off_hand','inventory'])for(const lifeSupported of [true,false]){
 const i=instance(hand),sampleTimes=[],update=i.update;
 let before=0;
 for(const time of [0,.25,.5,.75,1,1.25,1.5,1.75,2,2.25,3,10,100]){
  update(lifeSupported?time:0,time-before);before=time;
  const count=i.logs.length/26;
  if(count>sampleTimes.length)sampleTimes.push(time);
 }
 assert(JSON.stringify(sampleTimes)==='[0,1,2]','One-second sample spacing/cap wrong '+sampleTimes);
 const expected=[914100,hand==='main_hand'?1:hand==='off_hand'?2:0,...i.state.main,...i.state.off,1,57,18,0,199,195,180,hand==='inventory'?0:1];
 assert(i.logs.length===78&&i.v.kg_plate_qa_samples===3,'More than three numeric groups');
 for(let sample=0;sample<3;sample++)assert(JSON.stringify(i.logs.slice(sample*26,(sample+1)*26))===JSON.stringify(expected),'Numeric group/hand order wrong');
 // Disable/re-enable, re-entrant frames and a reset life clock cannot reset
 // the per-attachable cap. A new attachable initialization gets its own cap.
 i.state[hand==='off_hand'?'off':'main'][4]=0;i.update(200,100);
 i.state[hand==='off_hand'?'off':'main'][4]=1;i.update(201,1);i.update(0,0);i.update(1000,999);
 assert(i.logs.length===78&&i.v.kg_plate_qa_samples===3,'Flag toggle reset lifetime cap');
 const fresh=instance(hand);fresh.update(0);assert(fresh.logs.length===26&&fresh.v.kg_plate_qa_samples===1,'New attachable did not initialize');
}
// An already old entity starts with a new attachable-local sampling clock.
const old=instance();for(const time of [500,500.5,501,501.5,502,503])old.update(time,0);
assert(old.logs.length===78&&old.v.kg_plate_qa_samples===3,'Owner lifetime origin/cap wrong');
''')


if __name__ == '__main__':
    unittest.main()
