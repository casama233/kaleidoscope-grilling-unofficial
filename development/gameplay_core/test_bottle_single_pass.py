"""Independent single-pass audit against pinned original assets, not client evidence.

Run from repository root: python -B development/gameplay_core/test_bottle_single_pass.py
Does not import or execute the asset generator, modify assets, or need a sibling checkout.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from fnmatch import fnmatchcase
import hashlib
import json
import re
import subprocess
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RP = ROOT / 'projects/grilling/gameplay_core/resource_pack'
BP = ROOT / 'projects/grilling/gameplay_core/behavior_pack'
FIXTURES = ROOT / 'development/gameplay_core/fixtures'
ORIGINAL_GEOMETRIES_SHA256 = '8f2bd411e128f66878da90efd536215a3b420c482c7930a7b7a8d168c1c0e65c'
ORIGINAL_BOTTLE_PNG_SHA256 = '9a889a96a4bb34b999ddfc5bcb42b1f1a691fc1e65c91253726b7eee6a3dc94b'
SOURCE_TEXTURES = {
    'textures/blocks/seasoning_bottle': (0, ORIGINAL_BOTTLE_PNG_SHA256),
    'textures/a2766_special_seasoning/palette_v5': (32, '4ed27986868159012ad3927e2ca17d81d21c8fb35d19ba7a682583e86f3683e3'),
    'textures/a2766_special_seasoning/palette_v6': (64, 'd9e4347dcc8f0c4ced04620e096da71f88d20365b2168e0e9d728a21e93ba0ed'),
    'textures/a2766_special_seasoning/palette_v7': (96, '29763206a3c76d4e470377e84c03253438f9949e6251571f2f499e32496354ee'),
}
ORIGINAL_PALETTE_SHA256 = '60ff13fc2aaec2c378ed8c38b30e137db4b6d224c8f5cd29a40d3b76600a4859'
ORIGINAL_PENDING_MASK_SHA256 = 'ee7cc9297c08610291db9ff21db647f33f02aa4261fa4e60871b5a5222ffd7e3'
ORIGINAL_ROUTE_VARIANTS = {
    1: [0, 1, 2, 3, 4, 5, 0, 0], 2: [0, 1, 2, 3, 4, 5, 0, 0],
    **{r: [0, 1, 2, 3, 4, 0, 0, 0] for r in range(3, 9)},
}
FALLBACK = [0xB86B45, 0xE0A56A]


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_index():
    result = {}
    for path in (RP / 'models/entity').rglob('*.json'):
        for g in load(path).get('minecraft:geometry', []):
            identifier = g['description']['identifier']
            if identifier in result:
                raise AssertionError('Duplicate geometry identifier: ' + identifier)
            result[identifier] = g
    return result


def routes():
    names = ['empty_seasoning_bottle', 'pending_seasoning', 'special_seasoning']
    names += [f'special_seasoning_r{r}_v{v}' for r in range(1, 9) for v in range(8)]
    return {name: load(RP / f'attachables/{name}.attachable.json')['minecraft:attachable']['description'] for name in names}


def controllers():
    result = {}
    for path in (RP / 'render_controllers').glob('*.json'):
        for name, value in load(path).get('render_controllers', {}).items():
            if name in result:
                raise AssertionError('Duplicate controller: ' + name)
            result[name] = value
    return result


def cubes(g):
    return [c for b in g['bones'] for c in b.get('cubes', [])]


def rgba(rgb):
    return ((rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255, 255)


def original_texture(r, v):
    if v in [6, 7] or v == 5 and r >= 3:
        return f'textures/a2766_special_seasoning/palette_v{v}'
    return 'textures/blocks/seasoning_bottle'


def shifted_cubes(original, x_offset):
    expected = deepcopy(original)
    for cube in expected:
        for face in cube['uv'].values():
            face['uv'][0] += x_offset
    return expected


def visibility_value(expression, values):
    if isinstance(expression, (bool, int)):
        return bool(expression)
    match = re.fullmatch(r'\s*\(?\s*v\.kg_bottle_layer_(\d+)\s*==\s*(\d+)\s*\)?\s*', expression)
    if not match:
        raise AssertionError('Unexpected dynamic visibility syntax: ' + str(expression))
    layer, index = map(int, match.groups())
    if not 0 <= layer < 8 or not 1 <= index <= 9:
        raise AssertionError('Invalid dynamic visibility selector: ' + expression)
    return values[layer] == index


def bone_visibility(rc, bone, values):
    visible = True
    for row in rc.get('part_visibility', []):
        for pattern, expression in row.items():
            if fnmatchcase(bone, pattern):
                visible = visibility_value(expression, values)
    return visible


def effective_material(rc, bone, aliases):
    material = None
    for row in rc['materials']:
        for pattern, value in row.items():
            if fnmatchcase(bone, pattern):
                if not value.startswith('Material.'):
                    raise AssertionError('Unexpected material expression: ' + value)
                material = aliases[value.split('.', 1)[1]]
    return material


class SinglePassAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geos = geometry_index()
        cls.routes = routes()
        cls.controllers = controllers()
        cls.palette_path = FIXTURES / 'java-seasoning-colors-1.1.1.json'
        cls.palette = load(cls.palette_path)['ingredients']
        cls.ids = sorted(cls.palette)
        cls.pairs = {i + 1: cls.palette[identifier]['rgb'] for i, identifier in enumerate(cls.ids)}
        cls.pairs[9] = FALLBACK

    def test_original_rgba_and_all_retained_fixed_geometries_are_pinned(self):
        # Pin untouched-original bytes, so comparing generated output to mutable
        # local source files cannot silently bless a changed baseline.
        paths = sorted((RP / 'models/entity/a286_hand').glob('kg_a2766.special_seasoning.*.geo.json'))
        paths.append(RP / 'models/entity/a286_hand/kg_a2733.seasoning_bottle_hand.geo.json')
        self.assertEqual(len(paths), 85)
        rows = [(p.relative_to(RP).as_posix(), sha(p)) for p in sorted(paths)]
        digest = hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(digest, ORIGINAL_GEOMETRIES_SHA256)
        self.assertEqual(sha(RP / 'textures/blocks/seasoning_bottle.png'), ORIGINAL_BOTTLE_PNG_SHA256)
        for texture, (_, digest) in SOURCE_TEXTURES.items():
            self.assertEqual(sha(RP / (texture + '.png')), digest, texture)
        self.assertEqual(sha(self.palette_path), ORIGINAL_PALETTE_SHA256)
        self.assertEqual(sha(FIXTURES / 'a2770/grilling/kaleidoscope_grilling/models/item/seasoning_states/pending_8.json'), ORIGINAL_PENDING_MASK_SHA256)

    def test_frozen_source_route_fixture_matches_independently_read_original_aliases(self):
        source = load(FIXTURES / 'bottle-fixed-source-routes.json')
        self.assertEqual(source['source_commit'], '4d9cee9c0d8f256954b2e6b5148acf40f1ee09e1')
        expected = {}
        for r in range(1, 9):
            for v in range(8):
                original_v = ORIGINAL_ROUTE_VARIANTS[r][v]
                identifier = f'geometry.kg_a286.kg_a2766.special_seasoning.r{r}.v{original_v}'
                expected[f'kaleidoscope_grilling:special_seasoning_r{r}_v{v}'] = {
                    'geometry': {'default': identifier, 'contents': identifier + '.contents'},
                    'texture': original_texture(r, v),
                }
        expected['kaleidoscope_grilling:special_seasoning'] = expected['kaleidoscope_grilling:special_seasoning_r8_v0']
        self.assertEqual(source['routes'], expected)
        self.assertEqual(Counter(row['texture'] for row in source['routes'].values()), {
            'textures/blocks/seasoning_bottle': 43,
            'textures/a2766_special_seasoning/palette_v5': 6,
            'textures/a2766_special_seasoning/palette_v6': 8,
            'textures/a2766_special_seasoning/palette_v7': 8,
        })

    def test_every_one_of_67_routes_has_one_geometry_controller_and_texture(self):
        self.assertEqual(len(self.routes), 67)
        derived = set()
        for item, d in self.routes.items():
            with self.subTest(item=item):
                self.assertEqual(d['identifier'], 'kaleidoscope_grilling:' + item)
                self.assertEqual(set(d['geometry']), {'default'})
                self.assertEqual(len(d['textures']), 1)
                self.assertEqual(len(d['render_controllers']), 1)
                controller = d['render_controllers'][0]
                self.assertIsInstance(controller, str, 'Single pass is unconditional')
                rc = self.controllers[controller]
                self.assertEqual(rc['geometry'], 'Geometry.default')
                self.assertEqual(len(rc['textures']), 1)
                texture = rc['textures'][0]
                self.assertRegex(texture, r'^Texture\.[a-zA-Z0-9_]+$')
                self.assertIn(texture.split('.', 1)[1], d['textures'])
                self.assertNotIn('arrays', rc)
                derived.add(d['geometry']['default'])
                g = self.geos[d['geometry']['default']]
                self.assertEqual((g['description']['texture_width'], g['description']['texture_height']), (128, 128))
                self.assertEqual(g['bones'][0], {'name': 'grip', 'pivot': [0, 24, 0], 'binding': 'q.item_slot_to_bone_name(context.item_slot)'})
                for b in g['bones'][1:]:
                    self.assertEqual(b.get('parent'), 'grip')
                    self.assertEqual(b.get('pivot'), [0, 24, 0])
                    self.assertNotIn('binding', b)
                    self.assertNotIn('rotation', b)
                self.assertEqual(effective_material(rc, 'shell', d['materials']), 'entity_alphablend')
                for b in g['bones'][1:]:
                    if b['name'] != 'shell' and b.get('cubes'):
                        self.assertEqual(effective_material(rc, b['name'], d['materials']), 'entity', 'Contents use opaque material')
        self.assertEqual(len(derived), 65)

    def test_atlas_keeps_every_original_rgba_pixel_and_has_18_opaque_color_tiles(self):
        texture_paths = {texture for d in self.routes.values() for texture in d['textures'].values()}
        self.assertEqual(len(texture_paths), 1)
        with Image.open(RP / (next(iter(texture_paths)) + '.png')) as image:
            atlas = image.convert('RGBA')
        self.assertEqual(atlas.size, (128, 128))
        for texture, (offset, _) in SOURCE_TEXTURES.items():
            with Image.open(RP / (texture + '.png')) as image:
                original = image.convert('RGBA')
            self.assertEqual(original.size, (32, 32))
            self.assertEqual(atlas.crop((offset, 0, offset + 32, 32)).tobytes(), original.tobytes(), 'All original pixels, including transparent RGB, must survive exactly: ' + texture)
        expected = {rgba(rgb) for pair in self.pairs.values() for rgb in pair}
        self.assertEqual(len(expected), 18)
        solid = Counter()
        for y in range(32, 128, 16):
            for x in range(0, 128, 16):
                colors = atlas.crop((x, y, x + 16, y + 16)).getcolors()
                if colors and len(colors) == 1 and colors[0][0] == 256 and colors[0][1] in expected:
                    solid[colors[0][1]] += 1
        self.assertEqual(set(solid), expected)
        self.assertTrue(all(count == 1 for count in solid.values()), 'Each distinct palette RGB occupies exactly one solid tile')

    def dynamic_assets(self):
        d = self.routes['empty_seasoning_bottle']
        other = self.routes['pending_seasoning']
        self.assertEqual(d['geometry'], other['geometry'])
        self.assertEqual(d['render_controllers'], other['render_controllers'])
        g = self.geos[d['geometry']['default']]
        return d, g, self.controllers[d['render_controllers'][0]]

    def test_144_dynamic_color_bones_match_all_pinned_tint_bounds_and_uv_colors(self):
        d, g, rc = self.dynamic_assets()
        self.assertEqual(len(g['bones']), 146)
        shell = next(b for b in g['bones'] if b['name'] == 'shell')
        original_shell = self.geos['geometry.kg_a286.kg_a2733.seasoning_bottle_hand']
        self.assertEqual(shell['cubes'], cubes(original_shell), 'Shell UV and cubes are byte-independent exact values')
        mask = load(FIXTURES / 'a2770/grilling/kaleidoscope_grilling/models/item/seasoning_states/pending_8.json')
        pinned = {}
        for tint in range(16):
            element = next(e for e in mask['elements'] if any(face.get('tintindex') == tint for face in e['faces'].values()))
            pinned[tint] = ([8 - element['to'][0], element['from'][1] + 18, element['from'][2] - 8], [element['to'][i] - element['from'][i] for i in range(3)], set(element['faces']))
        texture_path = next(iter(d['textures'].values()))
        with Image.open(RP / (texture_path + '.png')) as image:
            atlas = image.convert('RGBA')
        self.lookup = {}
        for b in g['bones'][1:]:
            if b['name'] == 'shell':
                continue
            with self.subTest(bone=b['name']):
                self.assertEqual(len(b['cubes']), 1)
                cube = b['cubes'][0]
                candidates = [t for t, (origin, size, _) in pinned.items() if cube['origin'] == origin and cube['size'] == size]
                self.assertEqual(len(candidates), 1)
                tint = candidates[0]
                expressions = [expression for row in rc.get('part_visibility', []) for pattern, expression in row.items() if pattern == b['name']]
                self.assertEqual(len(expressions), 1)
                m = re.fullmatch(r'\s*\(?\s*v\.kg_bottle_layer_(\d+)\s*==\s*(\d+)\s*\)?\s*', expressions[0])
                self.assertIsNotNone(m)
                layer, index = map(int, m.groups())
                self.assertEqual(layer, tint // 2)
                self.assertIn(index, range(1, 10))
                self.assertNotIn((tint, index), self.lookup)
                self.lookup[tint, index] = b['name']
                self.assertEqual(set(cube['uv']), pinned[tint][2])
                expected_color = rgba(self.pairs[index][tint % 2])
                for face in cube['uv'].values():
                    self.assertEqual(face['uv_size'], [8, 8])
                    x, y = face['uv']
                    self.assertEqual((x % 16, y % 16), (4, 4), 'Four-pixel inset within a solid 16px tile')
                    self.assertGreaterEqual(y, 32, 'Color tiles cannot overwrite any of four original textures')
                    colors = atlas.crop((x - 4, y - 4, x + 12, y + 12)).getcolors()
                    self.assertEqual(colors, [(256, expected_color)])
        self.assertEqual(set(self.lookup), {(tint, index) for tint in range(16) for index in range(1, 10)})

    def test_pending_half_reflection_preserves_java_order_in_held_and_placed(self):
        # Independent numeric regression: Java ingredient_0_a X [5.5, 8]
        # becomes Bedrock X [0, 2.5], retaining the first palette color.
        mask = load(FIXTURES / 'a2770/grilling/kaleidoscope_grilling/models/item/seasoning_states/pending_8.json')
        source_a = next(e for e in mask['elements'] if e['name'] == 'ingredient_0_a')
        self.assertEqual((source_a['from'][0], source_a['to'][0]), (5.5, 8))
        self.assertEqual({f['tintindex'] for f in source_a['faces'].values()}, {0})
        _, held, _ = self.dynamic_assets()
        placed = self.geos['geometry.kg_a2770.pending_combined']
        self.assertEqual(len(next(b for b in held['bones'] if b['name'] == 'shell')['cubes']), 9)
        for layer in range(8):
            for half in range(2):
                tint = layer * 2 + half
                expected_x = (0, 2.5) if half == 0 else (-2.5, 0)
                original = self.geos[f'geometry.kg_a2770.pending_{tint}']['bones'][0]['cubes'][0]
                self.assertEqual((original['origin'][0], original['origin'][0] + original['size'][0]), expected_x)
                for geometry, y_offset in [(held, 18), (placed, 0)]:
                    bones = {b['name']: b for b in geometry['bones']}
                    for value in range(1, 10):
                        with self.subTest(layer=layer, half=half, value=value, geometry=geometry['description']['identifier']):
                            cube = bones[f'pending_{tint}_color_{value}']['cubes'][0]
                            self.assertEqual((cube['origin'][0], cube['origin'][0] + cube['size'][0]), expected_x)
                            self.assertEqual(cube['origin'][1], 0.5 + layer * 0.625 + y_offset)
                            self.assertEqual(cube['origin'][2], -2.5)
                            self.assertEqual(cube['size'], [2.5, 0.625, 5])

    def test_each_tint_is_one_hot_for_every_ingredient_and_unknown_fallback_in_all_eight_layers(self):
        # Reuse the independently built tint/UV lookup, not the generator's names.
        self.test_144_dynamic_color_bones_match_all_pinned_tint_bounds_and_uv_colors()
        _, g, rc = self.dynamic_assets()
        names = [b['name'] for b in g['bones'] if b['name'] not in ['grip', 'shell']]
        for active_layer in range(8):
            for index in range(10):
                with self.subTest(layer=active_layer, index=index):
                    values = [0] * 8
                    values[active_layer] = index
                    visible = {name for name in names if bone_visibility(rc, name, values)}
                    expected = set() if index == 0 else {self.lookup[active_layer * 2, index], self.lookup[active_layer * 2 + 1, index]}
                    self.assertEqual(visible, expected)
                    self.assertTrue(bone_visibility(rc, 'shell', values))
        for index in range(1, 10):
            visible = {name for name in names if bone_visibility(rc, name, [index] * 8)}
            self.assertEqual(visible, {self.lookup[tint, index] for tint in range(16)})
        uri = (BP / 'scripts/bottle_held_visual_core.js').as_uri()
        script = 'import {bottleHeldVisualPlan} from ' + json.dumps(uri) + ';\n'
        script += 'const ids=' + json.dumps(self.ids) + ';\n'
        script += "for(const id of ['kaleidoscope_grilling:empty_seasoning_bottle','kaleidoscope_grilling:pending_seasoning']){for(let i=0;i<8;i++){const a=Array(8).fill(ids[i]);if(JSON.stringify(bottleHeldVisualPlan(id,a))!==JSON.stringify(Array(8).fill(i+1)))throw Error('Ingredient index mismatch '+i)}if(JSON.stringify(bottleHeldVisualPlan(id,Array(8).fill('external:unknown')))!==JSON.stringify(Array(8).fill(9)))throw Error('Unknown fallback mismatch')}"
        subprocess.run(['node', '--input-type=module', '-'], input=script, text=True, capture_output=True, check=True)

    def test_all_64_fixed_variants_preserve_original_shell_contents_and_uv_exactly(self):
        for r in range(1, 9):
            for v in range(8):
                with self.subTest(remaining=r, variant=v):
                    d = self.routes[f'special_seasoning_r{r}_v{v}']
                    expected_identifier = f'geometry.kg_bottle_held.fixed.r{r}.v{v}'
                    self.assertEqual(d['geometry']['default'], expected_identifier)
                    g = self.geos[expected_identifier]
                    original_v = ORIGINAL_ROUTE_VARIANTS[r][v]
                    original_id = f'geometry.kg_a286.kg_a2766.special_seasoning.r{r}.v{original_v}'
                    bones = {b['name']: b for b in g['bones']}
                    offset = SOURCE_TEXTURES[original_texture(r, v)][0]
                    self.assertEqual(bones['shell']['cubes'], shifted_cubes(cubes(self.geos[original_id]), offset))
                    actual_contents = [c for b in g['bones'] if b['name'] not in ['grip', 'shell'] for c in b.get('cubes', [])]
                    expected_contents = shifted_cubes(cubes(self.geos[original_id + '.contents']), offset)
                    self.assertEqual(actual_contents, expected_contents)
                    for actual, expected in zip(bones['shell']['cubes'] + actual_contents, shifted_cubes(cubes(self.geos[original_id]), offset) + expected_contents):
                        self.assertEqual(list(actual['uv']), list(expected['uv']), 'Face order is preserved')
        self.assertEqual(self.routes['special_seasoning']['geometry'], self.routes['special_seasoning_r8_v0']['geometry'])


if __name__ == '__main__':
    unittest.main()
