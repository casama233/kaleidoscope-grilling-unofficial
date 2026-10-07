"""Author held-plate assets from reviewed Java item frames and canonical meshes.

Only source resources are generated here; packaging never changes gameplay.
Five count-dependent slots share one bound hand socket. Item rendering retains
Java FIXED's Z -180 rotation: the placed renderer's extra Z +180 is absent.
Inventory/hotbar dynamic composition and failed-skewer metadata variants remain
separate adaptation gaps. Matrix checks are not native/client acceptance.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/grilling/gameplay_core'
RP, BP = PROJECT / 'resource_pack', PROJECT / 'behavior_pack'
sys.path.insert(0, str(ROOT / 'development/gameplay_core'))
from held_pose_frames import (chain, translate, xyz, rotate, scale, mul,
    rigid_inverse, point, bedrock_rotation, native_skewer_calibration)
from secret_skewer_assets import (COMPLETE_STATES, state_slot_cubes, shaft_cubes,
    palette_refs)

NS = 'kaleidoscope_grilling:'
SOURCE_PIN = '9a1acdab27698457bec16c9362678e574895a28c'
SOURCE_FILES = {
 'common/src/main/resources/assets/kaleidoscope_grilling/models/item/skewer_plate.json':
    '02f7e718b4c4e3b1a71e27c6ece5e297126a7ad08259fc783e9442402c85aba8',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerPlateItemRenderer.java':
    '15019243a15415dae465d56ccb480f4a0c34168f39b705fb24a5b166fd7ed5a9',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerPlateRenderer.java':
    '81afc858b3eb2d347af3ba9c228178519931d1091c17eb2b884df721be426f93',
 'common/src/main/resources/assets/kaleidoscope_grilling/models/item/mysterious_skewer.json':
    'cef3ce739462073b2db74a1e0ca470a88c6942df8c3691472afe3b49b92a72d8',
 'common/src/main/resources/assets/kaleidoscope_grilling/models/item/dark_grilling.json':
    'b0cbc68867ba315fffc132d3837f593031ab9d7b1f9876b2525125e246ff3de7',
}
SOURCE_URL = 'https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/' + SOURCE_PIN + '/'
# Exact current Java builtin/entity display slots, reviewed at SOURCE_PIN.
PLATE_DISPLAY = {
 'thirdperson_righthand': {'rotation': [-119.08, -36.32, -178.63], 'translation': [0, 3.25, 2], 'scale': [.375]*3},
 'thirdperson_lefthand': {'rotation': [-119.08, -36.32, -178.63], 'translation': [0, 3.25, 2], 'scale': [.375]*3},
 'firstperson_righthand': {'rotation': [0, -135, 0], 'translation': [0, 3.75, 0], 'scale': [.4]*3},
 'firstperson_lefthand': {'rotation': [0, -135, 0], 'translation': [0, 3.75, 0], 'scale': [.4]*3},
}
LAYOUTS = [
 [], [[8, 4, 6.3, 0]], [[5.6, 4.15, 5.95, 0], [10.4, 4.2, 5.9, 0]],
 [[5.6, 3.95, 6.35, 0], [10.4, 4, 6.3, 0], [8, 7.375, 7.65, -22.5]],
 [[8, 3.95, 6.35, 0], [12.55, 4, 6.3, 0], [3.45, 4, 6.3, 0], [8, 7.325, 7.7, -45]],
 [[8, 3.95, 6.35, 0], [12.55, 4, 6.3, 0], [3.45, 4, 6.3, 0], [10.4, 7.325, 7.4, -22.5], [5.7, 7.375, 7.35, -22.5]],
]
PALETTE_RADIX, ROW_RADIX = 214, 123
PALETTE_MAX, PAIR_MAX, MARKER_MIN, MARKER_MAX, INVALID_MARKER = 9800343, 15128, 10, 747, 748
IDLE_STYLES = (0, 4, 6)
BINDING = 'q.item_slot_to_bone_name(context.item_slot)'
# Conservative Bedrock camera placement, not an authored Java translation.
# Full body + every selectable fixed/secret/ordinary row corner, count0..5,
# needs at least 8.4644 extra depth units to fit the narrower hand viewport
# X/depth .025..535, Y/depth -.285..-.015. At depth nine, the common mirrored
# X translation may be -4.564..-2.780 and Y 3.026..3.170. Keep one rigid
# translation inside those bounds; source display rotations/scales stay intact.
# This settled native-frame projection is not rendered-client acceptance.
PLATE_FP_CAMERA_OFFSET = [-4, 3.1, -9]
# This opt-in client diagnostic is not a rendering/runtime repair. The BP
# exact count1 fixture alone uses dormant word4=1 while its QA tag is enabled.
# Either raw hand flag with exact fixture marker133 enables the probe without
# decoded count, equipment-slot context or item occupancy. Normal bottles and
# count5 row4 paletteword1 cannot enable it through their natural word4=1.
QA_LOG_CANARY, QA_LOG_SAMPLES = 914100, 3
QA_LOG_FIELDS = ('v.kg_plate_qa_hand',
    *(f'v.kg_plate_qa_raw_{hand}_word_{word}' for hand in ('main', 'off') for word in range(8)),
    'v.kg_plate_count', 'v.kg_plate_desc_0', 'v.kg_plate_shape_0',
    'v.kg_plate_style_0', 'v.kg_plate_food_0_0', 'v.kg_plate_food_0_1',
    'v.kg_plate_food_0_2', 'v.kg_plate_owner_occupied == 1 ? 1 : 0')
QA_POST_TESTS = {
    'qa_a_flag': '1',
    'qa_b_large_word': 'v.kg_plate_qa_raw_word_0 == 8285209',
    'qa_c_small_words': 'v.kg_plate_qa_raw_word_5 == 57 && v.kg_plate_qa_raw_word_7 == 133',
    'qa_d_decoded': 'v.kg_plate_count == 1 && v.kg_plate_desc_0 == 57 && v.kg_plate_shape_0 == 18 && v.kg_plate_style_0 == 0 && v.kg_plate_food_0_0 == 199 && v.kg_plate_food_0_1 == 195 && v.kg_plate_food_0_2 == 180',
}
QA_BINARY_TEXTURE = 'textures/held/bottle_shell_palette'
QA_BINARY_DARK_UV, QA_BINARY_LIGHT_UV = [8, 40], [123, 40]
QA_BINARY_OFFSET = [0, .55, -2]
QA_BINARY_FRONT_Z, QA_BINARY_BACK_Z, QA_BINARY_GLYPH_DEPTH = -9.22, -6.6, .02
QA_BINARY_MIRROR_X_SUM = -1.25
QA_BINARY_FONT = {
    '0': ('111', '101', '101', '101', '111'),
    '1': ('010', '110', '010', '010', '111'),
    '2': ('111', '001', '111', '100', '111'),
    '3': ('111', '001', '111', '001', '111'),
    '4': ('101', '101', '111', '001', '001'),
    '5': ('111', '100', '111', '001', '111'),
    '6': ('111', '100', '111', '101', '111'),
    '7': ('111', '001', '010', '010', '010'),
    'H': ('101', '101', '111', '101', '101'),
    'M': ('101', '111', '111', '101', '101'),
    'L': ('100', '100', '100', '100', '111'),
    'C': ('111', '100', '100', '100', '111'),
    'D': ('110', '101', '101', '101', '110'),
}


def dump(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def verify_java_source(source_root):
    """Optional source-checkout witness; normal generation stays self-contained."""
    for relative, digest in SOURCE_FILES.items():
        assert hashlib.sha256((source_root / relative).read_bytes()).hexdigest() == digest, relative
    doc = json.loads((source_root / next(iter(SOURCE_FILES))).read_text())
    assert {key: doc['display'][key] for key in PLATE_DISPLAY} == PLATE_DISPLAY
    renderer = (source_root / list(SOURCE_FILES)[1]).read_text()
    assert 'Axis.ZP' not in renderer
    assert 'Axis.YP.rotationDegrees(slot[3])' in renderer and 'Axis.XP.rotationDegrees(90F)' in renderer
    layout_source = (source_root / list(SOURCE_FILES)[2]).read_text()
    prefix = layout_source.split('LAYOUTS = {', 1)[1].split('\n  };', 1)[0]
    values = [float(v) for v in re.findall(r'(-?\d+(?:\.\d+)?)F', prefix)]
    assert values == [v for rows in LAYOUTS for row in rows for v in row]
    from secret_skewer_assets import model
    bare = [e for e in model(21)['elements'] if not any('tintindex' in f for f in e['faces'].values())]
    for relative in list(SOURCE_FILES)[3:]:
        assert json.loads((source_root / relative).read_text())['elements'] == bare


def plate_pose(view, hand):
    """Use the existing native socket projection with the authored plate frame.

    The canonical source geometry is X-reflected, centered at X/Z eight, and
    raised Y24. This is the same source_offset as the existing skewer hand rig.
    FP alone adds the bounded, mirrored Bedrock camera translation below.
    No player or arm replacement, socket cancellation, or guessed held Euler.
    """
    key = ('firstperson_' if view == 'fp' else 'thirdperson_') + hand + 'hand'
    pose = PLATE_DISPLAY[key]
    sign = 1 if hand == 'right' else -1
    r = pose['rotation']; r = [r[0], r[1]*sign, r[2]*sign]
    tr = pose['translation']; tr = [tr[0]*sign, tr[1], tr[2]]
    size = pose['scale']; source_offset = [8, -24, 8]
    if view == 'tp':
        arm = rotate('x', 15)
        base = chain(translate([5*sign, 22, 0]), arm, translate([sign, -31, 1]))
        target = chain(translate([6*sign, 22, 0]), arm, translate([0, -10, -2]),
            rotate('x', -90), translate(tr), xyz(r), scale(size),
            translate([-8, -8, -8]), translate(source_offset))
        local = mul(rigid_inverse(base), target)
    else:
        base, camera = native_skewer_calibration(hand)
        java = chain(translate([9.039*sign, 15.682, 20.8]), translate(tr), xyz(r),
            scale(size), translate([-8, -8, -8]))
        camera_offset = [PLATE_FP_CAMERA_OFFSET[0]*sign, *PLATE_FP_CAMERA_OFFSET[1:]]
        target = chain(camera, translate(camera_offset), translate([0, -24, -32.4]), java, translate(source_offset))
        local = mul(rigid_inverse(base), target)
    position = point(local, [0, 24, 0]); position[1] -= 24; position[0] *= -1
    rotation = mul(local, scale([1/x for x in size]))
    return {'position': [round(v, 8) for v in position],
        'rotation': [round(v, 8) for v in bedrock_rotation(rotation)], 'scale': size}


def select_count(values):
    out = str(values[-1])
    for count in reversed(range(len(values)-1)):
        out = f'v.kg_plate_count == {count} ? {values[count]} : ' + out
    return out


def slot_pose(row, count):
    cell = LAYOUTS[count][row] if row < count else [8, 0, 8, 0]
    return {'position': [8-cell[0], cell[1], cell[2]-8], 'rotation': [0, -cell[3], 0]}


def animations():
    clips = {}
    for view in ('fp', 'tp'):
        for hand in ('right', 'left'):
            clips[f'animation.kg_plate_held.{view}_{hand}'] = {'loop': True,
                'bones': {'plate_pose': plate_pose(view, hand)}}
    bones = {}
    for row in range(5):
        poses = [slot_pose(row, count) for count in range(6)]
        bones[f'plate_slot_{row}'] = {channel: [select_count([pose[channel][axis] for pose in poses])
            for axis in range(3)] for channel in ('position', 'rotation')}
        # Ry(slot) Rx90 S.8 T(0,2.25,9.75) Rx-90 Rz-180 S1.5
        # T(-8,-8,-8). Source cubes already center X/Z, so the unchanged
        # FIXED frame reduces to Rz-180 S1.2 and translation(0,1.8,1.8).
        # The placed renderer's additional Rz+180 must NOT appear here.
        bones[f'plate_fixed_{row}'] = {'position': [0, 1.8, 1.8],
            'rotation': [0, 0, -180], 'scale': 1.2}
    clips['animation.kg_plate_held.layout'] = {'loop': True, 'bones': bones}
    return {'format_version': '1.8.0', 'animations': clips}


def geometry(alias, cubes, width=16, height=16, row=None):
    bones = [{'name': 'grip', 'pivot': [0, 24, 0], 'binding': BINDING},
        {'name': 'plate_pose', 'parent': 'grip', 'pivot': [0, 24, 0]}]
    if row is None:
        bone = {'name': 'plate_body', 'parent': 'plate_pose', 'pivot': [0, 24, 0]}
    else:
        bones += [{'name': f'plate_slot_{row}', 'parent': 'plate_pose', 'pivot': [0, 24, 0]},
            {'name': f'plate_fixed_{row}', 'parent': f'plate_slot_{row}', 'pivot': [0, 24, 0]}]
        bone = {'name': f'plate_row_{row}', 'parent': f'plate_fixed_{row}', 'pivot': [0, 24, 0]}
    if cubes:
        bone['cubes'] = deepcopy(cubes)
    bones.append(bone)
    return {'description': {'identifier': 'geometry.kg_plate_held.' + alias,
        'texture_width': width, 'texture_height': height, 'visible_bounds_width': 4,
        'visible_bounds_height': 4, 'visible_bounds_offset': [0, 1.5, 0]}, 'bones': bones}


def lift_cubes(source, amount):
    cubes = []
    for bone in source['bones']:
        assert not bone.get('rotation') and not bone.get('position') and not bone.get('scale'), 'Unreviewed source bone transform'
        for original in bone.get('cubes', []):
            cube = deepcopy(original); cube['origin'][1] += amount
            if 'pivot' in cube: cube['pivot'][1] += amount
            cubes.append(cube)
    return cubes


def qa_geometry():
    """Four tiny wood-textured posts reuse the exact plate hand/pivot rig.

    A/B/C/D have heights one/two/three/four and distinct X positions across
    the near tray edge. This separate geometry leaves the 526 production
    meshes byte-for-byte unchanged. Cube bases sit on the Y26 tray surface.
    """
    result = geometry('qa_probe', [])
    result['bones'].pop()  # No duplicate production plate_body pass.
    for index, name in enumerate(QA_POST_TESTS):
        uv = {face: {'uv': [1, 0], 'uv_size': [1, 2]}
            for face in ('north', 'east', 'south', 'west')}
        uv.update({face: {'uv': [1, 1], 'uv_size': [1, 1]}
            for face in ('up', 'down')})
        result['bones'].append({'name': name, 'parent': 'plate_pose',
            'pivot': [0, 24, 0], 'cubes': [{'origin': [-5.5 + index*3, 26, 4.5],
                'size': [1, index+1, 1], 'uv': uv}]})
    return {'format_version': '1.21.0', 'minecraft:geometry': [result]}


def binary_bit(value, bit):
    """Exact power-of-two extraction; no nonbinary radix or large equality."""
    high = f'math.floor({value}/{2**(bit+1)})'
    return f'math.floor({value}/{2**bit}) - {high} - {high}'


def qa_binary_rows():
    raw = 'v.kg_plate_qa_raw_word_0'
    rows = [(label, [binary_bit(raw, bit) for bit in range(top, top-8, -1)])
        for label, top in (('H', 23), ('M', 15), ('L', 7))]
    rows.append(('C', [binary_bit('v.kg_plate_count', bit) for bit in (2, 1, 0)] +
        [f'{raw} != math.floor({raw})', f'{raw} - math.floor({raw}) == 0.5', '0', '1', '1']))
    rows.append(('D', [f'{raw} < 0'] + [binary_bit('v.kg_plate_desc_0', bit) for bit in range(6, -1, -1)]))
    rows += [(str(slot), [binary_bit(f'v.kg_plate_food_0_{slot}', bit) for bit in range(7, -1, -1)])
        for slot in range(3)]
    return rows


def qa_binary_cube(origin, size, light=False, face_only=False):
    # Explicit one-texel faces avoid fractional box-net UVs. Both swatches
    # are interior, fully opaque, and uniform around bilinear sample edges.
    texel = QA_BINARY_LIGHT_UV if light else QA_BINARY_DARK_UV
    # Black front text has only its outward north face; the mirrored rear
    # copy switches to south. Omitted faces are not drawn, so the unchanged
    # one-sided material cannot show ghost reversed text around panel edges.
    faces = ('north', 'east', 'south', 'west', 'up', 'down') if light and not face_only else ('north',)
    uv = {face: {'uv': texel[:], 'uv_size': [1, 1]} for face in faces}
    return {'origin': [round(v, 5) for v in origin], 'size': [round(v, 5) for v in size], 'uv': uv}


def qa_binary_glyph(label, x, y, pixel=.12, z=QA_BINARY_FRONT_Z, depth=QA_BINARY_GLYPH_DEPTH, x_scale=1, padding=(.025, .025)):
    """Disjoint black strokes, ivory empty pixels and same-plane padding.

    Local opaque contrast travels with the glyph, independent of the distant
    backing silhouette. Contrasting rectangles meet without overlapping.
    """
    cubes = []
    for value in ('1', '0'):
        active, rectangles = {}, []
        for row, line in enumerate(QA_BINARY_FONT[label]):
            runs = [(match.start(), len(match.group())) for match in re.finditer(value+'+', line)]
            next_active = {}
            for run in runs:
                start, height = active.pop(run, (row, 0))
                next_active[run] = (start, height+1)
            rectangles += [(col, start, width, height) for (col, width), (start, height) in active.items()]
            active = next_active
        rectangles += [(col, start, width, height) for (col, width), (start, height) in active.items()]
        cubes += [qa_binary_cube([x+col*pixel*x_scale, y+(5-start-height)*pixel, z],
            [width*pixel*x_scale, height*pixel, depth], light=value == '0', face_only=True)
            for col, start, width, height in rectangles]
    width, height = 3*pixel*x_scale, 5*pixel
    px, py = padding
    cubes += [qa_binary_cube([cx, cy, z], [w, h, depth], light=True, face_only=True)
        for cx, cy, w, h in ((x-px, y-py, width+2*px, py), (x-px, y+height, width+2*px, py),
            (x-px, y, px, height), (x+width, y, px, height))]
    return cubes


def qa_binary_back(cubes):
    """Duplicate readable rear text in the same existing conditional bone.

    Reflect X and glyph shape about the panel center; a viewer on the other
    side therefore sees the same upright labels, MSB-left ordering and code.
    """
    back = deepcopy(cubes)
    for cube in back:
        cube['origin'][0] = round(QA_BINARY_MIRROR_X_SUM - cube['origin'][0] - cube['size'][0], 5)
        cube['origin'][2] = QA_BINARY_BACK_Z
        cube['uv'] = {'south': cube['uv']['north']}
    return back


def qa_binary_geometry():
    """Two-sided upright 8x8 code board; original hand rig intact.

    Authored X increases from MSB to LSB; rows descend Y. H/M/L are raw
    bits23..16/15..8/7..0. C is count2/1/0, fraction, half, fixed0/1/QA1.
    D is raw-negative flag plus descriptor6..0; 0/1/2 are foods7..0.
    One thick opaque ivory panel has explicit black 0/1 on both sides.
    Reference0/1 and the corner tab disambiguate orientation in either hand.
    """
    result = geometry('qa_binary', [], 128, 128)
    result['bones'].pop()
    # Final QA-only envelope X[-7.2,5.95], Y[24.80,34.70], Z[-11.22,-8.58].
    # The single panel is Z[-10.20,-9.60]. Black text/grid are one full unit
    # clear of each panel face, with common .02 depth and no socket layers.
    # Neither camera-side assumption nor native readability is certified here.
    backing = qa_binary_cube([-7.2, 24.25, -8.2], [13.15, 9.9, .6], True)
    front = []
    for col in range(8):
        front += qa_binary_glyph(str(7-col), -5.45+col*1.4-.45, 33.6, .10, x_scale=3, padding=(.08, .025))
    front.append(qa_binary_cube([-7.15, 33.95, QA_BINARY_FRONT_Z], [.3, .2, QA_BINARY_GLYPH_DEPTH]))
    # Grid bars share the black glyph plane and meet only at boundaries.
    # Vertical segments stop at horizontal bars; glyphs stay inside cells.
    for boundary in range(9):
        front.append(qa_binary_cube([-6.15, 24.7+boundary*1.1-.015, QA_BINARY_FRONT_Z],
            [11.2, .03, QA_BINARY_GLYPH_DEPTH]))
        for row in range(8):
            front.append(qa_binary_cube([-6.15+boundary*1.4-.015, 24.7+row*1.1+.015, QA_BINARY_FRONT_Z],
                [.03, 1.07, QA_BINARY_GLYPH_DEPTH]))
    for row, (label, expressions) in enumerate(qa_binary_rows()):
        cy = 32.95-row*1.1
        front += qa_binary_glyph(label, -7.10, cy-.325, .13, x_scale=2.3, padding=(.025, .05))
        for col, _ in enumerate(expressions):
            cx = -5.45+col*1.4
            for value in (0, 1):
                name = f'qa_binary_{row}_{col}_{value}'
                glyph = qa_binary_glyph(str(value), cx-.45, cy-.30, x_scale=2.5, padding=(.1, .08))
                result['bones'].append({'name': name, 'parent': 'plate_pose',
                    'pivot': [0, 24, 0], 'cubes': glyph + qa_binary_back(glyph)})
    result['bones'].insert(2, {'name': 'qa_binary_frame', 'parent': 'plate_pose',
        'pivot': [0, 24, 0], 'cubes': [backing] + front + qa_binary_back(front)})
    for bone in result['bones']:
        for cube in bone.get('cubes', []):
            cube['origin'] = [round(value+offset, 5)
                for value, offset in zip(cube['origin'], QA_BINARY_OFFSET)]
    return {'format_version': '1.21.0', 'minecraft:geometry': [result]}


def qa_binary_controller():
    visibility = [{'*': 0}, {'qa_binary_frame': 'v.kg_plate_qa_enabled == 1'}]
    for row, (_, expressions) in enumerate(qa_binary_rows()):
        for col, expression in enumerate(expressions):
            visibility += [{f'qa_binary_{row}_{col}_{value}':
                f'v.kg_plate_qa_enabled == 1 && ({expression}) == {value}'} for value in (0, 1)]
    return {'geometry': 'Geometry.qa_binary', 'materials': [{'*': 'Material.default'}],
        'textures': ['Texture.qa_binary'], 'part_visibility': visibility}


def property_read(hand, word):
    name = NS + f'bottle_{hand}_{word}'
    return f"(c.owning_entity->q.has_property('{name}') ? c.owning_entity->q.property('{name}') : 0)"


def owner_occupancy():
    return ("(c.item_slot == 'main_hand' && c.owning_entity->q.is_item_name_any('slot.weapon.mainhand','" + NS +
        "skewer_plate')) || (c.item_slot == 'off_hand' && c.owning_entity->q.is_item_name_any('slot.weapon.offhand','" + NS + "skewer_plate'))")


def decoder_scripts():
    initialize = ['v.kg_plate_owner_occupied = 0;', 'v.kg_plate_count = 0;']
    pre = []
    for hand in ('main', 'off'):
        for word in range(8):
            var = f'v.kg_plate_qa_raw_{hand}_word_{word}'
            initialize.append(var + ' = 0;')
            # Read both owner banks directly, before any hand selection,
            # flooring or decoding, to expose the previously gated-out path.
            pre.append(var + ' = ' + property_read(hand, word) + ';')
    for word in (0, 5, 7):
        var = f'v.kg_plate_qa_raw_word_{word}'
        initialize.append(var + ' = 0;')
        # Preserve existing post B/C observations in the selected raw bank.
        pre.append(var + f" = c.item_slot == 'off_hand' ? v.kg_plate_qa_raw_off_word_{word} : v.kg_plate_qa_raw_main_word_{word};")
    for word in range(8):
        var = f'v.kg_plate_word_{word}'; initialize.append(var + ' = 0;')
        # Read the raw word before validation. Clamping a748 transaction marker
        # to747 would incorrectly reveal a complete plate during partial writes.
        pre.append(var + " = math.floor(c.item_slot == 'off_hand' ? " + property_read('off', word) + ' : ' + property_read('main', word) + ');')
    pre += ['v.kg_plate_count = math.floor((v.kg_plate_word_7 - 10 + 0.5)/123);',
        'v.kg_plate_count = math.clamp(v.kg_plate_count, 0, 5);']
    valid = 'v.kg_plate_word_7 >= 10 && v.kg_plate_word_7 <= 747'
    valid += ' && ' + ' && '.join(f'v.kg_plate_word_{i} >= 0 && v.kg_plate_word_{i} <= {PALETTE_MAX if i < 5 else PAIR_MAX}' for i in range(7))
    pre.append('v.kg_plate_owner_occupied = (' + owner_occupancy() + ') && (' + valid + ');')
    descriptors = [
        'v.kg_plate_word_5 - math.floor(v.kg_plate_word_5/123)*123',
        'math.floor(v.kg_plate_word_5/123)',
        'v.kg_plate_word_6 - math.floor(v.kg_plate_word_6/123)*123',
        'math.floor(v.kg_plate_word_6/123)',
        '(v.kg_plate_word_7 - 10) - math.floor((v.kg_plate_word_7 - 10)/123)*123',
    ]
    for row, expression in enumerate(descriptors):
        desc = f'v.kg_plate_desc_{row}'; initialize.append(desc + ' = 0;')
        pre.append(desc + ' = math.clamp(' + expression + ', 0, 122);')
        shape = f'v.kg_plate_shape_{row}'; style = f'v.kg_plate_style_{row}'
        initialize += [shape + ' = 0;', style + ' = 0;']
        pre.append(style + ' = math.floor(math.clamp(' + desc + ' - 39, 0, 80)/27);')
        pre.append(shape + ' = math.clamp(' + desc + ' - 39, 0, 80) - ' + style + '*27;')
        word = f'v.kg_plate_word_{row}'
        foods = [word + ' - math.floor(' + word + '/214)*214',
            'math.floor(' + word + '/214) - math.floor(' + word + '/45796)*214',
            'math.floor(' + word + '/45796)']
        for slot, food in enumerate(foods):
            var = f'v.kg_plate_food_{row}_{slot}'; initialize.append(var + ' = 0;')
            pre.append(var + ' = math.clamp(' + food + ', 0, 213);')
    initialize += [f'v.kg_plate_qa_{name} = 0;' for name in
        ('enabled', 'hand', 'samples', 'next_log', 'elapsed', 'life_origin', 'clock', 'sample_due')]
    # The BP writer is still the exact tagged fixture's sole flag producer.
    # Match only the raw count1 fixture marker, excluding normal bottles and
    # count5 row4 palettes without borrowing decoded count, item-slot context,
    # item occupancy, or large-word/descriptor payload validation.
    raw_flag = lambda hand: f'(v.kg_plate_qa_raw_{hand}_word_4 == 1 && v.kg_plate_qa_raw_{hand}_word_7 == 133)'
    pre += ['v.kg_plate_qa_enabled = ' + raw_flag('main') + ' || ' + raw_flag('off') + ';',
        "v.kg_plate_qa_hand = c.item_slot == 'main_hand' ? 1 : c.item_slot == 'off_hand' ? 2 : 0;",
        'v.kg_plate_qa_life_origin = v.kg_plate_qa_enabled == 1 && v.kg_plate_qa_samples == 0 ? q.life_time : v.kg_plate_qa_life_origin;',
        'v.kg_plate_qa_elapsed = v.kg_plate_qa_enabled == 1 ? v.kg_plate_qa_elapsed + math.max(q.delta_time, 0) : v.kg_plate_qa_elapsed;',
        'v.kg_plate_qa_clock = v.kg_plate_qa_enabled == 1 ? math.max(q.life_time - v.kg_plate_qa_life_origin, v.kg_plate_qa_elapsed) : 0;',
        f'v.kg_plate_qa_sample_due = v.kg_plate_qa_enabled == 1 && v.kg_plate_qa_samples < {QA_LOG_SAMPLES} && v.kg_plate_qa_clock >= v.kg_plate_qa_next_log;']
    # query.log accepts a value. Each numeric-only sample is 26 values:
    # canary, hand, main raw0..7, off raw0..7, selected count/desc0/shape0/
    # style0/food0/1/2/owner occupied. At most three samples per attachable
    # lifetime; disabling/re-enabling QA never resets this cap. life_time is
    # preferred when it advances; delta_time supplies the zero-clock fallback.
    pre += [f'v.kg_plate_qa_sample_due ? q.log({value}) : 0;'
        for value in (str(QA_LOG_CANARY), *QA_LOG_FIELDS)]
    pre += ['v.kg_plate_qa_next_log = v.kg_plate_qa_sample_due ? v.kg_plate_qa_clock + 1 : v.kg_plate_qa_next_log;',
        'v.kg_plate_qa_samples = v.kg_plate_qa_sample_due ? v.kg_plate_qa_samples + 1 : v.kg_plate_qa_samples;']
    return {'initialize': initialize, 'pre_animation': pre,
        'animate': [{key: "c.is_first_person == " + str(int(key.startswith('fp'))) + " && c.item_slot == '" + ('main_hand' if key.endswith('right') else 'off_hand') + "'"}
            for key in ('fp_right', 'fp_left', 'tp_right', 'tp_left')] + ['layout']}


def decode_projection(words, occupied=True):
    """Reference decoder for tests; never part of exported runtime/gameplay."""
    assert len(words) == 8
    valid = occupied and all(math.isfinite(v) and int(v) == v for v in words)
    valid = valid and MARKER_MIN <= words[7] <= MARKER_MAX
    valid = valid and all(0 <= value <= (PALETTE_MAX if i < 5 else PAIR_MAX) for i, value in enumerate(words[:7]))
    if not valid: return {'owner': False, 'count': 0, 'rows': []}
    marker = words[7] - 10; count = marker // ROW_RADIX
    descriptors = [words[5] % ROW_RADIX, words[5] // ROW_RADIX,
        words[6] % ROW_RADIX, words[6] // ROW_RADIX, marker % ROW_RADIX]
    rows = []
    for row in range(count):
        word = words[row]; desc = descriptors[row]
        foods = [word % PALETTE_RADIX, word // PALETTE_RADIX % PALETTE_RADIX, word // (PALETTE_RADIX**2)]
        if 39 <= desc <= 119:
            index = desc-39; style = IDLE_STYLES[index//27]; shape = index%27
            rows.append({'descriptor': desc, 'foods': foods, 'style': style, 'state': COMPLETE_STATES[shape]})
        else: rows.append({'descriptor': desc, 'foods': foods})
    return {'owner': True, 'count': count, 'rows': rows}


def build():
    client = json.loads((RP / 'entity/grill_food_visual.entity.json').read_text())['minecraft:client_entity']['description']
    sources = {g['description']['identifier']: g for g in json.loads((RP / 'models/entity/grill_display.geo.json').read_text())['minecraft:geometry']}
    index = json.loads(re.search(r'GRILL_MODEL_INDEX=Object.freeze\((\{.*\})\)', (BP / 'scripts/grill_visual_data.js').read_text()).group(1))
    assert len(index) == 19 and sorted(index.values()) == list(range(19))
    assert [index[name] for name in sorted(index)] == list(range(19))
    body = json.loads((RP / 'models/blocks/skewer_plate.geo.json').read_text())['minecraft:geometry'][0]
    geometries = [geometry('body', lift_cubes(body, 24), body['description']['texture_width'], body['description']['texture_height'])]
    textures = {'body': 'textures/blocks/skewer_plate', 'stick': 'textures/secret_skewer_stick'}
    textures.update({k: v for k, v in palette_refs(213).items() if k.endswith(('_s0', '_s4', '_s6'))})
    controllers = {'controller.render.kg_plate_held.body': {'geometry': 'Geometry.body',
        'materials': [{'*': 'Material.default'}], 'textures': ['Texture.body'],
        'part_visibility': [{'*': 0}, {'plate_body': 'v.kg_plate_owner_occupied == 1'}]}}
    for row in range(5):
        empty = f'empty_{row}'; geometries.append(geometry(empty, [], row=row))
        models, fixed_textures = ['Geometry.' + empty], ['Texture.stick']
        for name in sorted(index):
            slot = index[name]; source = sources[client['geometry']['s' + str(slot*6)]]
            alias = f'fixed_{row}_{slot}'
            # Grill world meshes are authored Y minus one. Restore that one,
            # then add the standard hand pivot, preserving every cube/UV.
            geometries.append(geometry(alias, lift_cubes(source, 25),
                source['description']['texture_width'], source['description']['texture_height'], row=row))
            for cooked in (False, True):
                texture = f'fixed_{slot}_{int(cooked)}'
                textures[texture] = client['textures']['s' + str(slot*6 + (4 if cooked else 0))]
                models.append('Geometry.' + alias); fixed_textures.append('Texture.' + texture)
        desc = f'v.kg_plate_desc_{row}'
        visible = f'v.kg_plate_owner_occupied == 1 && v.kg_plate_count > {row}'
        def controller(alias, geometry_expr, texture_expr, condition, arrays=None):
            body = {'geometry': geometry_expr, 'materials': [{'*': 'Material.default'}],
                'textures': [texture_expr], 'part_visibility': [{'*': 0}, {f'plate_row_{row}': visible + ' && ' + condition}]}
            if arrays: body['arrays'] = arrays
            controllers['controller.render.kg_plate_held.' + alias] = body
        controller(f'fixed_{row}', 'Array.models[' + desc + ' <= 38 ? ' + desc + ' : 0]',
            'Array.items[' + desc + ' <= 38 ? ' + desc + ' : 0]', desc + ' >= 1 && ' + desc + ' <= 38',
            {'geometries': {'Array.models': models}, 'textures': {'Array.items': fixed_textures}})
        stick = f'stick_{row}'; geometries.append(geometry(stick, shaft_cubes(True), row=row))
        secret_condition = desc + ' >= 39 && ' + desc + ' <= 119'
        controller(stick, 'Geometry.' + stick, 'Texture.stick', secret_condition)
        for slot in range(3):
            aliases = []
            for shape, state in enumerate(COMPLETE_STATES):
                alias = f'secret_{row}_{shape}_{slot}'; aliases.append('Geometry.' + alias)
                geometries.append(geometry(alias, state_slot_cubes(state, slot, True), 256, 96, row=row))
            food = f'v.kg_plate_food_{row}_{slot}'
            controller(f'secret_{row}_{slot}', 'Array.states[v.kg_plate_shape_' + str(row) + ']',
                'Array.palette[' + food + ' + v.kg_plate_style_' + str(row) + '*214]',
                secret_condition + ' && ' + food + ' > 0', {'geometries': {'Array.states': aliases},
                'textures': {'Array.palette': [f'Texture.food_{i}_s{style}' for style in IDLE_STYLES for i in range(214)]}})
        # Generic identity-only fallbacks. Ordinary has its existing full mesh;
        # mystery/dark source base models are bare shafts. Their authored
        # source/state metadata overrides require a richer future contract.
        ordinary = json.loads((RP / 'models/entity/a22_bites/ordinary_skewer_stage0.geo.json').read_text())['minecraft:geometry'][0]
        special_models = []
        for special in range(3):
            alias = f'special_{row}_{special}'; special_models.append('Geometry.' + alias)
            cubes = lift_cubes(ordinary, 24) if special == 0 else shaft_cubes(True)
            width = ordinary['description']['texture_width'] if special == 0 else 16
            geometries.append(geometry(alias, cubes, width, 16, row=row))
        textures['special_0'] = 'textures/a22_bites/ordinary_skewer_stage0'
        textures['special_1'] = textures['special_2'] = 'textures/secret_skewer_stick'
        controller(f'special_{row}', 'Array.specials[math.clamp(' + desc + '-120,0,2)]',
            'Array.special_textures[math.clamp(' + desc + '-120,0,2)]', desc + ' >= 120 && ' + desc + ' <= 122',
            {'geometries': {'Array.specials': special_models}, 'textures': {'Array.special_textures': ['Texture.special_' + str(i) for i in range(3)]}})
    references = {g['description']['identifier'].rsplit('.', 1)[1]: g['description']['identifier'] for g in geometries}
    references['qa_probe'] = 'geometry.kg_plate_held.qa_probe'
    references['qa_binary'] = 'geometry.kg_plate_held.qa_binary'
    textures['qa_binary'] = QA_BINARY_TEXTURE
    controllers['controller.render.kg_plate_held.qa_probe'] = {
        'geometry': 'Geometry.qa_probe', 'materials': [{'*': 'Material.default'}],
        'textures': ['Texture.body'], 'part_visibility': [{'*': 0}] +
        [{name: 'v.kg_plate_qa_enabled == 1 && (' + condition + ')'}
            for name, condition in QA_POST_TESTS.items()]}
    # One authored state53 golden-apple ingredient, with no dynamic array or
    # decoded selector. Keep all production row/controller selections intact.
    assert COMPLETE_STATES[18] == 53
    controllers['controller.render.kg_plate_held.qa_forced_food'] = {
        'geometry': 'Geometry.secret_0_18_1', 'materials': [{'*': 'Material.default'}],
        'textures': ['Texture.food_195_s0'],
        'part_visibility': [{'*': 0}, {'plate_row_0': 'v.kg_plate_qa_enabled == 1'}]}
    controllers['controller.render.kg_plate_held.qa_binary'] = qa_binary_controller()
    attach = {'format_version': '1.26.0', 'minecraft:attachable': {'description': {
        'identifier': NS + 'skewer_plate', 'materials': {'default': 'entity_alphatest_one_sided'},
        'textures': textures, 'geometry': references, 'scripts': decoder_scripts(),
        'animations': {key: 'animation.kg_plate_held.' + key for key in ('fp_right', 'fp_left', 'tp_right', 'tp_left', 'layout')},
        'render_controllers': list(controllers)}}}
    compact = ('{"format_version":"1.21.0","minecraft:geometry":[\n' +
        ',\n'.join(json.dumps(g, separators=(',', ':')) for g in geometries) + '\n]}\n').encode()
    return {RP / 'models/entity/plate_held.geo.json': compact,
        RP / 'models/entity/plate_held_qa.geo.json': dump(qa_geometry()),
        RP / 'models/entity/plate_held_binary_qa.geo.json': (json.dumps(qa_binary_geometry(), separators=(',', ':')) + '\n').encode(),
        RP / 'attachables/skewer_plate.attachable.json': dump(attach),
        RP / 'animations/plate_held.animation.json': dump(animations()),
        RP / 'render_controllers/plate_held.render_controllers.json': dump({'format_version': '1.8.0', 'render_controllers': controllers})}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true')
    parser.add_argument('--java-source', type=Path); args = parser.parse_args()
    if args.java_source: verify_java_source(args.java_source)
    for path, data in build().items():
        if args.check: assert path.read_bytes() == data, 'Held plate source drift: ' + str(path.relative_to(ROOT))
        else: path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    print('Held plate source ' + ('check' if args.check else 'build') +
        ' PASS: count0..5, two hand owners, palettes/shapes/styles; native/client and dynamic GUI acceptance separate')


if __name__ == '__main__': main()
