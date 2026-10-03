"""Single-pass Java bottles with static palette UV candidates.

The owner verified the two-layer/default-finished probe. The complete expansion
still needs native acceptance. Identities, metadata and gameplay stay unchanged.
"""
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import argparse
import json
import re
from PIL import Image
import a2770_placed_visual_assets as placed

ROOT = Path(__file__).resolve().parents[2]
RP = ROOT / 'projects/grilling/gameplay_core/resource_pack'
BP = ROOT / 'projects/grilling/gameplay_core/behavior_pack'
NS = 'kaleidoscope_grilling:'
ATLAS = 'textures/held/bottle_shell_palette'
SOURCE_TEXTURES = ('textures/blocks/seasoning_bottle',
                   'textures/a2766_special_seasoning/palette_v5',
                   'textures/a2766_special_seasoning/palette_v6',
                   'textures/a2766_special_seasoning/palette_v7')


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def ingredient_ids():
    source = (BP / 'scripts/a2743_seasoning_contract_core.js').read_text()
    body = re.search(r'SEASONING_KINDS=Object.freeze\((\{.*?\})\)', source, re.S).group(1)
    ids = sorted(re.findall(r"'([^']+)'\s*:", body))
    assert len(ids) == 8 and len(set(ids)) == 8
    return ids


def palette_pairs():
    data = (BP / 'scripts/a2770_placed_visual_data.js').read_text()
    palette = json.loads(re.search(r'INGREDIENT_COLORS=Object.freeze\((\{.*?\})\)', data).group(1))
    fallback = [0xB86B45, 0xE0A56A]
    # Preserve the visual runtime index order and the unknown fallback.
    return [fallback] + [palette.get(i, fallback) for i in ingredient_ids()] + [fallback]


def atlas_image(pairs):
    atlas = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    originals = []
    for i, texture in enumerate(SOURCE_TEXTURES):
        with Image.open(RP / (texture + '.png')) as im:
            original = im.convert('RGBA')
        assert original.size == (32, 32)
        atlas.paste(original, (i * 32, 0))
        originals.append(original)
    slots = [(x * 16, y * 16) for y in range(2, 8) for x in range(8)]
    positions = {}
    for pair in pairs[1:]:
        for rgb in pair:
            if rgb in positions:
                continue
            x, y = slots.pop(0)
            positions[rgb] = (x, y)
            rgba = ((rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255, 255)
            atlas.paste(Image.new('RGBA', (16, 16), rgba), (x, y))
    for i, original in enumerate(originals):
        assert atlas.crop((i * 32, 0, i * 32 + 32, 32)).tobytes() == original.tobytes()
    return atlas, positions


def bound_root():
    return {'name': 'grip', 'pivot': [0, 24, 0],
            'binding': 'q.item_slot_to_bone_name(context.item_slot)'}


def child(source, name):
    bone = deepcopy(source)
    bone.update(name=name, parent='grip', pivot=[0, 24, 0])
    bone.pop('binding', None)
    return bone


def shift_texture_uv(bone, offset):
    for cube in bone.get('cubes', []):
        uv = cube.get('uv')
        if isinstance(uv, list):
            for axis in range(2):
                uv[axis] += offset[axis]
        else:
            for face in uv.values():
                for axis in range(2):
                    face['uv'][axis] += offset[axis]


def combined_shell(shell, identifier):
    assert len(shell['bones']) == 1
    geometry = deepcopy(shell)
    assert geometry['description']['texture_width'] == 32
    assert geometry['description']['texture_height'] == 32
    # Original UV numbers retain their exact original pixel coordinates.
    geometry['description'].update(identifier=identifier, texture_width=128, texture_height=128)
    geometry['bones'] = [bound_root(), child(shell['bones'][0], 'shell')]
    return geometry


def update_numeric_scripts(desc):
    # item_slot is attachable-animation context, not render-controller context.
    scripts = desc.setdefault('scripts', {})
    for phase in ['initialize', 'pre_animation']:
        scripts[phase] = [s for s in scripts.get(phase, []) if not s.startswith('v.kg_bottle_')]
    scripts['initialize'].append('v.kg_bottle_off_hand = 0;')
    scripts['pre_animation'].append("v.kg_bottle_off_hand = c.item_slot == 'off_hand';")
    for layer in range(8):
        var = 'v.kg_bottle_layer_' + str(layer)
        reads = []
        for hand in ['off', 'main']:
            name = NS + 'bottle_' + hand + '_' + str(layer)
            reads.append("(c.owning_entity->q.has_property('" + name + "') ? c.owning_entity->q.property('" + name + "') : 0)")
        prop = '(v.kg_bottle_off_hand ? ' + reads[0] + ' : ' + reads[1] + ')'
        scripts['initialize'].append(var + ' = 0;')
        scripts['pre_animation'].append(var + ' = math.floor(math.clamp(' + prop + ', 0, 9));')


def route(desc, identifier, controller):
    desc['geometry'] = {'default': identifier}
    desc['textures'] = {'default': ATLAS}
    desc['materials']['contents'] = 'entity'
    desc['render_controllers'] = [controller]


def build():
    placed.OUT.clear()
    placed.SOURCES.clear()
    placed.build()
    pairs = palette_pairs()
    atlas, positions = atlas_image(pairs)
    palette_png = BytesIO()
    atlas.save(palette_png, format='PNG', compress_level=9)
    result = {RP / (ATLAS + '.png'): palette_png.getvalue()}
    placed_index = {g['description']['identifier']: g for g in
                    load(RP / 'models/entity/a2770_placed/seasoning.geo.json')['minecraft:geometry']}
    shell = load(RP / 'models/entity/a286_hand/kg_a2733.seasoning_bottle_hand.geo.json')['minecraft:geometry'][0]
    combined = combined_shell(shell, 'geometry.kg_bottle_held.combined')
    visibility = [{'*': False}, {'grip': True}, {'shell': True}]
    for tint in range(16):
        for value in range(1, 10):
            name = f'pending_{tint}_color_{value}'
            source = placed_index[f'geometry.kg_a2770.pending_{tint}']['bones'][0]
            bone = child(source, name)
            x, y = positions[pairs[value][tint % 2]]
            for cube in bone.get('cubes', []):
                cube['origin'][1] += 18
                cube['uv'] = {face: {'uv': [x + 4, y + 4], 'uv_size': [8, 8]}
                              for face in cube['uv']}
            combined['bones'].append(bone)
            visibility.append({name: f'v.kg_bottle_layer_{tint // 2} == {value}'})
    materials = [{'*': 'Material.contents'}, {'shell': 'Material.default'}]
    controllers = {
        'controller.render.kg_bottle_held.dynamic': {
            'geometry': 'Geometry.default', 'materials': materials,
            'textures': ['Texture.default'], 'part_visibility': visibility},
        'controller.render.kg_bottle_held.fixed': {
            'geometry': 'Geometry.default', 'materials': materials,
            'textures': ['Texture.default']}}
    for item in ['empty_seasoning_bottle', 'pending_seasoning']:
        path = RP / 'attachables' / (item + '.attachable.json')
        doc = load(path)
        desc = doc['minecraft:attachable']['description']
        assert desc['identifier'] == NS + item
        update_numeric_scripts(desc)
        route(desc, 'geometry.kg_bottle_held.combined', 'controller.render.kg_bottle_held.dynamic')
        result[path] = doc

    # Original fixed shell/content geometries remain immutable source inputs.
    # Freeze their exact alias mapping, including original fallback variants.
    original_index = {}
    for path in sorted((RP / 'models').rglob('*.geo.json')):
        if path.name == 'bottle_held_contents.geo.json':
            continue
        for geometry in load(path)['minecraft:geometry']:
            original_index[geometry['description']['identifier']] = geometry
    source_routes = load(ROOT / 'development/gameplay_core/fixtures/bottle-fixed-source-routes.json')['routes']
    fixed = {}
    files = sorted((RP / 'attachables').glob('special_seasoning*.attachable.json'))
    assert len(files) == len(source_routes) == 65
    for path in files:
        item = path.name.removesuffix('.attachable.json')
        if item == 'special_seasoning':
            remaining, variant = 8, 0
        else:
            match = re.fullmatch(r'special_seasoning_r([1-8])_v([0-7])', item)
            assert match, item
            remaining, variant = map(int, match.groups())
        identifier = f'geometry.kg_bottle_held.fixed.r{remaining}.v{variant}'
        source = source_routes[NS + item]
        assert source['texture'] in SOURCE_TEXTURES
        if identifier not in fixed:
            original_shell = original_index[source['geometry']['default']]
            original_fill = original_index[source['geometry']['contents']]
            geometry = combined_shell(original_shell, identifier)
            assert len(original_fill['bones']) == 1
            assert original_fill['description']['texture_width'] == 32
            assert original_fill['description']['texture_height'] == 32
            geometry['bones'].append(child(original_fill['bones'][0], 'contents'))
            offset = (SOURCE_TEXTURES.index(source['texture']) * 32, 0)
            for bone in geometry['bones'][1:]:
                shift_texture_uv(bone, offset)
            fixed[identifier] = geometry
        else:
            # Default SPECIAL shares exactly the r8.v0 source route.
            assert fixed[identifier]['bones'][1]['cubes'] == original_index[source['geometry']['default']]['bones'][0]['cubes']
            assert fixed[identifier]['bones'][2]['cubes'] == original_index[source['geometry']['contents']]['bones'][0]['cubes']
        doc = load(path)
        desc = doc['minecraft:attachable']['description']
        assert desc['identifier'] == NS + item
        route(desc, identifier, 'controller.render.kg_bottle_held.fixed')
        result[path] = doc
    assert len(fixed) == 64
    result[RP / 'models/entity/bottle_held_contents.geo.json'] = {
        'format_version': '1.16.0', 'minecraft:geometry': [combined, *fixed.values()]}
    result[RP / 'render_controllers/bottle_held_contents.render_controllers.json'] = {
        'format_version': '1.8.0', 'render_controllers': controllers}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, doc in build().items():
        if args.check:
            assert (path.read_bytes() == doc if isinstance(doc, bytes) else load(path) == doc), path
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(doc, bytes):
                path.write_bytes(doc)
            else:
                path.write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('67 bottle attachables: one RC each; 8 dynamic layers and 64 fixed variants; native expansion acceptance pending')


if __name__ == '__main__':
    main()
