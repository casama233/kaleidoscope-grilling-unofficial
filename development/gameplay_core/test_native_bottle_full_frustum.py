"""Complete-model bottle projection, separate from Minecraft client acceptance.

The pinned native frame is settled, wide skin, zero bob and non-VR. Actual eye
position, FOV interpretation and animation blending remain client gates. Check
nominal 60 degrees on both axes at 1.49 and 16:9, with every cuboid corner in
front of the near plane. Equip lowering may intentionally leave the viewport.
"""
import copy
import json
import math
from pathlib import Path
import unittest
from held_pose_frames import point
from test_native_skewer_fp import reference_frame, visible
from test_native_bottle_fp import cases, projected, projected_by_bone, geometry_index, CURRENT, RP

BEFORE = json.loads((Path(__file__).parent / 'fixtures/bottle-frame-before-2.8.61-framing.json').read_text())['animations']


def full_frustum(points, aspect, axis, degrees=60, near=.1):
    tangent = math.tan(math.radians(degrees / 2))
    hx, hy = (aspect * tangent, tangent) if axis == 'vertical' else (tangent, tangent / aspect)
    return bool(points) and all(
        all(math.isfinite(c) for c in v)
        and v[2] < -near
        and abs(v[0]) < -v[2] * hx
        and abs(v[1]) < -v[2] * hy
        for v in points
    )


class NativeBottleFullFrustum(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = geometry_index()
        cls.routes = list(cases())

    def test_all_attachable_aliases_and_both_hands_are_enumerated(self):
        expected = set()
        filenames = set()
        for path in (RP / 'attachables').glob('*seasoning*.json'):
            desc = json.loads(path.read_text())['minecraft:attachable']['description']
            filenames.add(path.name)
            self.assertTrue(desc['geometry'], path.name)
            self.assertEqual(set(desc['geometry']), {'default'}, path.name)
            self.assertEqual(len(desc['render_controllers']), 1, path.name)
            for alias, ref in desc['geometry'].items():
                self.assertIsInstance(ref, str, (path.name, alias))
                self.assertIn(ref, self.index, (path.name, alias, ref))
                expected.update((path.name, hand, ref) for hand in ('right', 'left'))
        self.assertTrue({'empty_seasoning_bottle.attachable.json', 'pending_seasoning.attachable.json'} <= filenames)
        actual = {(name, hand, ref) for name, hand, ref, _ in self.routes}
        self.assertEqual(actual, expected)
        self.assertEqual(len(self.routes), len(actual))

    def assert_complete(self, aspect, axis):
        failures = []
        for name, hand, ref, geometry in self.routes:
            by_bone = projected_by_bone(geometry, CURRENT['animation.kg_a286.bottle_fp_' + hand], hand)
            self.assertTrue(any(by_bone.values()), ref)
            for bone in geometry['bones']:
                # An empty hierarchy root is valid; an empty renderable layer
                # fails rather than silently bypassing contents coverage.
                if bone['name'] != 'grip' or bone.get('cubes'):
                    self.assertTrue(by_bone[bone['name']], (name, ref, bone['name']))
                if by_bone[bone['name']] and not full_frustum(by_bone[bone['name']], aspect, axis):
                    failures.append((name, hand, ref, bone['name']))
        self.assertEqual(len(failures), 0, f'{len(failures)} shell/content bone routes do not fit {axis}60 at aspect={aspect}; first five: {failures[:5]}')

    def test_all_corners_vertical60_aspect149(self):
        self.assert_complete(1.49, 'vertical')

    def test_all_corners_horizontal60_aspect149(self):
        self.assert_complete(1.49, 'horizontal')

    def test_all_corners_vertical60_aspect16by9(self):
        self.assert_complete(16 / 9, 'vertical')

    def test_all_corners_horizontal60_aspect16by9(self):
        self.assert_complete(16 / 9, 'horizontal')

    def test_combined_empty_pending_include_shell_and_all_eight_layers_nine_colors(self):
        combined = 'geometry.kg_bottle_held.combined'
        geometry = self.index[combined]
        expected = {'grip', 'shell'} | {f'pending_{tint}_color_{value}' for tint in range(16) for value in range(1, 10)}
        self.assertEqual({b['name'] for b in geometry['bones']}, expected)
        self.assertEqual(len(geometry['bones']), 146)
        for filename in ('empty_seasoning_bottle.attachable.json', 'pending_seasoning.attachable.json'):
            desc = json.loads((RP / 'attachables' / filename).read_text())['minecraft:attachable']['description']
            self.assertEqual(set(desc['geometry'].values()), {combined})
            for hand in ('right', 'left'):
                points = projected_by_bone(geometry, CURRENT['animation.kg_a286.bottle_fp_' + hand], hand)
                self.assertEqual(set(points), expected)
                self.assertFalse(points['grip'])
                for bone in expected - {'grip'}:
                    self.assertTrue(points[bone], (filename, hand, bone))

    def test_all_fixed_variants_have_one_geometry_and_shell_contents_children(self):
        refs = set()
        files = []
        for name, hand, ref, geometry in self.routes:
            if not ref.startswith('geometry.kg_bottle_held.fixed.'):
                continue
            refs.add(ref)
            if hand == 'right':
                files.append(name)
            self.assertEqual(len(geometry['bones']), 3, ref)
            self.assertEqual({b['name'] for b in geometry['bones']}, {'grip', 'shell', 'contents'}, ref)
            self.assertFalse(geometry['bones'][0].get('cubes'), ref)
            for bone in geometry['bones'][1:]:
                self.assertEqual(bone['parent'], 'grip', ref)
                self.assertEqual(bone['pivot'], [0, 24, 0], ref)
                self.assertNotIn('binding', bone, ref)
                self.assertTrue(bone.get('cubes'), ref)
        self.assertEqual(refs, {f'geometry.kg_bottle_held.fixed.r{r}.v{v}' for r in range(1, 9) for v in range(8)})
        self.assertEqual(len(files), 65)  #64 fixed variants plus default special.
        self.assertEqual(len(self.routes), 166)  #83 items including 16 fill proxies, one geometry in both hands.

    def test_only_two_fp_positions_change_rotation_scale_and_other_tracks_stay_pinned(self):
        fp = {'animation.kg_a286.bottle_fp_right', 'animation.kg_a286.bottle_fp_left'}
        self.assertEqual(set(CURRENT), set(BEFORE))
        self.assertEqual({name for name in CURRENT if CURRENT[name] != BEFORE[name]}, fp)
        for name in fp:
            old = BEFORE[name]['bones']['grip']
            current = CURRENT[name]['bones']['grip']
            self.assertEqual(current['rotation'], old['rotation'])
            self.assertEqual(current['scale'], old['scale'])
            self.assertEqual(current['scale'], [.72] * 3)

    def test_authored_frame_now_has_only_the_requested_camera_translation(self):
        geometry = self.index['geometry.kg_a286.kg_a2733.seasoning_bottle_hand']
        for hand, sign in (('right', 1), ('left', -1)):
            key = 'animation.kg_a286.bottle_fp_' + hand
            before = projected(geometry, BEFORE[key], hand)
            after = projected(geometry, CURRENT[key], hand)
            self.assertEqual(len(before), len(after))
            for old, current in zip(before, after):
                for a, b, expected in zip(old, current, (-3 * sign, 5, -6)):
                    self.assertAlmostEqual(b - a, expected, places=7)

    def test_prior_any_corner_pass_is_rejected_by_complete_model_gate(self):
        geometry = self.index['geometry.kg_a286.kg_a2733.seasoning_bottle_hand']
        for hand in ('right', 'left'):
            points = projected(geometry, BEFORE['animation.kg_a286.bottle_fp_' + hand], hand)
            self.assertTrue(visible(points))
            for aspect in (1.49, 16 / 9):
                for axis in ('vertical', 'horizontal'):
                    self.assertFalse(full_frustum(points, aspect, axis))

    def test_behind_camera_and_near_plane_mutations_fail(self):
        geometry = self.index['geometry.kg_a286.kg_a2733.seasoning_bottle_hand']
        points = projected(geometry, CURRENT['animation.kg_a286.bottle_fp_right'], 'right')
        behind = [[v[0], v[1], v[2] + 100] for v in points]
        near = [[0, 0, -.05] for _ in points]
        for aspect in (1.49, 16 / 9):
            for axis in ('vertical', 'horizontal'):
                self.assertFalse(full_frustum(behind, aspect, axis))
                self.assertFalse(full_frustum(near, aspect, axis))

    def test_child_rotation_and_ancestor_rotation_are_applied(self):
        geometry = {'bones': [
            {'name': 'grip', 'pivot': [0, 24, 0], 'binding': 'q.item_slot_to_bone_name(context.item_slot)'},
            {'name': 'middle', 'parent': 'grip', 'pivot': [0, 24, 0], 'rotation': [0, 0, 90]},
            {'name': 'contents', 'parent': 'middle', 'pivot': [0, 24, 0], 'rotation': [0, 0, 90], 'cubes': [{'origin': [1, 24, 0], 'size': [1, 1, 1]}]},
        ]}
        pose = {'bones': {'grip': {}}}
        points = projected_by_bone(geometry, pose, 'left')['contents']
        # Reflected X (-1,0,0), two 90-degree Z rotations -> (1,0,0).
        expected = point(reference_frame('left'), [1, 0, 0])
        for actual, target in zip(points[0], expected):
            self.assertAlmostEqual(actual, target, places=8)
        wrong_parent = copy.deepcopy(geometry)
        wrong_parent['bones'][2]['parent'] = 'absent'
        with self.assertRaises(ValueError):
            projected_by_bone(wrong_parent, pose, 'left')


if __name__ == '__main__':
    unittest.main()
