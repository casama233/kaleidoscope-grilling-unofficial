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
VERSION = [2, 7, 64]

SAMPLES = {
    "raw_beef_skewer": 5,
    "grilled_beef_skewer": 5,
    "ordinary_skewer": 4,
}
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
    assert bp["header"]["name"] == "Kaleidoscope Grilling A2.7.64 Skewer Held Geometry Corrective BP"
    assert rp["header"]["name"] == "Kaleidoscope Grilling A2.7.64 Skewer Held Geometry Corrective RP"

    # Generated sample geometry must be exactly reproducible from A22 + [0,+7,+2].
    subprocess.run(
        [sys.executable, str(DEV / "a2764_rebake_skewer_hand_geometry.py"), "--check"],
        check=True,
    )
    generated = sorted((RP / "models/entity/a2764_skewer_hand").glob("*.geo.json"))
    assert len(generated) == 14, len(generated)

    all_skewers = sorted((RP / "attachables").glob("*_skewer.attachable.json"))
    assert len(all_skewers) == 39, len(all_skewers)

    sample_count = 0
    legacy_count = 0
    for path in all_skewers:
        item = path.name.removesuffix(".attachable.json")
        desc = load(path)["minecraft:attachable"]["description"]
        pre = desc.get("scripts", {}).get("pre_animation", [])
        assert pre and any("item_in_use_duration" in x for x in pre), path.name
        assert desc.get("render_controllers") == ["controller.render.kg_a22.bite"], path.name

        if item in SAMPLES:
            sample_count += 1
            assert "animations" not in desc, path.name
            assert "animate" not in desc.get("scripts", {}), path.name
            expected_stages = SAMPLES[item]
            unique_geometry = set(desc["geometry"].values())
            assert all(x.startswith(f"geometry.kg_a2764.{item}.stage") for x in unique_geometry), path.name
            assert len(unique_geometry) == expected_stages, (path.name, unique_geometry)
            for stage in range(expected_stages):
                target = RP / "models/entity/a2764_skewer_hand" / f"{item}_stage{stage}.geo.json"
                assert target.is_file(), target
                geo = load(target)["minecraft:geometry"][0]
                assert geo["description"]["identifier"] == f"geometry.kg_a2764.{item}.stage{stage}"
                root = geo["bones"][0]
                assert root["name"] == "root"
                assert root.get("pivot") == [0, 0, 0]
                assert root.get("binding") == "q.item_slot_to_bone_name(context.item_slot)"
        else:
            legacy_count += 1
            anim = desc.get("animations", {})
            assert anim.get("hold_first_person") == A2725_FIRST, path.name
            assert anim.get("hold_third_person") == A2725_THIRD, path.name
            animate = desc.get("scripts", {}).get("animate", [])
            assert animate == [
                {"hold_first_person": "context.is_first_person == 1.0"},
                {"hold_third_person": "context.is_first_person == 0.0"},
            ], path.name
            assert all(x.startswith("geometry.kg_a22.") for x in desc["geometry"].values()), path.name

    assert sample_count == 3
    assert legacy_count == 36

    report = load(PROJECT / "reports/a2764-skewer-held-geometry-corrective.json")
    assert report["version"] == "A2.7.64"
    assert report["phase"] == "sample_validation"
    assert report["sample_attachables"] == list(SAMPLES)
    assert report["sample_geometry_count"] == 14
    assert report["hand_space_translation"] == [0, 7, 2]
    assert report["root_animation_removed_for_samples"] is True
    assert report["remaining_legacy_attachables"] == 36
    assert report["bite_stage_logic_changed"] is False
    assert report["textures_changed"] is False
    assert report["gameplay_logic_changed"] is False
    assert report["minecraft_tested"] is False
    assert report["client_visuals_tested"] is False

    print(json.dumps({
        "version": "A2.7.64",
        "phase": "sample_validation",
        "sample_attachables": sample_count,
        "sample_geometry_files": len(generated),
        "remaining_a2725_attachables": legacy_count,
        "compiled_requested": args.compiled,
        "minecraft_tested": False,
        "client_visuals_tested": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
