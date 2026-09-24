from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RP = ROOT / "projects" / "grilling" / "gameplay_core" / "resource_pack"
REPORTS = ROOT / "projects" / "grilling" / "reports" / "java_display_transforms"

OLD_FP = "animation.kaleidoscope_grilling.a2725.skewer_hold_first_person"
OLD_TP = "animation.kaleidoscope_grilling.a2725.skewer_hold_third_person"
ROOT_BINDING = "q.item_slot_to_bone_name(context.item_slot)"

ANIM_IDS = {
    "fp_right": "animation.kaleidoscope_grilling.a2764.skewer_fp_right",
    "fp_left": "animation.kaleidoscope_grilling.a2764.skewer_fp_left",
    "tp_right": "animation.kaleidoscope_grilling.a2764.skewer_tp_right",
    "tp_left": "animation.kaleidoscope_grilling.a2764.skewer_tp_left",
}
JAVA_KEYS = {
    "fp_right": "firstperson_righthand",
    "fp_left": "firstperson_lefthand",
    "tp_right": "thirdperson_righthand",
    "tp_left": "thirdperson_lefthand",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_java_display():
    base = load(REPORTS / "beef_raw.json")["java_display"]
    expected = {alias: base[key] for alias, key in JAVA_KEYS.items()}
    checked = 0
    for path in sorted(REPORTS.glob("*.json")):
        doc = load(path)
        if "item/fixed_skewers/" not in str(doc.get("source_model", "")):
            continue
        display = doc.get("java_display", {})
        if not all(key in display for key in JAVA_KEYS.values()):
            continue
        for alias, key in JAVA_KEYS.items():
            if display[key] != expected[alias]:
                raise RuntimeError(f"fixed-skewer Java held transform drift: {path.name} {key}")
        checked += 1
    if checked < 30:
        raise RuntimeError(f"expected broad fixed-skewer Java display evidence, got {checked}")
    return expected, checked


def geometry_index():
    out = {}
    for path in sorted((RP / "models").rglob("*.geo.json")):
        doc = load(path)
        for geo in doc.get("minecraft:geometry", []):
            ident = geo.get("description", {}).get("identifier")
            if ident:
                if ident in out:
                    raise RuntimeError(f"duplicate geometry identifier: {ident}")
                out[ident] = path
    return out


def skewer_attachables():
    rows = []
    for path in sorted((RP / "attachables").glob("*.attachable.json")):
        doc = load(path)
        desc = doc.get("minecraft:attachable", {}).get("description", {})
        anims = set((desc.get("animations") or {}).values())
        if OLD_FP in anims or OLD_TP in anims:
            rows.append((path, doc))
    if len(rows) != 39:
        raise RuntimeError(f"expected 39 fixed-skewer attachables, got {len(rows)}")
    return rows


def patch_geometry(path: Path, expected_refs: set[str]):
    doc = load(path)
    geos = doc.get("minecraft:geometry", [])
    matched = [g for g in geos if g.get("description", {}).get("identifier") in expected_refs]
    if len(matched) != 1:
        raise RuntimeError(f"expected one referenced geometry in {path}, got {len(matched)}")
    geo = matched[0]
    bones = geo.get("bones", [])
    if not bones or bones[0].get("name") != "root":
        raise RuntimeError(f"root drift in {path}")
    root = bones[0]
    if root.get("binding") != ROOT_BINDING:
        raise RuntimeError(f"item-slot binding drift in {path}")
    if any(b.get("name") == "display" for b in bones):
        display = next(b for b in bones if b.get("name") == "display")
        if display.get("parent") != "root":
            raise RuntimeError(f"display parent drift in {path}")
        return False
    display = {"name": "display", "parent": "root", "pivot": [0, 0, 0]}
    direct = 0
    for bone in bones[1:]:
        parent = bone.get("parent")
        if parent == "root":
            bone["parent"] = "display"
            direct += 1
        elif parent is None:
            raise RuntimeError(f"unexpected extra root bone {bone.get('name')} in {path}")
    if direct == 0:
        raise RuntimeError(f"no shell bones moved under display in {path}")
    geo["bones"] = [root, display, *bones[1:]]
    write(path, doc)
    return True


def main():
    java, evidence_count = canonical_java_display()
    attachables = skewer_attachables()
    index = geometry_index()

    refs = set()
    for _, doc in attachables:
        desc = doc["minecraft:attachable"]["description"]
        for ref in (desc.get("geometry") or {}).values():
            if isinstance(ref, str):
                refs.add(ref)
    if len(refs) != 150:
        raise RuntimeError(f"expected 150 bite-stage geometry refs, got {len(refs)}")

    by_path: dict[Path, set[str]] = {}
    for ref in refs:
        path = index.get(ref)
        if path is None:
            raise RuntimeError(f"missing referenced geometry {ref}")
        if "models/entity/a22_bites/" not in path.as_posix():
            raise RuntimeError(f"unexpected fixed-skewer geometry location: {ref} -> {path}")
        by_path.setdefault(path, set()).add(ref)

    changed_geometries = 0
    for path, path_refs in sorted(by_path.items()):
        if patch_geometry(path, path_refs):
            changed_geometries += 1

    anim_path = RP / "animations" / "a2764_skewer_java_display.animation.json"
    animations = {"format_version": "1.8.0", "animations": {}}
    for alias, java_value in java.items():
        body = {}
        if "translation" in java_value:
            body["position"] = java_value["translation"]
        if "rotation" in java_value:
            body["rotation"] = java_value["rotation"]
        if "scale" in java_value:
            body["scale"] = java_value["scale"]
        animations["animations"][ANIM_IDS[alias]] = {"loop": True, "bones": {"display": body}}
    write(anim_path, animations)

    conditions = {
        "fp_right": "context.is_first_person == 1.0 && q.item_slot_to_bone_name(context.item_slot) == 'rightItem'",
        "fp_left": "context.is_first_person == 1.0 && q.item_slot_to_bone_name(context.item_slot) == 'leftItem'",
        "tp_right": "context.is_first_person == 0.0 && q.item_slot_to_bone_name(context.item_slot) == 'rightItem'",
        "tp_left": "context.is_first_person == 0.0 && q.item_slot_to_bone_name(context.item_slot) == 'leftItem'",
    }
    changed_attachables = 0
    for path, doc in attachables:
        desc = doc["minecraft:attachable"]["description"]
        desc["animations"] = dict(ANIM_IDS)
        scripts = dict(desc.get("scripts") or {})
        scripts["animate"] = [{alias: conditions[alias]} for alias in ("fp_right", "fp_left", "tp_right", "tp_left")]
        desc["scripts"] = scripts
        write(path, doc)
        changed_attachables += 1

    # Verify the same 39 paths captured before mutation; successful migration intentionally removes OLD_FP/OLD_TP.
    for path, _before_doc in attachables:
        doc = load(path)
        desc = doc["minecraft:attachable"]["description"]
        if set((desc.get("animations") or {}).values()) != set(ANIM_IDS.values()):
            raise RuntimeError(f"attachable animation contract drift after write: {path}")
        for ref in (desc.get("geometry") or {}).values():
            geo_doc = load(index[ref])
            geo = next(g for g in geo_doc["minecraft:geometry"] if g["description"]["identifier"] == ref)
            bones = {b.get("name"): b for b in geo.get("bones", [])}
            if bones.get("root", {}).get("binding") != ROOT_BINDING:
                raise RuntimeError(f"root binding lost after write: {ref}")
            if bones.get("display", {}).get("parent") != "root":
                raise RuntimeError(f"display hierarchy missing after write: {ref}")
            for name, bone in bones.items():
                if name not in {"root", "display"} and bone.get("parent") == "root":
                    raise RuntimeError(f"shell bone still directly under bound root: {ref} {name}")

    print(json.dumps({
        "fixed_skewer_attachables": changed_attachables,
        "bite_geometries": len(refs),
        "geometry_files_changed": changed_geometries,
        "java_display_reports_checked": evidence_count,
        "shared_animation": str(anim_path.relative_to(ROOT)).replace("\\", "/"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
