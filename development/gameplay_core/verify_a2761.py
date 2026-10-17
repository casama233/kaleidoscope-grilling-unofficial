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
VERSION = [2, 7, 61]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def function_body(text: str, name: str) -> str:
    marker = f"function {name}"
    start = text.index(marker)
    paren = text.index("(", start)
    depth = 0
    close = None
    for index in range(paren, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                close = index
                break
    assert close is not None, name
    brace = text.index("{", close)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace:index + 1]
    raise AssertionError(name)


def compare_compiled() -> list[dict]:
    result = []
    dist = PROJECT / "builds/dist"
    for name, source in (("behavior_pack", BP), ("resource_pack", RP)):
        manifest = load(source / "manifest.json")
        matches = [
            p.parent
            for p in dist.rglob("manifest.json")
            if load(p).get("header", {}).get("uuid") == manifest["header"]["uuid"]
        ]
        assert len(matches) == 1, (name, matches)
        target = matches[0]
        count = 0
        for path in source.rglob("*"):
            if not path.is_file() or path.name.startswith("."):
                continue
            compiled = target / path.relative_to(source)
            assert compiled.is_file(), compiled
            if path.suffix == ".json":
                assert load(path) == load(compiled), compiled
            else:
                assert path.read_bytes() == compiled.read_bytes(), compiled
            count += 1
        result.append({"pack": name, "compared_files": count, "matches_source": True})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiled", action="store_true")
    args = parser.parse_args()

    for path in PROJECT.rglob("*.json"):
        load(path)

    bp = load(BP / "manifest.json")
    rp = load(RP / "manifest.json")
    assert bp["header"]["version"] == VERSION
    assert rp["header"]["version"] == VERSION
    assert bp["header"]["uuid"] == "c68005c5-23ff-54e8-a3ff-da6349ad43c2"
    assert rp["header"]["uuid"] == "bbbd2d60-52e5-53a6-8b9a-c09b0f516389"
    assert bp["header"]["name"] == "Kaleidoscope Grilling A2.7.61 Interaction Safety BP"
    assert rp["header"]["name"] == "Kaleidoscope Grilling A2.7.61 Interaction Safety RP"

    main_text = (BP / "scripts/main.js").read_text(encoding="utf-8")
    capture = function_body(main_text, "captureInteractionIntent")
    validate = function_body(main_text, "interactionIntentStillCurrent")
    seasoning = function_body(main_text, "handleSeasoningBlock")
    push = function_body(main_text, "pushBottle")
    dispatch = function_body(main_text, "handleCustomBlockInteraction")

    assert "chooseInteractionHand" in capture and "makeIntent" in capture
    assert "intentMatches" in validate
    for token in (
        "heldByHand(player,hand)",
        "pushBottle(block,player,held,hand)",
        "decrementHand(player,hand)",
        "setHand(player,hand,bottleItem(out))",
    ):
        assert token in seasoning, token
    assert "decrementHand(player,hand)" in push
    assert "decrementMain(player)" not in push
    for token in (
        "interactionIntentStillCurrent(player,intent)",
        "handleGrill(block,player,intent.hand)",
        "handleSeasoningBlock(block,player,intent.hand)",
    ):
        assert token in dispatch, token

    block_event = main_text.split("world.beforeEvents.playerInteractWithBlock.subscribe", 1)[1].split(
        "world.afterEvents.playerPlaceBlock.subscribe", 1
    )[0]
    assert "intent=customTarget?captureInteractionIntent(p,e.itemStack):null" in block_event
    assert "handleCustomBlockInteraction(dim.getBlock(loc),p,intent)" in block_event
    assert "grillTarget?capture" not in block_event

    for test in ("test_a275_core.mjs", "test_a276_core.mjs", "test_a277_core.mjs"):
        subprocess.run(["node", str(DEV / test)], check=True)
    subprocess.run([sys.executable, str(DEV / "verify_a2761_java_interaction_contract.py")], check=True)
    for path in (BP / "scripts").glob("*.js"):
        subprocess.run(["node", "--check", str(path)], check=True)

    report = load(PROJECT / "reports/a2761-interaction-safety.json")
    assert report["version"] == "A2.7.61"
    assert report["java_reference"]["commit"] == "9a1acdab27698457bec16c9362678e574895a28c"
    assert report["fixes"]["seasoning_uses_event_hand"] is True
    assert report["fixes"]["custom_block_intent_rechecked_after_defer"] is True
    assert report["fixes"]["single_custom_block_dispatch_function"] is True
    assert report["identifiers_preserved"] is True
    assert report["gameplay_rule_changes"] is False
    assert report["minecraft_tested"] is False and report["bds_tested"] is False

    compiled = compare_compiled() if args.compiled else []
    print(
        json.dumps(
            {
                "version": "A2.7.61",
                "interaction_safety": True,
                "compiled": args.compiled,
                "compiled_packs": compiled,
                "minecraft_tested": False,
                "bds_tested": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
