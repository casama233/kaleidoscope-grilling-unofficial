"""Owner-dispatch source regressions; these do not certify engine rendering."""
from pathlib import Path
import importlib.util
import json
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
RP = ROOT / 'projects/grilling/gameplay_core/resource_pack'
BASE = '0996f05fd63ce37098d867d14b4760dad93d2501'


def load(path):
    return json.loads(path.read_text())


def old(path):
    return json.loads(subprocess.check_output(
        ['git', 'show', BASE + ':' + str(path.relative_to(ROOT))], cwd=ROOT))


class SecretHeldOwnerContextTests(unittest.TestCase):
    def test_both_native_profiles_resolve_owner_properties_before_controllers(self):
        for name in ('secret_skewer', 'secret_skewer_java_three_alt'):
            d = load(RP / f'attachables/{name}.attachable.json')['minecraft:attachable']['description']
            scripts = d['scripts']
            self.assertEqual(scripts['initialize'], ['v.kg_secret_off_hand = 0;'] +
                             [f'v.kg_secret_ingredient_{i} = 0;' for i in range(3)])
            reads = [s for s in scripts['pre_animation'] if s.startswith('v.kg_secret_')]
            self.assertEqual(reads[0], "v.kg_secret_off_hand = c.item_slot == 'off_hand';")
            self.assertEqual(len(reads), 4)
            for i, statement in enumerate(reads[1:]):
                values = []
                for hand in ('off', 'main'):
                    prop = f'kaleidoscope_grilling:secret_{hand}_{i}'
                    values.append(f"(c.owning_entity->q.has_property('{prop}') ? c.owning_entity->q.property('{prop}') : 0)")
                self.assertEqual(statement, f'v.kg_secret_ingredient_{i} = math.floor(math.clamp((v.kg_secret_off_hand ? {values[0]} : {values[1]}), 0, 213));')

    def test_controllers_only_use_resolved_numeric_indices(self):
        controllers = load(RP / 'render_controllers/secret_held.render_controllers.json')['render_controllers']
        self.assertEqual(set(controllers), {'controller.render.kg_secret_held.stick'} |
                         {f'controller.render.kg_secret_held.{i}' for i in range(3)})
        self.assertNotIn('q.property', json.dumps(controllers))
        self.assertNotIn('c.item_slot', json.dumps(controllers))
        for i in range(3):
            row = controllers[f'controller.render.kg_secret_held.{i}']
            self.assertEqual(row['geometry'], f'v.kg_secret_ingredient_{i} == 0 ? Geometry.part_{i}_0 : Geometry.part_{i}_1')
            self.assertEqual(row['textures'], [f'Array.food[v.kg_secret_ingredient_{i}]'])
            self.assertEqual(row['part_visibility'], [{'skewer_model': f'v.kg_bite_stage < {i + 1}'}])
            self.assertEqual(len(row['arrays']['textures']['Array.food']), 214)

    def test_existing_models_materials_passes_textures_and_eating_are_unchanged(self):
        self.assertEqual(load(RP / 'models/entity/secret_held.geo.json'), old(RP / 'models/entity/secret_held.geo.json'))
        for name in ('secret_skewer', 'secret_skewer_java_three_alt'):
            path = RP / f'attachables/{name}.attachable.json'
            actual = load(path)['minecraft:attachable']['description']
            before = old(path)['minecraft:attachable']['description']
            for field in ('identifier', 'materials', 'textures', 'geometry', 'render_controllers', 'animations'):
                self.assertEqual(actual[field], before[field])
            self.assertEqual(actual['scripts']['animate'], before['scripts']['animate'])
            self.assertEqual([s for s in actual['scripts']['pre_animation'] if not s.startswith('v.kg_secret_')], before['scripts']['pre_animation'])

    def test_secret_generator_is_repeatable_after_motion_and_native_variant_generation(self):
        spec = importlib.util.spec_from_file_location('secret_builder', ROOT / 'tools/build_secret_held.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for path, value in module.build().items():
            expected = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n'
            self.assertEqual(path.read_text(), expected, str(path))


if __name__ == '__main__':
    unittest.main()
