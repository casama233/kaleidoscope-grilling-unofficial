from __future__ import annotations

"""Render real GUI icons for Grilling's 3D skewer items.

A2.0 accidentally copied Java model material sheets directly into Bedrock's
item_texture atlas. Bedrock correctly treated those sheets as 2D inventory
icons, which is why creative inventory showed chopped UV fragments.

This renderer independently resolves the pinned Java item-model parent chain,
textures the actual model faces, applies the Java GUI orientation when present,
and rasterizes a deterministic transparent icon. Held/eating 3D visuals remain
owned by Bedrock attachables and are deliberately separate from these icons.
"""

import argparse
import copy
import json
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "projects/grilling/source_snapshots/common/src/main/resources/assets"
P = ROOT / "projects/grilling/gameplay_core"
BP = P / "behavior_pack"
RP = P / "resource_pack"
OUT = RP / "textures/items"
REPORTS = P / "reports"

FALLBACK_MODEL = {
    "mysterious_skewer": "kaleidoscope_grilling:item/ordinary_skewer",
    "dark_grilling": "kaleidoscope_grilling:item/ordinary_skewer",
}

SIZE = 64
MARGIN = 5


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rotation(angles):
    x, y, z = np.radians(np.array(angles, dtype=float))
    cx, sx = math.cos(x), math.sin(x)
    cy, sy = math.cos(y), math.sin(y)
    cz, sz = math.cos(z), math.sin(z)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=float)
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=float)
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=float)
    return rz @ ry @ rx


def model_path(identifier: str) -> Path:
    if ":" not in identifier:
        identifier = "minecraft:" + identifier
    ns, name = identifier.split(":", 1)
    if not re.fullmatch(r"[a-z0-9_.-]+", ns) or not re.fullmatch(r"[a-z0-9_./-]+", name):
        raise ValueError("unsafe model id " + identifier)
    return ASSETS / ns / "models" / (name + ".json")


def read_model(identifier: str, ancestry=()):
    if identifier in ancestry or len(ancestry) > 48:
        raise ValueError("model parent cycle")
    path = model_path(identifier)
    own = load_json(path)
    merged = {}
    if "parent" in own:
        merged = read_model(own["parent"], ancestry + (identifier,))
    else:
        merged = {}
    merged = copy.deepcopy(merged)
    for key, value in own.items():
        if key == "parent":
            continue
        if key in ("textures", "display"):
            base = dict(merged.get(key, {}))
            base.update(copy.deepcopy(value))
            merged[key] = base
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def resolve_texture(ref: str, aliases: dict) -> str:
    seen = set()
    while ref.startswith("#"):
        key = ref[1:]
        if key in seen or key not in aliases:
            raise ValueError("bad texture alias " + ref)
        seen.add(key)
        ref = aliases[key]
    return ref


def texture_image(ref: str) -> np.ndarray:
    if ":" not in ref:
        ref = "minecraft:" + ref
    ns, name = ref.split(":", 1)
    path = ASSETS / ns / "textures" / (name + ".png")
    return np.asarray(Image.open(path).convert("RGBA"))


def face_vertices(a, b, face):
    x, y, z = a
    X, Y, Z = b
    table = {
        "north": [[X, Y, z], [x, Y, z], [x, y, z], [X, y, z]],
        "south": [[x, Y, Z], [X, Y, Z], [X, y, Z], [x, y, Z]],
        "east": [[X, Y, Z], [X, Y, z], [X, y, z], [X, y, Z]],
        "west": [[x, Y, z], [x, Y, Z], [x, y, Z], [x, y, z]],
        "up": [[x, Y, z], [X, Y, z], [X, Y, Z], [x, Y, Z]],
        "down": [[x, y, Z], [X, y, Z], [X, y, z], [x, y, z]],
    }
    return np.array(table[face], dtype=float)


def uv_rect(uv):
    a, b, c, d = [float(x) for x in uv]
    return np.array([[a, b], [c, b], [c, d], [a, d]], dtype=float)


def default_uv(element, face):
    # Vanilla generated-box fallback. Most Grilling source models use explicit UV;
    # this covers the few ordinary full-cube-like faces without inventing atlas data.
    a = np.array(element["from"], dtype=float)
    b = np.array(element["to"], dtype=float)
    x1, y1, z1 = a
    x2, y2, z2 = b
    table = {
        "north": [x1, 16-y2, x2, 16-y1],
        "south": [x2, 16-y2, x1, 16-y1],
        "east": [z1, 16-y2, z2, 16-y1],
        "west": [z2, 16-y2, z1, 16-y1],
        "up": [x1, z1, x2, z2],
        "down": [x1, z2, x2, z1],
    }
    return table[face]


def model_faces(model):
    aliases = model.get("textures", {})
    cache = {}
    faces = []
    for element in model.get("elements", []):
        a = np.array(element["from"], dtype=float)
        b = np.array(element["to"], dtype=float)
        er = element.get("rotation")
        em = np.eye(3)
        pivot = np.zeros(3)
        rescale = None
        if er:
            angles = [0.0, 0.0, 0.0]
            angles["xyz".index(er["axis"])] = float(er["angle"])
            em = rotation(angles)
            pivot = np.array(er.get("origin", [8, 8, 8]), dtype=float)
            if er.get("rescale"):
                c = 1.0 / math.cos(math.radians(float(er["angle"])))
                rescale = np.full(3, c)
                rescale["xyz".index(er["axis"])] = 1.0
        for face, spec in element.get("faces", {}).items():
            tref = resolve_texture(str(spec["texture"]), aliases)
            if tref not in cache:
                cache[tref] = texture_image(tref)
            tex = cache[tref]
            uv = uv_rect(spec.get("uv", default_uv(element, face)))
            rot = int(spec.get("rotation", 0))
            if rot not in (0, 90, 180, 270):
                raise ValueError("unsupported UV rotation")
            uv = np.roll(uv, -(rot // 90), axis=0)
            uv *= np.array([tex.shape[1] / 16.0, tex.shape[0] / 16.0])
            pts = face_vertices(a, b, face)
            if er:
                rel = pts - pivot
                if rescale is not None:
                    rel = rel * rescale
                pts = rel @ em.T + pivot
            faces.append({"points": pts, "uv": uv, "tex": tex})
    return faces


def apply_gui_transform(faces, model):
    gui = model.get("display", {}).get("gui")
    if not gui:
        # A stable isometric fallback for source models without an authored GUI pose.
        gui = {"rotation": [25, 225, 0], "scale": [1, 1, 1], "translation": [0, 0, 0]}
    scale = np.array(gui.get("scale", [1, 1, 1]), dtype=float)
    matrix = rotation(gui.get("rotation", [0, 0, 0]))
    translation = np.array(gui.get("translation", [0, 0, 0]), dtype=float)
    center = np.array([8.0, 8.0, 8.0])
    result = []
    for f in faces:
        g = dict(f)
        p = (f["points"] - center) * scale
        # Java's model display transform is used only for its authored orientation.
        # Translation does not affect final framing, but retaining it preserves relative
        # placement for asymmetric models and keeps this path faithful to source data.
        g["points"] = p @ matrix.T + translation
        result.append(g)
    return result


def normal(points):
    n = -np.cross(points[1] - points[0], points[2] - points[0])
    m = np.linalg.norm(n)
    return n / m if m > 1e-9 else n


def render(faces, size=SIZE):
    if not faces:
        raise ValueError("model has no faces")
    points = np.concatenate([f["points"] for f in faces])
    # Java GUI items are viewed from the front after the authored GUI transform.
    # Use X/Y for screen and Z as depth, then fit the transformed silhouette.
    lo = points[:, :2].min(axis=0)
    hi = points[:, :2].max(axis=0)
    span = np.maximum(hi - lo, 1e-4)
    scale = min((size - 2*MARGIN) / span[0], (size - 2*MARGIN) / span[1])
    center = (lo + hi) / 2
    image = np.zeros((size, size, 4), dtype=np.float64)
    depthbuf = np.full((size, size), -np.inf, dtype=np.float64)
    # Slightly top/front-biased light, close to Java's GUI lighting while preserving
    # source pixel colors enough to stay recognisable.
    light = np.array([-0.25, 0.65, -0.72], dtype=float)
    light /= np.linalg.norm(light)

    for f in faces:
        p3 = f["points"]
        n = normal(p3)
        # Render both winding conventions safely. Java item models can contain thin
        # or intentionally reversed faces; alpha/depth resolves visibility.
        p = p3.copy()
        xy = (p[:, :2] - center) * scale
        xy[:, 1] *= -1
        xy += np.array([size/2, size/2])
        z = -p[:, 2]
        shade = 0.72 + 0.28 * max(0.0, float(np.dot(n, light)))
        for tri_index, ids in enumerate(([0, 1, 2], [0, 2, 3])):
            v = xy[list(ids)]
            t = f["uv"][list(ids)]
            zz = z[list(ids)]
            xl = max(0, int(math.floor(v[:, 0].min())))
            xh = min(size - 1, int(math.ceil(v[:, 0].max())))
            yl = max(0, int(math.floor(v[:, 1].min())))
            yh = min(size - 1, int(math.ceil(v[:, 1].max())))
            if xl > xh or yl > yh:
                continue
            den = (v[1,1]-v[2,1])*(v[0,0]-v[2,0]) + (v[2,0]-v[1,0])*(v[0,1]-v[2,1])
            if abs(den) < 1e-10:
                continue
            ys, xs = np.mgrid[yl:yh+1, xl:xh+1]
            xs = xs + .5
            ys = ys + .5
            aa = ((v[1,1]-v[2,1])*(xs-v[2,0]) + (v[2,0]-v[1,0])*(ys-v[2,1])) / den
            bb = ((v[2,1]-v[0,1])*(xs-v[2,0]) + (v[0,0]-v[2,0])*(ys-v[2,1])) / den
            cc = 1 - aa - bb
            mask = (aa >= -1e-7) & (bb >= -1e-7) & (cc >= -1e-7)
            if tri_index == 1:
                mask &= cc > 1e-7
            if not mask.any():
                continue
            u = np.floor(aa*t[0,0] + bb*t[1,0] + cc*t[2,0]).astype(int)
            w = np.floor(aa*t[0,1] + bb*t[1,1] + cc*t[2,1]).astype(int)
            tex = f["tex"]
            u = np.clip(u, 0, tex.shape[1]-1)
            w = np.clip(w, 0, tex.shape[0]-1)
            rgba = tex[w, u].astype(np.float64)
            alpha = rgba[..., 3] / 255.0
            depth = aa*zz[0] + bb*zz[1] + cc*zz[2]
            region = (slice(yl, yh+1), slice(xl, xh+1))
            visible = mask & (alpha > 0) & (depth >= depthbuf[region] - 1e-8)
            if not visible.any():
                continue
            dst = image[region]
            src_rgb = rgba[..., :3] * shade
            a = alpha[..., None]
            dst_rgb = dst[..., :3]
            dst_a = dst[..., 3:4] / 255.0
            out_a = a + dst_a * (1-a)
            out_rgb = np.divide(src_rgb*a + dst_rgb*dst_a*(1-a), out_a, out=np.zeros_like(src_rgb), where=out_a>1e-9)
            dst[..., :3][visible] = out_rgb[visible]
            dst[..., 3][visible] = (out_a[..., 0] * 255)[visible]
            image[region] = dst
            depthbuf[region][visible] = depth[visible]
    return Image.fromarray(np.clip(image, 0, 255).round().astype("uint8"), "RGBA")


def source_model_for(stem: str) -> str:
    direct = ASSETS / "kaleidoscope_grilling/models/item" / (stem + ".json")
    if direct.is_file():
        return "kaleidoscope_grilling:item/" + stem
    if stem in FALLBACK_MODEL:
        return FALLBACK_MODEL[stem]
    raise FileNotFoundError("no Java item model for " + stem)


def icon_items():
    result = []
    for p in sorted((BP / "items").glob("*.json")):
        item = load_json(p).get("minecraft:item", {})
        comp = item.get("components", {})
        stem = p.stem
        # The broken path affects formal 3D skewers. Ordinary/mysterious/dark use the
        # same historical source sheet and are fixed alongside them.
        if (stem.startswith("raw_") or stem.startswith("grilled_")) and stem.endswith("_skewer"):
            result.append(stem)
        elif stem in ("ordinary_skewer", "mysterious_skewer", "dark_grilling"):
            result.append(stem)
    return result


def contact_sheet(rows):
    cols = 8
    cell = 92
    out = Image.new("RGBA", (cols*cell, math.ceil(len(rows)/cols)*cell), (24, 27, 34, 255))
    draw = ImageDraw.Draw(out)
    for i, row in enumerate(rows):
        x = (i % cols) * cell
        y = (i // cols) * cell
        icon = Image.open(row["path"]).convert("RGBA")
        out.alpha_composite(icon, (x + 14, y + 2))
        label = row["id"].replace("raw_", "r_").replace("grilled_", "g_")[:14]
        draw.text((x + 3, y + 69), label, fill=(235,235,235,255))
    REPORTS.mkdir(parents=True, exist_ok=True)
    out.save(REPORTS / "a273-item-icon-contact.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=SIZE)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for stem in icon_items():
        mid = source_model_for(stem)
        model = read_model(mid)
        faces = apply_gui_transform(model_faces(model), model)
        icon = render(faces, args.size)
        alpha = np.asarray(icon)[..., 3]
        ys, xs = np.nonzero(alpha > 0)
        if not len(xs):
            raise RuntimeError("empty icon " + stem)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]
        if bbox[2]-bbox[0] < 8 or bbox[3]-bbox[1] < 8:
            raise RuntimeError("tiny icon silhouette " + stem + " " + repr(bbox))
        path = OUT / (stem + ".png")
        icon.save(path, optimize=True)
        rows.append({"id": stem, "model": mid, "bbox": bbox, "opaque_pixels": int((alpha > 0).sum()), "path": path})
    contact_sheet(rows)
    report = {
        "version": "A2.7.3-render-baseline",
        "renderer": "pinned Java model + authored GUI transform -> independent Bedrock UI icon",
        "count": len(rows),
        "items": [{k: v for k, v in row.items() if k != "path"} for row in rows],
        "minecraft_tested": False,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "a273-item-icons.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"icons": len(rows), "contact": str(REPORTS / "a273-item-icon-contact.png")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
