"""Reflow existing source-textured rack parts onto the runtime's fixed 5+4 layout.

This is the owner's direct-interaction adaptation, not unchanged Java geometry.
Idempotent: accepts either the prior source-converted models or its own output.
No textures, UUIDs, inventory indices, author packages or worlds are modified.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / 'projects/grilling/gameplay_core/behavior_pack'
RP = ROOT / 'projects/grilling/gameplay_core/resource_pack'


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    module = (BP / 'scripts/advanced_rack_layout.js').as_uri()
    layout = json.loads(subprocess.check_output([
        'node', '--input-type=module', '-e',
        f"import {{RACK_SEASONING_X,RACK_TOOL_X,RACK_OCCUPANCY_STATE}} from '{module}';"
        "process.stdout.write(JSON.stringify({seasonings:RACK_SEASONING_X,tools:RACK_TOOL_X,state:RACK_OCCUPANCY_STATE}));"
    ], text=True))
    models = RP / 'models/blocks'
    base = load(models / 'advanced_rack_0.geo.json')
    jar_model = load(models / 'advanced_rack_1.geo.json')
    old_bones = base['minecraft:geometry'][0]['bones']
    already_adapted = any(b['name'] == 'rack_tool_hook_0' for b in old_bones)
    if already_adapted:
        board = [deepcopy(b) for b in old_bones if not b['name'].startswith(('rack_tool_', 'rack_seasoning_'))]
        hook = [deepcopy(b) for b in old_bones if b.get('parent') == 'rack_tool_hook_0']
        hook_center = layout['tools'][0] * 16
        jar = deepcopy(next(b['cubes'] for b in old_bones if b['name'] == 'rack_seasoning_0'))
        jar_center = layout['seasonings'][0] * 16
    else:
        # Existing source-conversion part groups: board/shelves, first complete
        # hook (including UV-corrected faces), first source seasoning jar.
        board = deepcopy(old_bones[:8])
        hook = deepcopy(old_bones[8:15])
        hook_center = -4.45
        jar = [deepcopy(c) for b in jar_model['minecraft:geometry'][0]['bones'][29:] for c in b.get('cubes', [])]
        jar_center = -4.75
    bones = board
    for index, x in enumerate(layout['tools']):
        parent = f'rack_tool_hook_{index}'
        bones.append({'name': parent, 'parent': 'root', 'pivot': [0, 0, 0]})
        for part, source in enumerate(hook):
            bone = deepcopy(source)
            bone['name'] = f'rack_tool_part_{index}_{part}'
            bone['parent'] = parent
            for cube in bone.get('cubes', []):
                cube['origin'][0] = round(cube['origin'][0] + x * 16 - hook_center, 9)
            bones.append(bone)
    for index, x in enumerate(layout['seasonings']):
        cubes = deepcopy(jar)
        for cube in cubes:
            cube['origin'][0] = round(cube['origin'][0] + x * 16 - jar_center, 9)
        bones.append({'name': f'rack_seasoning_{index}', 'parent': 'root', 'pivot': [0, 0, 0], 'cubes': cubes})
    # Preserve the five established geometry identifiers and spice state values
    # for saved permutations, but every variant now has the same fixed layout.
    for level in range(5):
        model = deepcopy(base)
        geometry = model['minecraft:geometry'][0]
        geometry['description']['identifier'] = f'geometry.kg_a1.advanced_rack_{level}'
        geometry['bones'] = deepcopy(bones)
        save(models / f'advanced_rack_{level}.geo.json', model)
    block_path = BP / 'blocks/advanced_rack_block.json'
    block = load(block_path)
    data = block['minecraft:block']
    data['description']['states'][layout['state']] = list(range(32))

    def geometry(level):
        return {'identifier': f'geometry.kg_a1.advanced_rack_{level}', 'bone_visibility': {
            f'rack_seasoning_{slot}':
                f"math.floor(q.block_state('{layout['state']}') / {2**slot}) - 2 * math.floor(q.block_state('{layout['state']}') / {2**(slot+1)}) == 1"
            for slot in range(5)
        }}

    data['components']['minecraft:geometry'] = geometry(0)
    for level, permutation in enumerate(data['permutations'][:5]):
        permutation['components']['minecraft:geometry'] = geometry(level)
    save(block_path, block)
    save(ROOT / 'development/gameplay_core/a2746_advanced_rack_block.json', block)
    print('Fixed five seasoning cells and four source-textured hooks generated; not client acceptance')


if __name__ == '__main__':
    main()
