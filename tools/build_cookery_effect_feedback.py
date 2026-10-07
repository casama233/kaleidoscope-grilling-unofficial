"""Build owned Cookery feedback from reviewed public source; no host replacements.

Only the event and free-flight provider are implemented. PlayerCloudParticle's
nearest-player attraction and actual client rendering remain separate gaps.
"""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'development/gameplay_core/fixtures/java-cookery-effect-feedback-160.json'
OUT = ROOT / 'projects/grilling/gameplay_core/resource_pack/particles/feedback_cloud.json'


def build(check=False):
    fixture = json.loads(FIXTURE.read_text())
    data = copy.deepcopy(fixture['cloud_template'])
    # Keep internal state private to this emitter. Cloud's ?? operands must be
    # direct scalar variables, not the members supplied by setVector3.
    text = json.dumps(data)
    for axis in 'xyz':
        text = text.replace('variable.kt_v' + axis, 'variable.kg_velocity_' + axis)
    text = text.replace('variable.kt_', 'variable.kg_cloud_').replace('kt_init', 'kg_cloud_init')
    data = json.loads(text)
    effect = data['particle_effect']
    effect['description']['identifier'] = 'kaleidoscope_grilling:feedback_cloud'
    effect['description']['basic_render_parameters']['texture'] = 'textures/particle/kg_java_smoke'
    effect['components']['minecraft:particle_appearance_billboard']['uv'] = {
        'texture_width': 64, 'texture_height': 8,
        'uv': ['math.min(7,math.floor(variable.kg_cloud_age*7/variable.kg_cloud_life))*8', 0],
        'uv_size': [8, 8]
    }
    expected = json.dumps(data, indent=2) + '\n'
    if check:
        assert OUT.read_text() == expected, 'Stale owned Cloud feedback definition'
    else:
        OUT.write_text(expected)
    print(('Checked' if check else 'Built') + ' owned Cloud feedback; client acceptance remains separate.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
