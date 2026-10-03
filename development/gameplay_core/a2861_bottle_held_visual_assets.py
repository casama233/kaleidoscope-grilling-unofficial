"""Project Java pending ingredient layers onto the existing bottle hand socket.

Item identities and native metadata stay authoritative. This generator changes
only empty/pending render routes; native rendering remains a separate check.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import json
import re
import a2770_placed_visual_assets as placed

ROOT = Path(__file__).resolve().parents[2]
RP = ROOT / 'projects/grilling/gameplay_core/resource_pack'
BP = ROOT / 'projects/grilling/gameplay_core/behavior_pack'
NS = 'kaleidoscope_grilling:'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def ingredient_ids():
    source = (BP / 'scripts/a2743_seasoning_contract_core.js').read_text()
    body = re.search(r'SEASONING_KINDS=Object.freeze\((\{.*?\})\)', source, re.S).group(1)
    ids = sorted(re.findall(r"'([^']+)'\s*:", body))
    assert len(ids) == 8 and len(set(ids)) == 8
    return ids


def build():
    # Read the same pinned source mask, bounds and palette as the placed route.
    placed.OUT.clear()
    placed.SOURCES.clear()
    placed.build()
    data = (BP / 'scripts/a2770_placed_visual_data.js').read_text()
    palette = json.loads(re.search(r'INGREDIENT_COLORS=Object.freeze\((\{.*?\})\)', data).group(1))
    color_index = json.loads(re.search(r'PLACED_TINT_INDEX=Object.freeze\((\{.*?\})\)', data).group(1))
    pairs = [[0xB86B45, 0xE0A56A]] + [palette.get(i, [0xB86B45, 0xE0A56A]) for i in ingredient_ids()] + [[0xB86B45, 0xE0A56A]]
    source = load(RP / 'models/entity/a2770_placed/seasoning.geo.json')
    index = {g['description']['identifier']: g for g in source['minecraft:geometry']}
    shell = load(RP / 'models/entity/a286_hand/kg_a2733.seasoning_bottle_hand.geo.json')['minecraft:geometry'][0]
    # One bound root owns both shell and fill. Separate geometry instances can
    # otherwise receive different attachable pose transforms in the client.
    combined = deepcopy(shell)
    combined['description']['identifier'] = 'geometry.kg_bottle_held.combined'
    shell_bone = deepcopy(shell['bones'][0])
    shell_bone.update(name='shell', parent='grip')
    shell_bone.pop('binding', None)
    combined['bones'] = [
        {'name': 'grip', 'pivot': [0, 24, 0],
         'binding': 'q.item_slot_to_bone_name(context.item_slot)'}, shell_bone]
    controllers = {}
    result = {}
    for item in ['empty_seasoning_bottle', 'pending_seasoning']:
        path = RP / 'attachables' / (item + '.attachable.json')
        doc = load(path)
        desc = doc['minecraft:attachable']['description']
        # Both mechanic identities use the same empty shell plus their real
        # ordered ingredient layers. Pending no longer borrows a fixed r4 fill.
        desc['geometry'] = {'default': 'geometry.kg_bottle_held.combined'}
        desc['materials']['contents'] = 'entity'
        desc['render_controllers'] = []
        # item_slot exists in attachable animation context, but not render
        # controller context (confirmed by the actual .61 client error).
        # Resolve the hand and numeric player properties here, then share only
        # initialized numeric variables with the render controller.
        scripts = desc.setdefault('scripts', {})
        for phase in ['initialize', 'pre_animation']:
            scripts[phase] = [s for s in scripts.get(phase, [])
                              if not s.startswith('v.kg_bottle_')]
        scripts['initialize'].append('v.kg_bottle_off_hand = 0;')
        scripts['pre_animation'].append("v.kg_bottle_off_hand = c.item_slot == 'off_hand';")
        for layer in range(8):
            var = 'v.kg_bottle_layer_' + str(layer)
            # The stored properties belong to the player, not this attachable.
            # Native armor pre_animation uses owning_entity redirection too.
            reads = []
            for hand in ['off', 'main']:
                name = NS + 'bottle_' + hand + '_' + str(layer)
                reads.append("(c.owning_entity->q.has_property('" + name + "') ? c.owning_entity->q.property('" + name + "') : 0)")
            prop = '(v.kg_bottle_off_hand ? ' + reads[0] + ' : ' + reads[1] + ')'
            scripts['initialize'].append(var + ' = 0;')
            scripts['pre_animation'].append(var + ' = math.floor(math.clamp(' + prop + ', 0, 9));')
        for rgb, idx in color_index.items():
            desc['textures']['pending_color_' + str(idx)] = 'textures/a2770_placed/pending_color_' + str(idx)
        for tint in range(16):
            alias = 'pending_' + str(tint)
            layer, shade = divmod(tint, 2)
            value = 'v.kg_bottle_layer_' + str(layer)
            rc = 'controller.render.kg_bottle_held.' + alias
            desc['render_controllers'].append({rc: value + ' > 0'})
            textures = ['Texture.pending_color_' + str(color_index[str(pair[shade])]) for pair in pairs]
            controllers[rc] = {'arrays': {'textures': {'Array.colors': textures}},
                'geometry': 'Geometry.default', 'materials': [{'*': 'Material.contents'}],
                'part_visibility': [{'*': False}, {'grip': True}, {alias: True}],
                'textures': ['Array.colors[' + value + ']']}
            if item == 'empty_seasoning_bottle':
                bone = deepcopy(index['geometry.kg_a2770.' + alias]['bones'][0])
                bone.update(name=alias, parent='grip', pivot=[0, 24, 0])
                bone.pop('binding', None)
                for cube in bone.get('cubes', []):
                    cube['origin'][1] += 18
                    # Solid palettes need no atlas offsets. Use this geometry's
                    # texture dimensions so every sample stays in its texture.
                    cube['uv'] = {face: {'uv': [0, 0], 'uv_size': [32, 32]}
                                  for face in cube['uv']}
                combined['bones'].append(bone)
        desc['render_controllers'].append('controller.render.kg_bottle_held.shell')
        result[path] = doc
    controllers['controller.render.kg_bottle_held.shell'] = {
        'geometry': 'Geometry.default', 'materials': [{'*': 'Material.default'}],
        'part_visibility': [{'*': False}, {'grip': True}, {'shell': True}],
        'textures': ['Texture.default']}
    result[RP / 'models/entity/bottle_held_contents.geo.json'] = {'format_version': '1.16.0', 'minecraft:geometry': [combined]}
    result[RP / 'render_controllers/bottle_held_contents.render_controllers.json'] = {'format_version': '1.8.0', 'render_controllers': controllers}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, doc in build().items():
        if args.check:
            assert load(path) == doc, path
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(doc, indent=2) + '\n')
    print('Java bottle held contents: 16 exact half-layers; empty/pending native identities preserved')


if __name__ == '__main__':
    main()
