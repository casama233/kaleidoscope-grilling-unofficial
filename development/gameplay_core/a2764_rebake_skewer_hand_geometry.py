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
SAMPLES = ("raw_beef_skewer", "grilled_beef_skewer", "ordinary_skewer")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def shifted(vec):
    assert isinstance(vec, list) and len(vec) == 3, vec
    values = [vec[i] + OFFSET[i] for i in range(3)]
    return [int(v) if float(v).is_integer() else v for v in values]


def rebake(doc: dict, item: str, stage: int) -> dict:
    out = deepcopy(doc)
    rows = out["minecraft:geometry"]
    assert len(rows) == 1
    geo = rows[0]
    old_id = geo["description"]["identifier"]
    assert old_id == f"geometry.kg_a22.{item}.stage{stage}", old_id
    geo["description"]["identifier"] = f"geometry.kg_a2764.{item}.stage{stage}"

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


def source_files(item: str):
    return sorted(SOURCE.glob(f"{item}_stage*.geo.json"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    OUTPUT.mkdir(parents=True, exist_ok=True)
    written = []
    for item in SAMPLES:
        files = source_files(item)
        assert files, item
        for source in files:
            stage = int(source.stem.rsplit("_stage", 1)[1].split(".", 1)[0])
            out = rebake(load(source), item, stage)
            target = OUTPUT / source.name
            text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
            if args.check:
                assert target.is_file(), target
                assert target.read_text(encoding="utf-8") == text, target
            else:
                target.write_text(text, encoding="utf-8")
            written.append(target)

    assert len(written) == 14, len(written)
    print(f"A2.7.64 sample hand-space geometries: {len(written)}")


if __name__ == "__main__":
    main()
