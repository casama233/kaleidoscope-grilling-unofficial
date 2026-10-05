"""Actual beef silhouette + independent Bedrock vertex/texel regressions."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from bedrock_sprite_alignment import inspect_alignment

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from generated_food_sprite import helper_assets, main_faces, span_cubes, spans_from_alpha

# Numeric source facts only: exact installed 16×16 beef alpha, independently
# extracted from its hash-verified vanilla PNG. No copied color artwork.
BEEF_ROWS = ['0000', '0000', '0000', '0078', '00fc', '01fe', '03fe', '0ffe',
             '1ffe', '1ffe', '3ffc', '3ff8', '3ff0', '1fe0', '0f80', '0000']
BEEF_ALPHA_SHA256 = '869908ee834f182e6cfa87cffec0d68e8563d24f53748a5b115323002fbf2759'
FAILED_6717 = 'fb33b70bf9762c91224144e63d8a15b925761db5'


def beef_alpha():
    return [[255 if int(row, 16) & (1 << (15 - x)) else 0 for x in range(16)] for row in BEEF_ROWS]


def current_beef_cubes():
    fixture = json.loads((ROOT / 'development/gameplay_core/fixtures/secret-helper-sprite-spans.json').read_text())
    beef = next(row for row in fixture['items'] if row['id'] == 'minecraft:beef')
    assert beef['alpha_sha256'] == BEEF_ALPHA_SHA256
    geos, selected = helper_assets()
    return next(geo for geo in geos if geo['description']['identifier'] == selected[beef['index']])['bones'][1]['cubes']


class SpriteSilhouetteAlignment(unittest.TestCase):
    def test_actual_beef_alpha_all_edges_attach_to_their_main_face_texels(self):
        alpha = beef_alpha()
        self.assertEqual(hashlib.sha256(bytes(v for row in alpha for v in row)).hexdigest(), BEEF_ALPHA_SHA256)
        result = inspect_alignment(current_beef_cubes(), alpha)
        self.assertEqual(result['issues'], [])
        self.assertEqual(result['actual_alpha_contour_edges'], 50)
        self.assertEqual(result['opaque_side_texel_samples'], 94)
        self.assertEqual(result['sampled_vertex_depth_checks'], 1410)

    def test_frozen_native_failed_6717_is_rejected_without_changing_main_faces(self):
        path = 'projects/grilling/gameplay_core/resource_pack/models/entity/secret_helper_sprites.geo.json'
        prior = json.loads(subprocess.check_output(['git', 'show', FAILED_6717 + ':' + path], cwd=ROOT))
        current = current_beef_cubes()
        geos, selected = helper_assets()
        proof = json.loads((ROOT / 'development/gameplay_core/fixtures/secret-helper-sprite-spans.json').read_text())
        index = next(row['index'] for row in proof['items'] if row['id'] == 'minecraft:beef')
        old = next(geo for geo in prior['minecraft:geometry'] if geo['description']['identifier'] == selected[index])['bones'][1]['cubes']
        self.assertEqual(old[0], current[0])
        result = inspect_alignment(old, beef_alpha())
        reasons = {issue['reason'] for issue in result['issues']}
        self.assertIn('detached or reversed sampled texel', reasons)
        self.assertIn('actual alpha contour missing attached side', reasons)

    def test_independent_oracle_rejects_reintroduced_x_reflection(self):
        broken = deepcopy(current_beef_cubes())
        for side in broken[1:]:
            side['origin'][0] = -(side['origin'][0] + side['size'][0])
        self.assertTrue(inspect_alignment(broken, beef_alpha())['issues'])

    def test_independent_oracle_rejects_reversed_vertical_and_horizontal_uv(self):
        for vertical in (True, False):
            broken = deepcopy(current_beef_cubes())
            for side in broken[1:]:
                for face, uv in side['uv'].items():
                    if (face in ('east', 'west')) == vertical:
                        axis = 1 if vertical else 0
                        uv['uv'][axis] += uv['uv_size'][axis]
                        uv['uv_size'][axis] *= -1
            self.assertTrue(inspect_alignment(broken, beef_alpha())['issues'])

    def test_asymmetric_disjoint_hole_and_partial_alpha_cells(self):
        fixtures = [[[1, 0, 0, 0], [0, 0, 255, 0], [255, 255, 255, 255]],
                    [[255, 255, 255], [255, 0, 255], [255, 255, 255]],
                    [[255, 0, 255]]]
        for alpha in fixtures:
            height, width = len(alpha), len(alpha[0])
            cubes = [main_faces(), *span_cubes(spans_from_alpha(alpha), width, height)]
            self.assertEqual(inspect_alignment(cubes, alpha)['issues'], [])

    def test_64_pixel_sprite_keeps_same_model_footprint_and_texel_attachment(self):
        alpha = [[value for value in row for _ in range(4)] for row in beef_alpha() for _ in range(4)]
        cubes = [main_faces(), *span_cubes(spans_from_alpha(alpha), 64, 64)]
        result = inspect_alignment(cubes, alpha)
        self.assertEqual(result['issues'], [])
        self.assertEqual(result['actual_alpha_contour_edges'], 200)
        self.assertEqual(cubes[0], main_faces())


if __name__ == '__main__':
    unittest.main()
