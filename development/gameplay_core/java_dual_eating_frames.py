"""Exact ONE/THREE source arm and item matrices, pending native rig admission.

This module never swaps equipment. Detached-piece matrices alone do not
certify a native attachable renderer, slim rig binding, or observer view.
"""
import json
import math
from pathlib import Path
from java_active_eating_frames import sample, REFLECT
from held_pose_frames import chain, translate, rotate, scale, zyx, rigid_inverse, point, bedrock_rotation

SOURCE = json.loads((Path(__file__).parent / 'fixtures/java-eating-curves-1.1.1.json').read_text())['files']['EnderPearlEatingAnimation.java']
assert SOURCE['sha256'] == 'eab24f1e87a0d4f67abb3bd1b6d3804c90ba3d5fce39eb7c3d7760982dec244d'
ARRAYS = SOURCE['arrays']
PROFILES = ('ONE', 'THREE')

def authored_pose(profile, seconds):
    if profile not in PROFILES:
        raise ValueError('Only the source dual-arm branch is supported')
    t = max(0, min(4.5 if profile == 'ONE' else 5.0, seconds))
    if profile == 'ONE':
        arms = []
        for side in ('RIGHT', 'LEFT'):
            prefix = 'ONE_' + side + '_'
            arms.append(([sample(ARRAYS[prefix+'TIMES'], ARRAYS[prefix+axis], t) for axis in 'XYZ'],
                         [sample(ARRAYS[prefix+'TIMES'], ARRAYS[prefix+'ROT_'+axis], t) for axis in 'XYZ']))
        main = ([0, sample([0, .45833, 1.29167], [0, 0, -3], t), 0],
                [sample([.20833, .45833, 1.29167], [12.5, 0, 29.5], t), 0, 0], 1)
        # This is a source step, not a Catmull-Rom scale ramp.
        piece = ([-9, -2, 5], [75, 0, -275], 1 if t >= 1.16667 else 0)
    else:
        arms = []
        for side in ('RIGHT', 'LEFT'):
            arms.append(([sample(ARRAYS[side+'_POSITION_TIMES'], ARRAYS[side+'_POSITION_'+axis], t) for axis in 'XYZ'],
                         [sample(ARRAYS[side+'_ROTATION_TIMES'], ARRAYS[side+'_ROTATION_'+axis], t) for axis in 'XYZ']))
        main = ([0, sample(ARRAYS['MAIN_ITEM_POSITION_TIMES'], ARRAYS['MAIN_ITEM_POSITION_Y'], t), 0],
                [sample(ARRAYS['MAIN_ITEM_ROTATION_TIMES'], ARRAYS['MAIN_ITEM_ROTATION_X'], t), 0, 0], 1)
        piece = ([sample(ARRAYS['SECOND_ITEM_TRANSFORM_TIMES'], ARRAYS['SECOND_ITEM_POSITION_'+axis], t) for axis in 'XYZ'],
                 [sample(ARRAYS['SECOND_ITEM_TRANSFORM_TIMES'], ARRAYS['SECOND_ITEM_ROTATION_'+axis], t) for axis in 'XYZ'],
                 max(0, min(1, sample(ARRAYS['SECOND_ITEM_SCALE_TIMES'], ARRAYS['SECOND_ITEM_SCALE'], t))))
    return arms[0], arms[1], main, piece

def java_arm(profile, seconds, side=1, active=True, slim_item=False):
    if side not in (-1, 1):
        raise ValueError('side must be right +1 or left -1')
    authored = authored_pose(profile, seconds)
    p, r = authored[0 if active else 1]
    authored_sign = 1 if active else -1
    angles = [-r[0], side*r[1], r[2]]
    beta, gamma = map(math.radians, angles[1:])
    difference = -side
    position = [-side*(4 + authored_sign*p[0]) + difference*math.cos(gamma)*math.cos(beta),
                2-p[1] + difference*math.sin(gamma)*math.cos(beta),
                p[2] - difference*math.sin(beta)]
    if profile == 'ONE':
        position[1] += 3.8
        if active:
            angles[2] -= side*7.5
            # Source moveTowardHand uses the updated rotation's local Y axis.
            rotation = zyx(angles)
            position = [position[i] + rotation[i][1] for i in range(3)]
    if slim_item:
        position[0] += .5*side
    return chain(translate(position), zyx(angles))

def java_item_child(profile, seconds, side=1, active=True, include_scale=True):
    authored = authored_pose(profile, seconds)
    p, r, size = authored[2 if active else 3]
    authored_sign = 1 if active else -1
    anchor = (1.975, -8.925, -7.575) if active else (10, -8.875, -5.75)
    offset = [-side*authored_sign*(anchor[0]+p[0])+side, -anchor[1]-p[1], anchor[2]+p[2]]
    if active:
        return chain(translate(offset), rotate('x', 180+r[0]), rotate('y', side*r[1]),
                     rotate('z', side*r[2]), translate([0, 7, 2]))
    return chain(translate(offset), rotate('z', r[2]), rotate('y', side*r[1]),
                 rotate('x', -r[0]), rotate('x', 180 if profile == 'ONE' else 0),
                 rotate('z', 95), scale([size if include_scale else 1]*3))

def native_arm_target(profile, seconds, side=1, active=True, eye_height=1.62):
    camera = chain(translate([0, 24, 0]), rotate('y', 180))
    return chain(camera, translate([0, -16*eye_height, 0]), REFLECT,
                 translate([0, -24.016, 0]), java_arm(profile, seconds, side, active), REFLECT)

def child_matrix(profile, seconds, active_side=1, piece=False, slim=False, include_scale=True):
    """Factor either mesh into the active arm's normalized native item socket.

    The conversion convention is a mesh translated to pivot Y24. The helper
    target still uses its own arm and its own PlayerModel slim item shift.
    The renderer must account for any separately moved native socket; this
    source model does not assume a second ItemStack exists in the other hand.
    """
    target_side = -active_side if piece else active_side
    actual = java_arm(profile, seconds, active_side, True)
    target = java_arm(profile, seconds, target_side, not piece, slim)
    return chain(translate([-active_side, 7, 0]), REFLECT,
                 rigid_inverse(actual), target,
                 java_item_child(profile, seconds, target_side, not piece, include_scale),
                 translate([0, -8, 0]))

def child_bone(profile, seconds, active_side=1, piece=False, slim=False):
    # Zero-scale source frames must not be decomposed as rigid rotations.
    matrix = child_matrix(profile, seconds, active_side, piece, slim, include_scale=False)
    location = point(child_matrix(profile, seconds, active_side, piece, slim), [0, 0, 0])
    size = authored_pose(profile, seconds)[3][2] if piece else 1
    return {'position': [-location[0], location[1], location[2]],
            'rotation': bedrock_rotation(matrix), 'scale': [size]*3}
