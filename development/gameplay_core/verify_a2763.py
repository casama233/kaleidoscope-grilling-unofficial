from __future__ import annotations

from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'projects/grilling/gameplay_core'
BP = PROJECT / 'behavior_pack'
RP = PROJECT / 'resource_pack'
DEV = Path(__file__).resolve().parent
VERSION = [2, 7, 63]

def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--compiled', action='store_true')
    args = parser.parse_args()

    bp = load(BP / 'manifest.json')
    rp = load(RP / 'manifest.json')
    assert bp['header']['version'] == VERSION
    assert rp['header']['version'] == VERSION
    assert bp['header']['name'] == 'Kaleidoscope Grilling A2.7.63 Client Visual Gate BP'
    assert rp['header']['name'] == 'Kaleidoscope Grilling A2.7.63 Client Visual Gate RP'

    gate = DEV / 'verify_visual_refs.py'
    assert gate.is_file()
    subprocess.run([sys.executable, str(gate)], check=True)

    vat = load(BP / 'blocks/big_vat.json')['minecraft:block']
    default_fluid = vat['components']['minecraft:material_instances']['fluid']['texture']
    assert default_fluid == 'still_water_grey'
    fluid_by_state = {}
    for perm in vat.get('permutations', []):
        cond = str(perm.get('condition', ''))
        mats = perm.get('components', {}).get('minecraft:material_instances', {})
        if not isinstance(mats, dict) or 'fluid' not in mats:
            continue
        if "'water'" in cond: fluid_by_state['water'] = mats['fluid']['texture']
        if "'lava'" in cond: fluid_by_state['lava'] = mats['fluid']['texture']
    assert fluid_by_state == {'water':'still_water_grey','lava':'still_lava'}
    terrain = load(RP / 'textures/terrain_texture.json')['texture_data']
    assert 'kg_a26_water' not in terrain and 'kg_a26_lava' not in terrain
    # Preserve the A2733 corrective: hand-space geometry is baked; do not re-apply A2726 hold animation.
    for item in ('empty_seasoning_bottle','pending_seasoning','special_seasoning'):
        desc = load(RP / 'attachables' / f'{item}.attachable.json')['minecraft:attachable']['description']
        assert desc['geometry'] == {'default':'geometry.kg_a2733.seasoning_bottle_hand'}
        assert desc['render_controllers'] == ['controller.render.kg_a2733.seasoning_bottle_hand']
        assert 'animations' not in desc
        assert 'scripts' not in desc

    # Skewer hold correction remains wired for all bite-stage attachables.
    attachables = sorted((RP / 'attachables').glob('*.attachable.json'))
    skewer = []
    for path in attachables:
        desc = load(path)['minecraft:attachable']['description']
        if any(str(g).startswith('geometry.kg_a22.') for g in desc.get('geometry',{}).values()):
            skewer.append(path)
            animations = desc.get('animations',{})
            scripts = desc.get('scripts',{}).get('animate',[])
            assert animations.get('hold_first_person') == 'animation.kaleidoscope_grilling.a2725.skewer_hold_first_person', path
            assert animations.get('hold_third_person') == 'animation.kaleidoscope_grilling.a2725.skewer_hold_third_person', path
            aliases = []
            for entry in scripts:
                if isinstance(entry,str): aliases.append(entry)
                elif isinstance(entry,dict): aliases.extend(entry.keys())
            assert 'hold_first_person' in aliases and 'hold_third_person' in aliases, path
    assert len(skewer) == 39, len(skewer)

    report = load(PROJECT / 'reports/a2763-client-visual-reference-gate.json')
    assert report['version'] == 'A2.7.63'
    assert report['visual_reference_gate_added'] is True
    assert report['seasoning_a2733_double_transform_guard'] is True
    assert report['skewer_attachable_count_guard'] == 39
    assert report['big_vat_fluid_texture_fix']['replacement_vanilla_atlas_keys'] == ['still_water_grey','still_lava']
    assert report['gameplay_logic_changed'] is False
    assert report['minecraft_tested'] is False
    assert report['client_visuals_tested'] is False

    print(json.dumps({
        'version':'A2.7.63',
        'client_visual_reference_gate':True,
        'skewer_attachables':len(skewer),
        'compiled_requested':args.compiled,
        'minecraft_tested':False,
        'client_visuals_tested':False,
    }, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
