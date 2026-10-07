"""Held plate source conservation, frame and real expression harness checks.

These checks do not certify Bedrock Molang evaluation or native rendered pixels.
"""
from pathlib import Path
import itertools
import json
import math
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'development/gameplay_core')]
import build_plate_held as held
from held_pose_frames import (chain, translate, rotate, xyz, scale, point,
    bone_matrix, rigid_inverse, native_skewer_calibration)
from secret_skewer_assets import state_slot_cubes, shaft_cubes, COMPLETE_STATES
from test_eating_observer_projection import node


def load(relative):
    return json.loads((held.RP / relative).read_text())


class PlateHeldAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.attach = load('attachables/skewer_plate.attachable.json')['minecraft:attachable']['description']
        cls.geometries = {g['description']['identifier'].rsplit('.', 1)[1]: g
            for g in load('models/entity/plate_held.geo.json')['minecraft:geometry']}
        cls.controllers = load('render_controllers/plate_held.render_controllers.json')['render_controllers']

    def test_generated_assets_are_exact_and_only_rp(self):
        output = held.build()
        self.assertEqual(len(output), 4)
        for path, data in output.items():
            self.assertTrue(path.is_relative_to(held.RP))
            self.assertEqual(path.read_bytes(), data, str(path))
        self.assertEqual(load('animations/plate_held.animation.json'), held.animations())
        source = ROOT.parent / 'grilling-java-current'
        if source.is_dir(): held.verify_java_source(source)

    def test_one_socket_per_geometry_preserves_player_arms(self):
        self.assertEqual(len(self.geometries), 526)
        self.assertEqual(len(self.controllers), 31)
        self.assertFalse((held.RP / 'entity/player.entity.json').exists())
        self.assertFalse((held.RP / 'entity/player.json').exists())
        for geometry in self.geometries.values():
            self.assertEqual(sum(bool(b.get('binding')) for b in geometry['bones']), 1)
            self.assertEqual(geometry['bones'][0]['binding'], held.BINDING)
            self.assertEqual(geometry['bones'][0]['name'], 'grip')
            self.assertFalse(any(b['name'].startswith(('leftArm', 'rightArm', 'leftItem', 'rightItem')) for b in geometry['bones']))
        self.assertEqual(set(self.attach['animations']), {'fp_right', 'fp_left', 'tp_right', 'tp_left', 'layout'})
        self.assertNotIn('q.is_using_item', json.dumps(self.attach))
        self.assertFalse(any(k.startswith(('eat_', 'fp_eat_')) for k in self.attach['animations']))

    def test_fixed_and_secret_cubes_preserve_canonical_source(self):
        source_client = load('entity/grill_food_visual.entity.json')['minecraft:client_entity']['description']
        source_geometries = {g['description']['identifier']: g for g in load('models/entity/grill_display.geo.json')['minecraft:geometry']}
        for row in range(5):
            for fixed in range(19):
                source = source_geometries[source_client['geometry']['s' + str(fixed*6)]]
                self.assertEqual(self.geometries[f'fixed_{row}_{fixed}']['bones'][-1]['cubes'], held.lift_cubes(source, 25))
            self.assertEqual(self.geometries[f'stick_{row}']['bones'][-1]['cubes'], shaft_cubes(True))
            for shape, state in enumerate(COMPLETE_STATES):
                for slot in range(3):
                    self.assertEqual(self.geometries[f'secret_{row}_{shape}_{slot}']['bones'][-1]['cubes'], state_slot_cubes(state, slot, True))
            ordinary = load('models/entity/a22_bites/ordinary_skewer_stage0.geo.json')['minecraft:geometry'][0]
            self.assertEqual(len(self.geometries[f'special_{row}_0']['bones'][-1]['cubes']), 19)
            self.assertEqual(self.geometries[f'special_{row}_0']['bones'][-1]['cubes'], held.lift_cubes(ordinary, 24))
            for special in (1, 2): self.assertEqual(self.geometries[f'special_{row}_{special}']['bones'][-1]['cubes'], shaft_cubes(True))

    def test_every_count_slot_matches_item_renderer_without_placed_cancellation(self):
        fixed = {'position': [0, 1.8, 1.8], 'rotation': [0, 0, -180], 'scale': 1.2}
        for count in range(1, 6):
            for row, cell in enumerate(held.LAYOUTS[count]):
                actual = chain(bone_matrix(held.slot_pose(row, count)), bone_matrix(fixed))
                # Independent Java pipeline. The surrounding builtin item
                # frame subtracts X/Z eight; Y centering is in plate_pose.
                expected = chain(translate([cell[0]-8, cell[1], cell[2]-8]), rotate('y', cell[3]),
                    rotate('x', 90), scale([.8]*3), translate([0, 2.25, 9.75]),
                    xyz([-90, 0, -180]), scale([1.5]*3), translate([-8]*3))
                placed = chain(translate([cell[0]-8, cell[1], cell[2]-8]), rotate('y', cell[3]),
                    rotate('z', 180), rotate('x', 90), scale([.8]*3), translate([0, 2.25, 9.75]),
                    xyz([-90, 0, -180]), scale([1.5]*3), translate([-8]*3))
                differs_from_placed = False
                for source in itertools.product((0, 1, 8, 16), repeat=3):
                    result = point(actual, [source[0]-8, source[1], source[2]-8])
                    reference = point(expected, source)
                    for a, b in zip(result, reference): self.assertAlmostEqual(a, b, places=10)
                    differs_from_placed |= any(abs(a-b) > .1 for a, b in zip(result, point(placed, source)))
                self.assertTrue(differs_from_placed)
        for count in range(6):
            for row in range(count, 5): self.assertEqual(held.slot_pose(row, count), {'position': [0, 0, 0], 'rotation': [0, 0, 0]})

    def test_authored_first_person_frames_reconstruct_both_native_socket_projections(self):
        # Check the generated bone frame against the separately assembled Java
        # model transform, not copied Euler channels. Body visibility remains
        # partial at the default native camera edge; native acceptance is open.
        for hand in ('right', 'left'):
            sign = 1 if hand == 'right' else -1
            base, camera = native_skewer_calibration(hand)
            actual = chain(rigid_inverse(camera), base, translate([0, 24, 0]),
                bone_matrix(held.plate_pose('fp', hand)), translate([0, -24, 0]))
            expected = chain(translate([0, -24, -32.4]), translate([9.039*sign, 15.682, 20.8]),
                translate([0, 3.75, 0]), xyz([0, -135*sign, 0]), scale([.4]*3), translate([-8]*3))
            visible = 0
            for source in itertools.product((1, 8, 15), (0, 2), (1, 8, 15)):
                result = point(actual, [source[0]-8, source[1]+24, source[2]-8])
                for a, b in zip(result, point(expected, source)): self.assertAlmostEqual(a, b, places=7)
                visible += result[2] < -.1 and abs(result[0]/result[2]) < 1.3 and abs(result[1]/result[2]) < .75
                self.assertTrue(all(math.isfinite(v) for v in result))
            self.assertGreater(visible, 0)

    def test_real_decoder_owner_and_visibility_expressions_in_both_hands(self):
        # Evaluate the actual generated scripts/controllers under the existing
        # reviewed owner-context harness. Browser/SDK doubles are not Bedrock.
        node('const d=' + json.dumps(self.attach) + '; const rc=' + json.dumps(self.controllers) + r''';
const math={clamp:(x,a,b)=>Math.max(a,Math.min(b,x))};
const pack=foods=>foods[0]+foods[1]*214+foods[2]*45796;
function words(desc,count,foods=[1,107,213]){
 const rows=[0,0,0,0,0];for(let i=0;i<count;i++)rows[i]=desc;
 return [pack(foods),pack(foods),pack(foods),pack(foods),pack(foods),rows[0]+rows[1]*123,rows[2]+rows[3]*123,10+rows[4]+count*123];
}
function evaluate(main,off,hand,mainItem=d.identifier,offItem=d.identifier){
 const owner={has_property:n=>/^kaleidoscope_grilling:bottle_(main|off)_[0-7]$/.test(n),
 property:n=>(n.includes(':bottle_off_')?off:main)[Number(n.slice(-1))],
 is_item_name_any:(slot,...names)=>names.includes(slot==='slot.weapon.offhand'?offItem:mainItem)};
 const v={};evaluatePreAnimation(d.scripts.pre_animation,{}, {item_slot:hand,owning_entity:owner},math,v);return v;
}
const truth=(expr,v)=>Boolean(new Function('v','math','return '+expr)(v,math));
function passes(v){return Object.values(rc).map(c=>truth(c.part_visibility.at(-1)[Object.keys(c.part_visibility.at(-1))[0]],v));}
function selected(expr,arrays,v){
 if(!expr.startsWith('Array.'))return expr;
 const start=expr.indexOf('['),end=expr.lastIndexOf(']'),name=expr.slice(0,start);
 const index=new Function('v','math','return '+expr.slice(start+1,end))(v,math);
 if(!Number.isInteger(index)||!arrays[name]?.[index])throw Error('Invalid render array index '+expr);
 return arrays[name][index];
}
for(const hand of ['main_hand','off_hand'])for(let count=0;count<=5;count++)for(let desc=1;desc<=122;desc++){
 const w=words(desc,count),other=words(desc===1?122:1,5,[213,0,2]);
 const v=evaluate(hand==='main_hand'?w:other,hand==='off_hand'?w:other,hand);
 if(!v.kg_plate_owner_occupied||v.kg_plate_count!==count)throw Error('Owner/count mismatch');
 for(let row=0;row<count;row++){
  if(v['kg_plate_desc_'+row]!==desc)throw Error('Row descriptor mismatch');
  for(const [slot,food]of [1,107,213].entries())if(v['kg_plate_food_'+row+'_'+slot]!==food)throw Error('Palette digit mismatch');
  if(desc>=39&&desc<=119){const index=desc-39;if(v['kg_plate_style_'+row]!==Math.floor(index/27)||v['kg_plate_shape_'+row]!==index%27)throw Error('Shape/style mismatch');}
 }
 for(let row=count;row<5;row++)for(const c of Object.values(rc))if(Object.hasOwn(c.part_visibility.at(-1),'plate_row_'+row)&&truth(c.part_visibility.at(-1)['plate_row_'+row],v))throw Error('Beyond-count row visible');
 const expected=1+count*(desc>=39&&desc<=119?4:1);
 if(passes(v).filter(Boolean).length!==expected)throw Error('Unexpected pass count '+desc+'/'+count);
 for(const c of Object.values(rc)){
  const geometry=selected(c.geometry,c.arrays?.geometries??{},v),texture=selected(c.textures[0],c.arrays?.textures??{},v);
  if(!d.geometry[geometry.replace('Geometry.','')]||!d.textures[texture.replace('Texture.','')])throw Error('Unresolved selected resource');
 }
}
for(const hand of ['main_hand','off_hand']){
 const plate=words(66,5,[213,0,106]),bottle=[1,2,3,4,5,6,7,8];
 const main=hand==='main_hand'?plate:bottle,off=hand==='off_hand'?plate:bottle;
 const mainItem=hand==='main_hand'?d.identifier:'kaleidoscope_grilling:empty_seasoning_bottle';
 const offItem=hand==='off_hand'?d.identifier:'kaleidoscope_grilling:empty_seasoning_bottle';
 const v=evaluate(main,off,hand,mainItem,offItem);
 if(!v.kg_plate_owner_occupied||passes(v).filter(Boolean).length!==16)throw Error('Mixed bottle/plate or zero palette routing wrong');
 const opposite=evaluate(main,off,hand==='main_hand'?'off_hand':'main_hand',mainItem,offItem);
 if(opposite.kg_plate_owner_occupied||passes(opposite).some(Boolean))throw Error('Opposite bottle hand rendered plate');
}

for(const hand of ['main_hand','off_hand'])for(const marker of [0,9,748,9800343]){
 const w=words(119,5);w[7]=marker;const v=evaluate(w,w,hand);
 if(v.kg_plate_owner_occupied||passes(v).some(Boolean))throw Error('Invalid/transaction marker leaked');
}
for(const hand of ['main_hand','off_hand']){
 const w=words(119,5);let v=evaluate(w,w,hand,'minecraft:stick','minecraft:stick');
 if(v.kg_plate_owner_occupied||passes(v).some(Boolean))throw Error('Stale hand owner leaked');
 v=evaluate(w,w,'inventory');if(v.kg_plate_owner_occupied||passes(v).some(Boolean))throw Error('Unknown equipment socket admitted');
 for(let word=0;word<7;word++){const bad=[...w];bad[word]=word<5?9800344:15129;v=evaluate(bad,bad,hand);if(v.kg_plate_owner_occupied||passes(v).some(Boolean))throw Error('Out-of-range payload admitted');}
 const empty=evaluate(words(0,0,[0,0,0]),words(0,0,[0,0,0]),hand);
 if(!empty.kg_plate_owner_occupied||passes(empty).filter(Boolean).length!==1)throw Error('Empty plate body/row handling wrong');
 const unsupported=evaluate(words(0,5,[0,0,0]),words(0,5,[0,0,0]),hand);
 if(!unsupported.kg_plate_owner_occupied||passes(unsupported).filter(Boolean).length!==1)throw Error('Suppressed descriptor must leave body only');
}
for(const hand of ['main_hand','off_hand'])for(const firstPerson of [0,1]){
 // Evaluate dispatch using real camera/item-slot context, independently of row gates.
 const routes=d.scripts.animate.filter(row=>typeof row==='object').filter(row=>Boolean(new Function('c','return '+Object.values(row)[0])({item_slot:hand,is_first_person:firstPerson})));
 const alias=(firstPerson?'fp_':'tp_')+(hand==='main_hand'?'right':'left');if(routes.length!==1||Object.keys(routes[0])[0]!==alias)throw Error('Plate hand/camera dispatch mismatch');
}
''')

    def test_palette_extrema_and_all_shapes_styles_count_markers(self):
        for foods in itertools.product((0, 1, 106, 107, 212, 213), repeat=3):
            word = sum(food * 214**slot for slot, food in enumerate(foods))
            for style_index, style in enumerate((0, 4, 6)):
                for shape in range(27):
                    desc = 39 + shape + 27*style_index
                    decoded = held.decode_projection([word]*5 + [desc+123*desc, desc+123*desc, 10+desc+123*5])
                    self.assertTrue(decoded['owner']); self.assertEqual(decoded['count'], 5)
                    self.assertEqual(decoded['rows'][4], {'descriptor': desc, 'foods': list(foods), 'style': style, 'state': COMPLETE_STATES[shape]})
        self.assertEqual(held.PALETTE_MAX, 214**3-1)
        self.assertLess(held.PALETTE_MAX, 2**24)
        for marker in (0, 9, 748, 9800343): self.assertFalse(held.decode_projection([0]*7+[marker])['owner'])
        self.assertEqual(held.decode_projection([0]*7+[10]), {'owner': True, 'count': 0, 'rows': []})


if __name__ == '__main__': unittest.main()
