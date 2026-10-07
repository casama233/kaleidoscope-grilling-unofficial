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
    bone_matrix, rigid_inverse, native_skewer_calibration, zyx)
from secret_skewer_assets import state_slot_cubes, shaft_cubes, COMPLETE_STATES
from test_eating_observer_projection import node
from test_native_skewer_fp import reference_frame


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

    def test_first_person_frames_preserve_authored_projection_plus_camera_translation(self):
        # Check the generated bone frame against the separately assembled Java
        # model transform plus the explicit Bedrock camera translation. The
        # source rotation/scale remain authored; native acceptance is still open.
        for hand in ('right', 'left'):
            sign = 1 if hand == 'right' else -1
            base, camera = native_skewer_calibration(hand)
            actual = chain(rigid_inverse(camera), base, translate([0, 24, 0]),
                bone_matrix(held.plate_pose('fp', hand)), translate([0, -24, 0]))
            expected = chain(translate([0, -24, -32.4]), translate([9.039*sign, 15.682, 20.8]),
                translate([0, 3.75, 0]), xyz([0, -135*sign, 0]), scale([.4]*3), translate([-8]*3))
            offset = [-4*sign, 3.1, -9]
            for source in itertools.product((1, 8, 15), (0, 2), (1, 8, 15)):
                result = point(actual, [source[0]-8, source[1]+24, source[2]-8])
                for a, b, delta in zip(result, point(expected, source), offset):
                    self.assertAlmostEqual(a, b+delta, places=7)
                self.assertTrue(all(math.isfinite(v) for v in result))

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


def cube_corners(cube):
    """Every reflected source corner, including cube-local rotation/inflation."""
    pivot = cube.get('pivot', [0, 0, 0]); pivot = [-pivot[0], pivot[1], pivot[2]]
    rotation = cube.get('rotation', [0, 0, 0])
    matrix = chain(translate(pivot), zyx([-rotation[0], -rotation[1], rotation[2]]),
        translate([-v for v in pivot]))
    origin, size, inflate = cube['origin'], cube['size'], cube.get('inflate', 0)
    return [point(matrix, [(-1 if axis == 0 else 1) *
        (origin[axis]-inflate+corner[axis]*(size[axis]+2*inflate)) for axis in range(3)])
        for corner in itertools.product((0, 1), repeat=3)]


class PlateFirstPersonFraming(unittest.TestCase):
    """Complete rigid-model framing; no Bedrock pixel/controller certification.

    The independent pinned native socket is settled, wide skin, zero bob,
    non-VR. Every possible active row mesh is included, so its union bounds all
    mixed combinations, palettes and styles without enumerating their product.
    Equip lowering and actual FOV/eye/blending remain native-client gates.
    """
    X_VIEW = (.025, .535)
    Y_VIEW = (-.285, -.015)

    @classmethod
    def setUpClass(cls):
        cls.geometries = {g['description']['identifier'].rsplit('.', 1)[1]: g
            for g in load('models/entity/plate_held.geo.json')['minecraft:geometry']}
        cls.aliases = {}
        cls.source_corners = {}
        for alias, geometry in cls.geometries.items():
            cls.source_corners[alias] = [p for bone in geometry['bones']
                for cube in bone.get('cubes', []) for p in cube_corners(cube)]
        for row in range(5):
            cls.aliases[row] = {f'fixed_{row}_{i}' for i in range(19)} | {f'stick_{row}'} | \
                {f'secret_{row}_{shape}_{slot}' for shape in range(27) for slot in range(3)} | \
                {f'special_{row}_{i}' for i in range(3)}
        cls.cases = {}
        fixed = {'position': [0, 1.8, 1.8], 'rotation': [0, 0, -180], 'scale': 1.2}
        for hand in ('right', 'left'):
            # reference_frame independently assembles the native player/socket
            # fixture; do not use the generator's native_skewer_calibration.
            root = chain(reference_frame(hand), bone_matrix(held.plate_pose('fp', hand)),
                translate([0, -24, 0]))
            for count in range(6):
                cls.cases[hand, count, 'body'] = [point(root, p) for p in cls.source_corners['body']]
                for row in range(count):
                    matrix = chain(root, translate([0, 24, 0]),
                        bone_matrix(held.slot_pose(row, count)), bone_matrix(fixed), translate([0, -24, 0]))
                    for alias in sorted(cls.aliases[row]):
                        cls.cases[hand, count, alias] = [point(matrix, p) for p in cls.source_corners[alias]]
        cls.points = [([p[0] if hand == 'right' else -p[0], p[1], p[2]])
            for (hand, _, _), points in cls.cases.items() for p in points]

    def test_full_body_and_every_selectable_row_family_count_zero_through_five(self):
        self.assertEqual(len(self.cases), 3132)
        self.assertEqual(len(self.points), 384336)
        for row in range(5):
            actual = {alias for alias, geometry in self.geometries.items()
                if geometry['bones'][-1]['name'] == f'plate_row_{row}' and has_cubes(geometry)}
            self.assertEqual(actual, self.aliases[row])
        for (hand, count, alias), points in self.cases.items():
            self.assertTrue(points, (hand, count, alias))
            sign = 1 if hand == 'right' else -1
            self.assertTrue(all(all(math.isfinite(v) for v in p) and p[2] < -.1 and
                self.X_VIEW[0] < sign*p[0]/-p[2] < self.X_VIEW[1] and
                self.Y_VIEW[0] < p[1]/-p[2] < self.Y_VIEW[1] for p in points),
                f'Complete model leaves narrower hand viewport: {hand}/{count}/{alias}')

    def test_projection_covers_the_actual_identity_geometry_hierarchy(self):
        for alias, geometry in self.geometries.items():
            if alias == 'body':
                names = ['grip', 'plate_pose', 'plate_body']
            else:
                row = alias.split('_')[1]
                names = ['grip', 'plate_pose', f'plate_slot_{row}', f'plate_fixed_{row}', f'plate_row_{row}']
            self.assertEqual([b['name'] for b in geometry['bones']], names, alias)
            for index, bone in enumerate(geometry['bones']):
                self.assertEqual(bone['pivot'], [0, 24, 0], (alias, bone['name']))
                self.assertFalse(set(bone) & {'position', 'rotation', 'scale'}, (alias, bone['name']))
                if index:
                    self.assertEqual(bone['parent'], names[index-1], (alias, bone['name']))
                else:
                    self.assertNotIn('parent', bone)
                    self.assertEqual(bone['binding'], held.BINDING)

    def test_complete_model_also_fits_horizontal_and_vertical_sixty_degree_cameras(self):
        tangent = math.tan(math.radians(30))
        for aspect in (1.49, 16/9):
            for axis in ('horizontal', 'vertical'):
                hx, hy = (tangent, tangent/aspect) if axis == 'horizontal' else (tangent*aspect, tangent)
                self.assertTrue(all(p[2] < -.1 and abs(p[0]) < -p[2]*hx and
                    abs(p[1]) < -p[2]*hy for p in self.points), (axis, aspect))

    def test_source_corner_constraints_derive_a_bounded_mirrored_translation(self):
        self.assertEqual(held.PLATE_FP_CAMERA_OFFSET, [-4, 3.1, -9])
        # Undo only the tested common camera translation to measure the intact
        # authored frame. These are model-frame measurements, not pixel data.
        source = [[p[0]+4, p[1]-3.1, p[2]+9] for p in self.points]
        intervals = []
        minimum_depths = []
        for axis, (low, high) in enumerate((self.X_VIEW, self.Y_VIEW)):
            lower = max(-low*p[2]-p[axis] for p in source)
            upper = min(-high*p[2]-p[axis] for p in source)
            minimum_depths.append((lower-upper)/(high-low))
            intervals.append((low*9+lower, high*9+upper))
        self.assertAlmostEqual(max(minimum_depths), 8.46439919, places=6)
        self.assertLess(intervals[0][0], -4); self.assertGreater(intervals[0][1], -4)
        self.assertLess(intervals[1][0], 3.1); self.assertGreater(intervals[1][1], 3.1)
        # Eight units cannot satisfy the whole-model vertical bounds with any
        # common Y translation; nine creates the documented safe interval.
        self.assertGreater(max(minimum_depths), 8)
        self.assertLess(max(minimum_depths), 9)

    def test_unadapted_source_frame_witness_rejects_prior_partial_body_gate(self):
        for hand, sign in (('right', 1), ('left', -1)):
            current = self.cases[hand, 0, 'body']
            source = [[p[0]+4*sign, p[1]-3.1, p[2]+9] for p in current]
            # The former any-corner envelope passes while whole-tray coverage
            # fails. Preserve this reproducer rather than relaxing the gate.
            self.assertTrue(any(p[2] < -.1 and abs(p[0]/p[2]) < 1.3 and
                abs(p[1]/p[2]) < .75 for p in source))
            self.assertFalse(all(p[2] < -.1 and
                self.X_VIEW[0] < sign*p[0]/-p[2] < self.X_VIEW[1] and
                self.Y_VIEW[0] < p[1]/-p[2] < self.Y_VIEW[1] for p in source))


def has_cubes(geometry):
    return any(bone.get('cubes') for bone in geometry['bones'])


if __name__ == '__main__': unittest.main()
