"""Pinned player-bone projection regression, not Minecraft client acceptance."""
import itertools
import json
import unittest
from pathlib import Path
from held_pose_frames import RP, chain, translate, zyx, rotate, rigid_inverse, bone_matrix, point

FIXTURE = json.loads((Path(__file__).parent/'fixtures/native-fp-frame-1.26.50.4.json').read_text())

def reference_frame(hand, slim=False, height=1, bob=(0,0,0)):
    # Independently assemble the public player hierarchy and empty_hand offsets.
    # Do not call the runtime generator's calibration or make_pose here.
    if hand == 'left':
        # Independently assemble actual native left bones. empty_hand has no
        # leftarm pose; swap_item/bob/slim offsets remain on the native parent.
        arm = FIXTURE['player_bones']['leftarm']['pivot']
        item = FIXTURE['player_bones']['leftitem']['pivot']
        camera = chain(translate(FIXTURE['native_camera_model']['pivot']),rotate('y',180))
        parent = translate([-arm[0]+bob[0],arm[1]-(.5 if slim else 0)-10*(1-height)+bob[1],arm[2]+bob[2]])
        socket = translate([-(item[0]-arm[0]),-7,0])
        return chain(rigid_inverse(camera),parent,socket)
    sign = 1 if hand == 'right' else -1
    arm = FIXTURE['player_bones']['rightarm']['pivot']
    item = FIXTURE['player_bones']['rightitem']['pivot']
    pose = FIXTURE['empty_hand']['rightarm']
    position = [-arm[0]-pose['position'][0], arm[1]+pose['position'][1], pose['position'][2]]
    rotation = [-95,45,115]  # evaluate the pinned non-VR expressions
    position[0] *= sign
    rotation[1] *= sign
    rotation[2] *= sign
    offset = [-(item[0]-arm[0])*sign, -7, 0]  # empty_hand cancels item Z
    base = chain(translate(position),zyx(rotation),translate(offset),translate([0,-24,0]))
    camera = chain(translate(FIXTURE['native_camera_model']['pivot']),rotate('y',180))
    return chain(rigid_inverse(camera),base,translate([0,24,0]))

def vertices(geometry, animation, hand):
    matrix = reference_frame(hand)
    for name in ('skewer_pose','skewer_model'):
        matrix = chain(matrix,bone_matrix(animation['bones'][name]))
    matrix = chain(matrix,translate([0,-24,0]))
    out = []
    for bone in geometry['bones']:
        for cube in bone.get('cubes',[]):
            pivot = cube.get('pivot',[0,0,0]);pivot = [-pivot[0],pivot[1],pivot[2]]
            r = cube.get('rotation',[0,0,0])
            local = chain(matrix,translate(pivot),zyx([-r[0],-r[1],r[2]]),translate([-v for v in pivot]))
            corners = []
            for c in itertools.product((0,1),repeat=3):
                v = [cube['origin'][i]+c[i]*cube['size'][i] for i in range(3)];v[0] *= -1
                corners.append(point(local,v))
            out.append(corners)
    return out

def visible(points):
    # Fixed 16:9 projection envelope; not a claim about every device/FOV.
    return any(v[2]<-.1 and abs(v[0]/v[2])<1.3 and abs(v[1]/v[2])<.75 for v in points)

class NativeSkewerFirstPersonTests(unittest.TestCase):
    def test_old_potato_pose_misses_the_player_projection(self):
        geo = json.loads((RP/'models/entity/a287_hand/kg_a22.grilled_potato_slice_skewer.stage0.geo.json').read_text())['minecraft:geometry'][0]
        previous = FIXTURE['previous_skewer_fp']['animation.kg_a287.skewer_fp_right']
        self.assertFalse(any(visible(cube) for cube in vertices(geo,previous,'right')))

    def test_all_bite_stages_show_food_and_handle_in_both_hands(self):
        animations = json.loads((RP/'animations/a287_skewer_held.animation.json').read_text())['animations']
        count = 0
        for p in sorted((RP/'models/entity/a287_hand').glob('*.geo.json')):
            geo = json.loads(p.read_text())['minecraft:geometry'][0]
            for hand in ('right','left'):
                cubes = vertices(geo,animations['animation.kg_a287.skewer_fp_'+hand],hand)
                self.assertTrue(visible(cubes[0]),(p.name,hand,'bamboo'))
                if len(cubes)>1:  # completed bite stages intentionally contain only bamboo
                    self.assertTrue(any(visible(c) for c in cubes[1:]),(p.name,hand,'food'))
                count += 1
        self.assertEqual(count,300)

    def test_third_person_stays_identical(self):
        current = json.loads((RP/'animations/a287_skewer_held.animation.json').read_text())['animations']
        for hand in ('right','left'):
            key = 'animation.kg_a287.skewer_tp_'+hand
            self.assertEqual(current[key],FIXTURE['previous_skewer_fp'][key])

if __name__ == '__main__': unittest.main()
