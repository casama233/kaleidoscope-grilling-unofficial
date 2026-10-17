"""Source matrix invariants; not a Minecraft renderer/camera certificate."""
import hashlib
import itertools
import math
from pathlib import Path
import unittest
from java_active_eating_frames import (PROFILES, REFLECT, authored_pose,
    java_arm, java_item_child, java_item_target, active_child_matrix,
    active_child_bone, native_arm_target)
from held_pose_frames import chain, translate, rotate, scale, point, bone_matrix


class JavaActiveEatingFrames(unittest.TestCase):
    def assertMatrix(self, actual, expected, tolerance=1e-9):
        self.assertLess(max(abs(actual[i][j]-expected[i][j])
                            for i in range(4) for j in range(4)), tolerance)

    def test_projection_mask_cannot_kill_startup_before_sync(self):
        root = Path(__file__).resolve().parents[2]
        source=(root/'projects/grilling/gameplay_core/behavior_pack/scripts/main.js').read_text()
        scoped=source.split("controller:'kg_java_eating_first_person'",1)[1].split('});',1)[0]
        stop=scoped.split('stopExpression:',1)[1]
        self.assertIn('!q.is_using_item',stop)
        self.assertIn('!q.is_item_name_any',stop)
        self.assertNotIn('eat_projection',stop)
        # This models only lifecycle predicates, not transport ordering/rendering.
        for projection in (False,True):
            using=True; same_item=True
            stopped=not using or not same_item
            visible=using and projection
            self.assertFalse(stopped)
            self.assertEqual(visible,projection)
        for using,same_item in ((False,True),(True,False)):
            self.assertTrue(not using or not same_item)

    def test_source_bytes_are_the_pinned_java_release(self):
        root = Path(__file__).resolve().parents[2]
        source = root/'projects/grilling/integration/immersion_lab/sources/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerEatingAnimation.java'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         'b4e97ccd8fd30b0b928315ce07a0f7e68489cce3efe3b7dd9892c021c8ed95eb')

    def test_full_renderer_and_child_factorization_agree(self):
        camera = chain(translate([0,24,0]),rotate('y',180))
        cases = 0
        for profile, hand, slim, eye in itertools.product(PROFILES,(-1,1),(False,True),(1.27,1.62)):
            for frame in range(181):
                t=frame/40
                actual=chain(native_arm_target(profile,t,hand,eye),
                             translate([hand,-7,0]),active_child_matrix(profile,t,hand,slim),
                             translate([0,-24,0]))
                target=chain(camera,java_item_target(profile,t,hand,eye,slim))
                self.assertMatrix(actual,target)
                cases+=1
        self.assertEqual(cases,4344)

    def test_non_idle_child_goldens_and_none_context_scale(self):
        cases=[('FOUR',0,[0,-3,-8],0),
               ('FOUR',.95833,[0,-3.409175234996142,-7.736152400301765],12.5),
               ('TWO',2.25,[-1,-2,-8],0),
               ('THREE_ALT',2.33333,[0,-4.373732907437244,-7.537365098246147],20)]
        for profile,t,position,tilt in cases:
            bone=active_child_bone(profile,t)
            for a,b in zip(bone['position'],position):self.assertAlmostEqual(a,b,places=8)
            self.assertEqual(bone['scale'],[1,1,1])
            self.assertAlmostEqual(authored_pose(profile,t)[2][1],tilt,places=8)
            self.assertMatrix(bone_matrix(bone),active_child_matrix(profile,t))
        self.assertAlmostEqual(authored_pose('TWO',2.25)[2][2],-90)
        self.assertAlmostEqual(authored_pose('THREE_ALT',2.33333)[2][0],-.75)

    def test_slim_hand_shift_is_model_x_not_local_x(self):
        for profile,hand in itertools.product(PROFILES,(-1,1)):
            for t in (0,.95833,2.25,3.45833,4.5):
                wide,slim=java_arm(profile,t,hand),java_arm(profile,t,hand,True)
                self.assertAlmostEqual(slim[0][3]-wide[0][3],.5*hand)
                self.assertAlmostEqual(slim[1][3],wide[1][3])
                self.assertAlmostEqual(slim[2][3],wide[2][3])
                for i in range(3):
                    for j in range(3):self.assertAlmostEqual(slim[i][j],wide[i][j])

    def test_slim_delta_can_move_into_player_socket(self):
        for profile,hand in itertools.product(PROFILES,(-1,1)):
            for frame in range(181):
                t=frame/40
                wide=active_child_bone(profile,t,hand,False)
                slim=active_child_bone(profile,t,hand,True)
                delta=[b-a for a,b in zip(wide['position'],slim['position'])]
                socket=chain(translate([hand,-7,0]),bone_matrix({'position':delta}))
                self.assertMatrix(chain(socket,bone_matrix(wide)),
                                  chain(translate([hand,-7,0]),bone_matrix(slim)))

    def test_helper_arm_profiles_cannot_silently_use_this_path(self):
        for profile in ('ONE','THREE','THREE_RANDOM','UNKNOWN'):
            with self.assertRaises(ValueError):active_child_matrix(profile,0)

    def test_source_time_clamping_and_both_hands(self):
        for profile,hand in itertools.product(PROFILES,(-1,1)):
            self.assertMatrix(active_child_matrix(profile,-1,hand),active_child_matrix(profile,0,hand))
            self.assertMatrix(active_child_matrix(profile,7,hand),active_child_matrix(profile,4.5,hand))


if __name__=='__main__':unittest.main()
