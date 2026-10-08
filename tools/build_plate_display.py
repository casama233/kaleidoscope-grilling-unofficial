"""Reuse the current audited grill geometry/palette for plate and wall copies.

This generates only transient display assets. It does not edit meshes, textures,
station storage, or packaging. Java 1.1.1 SkewerPlateRenderer supplies LAYOUTS and
the cancelled FIXED transform; SkewerRecipeBlockRenderer supplies the flattened
wall fallback. Native client acceptance remains a separate gate.
"""
from pathlib import Path
import argparse
import json
import math

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'projects/grilling/gameplay_core'
BP, RP = P / 'behavior_pack', P / 'resource_pack'
NS = 'kaleidoscope_grilling:'


def dump(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def build():
    server = json.loads((BP / 'entities/grill_food_visual.json').read_text())
    desc = server['minecraft:entity']['description']
    desc['identifier'] = NS + 'plate_food_visual'
    for name in ('flips', 'hop'):
        del desc['properties'][NS + name]
    desc['properties'][NS + 'display_mode'] = {'type': 'int', 'range': [0, 1], 'default': 0, 'client_sync': True}

    client = json.loads((RP / 'entity/grill_food_visual.entity.json').read_text())
    desc = client['minecraft:client_entity']['description']
    desc['identifier'] = NS + 'plate_food_visual'
    # Keep exact current model and food-palette bindings. Plate copies have no
    # grill flip history/hop animation and never mutate their source ItemStack.
    desc['scripts'] = {'pre_animation': [line for line in desc['scripts']['pre_animation'] if 'flip' not in line], 'animate': ['pose']}
    desc['animations'] = {'pose': 'animation.kg_station.plate_food'}
    wall = "q.property('kaleidoscope_grilling:display_mode') == 1"
    secret = "q.property('kaleidoscope_grilling:model') == 114"
    depth = .1 / 2.75
    # Current fixed geometry has y = source_y - 1; secret has y = source_y.
    # The plate's cancelled FIXED transform is scale 1.2, offset (0,7.8,1.8)
    # about source centre (8,8,8). Wall fallback is .5 * Rz(-55) * depth * FIXED.
    animation = {'format_version': '1.8.0', 'animations': {'animation.kg_station.plate_food': {'loop': True, 'bones': {'root': {
        'rotation': [f'{wall} ? 90 : 0', 0, f'{wall} ? -125 : 0'],
        'position': [
            f'{wall} ? {-1.125 * math.sin(math.radians(55)):.12f} : 0',
            f'{wall} ? {1.125 * math.cos(math.radians(55)):.12f} : ({secret} ? -1.8 : -0.6)',
            f'{wall} ? ({secret} ? {-1.125 * depth:.12f} : {-0.375 * depth:.12f}) : 1.8',
        ],
        'scale': [f'{wall} ? 0.75 : 1.2', f'{wall} ? {0.75 * depth:.12f} : 1.2', f'{wall} ? 0.75 : 1.2'],
    }}}}}
    return {
        BP / 'entities/plate_food_visual.json': dump(server),
        RP / 'entity/plate_food_visual.entity.json': dump(client),
        RP / 'animations/plate_food_visual.animation.json': dump(animation),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = build()
    if args.check:
        for path, data in output.items():
            assert path.exists() and path.read_bytes() == data, f'stale plate display asset: {path.relative_to(ROOT)}'
        print(f'plate display assets current: {len(output)}; native rendering not simulated')
    else:
        for path, data in output.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        print(f'wrote {len(output)} plate display assets from current grill palette')
