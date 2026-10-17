"""Pinned Java active-arm/NONE-context item transforms, not client acceptance.

Only TWO, THREE_ALT and FOUR use this source branch. ONE/THREE have a
different two-arm renderer and must never silently reuse this factorization.
All translations below are model pixels; source model rotations use degrees.
"""
import json
import math
from pathlib import Path
from held_pose_frames import (chain, translate, scale, rotate, zyx, point,
                              rigid_inverse, bedrock_rotation)

FIXTURE = Path(__file__).parent / 'fixtures/java-eating-curves-1.1.1.json'
SOURCE = json.loads(FIXTURE.read_text())['files']['SkewerEatingAnimation.java']
assert SOURCE['sha256'] == 'b4e97ccd8fd30b0b928315ce07a0f7e68489cce3efe3b7dd9892c021c8ed95eb'
ARRAYS = SOURCE['arrays']
PROFILES = ('TWO', 'THREE_ALT', 'FOUR')
REFLECT = scale([-1, -1, 1])


def sample(times, values, time):
    """Original endpoint-clamped Catmull-Rom, including repeated neighbours."""
    if time <= times[0]:
        return values[0]
    if time >= times[-1]:
        return values[-1]
    right = next(i for i, t in enumerate(times) if t >= time)
    left = right - 1
    u = (time-times[left])/(times[right]-times[left])
    p0, p1, p2, p3 = [values[i] for i in (max(0,left-1), left, right,
                                        min(len(values)-1,right+1))]
    return .5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+
               (-p0+3*p1-3*p2+p3)*u*u*u)


def authored_pose(profile, seconds):
    if profile not in PROFILES:
        raise ValueError('The helper-arm branch needs a separate renderer')
    t = min(4.5, max(0., seconds))
    prefix = {'FOUR':'', 'TWO':'TWO_', 'THREE_ALT':'SQUID_'}[profile]
    position = [sample(ARRAYS[prefix+'POSITION_TIMES'],
                       ARRAYS[prefix+'POSITION_'+axis], t) for axis in 'XYZ']
    rotation = [sample(ARRAYS[prefix+'ROTATION_TIMES'],
                       ARRAYS[prefix+'ROTATION_'+axis], t) for axis in 'XYZ']
    if profile == 'FOUR':
        item_y, item_rx, item_rz = 0, sample(ARRAYS['ITEM_ROTATION_TIMES'],
                                            ARRAYS['ITEM_ROTATION_X'], t), 0
    elif profile == 'TWO':
        item_y = 0
        # These literals are inline in Java sampleTwo, not named fixture arrays.
        item_rx = sample([.45833,.95833,1.20833], [0,12.5,0], t)
        item_rz = sample(ARRAYS['TWO_ITEM_ROTATION_Z_TIMES'],
                         ARRAYS['TWO_ITEM_ROTATION_Z'], t)
    else:
        item_y = sample(ARRAYS['SQUID_ITEM_POSITION_TIMES'],
                        ARRAYS['SQUID_ITEM_POSITION_Y'], t)
        item_rx = sample(ARRAYS['SQUID_ITEM_ROTATION_TIMES'],
                         ARRAYS['SQUID_ITEM_ROTATION_X'], t)
        item_rz = 0
    return position, rotation, (item_y, item_rx, item_rz)


def java_arm(profile, seconds, hand=1, slim_item=False):
    if hand not in (-1, 1):
        raise ValueError('hand must be right +1 or left -1')
    p, r, _ = authored_pose(profile, seconds)
    angles = [-r[0], (-hand if profile=='TWO' else hand)*r[1], hand*r[2]]
    beta, gamma = map(math.radians, angles[1:])
    difference = -hand
    position = [-hand*(4+p[0])+difference*math.cos(gamma)*math.cos(beta),
                2-p[1]+difference*math.sin(gamma)*math.cos(beta)+(2 if profile=='TWO' else 0),
                p[2]-difference*math.sin(beta)]
    # PlayerModel.translateToHand changes MODEL X before translateAndRotate.
    # It is not a constant local-axis shift and does not move the visible arm.
    if slim_item:
        position[0] += .5*hand
    return chain(translate(position), zyx(angles))


def java_item_child(profile, seconds, hand=1):
    _, _, (item_y, item_rx, item_rz) = authored_pose(profile, seconds)
    return chain(translate([-hand, 9-item_y, -6]), rotate('x',180+item_rx),
                 rotate('z',hand*item_rz), translate([0,7,2]))


def java_item_target(profile, seconds, hand=1, eye_height=1.62, slim=False):
    """Source renderer target before the external incoming camera pose."""
    return chain(translate([0,-16*eye_height,0]), REFLECT,
                 translate([0,-24.016,0]), java_arm(profile,seconds,hand,slim),
                 java_item_child(profile,seconds,hand), translate([-8,-8,-8]),
                 translate([8,-24,8]))


def active_child_matrix(profile, seconds, hand=1, slim=False):
    """Exact child factorization, independent of camera and eye height.

    Native arm local mesh is REFLECT * Java local mesh. The normalized native
    arm-to-item socket is T(hand,-7,0). Converted skewer bones have pivot Y24.
    """
    arm = java_arm(profile,seconds,hand)
    hand_adjustment = chain(rigid_inverse(arm), java_arm(profile,seconds,hand,slim))
    return chain(translate([-hand,7,0]), REFLECT, hand_adjustment,
                 java_item_child(profile,seconds,hand), translate([0,-8,0]))


def active_child_bone(profile, seconds, hand=1, slim=False):
    m = active_child_matrix(profile,seconds,hand,slim)
    p = point(m,[0,0,0])
    return {'position':[-p[0],p[1],p[2]],
            'rotation':bedrock_rotation(m), 'scale':[1,1,1]}


def native_arm_target(profile, seconds, hand=1, eye_height=1.62):
    """Explicit existing head-centred projection model, still needs client QA."""
    camera = chain(translate([0,24,0]), rotate('y',180))
    return chain(camera, translate([0,-16*eye_height,0]), REFLECT,
                 translate([0,-24.016,0]), java_arm(profile,seconds,hand), REFLECT)
