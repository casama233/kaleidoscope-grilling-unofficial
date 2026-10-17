"""Exact G105 pose scope and natural-grip diagnostics; native QA is separate."""
from copy import deepcopy
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from bottle_pose_review import LEDGER, reviewed_before
from held_pose_frames import RP, chain, rigid_inverse, native_skewer_calibration, point
from test_native_bottle_fp import cases, geometry_index, projected, CURRENT


class BottlePoseReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = [RP / 'animations' / name for name in ('a286_held.animation.json', 'seasoning_held.animation.json')]
        cls.before = {path.name: reviewed_before(path) for path in cls.paths}

    def test_exact_review_reversal_preserves_every_nonposition_field(self):
        ledger = json.loads(LEDGER.read_text())
        self.assertEqual(ledger['camera_offset_before'], [-3, 5, -6])
        self.assertEqual(ledger['camera_offset_after'], [-1, 3, -3])
        self.assertEqual([len(row['operations']) for row in ledger['files'].values()], [2, 144])
        idle = self.before['a286_held.animation.json']['animations']
        self.assertEqual({key for key in CURRENT if CURRENT[key] != idle[key]}, {
            'animation.kg_a286.bottle_fp_right', 'animation.kg_a286.bottle_fp_left'})

    def test_all_existing_use_curves_receive_only_constant_idle_frame_shift(self):
        before = self.before['seasoning_held.animation.json']['animations']
        after = json.loads(self.paths[1].read_bytes())['animations']
        self.assertEqual(before.keys(), after.keys())
        for name in before:
            hand = name.rsplit('.', 1)[-1]
            sign = 1 if hand == 'right' else -1
            base, camera = native_skewer_calibration(hand)
            frame = chain(rigid_inverse(base), camera)
            zero, shift = point(frame, [0, 0, 0]), point(frame, [2 * sign, -2, 3])
            expected = [-(shift[0] - zero[0]), shift[1] - zero[1], shift[2] - zero[2]]
            old, new = before[name]['bones']['grip'], after[name]['bones']['grip']
            for key in old['position']:
                for actual, prior, delta in zip(new['position'][key], old['position'][key], expected):
                    self.assertAlmostEqual(actual - prior, delta, places=7, msg=(name, key))
            self.assertEqual(new['rotation'], old['rotation'])
            self.assertEqual(new['scale'], old['scale'])
            self.assertEqual(new['scale'], [.72] * 3)
            for field in ('loop', 'animation_length'):
                self.assertEqual(after[name][field], before[name][field])

    def test_every_route_has_finite_front_facing_natural_idle_region(self):
        routes = list(cases())
        self.assertEqual(len(routes), 166)
        geometry = geometry_index()['geometry.kg_bottle_held.combined']
        for hand, sign in (('right', 1), ('left', -1)):
            name = 'animation.kg_a286.bottle_fp_' + hand
            old = projected(geometry, self.before['a286_held.animation.json']['animations'][name], hand)
            new = projected(geometry, CURRENT[name], hand)
            for current, previous in zip(new, old):
                for actual, prior, delta in zip(current, previous, [2 * sign, -2, 3]):
                    self.assertAlmostEqual(actual - prior, delta, places=7)
            center = [(min(p[i] for p in new) + max(p[i] for p in new)) / 2 for i in range(3)]
            self.assertGreater(sign * center[0], 7)
            self.assertLess(center[1], -1)
            self.assertTrue(-16 < center[2] < -13)
            width = lambda rows: max(p[0] / -p[2] for p in rows) - min(p[0] / -p[2] for p in rows)
            self.assertGreater(width(new) / width(old), 1.15)
        for filename, hand, ref, mesh in routes:
            points = projected(mesh, CURRENT['animation.kg_a286.bottle_fp_' + hand], hand)
            self.assertTrue(points, (filename, hand, ref))
            self.assertTrue(all(all(math.isfinite(value) for value in p) and p[2] < -.1 for p in points))

    def test_current_gate_rejects_stale_position_or_unrelated_field_mutation(self):
        for path in self.paths:
            current = json.loads(path.read_bytes())
            first = next(iter(current['animations']))
            variants = []
            changed = deepcopy(current)
            changed['animations'][first]['loop'] = not changed['animations'][first]['loop']
            variants.append(changed)
            variants.append(self.before[path.name])
            for changed in variants:
                with self.assertRaises(AssertionError):
                    reviewed_before(path, json.dumps(changed, indent=2).encode() + b'\n')


if __name__ == '__main__':
    unittest.main()
