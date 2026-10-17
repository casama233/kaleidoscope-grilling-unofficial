"""Source resolver/matrix regressions; no native player or client acceptance."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import unittest

import java_dual_eating_frames as dual
from java_eating_piece_resolver import SOURCE, fixed_model, ingredient_index, available_fixed_piece, model_path
from held_pose_frames import chain, translate, rotate, point, bone_matrix
from java_active_eating_frames import REFLECT

ROOT = Path(__file__).resolve().parents[2]

class DualEatingFrames(unittest.TestCase):
    def assertMatrix(self, actual, expected):
        self.assertLess(max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4)), 1e-8)

    def test_source_curves_are_the_exact_existing_forge_release(self):
        source = ROOT / 'projects/grilling/integration/immersion_lab/sources/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/EnderPearlEatingAnimation.java'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), dual.SOURCE['sha256'])
        self.assertEqual(hashlib.sha256(SOURCE['content'].encode()).hexdigest(), SOURCE['sha256'])
        raw = SOURCE['content'].encode()
        self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(), SOURCE['git_blob_sha1'])

    def test_both_arm_and_detached_mesh_factorizations_match_source_renderer(self):
        cases = 0
        camera = chain(translate([0,24,0]),rotate('y',180))
        for profile, hand, slim, piece, eye in itertools.product(dual.PROFILES, (-1,1), (False,True), (False,True), (1.27,1.62)):
            for frame in range(201):
                t = frame / 40
                side = -hand if piece else hand
                parent = chain(dual.native_arm_target(profile,t,hand,eye_height=eye),translate([hand,-7,0]))
                actual = chain(parent,dual.child_matrix(profile,t,hand,piece,slim),translate([0,-24,0]))
                reference = chain(camera,translate([0,-16*eye,0]),REFLECT,translate([0,-24.016,0]),
                                  dual.java_arm(profile,t,side,not piece,slim),dual.java_item_child(profile,t,side,not piece),translate([0,-32,0]))
                self.assertMatrix(actual,reference)
                self.assertMatrix(bone_matrix(dual.child_bone(profile,t,hand,piece,slim)),dual.child_matrix(profile,t,hand,piece,slim))
                # Every converted vertex follows the helper source arm, even
                # though the candidate factorization is rooted in the active socket.
                for vertex in ([0,24,0],[-1,31.25,-1],[1,32.75,1]):
                    for a,b in zip(point(actual,vertex),point(reference,vertex)):
                        self.assertAlmostEqual(a,b,places=7)
                cases += 1
        self.assertEqual(cases,6432)

    def test_one_source_scale_step_and_three_scale_window(self):
        self.assertEqual(dual.authored_pose('ONE',1.16666)[3][2],0)
        self.assertEqual(dual.authored_pose('ONE',1.16667)[3],([-9,-2,5],[75,0,-275],1))
        self.assertEqual(dual.authored_pose('ONE',4.5)[3][2],1)
        for t, expected in [(0,0),(3.5,0),(3.54167,1),(4.16667,1),(4.20833,0),(5,0)]:
            self.assertEqual(dual.authored_pose('THREE',t)[3][2],expected)
        self.assertEqual(dual.child_bone('THREE',0,piece=True)['scale'],[0,0,0])

    def test_helper_arm_z_rotation_is_authored_not_active_hand_mirrored(self):
        # The dual Java branch uses unmirrored authored Z, unlike TWO/FOUR.
        for hand in (-1,1):
            matrix=dual.java_arm('THREE',2.875,-hand,active=False)
            self.assertAlmostEqual(matrix[2][3],-6 + (-hand)*math.sin(math.radians((-hand)*-36.835)))
        for profile in dual.PROFILES:
            for active in (False,True):
                for hand in (-1,1):
                    wide=dual.java_arm(profile,2,hand,active)
                    slim=dual.java_arm(profile,2,hand,active,True)
                    self.assertAlmostEqual(slim[0][3]-wide[0][3],.5*hand)
                    self.assertEqual([row[:3] for row in wide],[row[:3] for row in slim])

    def test_profile_clamps_and_unsupported_branch_rejection(self):
        for profile,limit in [('ONE',4.5),('THREE',5)]:
            self.assertEqual(dual.authored_pose(profile,-1),dual.authored_pose(profile,0))
            self.assertEqual(dual.authored_pose(profile,8),dual.authored_pose(profile,limit))
        for profile in ('TWO','THREE_ALT','FOUR','THREE_RANDOM'):
            with self.assertRaises(ValueError):dual.authored_pose(profile,0)

class EatingPieceResolver(unittest.TestCase):
    def test_known_java_piece_paths_and_ingredient_fallback(self):
        self.assertEqual(fixed_model('kaleidoscope_grilling:raw_fish_skewer','ONE'),
                         'kaleidoscope_grilling:item/fixed_skewers/fish/fish_skewer_raw_piece_1')
        self.assertEqual(fixed_model('kaleidoscope_grilling:grilled_ender_pearl_skewer','THREE'),
                         'kaleidoscope_grilling:item/fixed_skewers/ender_pearl/ender_pearl_skewer_piece_3')
        for name in ('secret_skewer','mysterious_skewer','dark_grilling'):
            self.assertIsNone(fixed_model('kaleidoscope_grilling:'+name,'THREE'))
        self.assertIsNone(fixed_model('minecraft:apple','ONE'))
        self.assertIsNone(fixed_model(None,'ONE'))
        self.assertIsNotNone(available_fixed_piece(ROOT,'kaleidoscope_grilling:ordinary_skewer','THREE'))
        self.assertIsNone(available_fixed_piece(ROOT,'kaleidoscope_grilling:missing_skewer','THREE'))

    def test_all_47_piece_assets_match_pinned_source_hashes(self):
        manifest=json.loads((ROOT/'projects/grilling/source_manifest.json').read_text())
        pieces=[row for row in manifest['files'] if '_piece_' in row['path']]
        self.assertEqual(len(pieces),47)
        for row in pieces:
            raw=(ROOT/'projects/grilling/source_snapshots'/row['path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['local_sha256'],row['path'])
            self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),row['upstream_git_blob_sha1'])

    def test_inventory_metadata_is_never_used_as_a_rendering_carrier(self):
        for count in range(4):
            rows=tuple({'id':i,'nameTag':'preserved','foreign':{'data':[1,2]}} for i in range(count))
            before=json.dumps(rows,sort_keys=True)
            self.assertEqual(ingredient_index('ONE',count),0 if count else None)
            self.assertEqual(ingredient_index('THREE',count),count-1 if count else None)
            self.assertEqual(json.dumps(rows,sort_keys=True),before)
        self.assertIsNone(ingredient_index('ONE',-1))

    def test_current_fixed_dual_candidates_have_source_piece_models(self):
        source=(ROOT/'projects/grilling/gameplay_core/behavior_pack/scripts/data.js').read_text()
        table=json.loads(re.search(r'PROFILE_BY_ITEM=Object.freeze\((\{.*?\})\)',source)[1])
        candidates=[]
        for item,profile in table.items():
            if profile=='ONE' or profile in ('THREE','THREE_RANDOM'):
                model=available_fixed_piece(ROOT,item,'ONE' if profile=='ONE' else 'THREE')
                if model:
                    candidates.append(item)
                    wrapper=json.loads(model_path(ROOT,model).read_text())
                    self.assertIn('parent',wrapper)
                    self.assertTrue(model_path(ROOT,wrapper['parent']).exists())
        self.assertGreaterEqual(len(candidates),20)

if __name__=='__main__':unittest.main()
