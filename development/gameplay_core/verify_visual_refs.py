from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "projects/grilling/gameplay_core"
BP = PROJECT / "behavior_pack"
RP = PROJECT / "resource_pack"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def asset_exists(raw: str) -> bool:
    value = str(raw or "").replace("\\", "/")
    if not value or value.startswith("http"):
        return False
    base = RP / value
    if base.is_file():
        return True
    return any((RP / f"{value}{ext}").is_file() for ext in (".png", ".tga", ".jpg", ".jpeg"))

def collect_geometry_ids() -> set[str]:
    ids: set[str] = set()
    for path in RP.rglob("*.geo.json"):
        doc = load(path)
        for row in doc.get("minecraft:geometry", []):
            identifier = row.get("description", {}).get("identifier")
            if identifier:
                assert identifier not in ids, f"duplicate geometry identifier {identifier}: {path}"
                ids.add(identifier)
    return ids

def collect_render_controller_ids() -> set[str]:
    ids: set[str] = set()
    for path in (RP / "render_controllers").glob("*.json"):
        doc = load(path)
        for identifier in doc.get("render_controllers", {}):
            assert identifier not in ids, f"duplicate render controller {identifier}: {path}"
            ids.add(identifier)
    return ids

def collect_animation_ids() -> set[str]:
    ids: set[str] = set()
    for path in (RP / "animations").glob("*.json"):
        doc = load(path)
        for identifier in doc.get("animations", {}):
            assert identifier not in ids, f"duplicate animation {identifier}: {path}"
            ids.add(identifier)
    return ids

def audit_attachables(geometry_ids: set[str], rc_ids: set[str], animation_ids: set[str]) -> tuple[int, int, int, int]:
    files = sorted((RP / "attachables").glob("*.json"))
    identifiers: set[str] = set()
    geometry_refs = rc_refs = animation_refs = texture_refs = 0
    for path in files:
        desc = load(path)["minecraft:attachable"]["description"]
        identifier = desc["identifier"]
        assert identifier not in identifiers, f"duplicate attachable identifier {identifier}"
        identifiers.add(identifier)

        for alias, ref in desc.get("geometry", {}).items():
            if isinstance(ref, str) and ref.startswith("geometry."):
                assert ref in geometry_ids, f"{path}: missing geometry {alias} -> {ref}"
                geometry_refs += 1

        for entry in desc.get("render_controllers", []):
            if isinstance(entry, str):
                assert entry in rc_ids, f"{path}: missing render controller {entry}"
                rc_refs += 1
            elif isinstance(entry, dict):
                for key in entry:
                    assert key in rc_ids, f"{path}: missing render controller {key}"
                    rc_refs += 1

        animations = desc.get("animations", {})
        for alias, ref in animations.items():
            if isinstance(ref, str) and ref.startswith("animation."):
                assert ref in animation_ids, f"{path}: missing animation {alias} -> {ref}"
                animation_refs += 1

        for entry in desc.get("scripts", {}).get("animate", []):
            aliases = [entry] if isinstance(entry, str) else list(entry) if isinstance(entry, dict) else []
            for alias in aliases:
                assert alias in animations, f"{path}: scripts.animate references undefined alias {alias}"

        for alias, texture in desc.get("textures", {}).items():
            if isinstance(texture, str) and texture.startswith("textures/"):
                assert asset_exists(texture), f"{path}: missing texture {alias} -> {texture}"
                texture_refs += 1

        material_values = desc.get("materials", {})
        assert material_values, f"{path}: attachable has no material mapping"
    return len(files), geometry_refs, rc_refs, animation_refs + texture_refs

def audit_atlas(path: Path) -> tuple[int, int]:
    doc = load(path)
    rows = doc.get("texture_data", {})
    seen_paths = 0
    for key, row in rows.items():
        values = row.get("textures") if isinstance(row, dict) else None
        textures = values if isinstance(values, list) else [values]
        assert textures and all(isinstance(v, str) and v for v in textures), f"{path}: invalid atlas entry {key}"
        for texture in textures:
            assert asset_exists(texture), f"{path}: missing texture file {key} -> {texture}"
            seen_paths += 1
    return len(rows), seen_paths

def audit_block_geometry_and_materials(geometry_ids: set[str], terrain_keys: set[str]) -> tuple[int, int]:
    blocks = 0
    geometry_refs = 0
    for path in sorted((BP / "blocks").glob("*.json")):
        doc = load(path)
        block = doc.get("minecraft:block")
        if not isinstance(block, dict):
            continue
        blocks += 1
        components = block.get("components", {})

        geometry = components.get("minecraft:geometry")
        identifier = None
        if isinstance(geometry, str):
            identifier = geometry
        elif isinstance(geometry, dict):
            identifier = geometry.get("identifier")
        if isinstance(identifier, str) and identifier.startswith("geometry.") and identifier != "minecraft:geometry.full_block":
            assert identifier in geometry_ids, f"{path}: missing block geometry {identifier}"
            geometry_refs += 1

        instances = components.get("minecraft:material_instances", {})
        if isinstance(instances, dict):
            for slot, row in instances.items():
                if not isinstance(row, dict):
                    continue
                texture = row.get("texture")
                if isinstance(texture, str) and texture and not texture.startswith("minecraft:"):
                    assert texture in terrain_keys, f"{path}: material {slot} uses missing terrain key {texture}"
    return blocks, geometry_refs

def audit_item_icons(item_keys: set[str]) -> tuple[int, int]:
    items = refs = 0
    for path in sorted((BP / "items").glob("*.json")):
        doc = load(path)
        item = doc.get("minecraft:item")
        if not isinstance(item, dict):
            continue
        items += 1
        icon = item.get("components", {}).get("minecraft:icon")
        key = icon if isinstance(icon, str) else icon.get("texture") if isinstance(icon, dict) else None
        if isinstance(key, str) and key and not key.startswith("minecraft:"):
            assert key in item_keys, f"{path}: missing item atlas key {key}"
            refs += 1
    return items, refs

def audit_seasoning_bottle_runtime_chain() -> None:
    items = ("empty_seasoning_bottle", "pending_seasoning", "special_seasoning")
    expected_geometry = "geometry.kg_a2733.seasoning_bottle_hand"
    expected_rc = "controller.render.kg_a2733.seasoning_bottle_hand"
    for item in items:
        path = RP / "attachables" / f"{item}.attachable.json"
        desc = load(path)["minecraft:attachable"]["description"]
        assert desc.get("geometry") == {"default": expected_geometry}, path
        assert desc.get("render_controllers") == [expected_rc], path
        assert desc.get("textures") == {"default": "textures/blocks/seasoning_bottle"}, path
        assert "animations" not in desc, f"{path}: A2733 hand-space geometry must not receive the retired A2726 -6Y animation again"
        assert "scripts" not in desc, f"{path}: A2733 hand-space geometry must not double-apply a hold transform"

    geo = load(RP / "models/entity/a2733_seasoning_bottle_hand.geo.json")["minecraft:geometry"][0]
    root = geo["bones"][0]
    assert root["name"] == "root"
    assert root.get("binding") == "q.item_slot_to_bone_name(context.item_slot)"
    assert all(
        bone.get("name") == "root" or (
            isinstance(bone.get("pivot"), list) and len(bone["pivot"]) == 3 and float(bone["pivot"][1]) == -6.0
        )
        for bone in geo["bones"]
    ), "A2733 seasoning hand geometry lost its baked -6Y hand-space transform"

def main() -> None:
    geometry_ids = collect_geometry_ids()
    rc_ids = collect_render_controller_ids()
    animation_ids = collect_animation_ids()

    item_atlas = load(RP / "textures/item_texture.json").get("texture_data", {})
    terrain_atlas = load(RP / "textures/terrain_texture.json").get("texture_data", {})

    attachable_files, attachable_geometry_refs, attachable_rc_refs, attachable_other_refs = audit_attachables(
        geometry_ids, rc_ids, animation_ids
    )
    item_atlas_entries, item_texture_paths = audit_atlas(RP / "textures/item_texture.json")
    terrain_atlas_entries, terrain_texture_paths = audit_atlas(RP / "textures/terrain_texture.json")
    block_files, block_geometry_refs = audit_block_geometry_and_materials(geometry_ids, set(terrain_atlas))
    item_files, item_icon_refs = audit_item_icons(set(item_atlas))
    audit_seasoning_bottle_runtime_chain()

    result = {
        "visual_reference_gate": "PASS",
        "geometry_identifiers": len(geometry_ids),
        "render_controller_identifiers": len(rc_ids),
        "animation_identifiers": len(animation_ids),
        "attachable_files": attachable_files,
        "attachable_geometry_refs": attachable_geometry_refs,
        "attachable_render_controller_refs": attachable_rc_refs,
        "attachable_animation_or_texture_refs": attachable_other_refs,
        "item_atlas_entries": item_atlas_entries,
        "item_texture_paths": item_texture_paths,
        "terrain_atlas_entries": terrain_atlas_entries,
        "terrain_texture_paths": terrain_texture_paths,
        "block_files": block_files,
        "block_geometry_refs": block_geometry_refs,
        "item_files": item_files,
        "item_icon_refs": item_icon_refs,
        "seasoning_bottle_a2733_chain": "PASS",
        "minecraft_tested": False,
        "client_visuals_tested": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
