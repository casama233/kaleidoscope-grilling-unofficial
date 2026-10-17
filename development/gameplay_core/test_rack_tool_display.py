"""Source/mesh math and state assets; no emulated or claimed Minecraft pixels."""
from copy import deepcopy
import json
import re
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from build_rack_tool_display import build, FIXTURE, BP, RP, fixed_display, alpha_rows
from bedrock_sprite_alignment import inspect_alignment, uv_to_point
from held_pose_frames import chain, rotate, scale, bone_matrix, point


class RackToolDisplay(unittest.TestCase):
    def setUp(self):
        self.proof = json.loads(FIXTURE.read_text())
        self.geos = json.loads((RP / 'models/entity/rack_tool_visual.geo.json').read_text())['minecraft:geometry']
        self.fit = json.loads((ROOT / 'docs/RACK-TOOL-DISPLAY-FIT.json').read_text())
        self.clip = json.loads((RP / 'animations/rack_tool_visual.animation.json').read_text())['animations']['animation.kg_station.rack_tool']['bones']['root']

    def root_pose(self, index):
        def evaluate(value):
            if not isinstance(value, str):
                return value
            match = re.fullmatch(r"q.property\('kaleidoscope_grilling:model'\) == (\d+) \? ([-\d.]+) : (.*)", value)
            return float(match[2]) if match and int(match[1]) == index else evaluate(match[3]) if match else float(value)
        return {key: [evaluate(v) for v in value] if isinstance(value, list) else evaluate(value) for key, value in self.clip.items()}

    def assertNear(self, a, b):
        for x, y in zip(a, b):
            self.assertAlmostEqual(x, y, places=8)

    def test_checked_in_assets_are_exact_generator_output_without_external_png_copies(self):
        output = build()
        self.assertEqual(len(output), 7)
        self.assertFalse(any(path.suffix == '.png' for path in output))
        for path, expected in output.items():
            self.assertEqual(path.read_bytes(), expected, str(path))

    def test_actual_item_parent_models_and_both_shovel_overrides_resolve_fixed(self):
        for row in self.proof['items']:
            self.assertEqual(fixed_display(self.proof, row['id']), {'rotation': [0, 180, 0], 'scale': [1, 1, 1]})
        models = {Path(r['path']).stem: r['data'] for r in self.proof['cookery_java']['models']}
        self.assertEqual([r['model'] for r in models['kitchen_shovel']['overrides']],
                         ['kaleidoscope_cookery:item/kitchen_shovel_no_oil', 'kaleidoscope_cookery:item/kitchen_shovel_has_oil'])
        self.assertEqual(models['kitchen_shovel_has_oil']['parent'], 'minecraft:item/handheld')
        self.assertNotIn('display', models['kitchen_shovel_has_oil'])
        self.assertEqual(self.proof['grilling_java']['display_context'], 'FIXED')
        self.assertEqual(self.proof['grilling_java']['scale'], .75)

    def test_every_alpha_contour_is_extruded_and_attached_to_its_actual_texel(self):
        for row, geo in zip(self.proof['items'], self.geos):
            result = inspect_alignment(geo['bones'][1]['cubes'], alpha_rows(row))
            self.assertEqual(result['issues'], [], row['id'])
            self.assertGreater(result['actual_alpha_contour_edges'], 20)
            self.assertGreater(result['sampled_vertex_depth_checks'], 100)

    def test_sprite_basis_plus_bedrock_zyx_equals_complete_java_fixed_chain(self):
        # Independent literal source order includes inherited FIXED, not Java
        # Euler values copied into Bedrock's different bone channel convention.
        target = chain(scale([.75] * 3), rotate('x', -180), rotate('y', 25), rotate('z', -45), rotate('y', 180))
        for index, geo in enumerate(self.geos):
            fit = self.fit['items'][index]
            basis = geo['bones'][1]
            actual = chain(bone_matrix(self.root_pose(index)), bone_matrix(basis))
            for u, v in [(0, 0), (16, 16), (2.5, 13.5), (12.5, 3.5), (8, 8)]:
                for face, java_z in [('north', .5), ('south', -.5)]:
                    local = uv_to_point(basis['cubes'][0], face, u, v)
                    projected = point(actual, [-local[0], local[1], local[2]])
                    expected = point(target, [u - 8, 8 - v, java_z])
                    self.assertNear(projected, [(v-c)*fit['uniform_fit'] for v,c in zip(expected,fit['center_pixels'])])
        self.assertNear(point(target, [1, 1, 0]), [0, -(.75 * 2 ** .5), 0])
        normal = point(target, [0, 0, 1])
        self.assertGreater(abs(normal[2]), .67)  # clearly broadside, not edge-on
        self.assertAlmostEqual(normal[1], 0, places=8)

    def test_all_fitted_opaque_corners_stay_strictly_inside_shared_clicked_cell(self):
        layout = self.fit['layout']
        self.assertEqual(layout['centerY'], 7/16)
        self.assertAlmostEqual(layout['centerY'] - self.fit['previous_native_anchor_y'], .0875)
        for index, (row, geo) in enumerate(zip(self.proof['items'], self.geos)):
            actual = chain(bone_matrix(self.root_pose(index)), bone_matrix(geo['bones'][1]))
            fit = self.fit['items'][index]
            self.assertGreater(fit['uniform_fit'], 0)
            self.assertLessEqual(fit['uniform_fit'], 1)
            self.assertAlmostEqual(self.root_pose(index)['scale'], .75*fit['uniform_fit'], places=9)
            for y,line in enumerate(alpha_rows(row)):
                for x,alpha in enumerate(line):
                    if not alpha:
                        continue
                    for u in (x,x+1):
                        for v in (y,y+1):
                            for face in ('north','south'):
                                raw = uv_to_point(geo['bones'][1]['cubes'][0],face,u,v)
                                p = point(actual,[-raw[0],raw[1],raw[2]])
                                self.assertLess(abs(p[0]/16),layout['cellWidth']/2)
                                self.assertGreater(p[1]/16+layout['centerY'],layout['rowMin'])
                                self.assertLess(p[1]/16+layout['centerY'],layout['rowMax'])

    def test_source_rotation_order_or_missing_fixed_is_detectably_wrong(self):
        intended = chain(rotate('x', -180), rotate('y', 25), rotate('z', -45), rotate('y', 180))
        for bad in [chain(rotate('z', -45), rotate('y', 25), rotate('x', -180), rotate('y', 180)),
                    chain(rotate('x', -180), rotate('y', 25), rotate('z', -45))]:
            self.assertGreater(sum(abs(a-b) for a,b in zip(point(intended, [3, 7, .5]), point(bad, [3, 7, .5]))), 1)

    def test_projection_entity_cannot_own_or_equip_any_stored_item(self):
        doc = json.loads((BP / 'entities/rack_tool_visual.json').read_text())['minecraft:entity']
        self.assertNotIn('runtime_identifier', doc['description'])
        for forbidden in ['minecraft:inventory', 'minecraft:equippable', 'minecraft:loot']:
            self.assertNotIn(forbidden, doc['components'])
        self.assertIn('minecraft:transient', doc['components'])
        self.assertEqual(doc['description']['properties']['kaleidoscope_grilling:model']['range'], [0, 5])
        client = json.loads((RP / 'entity/rack_tool_visual.entity.json').read_text())['minecraft:client_entity']['description']
        self.assertNotIn('enable_attachables', client)
        self.assertEqual(list(client['textures'].values()), [r['texture'] for r in self.proof['items']])

    def test_plate_native_geometry_and_animation_are_unmodified(self):
        animation = json.loads((RP / 'animations/equipment_visual.animation.json').read_text())['animations']['animation.kg_station.equipment']
        self.assertEqual(animation['bones']['root']['scale'], "q.property('kaleidoscope_grilling:pose') == 0 ? 0.42 : 0.3")
        self.assertEqual(animation['bones']['rightitem']['rotation'], ["q.property('kaleidoscope_grilling:pose') == 0 ? 0 : 90", 0, 0])


if __name__ == '__main__':
    unittest.main()
