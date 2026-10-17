"""Pose-matrix eye-frame calibration for exact secret active contexts only.

Uses the same bounded empirical +3.41 world-Y calibration as idle6711. It is
not an arbitrary screen translation or a universal intrinsic engine-eye claim.
Shared profile positions retain their exact base behavior for all other foods.
"""
from functools import lru_cache
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'development/gameplay_core'))
from held_pose_frames import chain, point, translate

FIX = ROOT / 'development/gameplay_core/fixtures/secret-idle-fp-calibration-1.26.52.3.json'
PROFILE_IDS = {
    'THREE': 'kaleidoscope_grilling:secret_skewer',
    'THREE_ALT': 'kaleidoscope_grilling:secret_skewer_java_three_alt',
}


@lru_cache(maxsize=1)
def world_y_delta():
    return json.loads(FIX.read_text())['world_y_delta']


def calibrated_target(target):
    # Left multiplication changes the common camera/world origin, not the
    # authored arm rotation or its child/helper's local source curve.
    return chain(translate([0, world_y_delta(), 0]), target)


def position_expression(profile, hand, target, axis, original, number):
    if profile not in PROFILE_IDS or axis != 1:
        return original
    before = point(target, [0, 0, 0])
    after = point(calibrated_target(target), [0, 0, 0])
    delta = after[axis] - before[axis]
    slot = 'slot.weapon.mainhand' if hand == 'right' else 'slot.weapon.offhand'
    predicate = "q.is_item_name_any('" + slot + "','" + PROFILE_IDS[profile] + "')"
    return original + ' + (' + predicate + ' ? ' + number(delta) + ' : 0)'
