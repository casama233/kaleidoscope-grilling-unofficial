"""Independent frame/visibility checks; client rendering remains a separate gate."""
import itertools
import json
import math
import unittest
from held_pose_frames import (RP, expected_animations, make_pose, bone_matrix, chain,
    translate, rotate, point, rigid_inverse, calibration, zyx)

class HeldPoseFrameTests(unittest.TestCase):
    def test_runtime_is_reproducible_and_not_raw_java_euler(self):
        expected=expected_animations()
        for filename in ('a287_skewer_held.animation.json','a286_held.animation.json'):
            for name,body in json.loads((RP/'animations'/filename).read_text())['animations'].items():
                self.assertEqual(body,expected[name])
        # Independent values obtained from native Blockbench Java and Bedrock
        # frame comparison, not from the old copied-Euler implementation.
        rot=expected['animation.kg_a287.skewer_tp_right']['bones']['skewer_pose']['rotation']
        for a,b in zip(rot,[171.60178562,-2.24451015,174.78346239]):self.assertAlmostEqual(a,b,places=7)

    def test_skewer_points_forward_instead_of_up_the_arm(self):
        for hand in ('right','left'):
            pose=make_pose('skewer','tp',hand)['skewer_pose']
            m=chain(rotate('x',15),bone_matrix(pose))
            direction=[m[i][2]/.8 for i in range(3)]
            self.assertLess(direction[2],-.9)
            self.assertLess(abs(direction[1]),.35)
        old={'rotation':[-98.57,1.45,-174.51],'scale':[.8]*3}
        matrix=chain(rotate('x',15),bone_matrix(old))
        self.assertGreater(matrix[1][2]/.8,.95) # reproduces arm occlusion

    def test_every_held_geometry_has_finite_visible_first_person_bounds(self):
        index={g['description']['identifier']:g for p in (RP/'models').rglob('*.json')
               for g in json.loads(p.read_text()).get('minecraft:geometry',[])}
        expected=expected_animations();checked=0
        for p in (RP/'attachables').glob('*.json'):
            desc=json.loads(p.read_text())['minecraft:attachable']['description']
            for hand in ('right','left'):
                bones=expected[desc['animations']['fp_'+hand]]['bones']
                base,camera=calibration(hand)
                combined=chain(rigid_inverse(camera),base,translate([0,24,0]))
                for bone in bones.values():combined=chain(combined,bone_matrix(bone))
                combined=chain(combined,translate([0,-24,0]))
                for ref in set(desc['geometry'].values()):
                    positions=[]
                    for bone in index[ref]['bones']:
                        for cube in bone.get('cubes',[]):
                            origin=cube['origin'];size=cube['size']
                            pivot=cube.get('pivot',[0,0,0]);pivot=[-pivot[0],pivot[1],pivot[2]]
                            rotation=cube.get('rotation',[0,0,0])
                            cm=chain(combined,translate(pivot),zyx([-rotation[0],-rotation[1],rotation[2]]),translate([-x for x in pivot]))
                            for corner in itertools.product((0,1),repeat=3):
                                v=[origin[i]+corner[i]*size[i]for i in range(3)];v[0]*=-1
                                positions.append(point(cm,v))
                    self.assertTrue(positions,ref)
                    self.assertTrue(all(math.isfinite(v)for pnt in positions for v in pnt),ref)
                    visible=[v for v in positions if v[2]<-.1 and abs(v[0]/v[2])<1.3 and abs(v[1]/v[2])<.75]
                    self.assertTrue(visible,(desc['identifier'],hand,ref))
                    checked+=1
        self.assertGreater(checked,400)

    def test_single_bound_root_and_no_player_override(self):
        self.assertFalse((RP/'entity/player.entity.json').exists())
        self.assertFalse((RP/'entity/player.json').exists())
        for p in (RP/'models/entity/a287_hand').glob('*.json'):
            bones=json.loads(p.read_text())['minecraft:geometry'][0]['bones']
            self.assertEqual(sum(bool(b.get('binding'))for b in bones),1)

if __name__=='__main__':unittest.main()
