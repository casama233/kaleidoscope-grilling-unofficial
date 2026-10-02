"""Build bounded one-particle feedback using hash-pinned Mojang sample definitions."""
from pathlib import Path
import argparse
import copy
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
RP = ROOT / 'projects/grilling/gameplay_core/resource_pack'

def build(check=False):
    fixture = json.loads((ROOT / 'development/gameplay_core/fixtures/feedback-mojang-1.26.50.4.json').read_text())
    for row in fixture['files']:
        assert hashlib.sha256(row['text'].encode()).hexdigest() == row['sha256'], row['path']
        data = copy.deepcopy(json.loads(row['text']))
        name = Path(row['path']).stem
        effect = data['particle_effect']
        effect['description']['identifier'] = 'kaleidoscope_grilling:feedback_' + name
        components = effect['components']
        for key in list(components):
            if key.startswith(('minecraft:emitter_rate_', 'minecraft:emitter_lifetime_', 'minecraft:emitter_shape_')):
                del components[key]
        components['minecraft:emitter_rate_instant'] = {'num_particles': 1}
        components['minecraft:emitter_lifetime_once'] = {'active_time': .05}
        velocity = ['variable.kg_velocity.' + axis for axis in 'xyz']
        components['minecraft:emitter_shape_point'] = {'offset': [0, 0, 0], 'direction': velocity}
        components['minecraft:particle_initial_speed'] = 'math.sqrt(' + ' + '.join(v + ' * ' + v for v in velocity) + ')'
        # Flame originally relies on its manual emitter for movement; make the
        # supplied event velocity effective in this standalone definition too.
        components.setdefault('minecraft:particle_motion_dynamic', {'linear_acceleration': [0, 0, 0]})
        path = RP / 'particles' / ('feedback_' + name + '.json')
        expected = json.dumps(data, indent=2) + '\n'
        if check:
            assert path.read_text() == expected, 'Stale particle definition: ' + str(path)
        else:
            path.write_text(expected)
    print(('Checked' if check else 'Built') + ' six owned instant-one particle definitions; renderer acceptance remains separate.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
