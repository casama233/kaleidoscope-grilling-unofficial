from __future__ import annotations

import argparse
import json
import struct
import zlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects" / "grilling" / "gameplay_core"
BP = PROJECT / "behavior_pack"
RP = PROJECT / "resource_pack"
JAVA_DISPLAY = ROOT / "projects" / "grilling" / "reports" / "java_display_transforms"

SEVERITY_ORDER = {"error": 0, "high": 1, "medium": 2, "info": 3}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def geometry_ref(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("identifier")
    return None


def png_alpha(path: Path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos = 8
    ihdr = None
    idat = bytearray()
    trns = None
    palette = None
    while pos + 12 <= len(data):
        length = struct.unpack(">I", data[pos:pos+4])[0]
        kind = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+length]
        pos += 12 + length
        if kind == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", chunk)
        elif kind == b"IDAT":
            idat.extend(chunk)
        elif kind == b"tRNS":
            trns = bytes(chunk)
        elif kind == b"PLTE":
            palette = bytes(chunk)
        elif kind == b"IEND":
            break
    if not ihdr:
        return None
    width, height, bit_depth, color_type, compression, filtering, interlace = ihdr
    if bit_depth != 8 or interlace != 0 or compression != 0 or filtering != 0:
        return {"supported": False, "width": width, "height": height}
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
    if not channels:
        return {"supported": False, "width": width, "height": height}
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    rows = []
    prev = bytearray(stride)
    p = 0
    for _ in range(height):
        f = raw[p]
        p += 1
        scan = bytearray(raw[p:p+stride])
        p += stride
        out = bytearray(stride)
        for i, x in enumerate(scan):
            a = out[i-channels] if i >= channels else 0
            b = prev[i]
            c = prev[i-channels] if i >= channels else 0
            if f == 0:
                val = x
            elif f == 1:
                val = (x + a) & 255
            elif f == 2:
                val = (x + b) & 255
            elif f == 3:
                val = (x + ((a + b) >> 1)) & 255
            elif f == 4:
                pr = a + b - c
                pa, pb, pc = abs(pr-a), abs(pr-b), abs(pr-c)
                pred = a if pa <= pb and pa <= pc else b if pb <= pc else c
                val = (x + pred) & 255
            else:
                return {"supported": False, "width": width, "height": height}
            out[i] = val
        rows.append(out)
        prev = out
    alphas = []
    if color_type == 6:
        for row in rows:
            alphas.extend(row[3::4])
    elif color_type == 4:
        for row in rows:
            alphas.extend(row[1::2])
    elif color_type == 3 and trns is not None:
        for row in rows:
            for idx in row:
                alphas.append(trns[idx] if idx < len(trns) else 255)
    else:
        alphas = [255] * (width * height)
    return {
        "supported": True,
        "width": width,
        "height": height,
        "min_alpha": min(alphas) if alphas else 255,
        "max_alpha": max(alphas) if alphas else 255,
        "transparent_pixels": sum(a == 0 for a in alphas),
        "partial_alpha_pixels": sum(0 < a < 255 for a in alphas),
        "opaque_pixels": sum(a == 255 for a in alphas),
    }


def add(findings, severity, code, subject, detail, evidence=None):
    row = {"severity": severity, "code": code, "subject": subject, "detail": detail}
    if evidence is not None:
        row["evidence"] = evidence
    findings.append(row)


def collect_geometries(findings):
    index = {}
    duplicates = {}
    for path in sorted(RP.rglob("*.geo.json")):
        doc = load_json(path)
        for geo in doc.get("minecraft:geometry", []):
            ident = geo.get("description", {}).get("identifier")
            if not ident:
                add(findings, "error", "geometry_missing_identifier", str(path.relative_to(ROOT)), "geometry has no identifier")
                continue
            if ident in index:
                duplicates.setdefault(ident, [index[ident]["path"]]).append(path)
            else:
                index[ident] = {"path": path, "geo": geo}
    for ident, paths in duplicates.items():
        add(findings, "error", "duplicate_geometry_identifier", ident, "geometry identifier is defined more than once",
            [str(p.relative_to(ROOT)) for p in paths])
    return index


def collect_animations():
    out = {}
    for path in sorted((RP / "animations").rglob("*.json")) if (RP / "animations").exists() else []:
        doc = load_json(path)
        for ident, body in doc.get("animations", {}).items():
            out[ident] = {"path": path, "body": body}
    return out


def collect_render_controllers():
    out = {}
    root = RP / "render_controllers"
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        doc = load_json(path)
        for ident, body in doc.get("render_controllers", {}).items():
            out[ident] = {"path": path, "body": body}
    return out


def collect_ids():
    ids = set()
    for folder, key in ((BP / "items", "minecraft:item"), (BP / "blocks", "minecraft:block")):
        if not folder.exists():
            continue
        for path in folder.rglob("*.json"):
            body = load_json(path).get(key, {})
            ident = body.get("description", {}).get("identifier")
            if ident:
                ids.add(ident)
    return ids


def terrain_textures():
    path = RP / "textures" / "terrain_texture.json"
    if not path.exists():
        return {}
    data = load_json(path).get("texture_data", {})
    out = {}
    for key, value in data.items():
        tex = value.get("textures") if isinstance(value, dict) else None
        if isinstance(tex, str):
            out[key] = tex
    return out


def check_geometry_structure(findings, geometry_index):
    stats = Counter()
    for ident, row in geometry_index.items():
        geo = row["geo"]
        path = row["path"]
        bones = geo.get("bones", [])
        names = [b.get("name") for b in bones if b.get("name")]
        name_set = set(names)
        for bone in bones:
            parent = bone.get("parent")
            if parent and parent not in name_set:
                add(findings, "error", "missing_bone_parent", ident,
                    f"bone {bone.get('name')} references missing parent {parent}", str(path.relative_to(ROOT)))
            if bone.get("binding"):
                stats["bound_bones"] += 1
            for cube in bone.get("cubes", []):
                size = cube.get("size")
                if not isinstance(size, list) or len(size) != 3:
                    continue
                neg = [v for v in size if isinstance(v, (int, float)) and v < 0]
                zeros = sum(isinstance(v, (int, float)) and abs(v) < 1e-9 for v in size)
                if neg:
                    add(findings, "error", "negative_cube_size", ident,
                        f"bone {bone.get('name')} contains negative cube size {size}", str(path.relative_to(ROOT)))
                elif zeros >= 2:
                    add(findings, "high", "degenerate_line_or_point", ident,
                        f"bone {bone.get('name')} contains a cube with {zeros} zero axes: {size}", str(path.relative_to(ROOT)))
                elif zeros == 1:
                    stats["single_plane_cubes"] += 1
    return dict(stats)


def check_blocks(findings, geometry_index):
    atlas = terrain_textures()
    texture_alpha_cache = {}
    stats = Counter()
    for path in sorted((BP / "blocks").rglob("*.json")):
        block = load_json(path).get("minecraft:block", {})
        ident = block.get("description", {}).get("identifier", str(path.relative_to(ROOT)))
        components = [block.get("components", {})] + [
            p.get("components", {}) for p in block.get("permutations", []) if isinstance(p, dict)
        ]
        refs = set()
        material_slots = set()
        material_rows = []
        for comp in components:
            ref = geometry_ref(comp.get("minecraft:geometry"))
            if ref:
                refs.add(ref)
            mats = comp.get("minecraft:material_instances")
            if isinstance(mats, dict):
                material_slots.update(mats.keys())
                material_rows.append(mats)
        for ref in refs:
            if ref not in geometry_index:
                add(findings, "error", "missing_block_geometry", ident, f"references missing geometry {ref}",
                    str(path.relative_to(ROOT)))
                continue
            geo = geometry_index[ref]["geo"]
            if any(b.get("binding") for b in geo.get("bones", [])):
                add(findings, "error", "world_geometry_has_binding", ident,
                    f"placed block geometry {ref} contains attachable bone binding",
                    str(geometry_index[ref]["path"].relative_to(ROOT)))
            used_slots = set()
            for bone in geo.get("bones", []):
                for cube in bone.get("cubes", []):
                    uv = cube.get("uv", {})
                    if isinstance(uv, dict):
                        for face in uv.values():
                            if isinstance(face, dict) and face.get("material_instance"):
                                used_slots.add(face["material_instance"])
            missing = sorted(x for x in used_slots if x not in material_slots)
            if missing:
                add(findings, "error", "missing_material_instance_slot", ident,
                    f"geometry {ref} uses material slots not defined by block: {missing}",
                    str(geometry_index[ref]["path"].relative_to(ROOT)))
        seen_material = set()
        for mats in material_rows:
            for slot, mat in mats.items():
                if not isinstance(mat, dict):
                    continue
                key = (slot, mat.get("texture"), mat.get("render_method"))
                if key in seen_material:
                    continue
                seen_material.add(key)
                texture_key = mat.get("texture")
                method = mat.get("render_method")
                if not texture_key or texture_key not in atlas:
                    if texture_key:
                        add(findings, "error", "missing_terrain_texture_key", ident,
                            f"material {slot} references missing terrain texture key {texture_key}",
                            str(path.relative_to(ROOT)))
                    continue
                tex_rel = atlas[texture_key]
                tex_path = RP / (tex_rel + ".png")
                if not tex_path.is_file():
                    add(findings, "error", "missing_block_texture_file", ident,
                        f"terrain key {texture_key} points to missing {tex_rel}.png", str(path.relative_to(ROOT)))
                    continue
                if tex_path not in texture_alpha_cache:
                    try:
                        texture_alpha_cache[tex_path] = png_alpha(tex_path)
                    except Exception:
                        texture_alpha_cache[tex_path] = None
                alpha = texture_alpha_cache[tex_path]
                if alpha and alpha.get("supported") and alpha.get("min_alpha") == 255 and method in {"alpha_test", "blend"}:
                    add(findings, "medium", "unnecessary_transparent_render_method", ident,
                        f"{slot} uses {method} but texture {tex_rel}.png is fully opaque",
                        {"texture": tex_rel, "method": method})
                if method == "blend":
                    stats["blend_materials"] += 1
                elif method == "alpha_test":
                    stats["alpha_test_materials"] += 1
                elif method == "opaque":
                    stats["opaque_materials"] += 1
        stats["blocks"] += 1
    return dict(stats)


def animation_aliases(attachable):
    return attachable.get("animations", {}) if isinstance(attachable.get("animations"), dict) else {}


def check_attachables(findings, geometry_index, animations, controllers, known_ids):
    stats = Counter()
    attachable_ids = set()
    root = RP / "attachables"
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        desc = load_json(path).get("minecraft:attachable", {}).get("description", {})
        ident = desc.get("identifier")
        if not ident:
            add(findings, "error", "attachable_missing_identifier", str(path.relative_to(ROOT)), "attachable has no identifier")
            continue
        attachable_ids.add(ident)
        stats["attachables"] += 1
        if ident not in known_ids:
            add(findings, "medium", "attachable_identifier_not_in_bp", ident,
                "attachable identifier is not declared as a canonical BP item/block", str(path.relative_to(ROOT)))
        geo_refs = []
        for ref in (desc.get("geometry") or {}).values():
            if isinstance(ref, str):
                geo_refs.append(ref)
        bound_names = set()
        for ref in geo_refs:
            row = geometry_index.get(ref)
            if not row:
                add(findings, "error", "missing_attachable_geometry", ident, f"references missing geometry {ref}",
                    str(path.relative_to(ROOT)))
                continue
            for bone in row["geo"].get("bones", []):
                if bone.get("binding"):
                    bound_names.add(bone.get("name"))
        if geo_refs and not bound_names:
            add(findings, "high", "attachable_has_no_bound_bone", ident,
                "held geometry has no q.item_slot_to_bone_name binding; hand anchoring depends on fallback behavior",
                {"geometries": geo_refs})
        aliases = animation_aliases(desc)
        for alias, anim_id in aliases.items():
            if anim_id not in animations:
                add(findings, "error", "missing_attachable_animation", ident,
                    f"animation alias {alias} references missing {anim_id}", str(path.relative_to(ROOT)))
                continue
            targeted = set(animations[anim_id]["body"].get("bones", {}).keys())
            risky = sorted(targeted & bound_names)
            if risky:
                add(findings, "high", "animation_moves_bound_bone", ident,
                    f"animation {anim_id} directly transforms bound bone(s) {risky}",
                    str(animations[anim_id]["path"].relative_to(ROOT)))
        for rc in desc.get("render_controllers", []):
            rc_id = rc if isinstance(rc, str) else None
            if rc_id and rc_id not in controllers:
                add(findings, "error", "missing_render_controller", ident,
                    f"references missing render controller {rc_id}", str(path.relative_to(ROOT)))
        for tex_name, tex in (desc.get("textures") or {}).items():
            if not isinstance(tex, str) or not tex.startswith("textures/"):
                continue
            tex_path = RP / (tex + ".png")
            if not tex_path.is_file():
                add(findings, "error", "missing_attachable_texture", ident,
                    f"texture alias {tex_name} points to missing {tex}.png", str(path.relative_to(ROOT)))

    # Known Java-display parity gaps that can be proven from committed reference data.
    rack_report = JAVA_DISPLAY / "advanced_rack_0.json"
    if rack_report.is_file():
        report = load_json(rack_report)
        if report.get("java_display") and "kaleidoscope_grilling:advanced_rack" not in attachable_ids:
            add(findings, "high", "java_display_not_applied", "kaleidoscope_grilling:advanced_rack",
                "Java Advanced Rack has explicit first/third-person transforms but the canonical RP has no held attachable",
                str(rack_report.relative_to(ROOT)))

    for ident in sorted(attachable_ids):
        short = ident.split(":", 1)[-1]
        report_name = None
        if short == "ordinary_skewer":
            report_name = "ordinary_full"
        elif short.startswith("raw_") and short.endswith("_skewer"):
            report_name = short[len("raw_"):-len("_skewer")] + "_raw"
        elif short.startswith("grilled_") and short.endswith("_skewer"):
            report_name = short[len("grilled_"):-len("_skewer")] + "_cooked"
        if report_name:
            report_path = JAVA_DISPLAY / (report_name + ".json")
            if report_path.is_file() and load_json(report_path).get("java_display"):
                path = root / (short + ".attachable.json")
                desc = load_json(path)["minecraft:attachable"]["description"]
                anim_values = set((desc.get("animations") or {}).values())
                if any("a2725.skewer_hold_" in x for x in anim_values if isinstance(x, str)):
                    add(findings, "high", "skewer_uses_generic_bound_root_offset", ident,
                        "Java has item-specific hand rotation/translation/scale, but canonical attachable still uses the generic A2.7.25 bound-root hold offset",
                        str(report_path.relative_to(ROOT)))

    seasoning = {"kaleidoscope_grilling:empty_seasoning_bottle",
                 "kaleidoscope_grilling:pending_seasoning",
                 "kaleidoscope_grilling:special_seasoning"}
    seasoning_report = JAVA_DISPLAY / "seasoning_bottles_1.json"
    if seasoning_report.is_file() and load_json(seasoning_report).get("java_display"):
        for ident in sorted(seasoning & attachable_ids):
            path = root / (ident.split(":", 1)[-1] + ".attachable.json")
            desc = load_json(path)["minecraft:attachable"]["description"]
            if not desc.get("animations"):
                add(findings, "high", "seasoning_java_display_not_applied", ident,
                    "held shell is anchored safely, but Java first/third-person rotation/translation/scale is still not applied",
                    str(seasoning_report.relative_to(ROOT)))

    return dict(stats)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", dest="json_path")
    parser.add_argument("--fail-on-error", action="store_true")
    args = parser.parse_args()

    findings = []
    geometries = collect_geometries(findings)
    animations = collect_animations()
    controllers = collect_render_controllers()
    known_ids = collect_ids()
    geometry_stats = check_geometry_structure(findings, geometries)
    block_stats = check_blocks(findings, geometries)
    attachable_stats = check_attachables(findings, geometries, animations, controllers, known_ids)

    findings.sort(key=lambda x: (SEVERITY_ORDER.get(x["severity"], 99), x["code"], x["subject"]))
    counts = Counter(x["severity"] for x in findings)
    report = {
        "scope": "canonical Gameplay Core render audit",
        "project": str(PROJECT.relative_to(ROOT)).replace("\\", "/"),
        "summary": {
            "errors": counts["error"],
            "high": counts["high"],
            "medium": counts["medium"],
            "info": counts["info"],
            "geometries": len(geometries),
            "animations": len(animations),
            "render_controllers": len(controllers),
            **geometry_stats,
            **block_stats,
            **attachable_stats,
        },
        "findings": findings,
        "validation_boundary": (
            "Static render-chain audit only. It can prove references, geometry/material contracts and known "
            "Java-transform drift, but it cannot certify final Minecraft client pixels, GPU alpha behavior, "
            "FOV, skin interaction, animation timing or Android rendering."
        ),
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.json_path:
        out = Path(args.json_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    if args.fail_on_error and counts["error"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
