"""Java parity repairs; add uncovered plant and placed-display paths to the chain."""
from pathlib import Path
import itertools
import json
import os
import subprocess
import sys
from verify_a28117 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / 'projects/grilling/gameplay_core/behavior_pack'


def check_farming_data():
    """Guard the audited Java recipe inputs and compost rates, including mixed fences.

    Vanilla fences/wooden_fences were read from SHA1-verified Mojang client JARs:
    1.20.1 0c3ec587af28e5a785c0b4a7b8a30f9a8f78f838;
    1.21.1 30c73b1c5da787909b2f73340419fdf13b9def88.
    Both have these 12 members. This is data coverage, not native recipe execution.
    """
    load = lambda path: json.loads(path.read_text())
    vat = load(BP / 'recipes/big_vat.json')['minecraft:recipe_shaped']
    assert vat['pattern'] == ['B B', 'BUB', 'BBB']
    assert vat['key'] == {'B': {'item': 'minecraft:brick'}, 'U': {'item': 'minecraft:bucket'}}
    assert vat['unlock'] == [{'item': 'minecraft:brick'}]
    assert vat['result'] == {'item': 'kaleidoscope_grilling:big_vat', 'count': 1}
    fences = {'minecraft:' + name + '_fence' for name in (
        'oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak',
        'mangrove', 'cherry', 'bamboo', 'crimson', 'warped', 'nether_brick',
    )}
    pairs, identifiers = set(), set()
    paths = sorted((BP / 'recipes').rglob('oil_press*.json'))
    assert len(paths) == 78
    for path in paths:
        recipe = load(path)['minecraft:recipe_shaped']
        identifier = recipe['description']['identifier']
        assert identifier not in identifiers, path
        identifiers.add(identifier)
        assert recipe['tags'] == ['crafting_table']
        assert recipe['pattern'] == ['LIL', 'F G', 'LHL']
        keys = recipe['key']
        assert set(keys) == {'L', 'I', 'F', 'G', 'H'}
        assert keys['L'] == {'tag': 'minecraft:logs'}
        assert keys['I'] == {'item': 'minecraft:iron_ingot'}
        assert keys['H'] == {'item': 'minecraft:hopper'}
        left, right = keys['F']['item'], keys['G']['item']
        assert left in fences and right in fences, path
        assert recipe['assume_symmetry'] is True
        assert recipe['unlock'] == [{'item': 'minecraft:iron_ingot'}]
        assert recipe['result'] == {'item': 'kaleidoscope_grilling:oil_press', 'count': 1}
        pairs.update(((left, right), (right, left)))
    assert pairs == set(itertools.product(fences, repeat=2))
    for name, chance in [('houttuynia', 65), ('pepper_sapling', 30), ('pepper_leaves', 30)]:
        item = load(BP / f'items/{name}.json')['minecraft:item']
        assert item['components']['minecraft:compostable'] == {'composting_chance': chance}
    print('G118 Java farming data PASS: 7 bricks, 144 directed fence combinations and 3 compost rates')


def main(expected_version=(2, 8, 118)):
    previous(expected_version=expected_version)
    check_farming_data()
    subprocess.run([
        'node', '--experimental-vm-modules', '--test',
        'development/gameplay_core/test_plant_fertilizer_runtime.mjs',
    ], cwd=ROOT, check=True)
    subprocess.run([
        'node', '--test', 'development/gameplay_core/test_plate_recipe_visual.mjs',
    ], cwd=ROOT, check=True)
    subprocess.run([
        sys.executable, '-B', 'tools/build_plate_display.py', '--check',
    ], cwd=ROOT, check=True)
    print('G118 cooking, storage, farming and placed-display source repairs PASS; native/client acceptance remain separate')


if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
