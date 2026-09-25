from __future__ import annotations

from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "projects/grilling/gameplay_core"
BP = PROJECT / "behavior_pack"
RP = PROJECT / "resource_pack"
DEV = Path(__file__).resolve().parent
VERSION = [2, 7, 65]
A2725_FIRST = "animation.kaleidoscope_grilling.a2725.skewer_hold_first_person"
A2725_THIRD = "animation.kaleidoscope_grilling.a2725.skewer_hold_third_person"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiled", action="store_true")
    args = parser.parse_args()

    bp = load(BP / "manifest.json")
    rp = load(RP / "manifest.json")
    assert bp["header"]["version"] == VERSION
    assert rp["header"]["version"] == VERSION
    assert bp["header"]["name"] == "Kaleidoscope Grilling A2.7.65 Full Skewer Hand Geometry BP"
    assert rp["header"]["name"] == "Kaleidoscope Grilling A2.7.65 Full Skewer Hand Geometry RP"

    subprocess.run(
        [sys.executable, str(DEV / "a2764_rebake_skewer_hand_geometry.py"), "--check"],
        check=True,
    )

    source_geometry = sorted((RP / "models/entity/a22_bites").glob("*.geo.json"))
    baked_geometry = sorted((RP / "models/entity/a2764_skewer_hand").glob("*.geo.json"))
    assert len(source_geometry) == 150
    assert len(baked_geometry) == 150
    assert {p.name for p in source_geometry} == {p.name for p in baked_geometry}

    attachables = sorted((RP / "attachables").glob("*_skewer.attachable.json"))
    assert len(attachables) == 39

    geometry_refs = set()
    a2725_refs = 0
    for path in attachables:
        desc = load(path)["minecraft:attachable"]["description"]
        pre = desc.get("scripts", {}).get("pre_animation", [])
        assert pre and any("item_in_use_duration" in x for x in pre), path.name
        assert "animate" not in desc.get("scripts", {}), path.name
        assert "animations" not in desc, path.name
        assert desc.get("render_controllers") == ["controller.render.kg_a22.bite"], path.name

        refs = list(desc.get("geometry", {}).values())
        assert refs, path.name
        assert all(str(x).startswith("geometry.kg_a2764.") for x in refs), path.name
        geometry_refs.update(refs)

        raw = path.read_text(encoding="utf-8")
        a2725_refs += raw.count(A2725_FIRST) + raw.count(A2725_THIRD)

    assert a2725_refs == 0
    assert (RP / "animations/a2725_skewer_hold.animation.json").is_file()

    baked_ids = {
        load(path)["minecraft:geometry"][0]["description"]["identifier"]
        for path in baked_geometry
    }
    assert geometry_refs <= baked_ids
    assert len(geometry_refs) == 150, (len(geometry_refs), len(baked_ids))

    report = load(PROJECT / "reports/a2765-full-skewer-hand-geometry.json")
    assert report["version"] == "A2.7.65"
    assert report["attachable_count"] == 39
    assert report["source_geometry_count"] == 150
    assert report["baked_geometry_count"] == 150
    assert report["a2725_runtime_reference_count"] == 0
    assert report["hand_space_translation"] == [0, 7, 2]
    assert report["bite_stage_logic_changed"] is False
    assert report["textures_changed"] is False
    assert report["gameplay_logic_changed"] is False
    assert report["minecraft_tested"] is False
    assert report["client_visuals_tested"] is False

    print(json.dumps({
        "version": "A2.7.65",
        "attachables": len(attachables),
        "source_geometry": len(source_geometry),
        "baked_geometry": len(baked_geometry),
        "geometry_refs": len(geometry_refs),
        "a2725_runtime_reference_count": a2725_refs,
        "compiled_requested": args.compiled,
        "minecraft_tested": False,
        "client_visuals_tested": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
