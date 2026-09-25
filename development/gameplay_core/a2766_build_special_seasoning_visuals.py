from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "projects/grilling/gameplay_core"
BP = PROJECT / "behavior_pack"
RP = PROJECT / "resource_pack"
SOURCE = ROOT / "projects/grilling/resource_pack/models/entity/kg_a1"
GEOMETRY_OUT = RP / "models/entity/a2766_special_seasoning"
ITEM_OUT = BP / "items"
ATTACHABLE_OUT = RP / "attachables"

RC_ID = "controller.render.kg_a2733.seasoning_bottle_hand"
TEXTURE = "textures/blocks/seasoning_bottle"
DISPLAY = "item.kaleidoscope_grilling:special_seasoning.name"
PREFIX = "kaleidoscope_grilling:special_seasoning_r"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def shift_hand(vec):
    assert isinstance(vec, list) and len(vec) == 3, vec
    out = [vec[0], vec[1] - 6, vec[2]]
    return [int(v) if float(v).is_integer() else v for v in out]


def geometry_doc(variant: int, remaining: int) -> dict:
    source = SOURCE / f"seasoning_v{variant}_r{remaining}.geo.json"
    doc = deepcopy(load(source))
    rows = doc["minecraft:geometry"]
    assert len(rows) == 1
    geo = rows[0]
    assert geo["description"]["identifier"] == f"geometry.kg_a1.seasoning_v{variant}_r{remaining}"
    geo["description"]["identifier"] = f"geometry.kg_a2766.special_seasoning.r{remaining}.v{variant}"
    geo["description"]["visible_bounds_width"] = 3
    geo["description"]["visible_bounds_height"] = 3

    root = geo["bones"][0]
    assert root["name"] == "root"
    assert root.get("pivot") == [0, 0, 0]
    root["binding"] = "q.item_slot_to_bone_name(context.item_slot)"

    for bone in geo["bones"][1:]:
        if "pivot" in bone:
            bone["pivot"] = shift_hand(bone["pivot"])
        for cube in bone.get("cubes", []):
            cube["origin"] = shift_hand(cube["origin"])
            if "pivot" in cube:
                cube["pivot"] = shift_hand(cube["pivot"])
    return doc


def item_doc(variant: int, remaining: int) -> dict:
    identifier = f"{PREFIX}{remaining}_v{variant}"
    return {
        "format_version": "1.26.30",
        "minecraft:item": {
            "description": {
                "identifier": identifier,
                "menu_category": {"category": "none"},
            },
            "components": {
                "minecraft:display_name": {"value": DISPLAY},
                "minecraft:icon": {"textures": {"default": "special_seasoning"}},
                "minecraft:max_stack_size": 1,
                "minecraft:hand_equipped": True,
                "minecraft:block_placer": {
                    "block": "kaleidoscope_grilling:seasoning_bottle_1",
                    "replace_block_item": False,
                },
            },
        },
    }


def attachable_doc(variant: int, remaining: int) -> dict:
    identifier = f"{PREFIX}{remaining}_v{variant}"
    return {
        "format_version": "1.26.0",
        "minecraft:attachable": {
            "description": {
                "identifier": identifier,
                "materials": {"default": "entity_alphablend"},
                "textures": {"default": TEXTURE},
                "geometry": {
                    "default": f"geometry.kg_a2766.special_seasoning.r{remaining}.v{variant}"
                },
                "render_controllers": [RC_ID],
            }
        },
    }


def text(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def target_paths(variant: int, remaining: int):
    stem = f"special_seasoning_r{remaining}_v{variant}"
    return (
        GEOMETRY_OUT / f"{stem}.geo.json",
        ITEM_OUT / f"{stem}.json",
        ATTACHABLE_OUT / f"{stem}.attachable.json",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    GEOMETRY_OUT.mkdir(parents=True, exist_ok=True)
    expected_geo = set()
    expected_items = set()
    expected_attachables = set()

    for variant in range(8):
        for remaining in range(1, 9):
            geo_path, item_path, attach_path = target_paths(variant, remaining)
            rows = (
                (geo_path, geometry_doc(variant, remaining)),
                (item_path, item_doc(variant, remaining)),
                (attach_path, attachable_doc(variant, remaining)),
            )
            expected_geo.add(geo_path.name)
            expected_items.add(item_path.name)
            expected_attachables.add(attach_path.name)
            for path, doc in rows:
                if args.check:
                    assert path.is_file(), path
                    assert load(path) == doc, path
                else:
                    path.write_text(text(doc), encoding="utf-8")

    actual_geo = {p.name for p in GEOMETRY_OUT.glob("*.geo.json")}
    actual_items = {p.name for p in ITEM_OUT.glob("special_seasoning_r*_v*.json")}
    actual_attachables = {p.name for p in ATTACHABLE_OUT.glob("special_seasoning_r*_v*.attachable.json")}
    assert actual_geo == expected_geo, {"geo_missing": sorted(expected_geo-actual_geo), "geo_extra": sorted(actual_geo-expected_geo)}
    assert actual_items == expected_items, {"item_missing": sorted(expected_items-actual_items), "item_extra": sorted(actual_items-expected_items)}
    assert actual_attachables == expected_attachables, {"attach_missing": sorted(expected_attachables-actual_attachables), "attach_extra": sorted(actual_attachables-expected_attachables)}
    print("A2.7.66 special seasoning visual proxies: 64 items + 64 attachables + 64 geometries")


if __name__ == "__main__":
    main()
