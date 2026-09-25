from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[2]
RP = ROOT / "projects/grilling/gameplay_core/resource_pack"
SOURCE = RP / "models/entity/a22_bites"
OUTPUT = RP / "models/entity/a2764_skewer_hand"
OFFSET = (0.0, 7.0, 2.0)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def shifted(vec):
    assert isinstance(vec, list) and len(vec) == 3, vec
    values = [vec[i] + OFFSET[i] for i in range(3)]
    return [int(v) if float(v).is_integer() else v for v in values]


def rebake(doc: dict) -> dict:
    out = deepcopy(doc)
    rows = out["minecraft:geometry"]
    assert len(rows) == 1
    geo = rows[0]
    old_id = geo["description"]["identifier"]
    assert old_id.startswith("geometry.kg_a22."), old_id
    geo["description"]["identifier"] = old_id.replace("geometry.kg_a22.", "geometry.kg_a2764.", 1)

    for bone in geo["bones"]:
        if bone.get("name") == "root":
            assert bone.get("binding") == "q.item_slot_to_bone_name(context.item_slot)"
            assert bone.get("pivot") == [0, 0, 0]
            continue
        if "pivot" in bone:
            bone["pivot"] = shifted(bone["pivot"])
        for cube in bone.get("cubes", []):
            cube["origin"] = shifted(cube["origin"])
            if "pivot" in cube:
                cube["pivot"] = shifted(cube["pivot"])
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    sources = sorted(SOURCE.glob("*.geo.json"))
    assert len(sources) == 150, len(sources)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    expected_names = set()
    for source in sources:
        out = rebake(load(source))
        target = OUTPUT / source.name
        expected_names.add(target.name)
        text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
        if args.check:
            assert target.is_file(), target
            assert load(target) == out, target
        else:
            target.write_text(text, encoding="utf-8")

    actual_names = {p.name for p in OUTPUT.glob("*.geo.json")}
    assert actual_names == expected_names, {
        "missing": sorted(expected_names - actual_names),
        "extra": sorted(actual_names - expected_names),
    }
    print(f"A2.7.65 full hand-space geometries: {len(expected_names)}")


if __name__ == "__main__":
    main()
