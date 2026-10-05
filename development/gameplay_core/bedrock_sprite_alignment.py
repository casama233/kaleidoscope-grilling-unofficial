"""Independent texel-to-surface oracle for the established Bedrock face mapping.

Derived from official Blockbench 5.2.1 Bedrock parseCube and CubeFace.UVToLocal,
not from the food generator. The codec reflects JSON X and reverses up/down UV
endpoints. Face parameterization is evaluated in that imported editor frame,
then returned to Bedrock coordinates. No GPU/rendered pixel parity is implied.
"""
import math

FACE_BY_EDGE = {'up': 'up', 'down': 'down', 'left': 'east', 'right': 'west'}
NEIGHBORS = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}


def uv_to_point(cube, face, u, v):
    origin, size = cube['origin'], cube['size']
    low = [-(origin[0] + size[0]), origin[1], origin[2]]
    high = [-origin[0], origin[1] + size[1], origin[2] + size[2]]
    mapping = cube['uv'][face]
    u0, v0 = mapping['uv']
    u1, v1 = u0 + mapping['uv_size'][0], v0 + mapping['uv_size'][1]
    if face in ('up', 'down'):
        u0, v0, u1, v1 = u1, v1, u0, v0
    a, b = (u - u0) / (u1 - u0), (v - v0) / (v1 - v0)
    if mapping.get('uv_rotation', 0):
        for _ in range(mapping['uv_rotation'] // 90):
            a, b = 1 - b, a
    x, y, z = low
    if face == 'north':
        x, y = high[0] + a * (low[0] - high[0]), high[1] + b * (low[1] - high[1])
    elif face == 'south':
        x, y, z = low[0] + a * (high[0] - low[0]), high[1] + b * (low[1] - high[1]), high[2]
    elif face == 'east':
        x, y, z = high[0], high[1] + b * (low[1] - high[1]), high[2] + a * (low[2] - high[2])
    elif face == 'west':
        y, z = high[1] + b * (low[1] - high[1]), low[2] + a * (high[2] - low[2])
    elif face == 'up':
        x, y, z = low[0] + a * (high[0] - low[0]), high[1], low[2] + b * (high[2] - low[2])
    elif face == 'down':
        x, z = low[0] + a * (high[0] - low[0]), high[2] + b * (low[2] - high[2])
    return [-x, y, z]


def near(a, b):
    return all(math.isclose(x, y, abs_tol=1e-8) for x, y in zip(a, b))


def inspect_alignment(cubes, alpha_rows):
    """Compare rendered side UV samples against actual front/back texel edges.

    Every opaque side texel must sit on its own main-sprite pixel boundary.
    Every actual alpha contour edge must have such a side. Java's merged spans
    may also draw internal boundaries; they still must attach to their texels.
    """
    height, width = len(alpha_rows), len(alpha_rows[0])
    sx, sy = 16 / width, 16 / height
    front = cubes[0]
    issues = []
    attached = set()
    samples = 0
    point_checks = 0
    for index, side in enumerate(cubes[1:], 1):
        for face, mapping in side['uv'].items():
            edge = next((name for name, value in FACE_BY_EDGE.items() if value == face), None)
            if edge is None:
                issues.append({'cube': index, 'reason': 'unexpected side face', 'face': face})
                continue
            ua, va = mapping['uv']
            ub, vb = ua + mapping['uv_size'][0], va + mapping['uv_size'][1]
            x_range = range(max(0, math.floor(min(ua, ub) / sx)), min(width, math.ceil(max(ua, ub) / sx)))
            y_range = range(max(0, math.floor(min(va, vb) / sy)), min(height, math.ceil(max(va, vb) / sy)))
            for y in y_range:
                for x in x_range:
                    if not alpha_rows[y][x]:
                        continue
                    samples += 1
                    u, v = (x + .5) * sx, (y + .5) * sy
                    boundary_u = (x + (edge == 'right')) * sx if edge in ('left', 'right') else u
                    boundary_v = (y + (edge == 'down')) * sy if edge in ('up', 'down') else v
                    north = uv_to_point(front, 'north', boundary_u, boundary_v)
                    south = uv_to_point(front, 'south', boundary_u, boundary_v)
                    expected = [(a + b) / 2 for a, b in zip(north, south)]
                    actual = uv_to_point(side, face, u, v)
                    endpoints_match = True
                    for longitudinal in (0, .5, 1):
                        long_u = (x + longitudinal) * sx if edge in ('up', 'down') else boundary_u
                        long_v = (y + longitudinal) * sy if edge in ('left', 'right') else boundary_v
                        n = uv_to_point(front, 'north', long_u, long_v)
                        s = uv_to_point(front, 'south', long_u, long_v)
                        for depth in (0, .1, .5, .9, 1):
                            sample_u = (x + depth) * sx if edge in ('left', 'right') else (x + longitudinal) * sx
                            sample_v = (y + depth) * sy if edge in ('up', 'down') else (y + longitudinal) * sy
                            point = uv_to_point(side, face, sample_u, sample_v)
                            point_checks += 1
                            if not near(point[:2], n[:2]) or not near(point[:2], s[:2]) or not -.50000001 <= point[2] <= .50000001:
                                endpoints_match = False
                            if depth in (0, 1) and not math.isclose(abs(point[2]), .5, abs_tol=1e-8):
                                endpoints_match = False
                    if not near(north[:2], south[:2]) or not near(actual, expected):
                        issues.append({'cube': index, 'face': face, 'pixel': [x, y], 'reason': 'detached or reversed sampled texel', 'expected': expected, 'actual': actual})
                    elif side['origin'][2] != -.5 or side['size'][2] != 1:
                        issues.append({'cube': index, 'reason': 'side does not bridge both main planes'})
                    elif not endpoints_match:
                        issues.append({'cube': index, 'face': face, 'pixel': [x, y], 'reason': 'side cell endpoints or depth samples misalign with main cell edge'})
                    else:
                        attached.add((edge, x, y))
    exposed = 0
    for y in range(height):
        for x in range(width):
            if not alpha_rows[y][x]:
                continue
            for edge, (dx, dy) in NEIGHBORS.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and alpha_rows[ny][nx]:
                    continue
                exposed += 1
                if (edge, x, y) not in attached:
                    issues.append({'pixel': [x, y], 'face': FACE_BY_EDGE[edge], 'reason': 'actual alpha contour missing attached side'})
    return {'opaque_side_texel_samples': samples, 'actual_alpha_contour_edges': exposed, 'sampled_vertex_depth_checks': point_checks, 'issues': issues}
