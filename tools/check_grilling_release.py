from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects" / "grilling" / "gameplay_core"
BP = PROJECT / "behavior_pack"
RP = PROJECT / "resource_pack"
SCRIPTS = BP / "scripts"

EXPECTED_BP_UUID = "c68005c5-23ff-54e8-a3ff-da6349ad43c2"
EXPECTED_RP_UUID = "bbbd2d60-52e5-53a6-8b9a-c09b0f516389"
EXPECTED_COOKERY_BP_UUID = "10f37ae2-9ccf-435f-b34b-0eec8191cd94"
IMPORT_RE = re.compile(r"""(?:from\s+)?["'](\./[^"']+)["']""")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message: str):
    raise AssertionError(message)


def version_tuple(value):
    if not isinstance(value, list) or len(value) != 3:
        fail(f"invalid manifest version: {value!r}")
    return tuple(int(x) for x in value)


def find_compiled_pack(dist: Path, expected_uuid: str) -> Path:
    matches = []
    for manifest in dist.rglob("manifest.json"):
        try:
            if load_json(manifest).get("header", {}).get("uuid") == expected_uuid:
                matches.append(manifest.parent)
        except Exception:
            continue
    if len(matches) != 1:
        fail(f"compiled pack lookup for {expected_uuid}: expected 1, got {matches}")
    return matches[0]


def compare_compiled(source: Path, target: Path) -> int:
    compared = 0
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel = path.relative_to(source)
        other = target / rel
        if not other.is_file():
            fail(f"compiled output missing {rel}")
        if path.suffix == ".json":
            if load_json(path) != load_json(other):
                fail(f"compiled JSON differs: {rel}")
        elif path.read_bytes() != other.read_bytes():
            fail(f"compiled file differs: {rel}")
        compared += 1
    return compared


def check_identifiers():
    seen = {}
    for folder, key in ((BP / "blocks", "minecraft:block"), (BP / "items", "minecraft:item")):
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*.json")):
            doc = load_json(path)
            body = doc.get(key)
            if not isinstance(body, dict):
                continue
            identifier = body.get("description", {}).get("identifier")
            if not identifier:
                continue
            if identifier in seen:
                fail(f"duplicate identifier {identifier}: {seen[identifier]} and {path}")
            seen[identifier] = path
    return len(seen)


def check_interaction_contracts():
    main = (SCRIPTS / "main.js").read_text(encoding="utf-8")
    plate = (SCRIPTS / "a25_plate_recipe_runtime.js").read_text(encoding="utf-8")
    knead = (SCRIPTS / "a271_sweet_potato_runtime.js").read_text(encoding="utf-8")
    oil = (SCRIPTS / "a26_oil_machine_runtime.js").read_text(encoding="utf-8")
    oil_world = (SCRIPTS / "a23_oil_world.js").read_text(encoding="utf-8")
    offhand_oil = (SCRIPTS / "a2737_offhand_oil_fill_runtime.js").read_text(encoding="utf-8")
    cold_houttuynia = (SCRIPTS / "a2722_cold_houttuynia_runtime.js").read_text(encoding="utf-8")
    rack = (SCRIPTS / "a2746_advanced_rack_runtime.js").read_text(encoding="utf-8")
    typed_oil = (SCRIPTS / "a2736_typed_oil_pot_block_runtime.js").read_text(encoding="utf-8")
    cuisine = (SCRIPTS / "a2750_cookery_cuisine_runtime.js").read_text(encoding="utf-8")
    intent = (SCRIPTS / "interaction_intent.js").read_text(encoding="utf-8")

    required = {
        "main respects earlier interaction ownership": (main, "playerInteractWithBlock.subscribe(e=>{\n if(e.cancel)return;"),
        "plate uses one-shot block input": (plate, "isInitialBlockPress(e.isFirstEvent)"),
        "plate captures interaction hand intent": (plate, "captureInteractionIntent(p,e.itemStack)"),
        "plate revalidates deferred intent": (plate, "interactionIntentStillCurrent(p,intent)"),
        "air-use recipe path is main-hand owned": (plate, "const intent=captureInteractionIntent(p,e.itemStack);if(intent.hand!=='main')return;"),
        "air-use recipe path revalidates offhand": (plate, "interactionStackSignature(heldOff(p))!==offSignature"),
        "powder kneading uses event-hand intent": (knead, "captureInteractionIntent(player,eventStack)"),
        "oil machine uses one-shot block input": (oil, "isInitialBlockPress(e.isFirstEvent)"),
        "oil machine captures interaction hand intent": (oil, "captureInteractionIntent(p,e.itemStack)"),
        "oil machine revalidates deferred intent": (oil, "interactionIntentStillCurrent(p,intent)"),
        "world oil respects earlier ownership": (oil_world, "if(e.cancel)return;"),
        "world oil excludes Cookery oil-pot ownership": (oil_world, "kaleidoscope_cookery:oil_pot"),
        "world oil uses one-shot block input": (oil_world, "isInitialBlockPress(e.isFirstEvent)"),
        "world oil revalidates interaction intent": (oil_world, "interactionIntentStillCurrent(p,intent)"),
        "world oil north face is negative Z": (oil_world, "North:[0,0,-1],South:[0,0,1]"),
        "world oil registry uses pre-mutation dirty snapshot": (oil_world, "const rows=readReg(),before=JSON.stringify(rows),keep=[];"),
        "offhand oil fill requires main-hand event ownership": (offhand_oil, "if(intent.hand!=='main')return;"),
        "offhand oil fill revalidates both hands": (offhand_oil, "interactionStackSignature(getOffHand(player))!==offSignature"),
        "cold houttuynia requires main-hand event ownership": (cold_houttuynia, "if(intent.hand!=='main')return;"),
        "cold houttuynia revalidates offhand oil": (cold_houttuynia, "interactionStackSignature(off(player))!==offSignature"),
        "rack rejects stale remote form actions": (rack, "rackInUseRange(player,live)"),
        "typed oil pot captures interaction intent": (typed_oil, "captureInteractionIntent(p,e.itemStack)"),
        "typed oil pot keeps Java main-hand bucket rule": (typed_oil, "if(intent.hand!=='main')return;"),
        "Cookery cuisine captures interaction intent": (cuisine, "captureInteractionIntent(player,event.itemStack)"),
        "Cookery seasoning remains Java main-hand only": (cuisine, "if(hand==='main'&&used?.typeId===SEASONING_ID)"),
        "Cookery oil metadata uses the actual event hand": (cuisine, "typedHeldOil(used)"),
        "shared intent tracks main and offhand": (intent, "chooseInteractionHand(eventDesc,main,off)"),
    }
    for label, (text, token) in required.items():
        if token not in text.replace("\r\n", "\n"):
            fail(f"interaction ownership contract missing: {label}")

    if "handlePlateBlock(block,player,hand='main')" not in plate:
        fail("plate block handler lost explicit hand ownership")
    if "interactPress(block,p,item,hand=null)" not in oil or "interactVat(block,p,item,hand=null)" not in oil:
        fail("oil-machine handlers lost explicit hand ownership")
    return len(required) + 2


def check_big_vat_render_contract():
    block = load_json(BP / "blocks" / "big_vat.json")["minecraft:block"]
    materials = [block.get("components", {}).get("minecraft:material_instances", {})]
    for permutation in block.get("permutations", []):
        value = permutation.get("components", {}).get("minecraft:material_instances")
        if isinstance(value, dict):
            materials.append(value)
    for value in materials:
        shell = value.get("*", {})
        if shell.get("render_method") != "opaque":
            fail("Big Vat shell must stay opaque after solid-rim corrective")

    expected_strips = {
        "a2762_rim_top_north": ([-8, 16, -8], [16, 0, 2], [0, 0], [16, 2]),
        "a2762_rim_top_south": ([-8, 16, 6], [16, 0, 2], [0, 14], [16, 2]),
        "a2762_rim_top_west": ([-8, 16, -6], [2, 0, 12], [0, 2], [2, 12]),
        "a2762_rim_top_east": ([6, 16, -6], [2, 0, 12], [14, 2], [2, 12]),
    }
    for level in range(5):
        geo = load_json(RP / "models" / "blocks" / f"big_vat_{level}.geo.json")["minecraft:geometry"][0]
        bones = {b.get("name"): b for b in geo.get("bones", [])}
        top = bones.get("instance_0_element_0_0", {}).get("cubes", [{}])[0]
        if "up" in top.get("uv", {}):
            fail(f"Big Vat level {level} restored the alpha-cutout top face")
        for name, (origin, size, uv, uv_size) in expected_strips.items():
            bone = bones.get(name)
            if not bone or len(bone.get("cubes", [])) != 1:
                fail(f"Big Vat level {level} missing solid rim strip {name}")
            cube = bone["cubes"][0]
            face = cube.get("uv", {}).get("up", {})
            if cube.get("origin") != origin or cube.get("size") != size or face.get("uv") != uv or face.get("uv_size") != uv_size:
                fail(f"Big Vat level {level} solid rim strip drift: {name}")
        if any("binding" in b for b in geo.get("bones", [])):
            fail(f"placed Big Vat geometry {level} must not contain attachable bindings")

    hand = load_json(RP / "models" / "entity" / "a2762_big_vat_hand.geo.json")["minecraft:geometry"][0]
    if hand.get("description", {}).get("identifier") != "geometry.kg_a2762.big_vat_hand":
        fail("Big Vat hand geometry identifier drift")
    hb = {b.get("name"): b for b in hand.get("bones", [])}
    if hb.get("root", {}).get("binding") != "q.item_slot_to_bone_name(context.item_slot)":
        fail("Big Vat hand geometry lost item-slot binding")
    if hb.get("display", {}).get("parent") != "root":
        fail("Big Vat hand display bone must remain below the bound root")
    if "up" in hb.get("instance_0_element_0_0", {}).get("cubes", [{}])[0].get("uv", {}):
        fail("Big Vat hand geometry restored the alpha-cutout top face")
    for name in expected_strips:
        if hb.get(name, {}).get("parent") != "display":
            fail(f"Big Vat hand rim strip lost display parent: {name}")

    attachable = load_json(RP / "attachables" / "big_vat.attachable.json")["minecraft:attachable"]["description"]
    if attachable.get("identifier") != "kaleidoscope_grilling:big_vat":
        fail("Big Vat attachable identifier drift")
    if attachable.get("materials", {}).get("default") != "entity":
        fail("Big Vat held material must remain opaque")
    if attachable.get("geometry", {}).get("default") != "geometry.kg_a2762.big_vat_hand":
        fail("Big Vat attachable geometry drift")

    animation = load_json(RP / "animations" / "a2762_big_vat_hand.animation.json")["animations"]
    java = load_json(ROOT / "projects" / "grilling" / "reports" / "java_display_transforms" / "big_vat.json")["java_display"]
    mapping = {
        "firstperson_righthand": "animation.kaleidoscope_grilling.a2762.big_vat_fp_right",
        "firstperson_lefthand": "animation.kaleidoscope_grilling.a2762.big_vat_fp_left",
        "thirdperson_righthand": "animation.kaleidoscope_grilling.a2762.big_vat_tp_right",
        "thirdperson_lefthand": "animation.kaleidoscope_grilling.a2762.big_vat_tp_left",
    }
    for java_key, animation_id in mapping.items():
        expected = java[java_key]
        actual = animation[animation_id]["bones"]["display"]
        for key in ("rotation", "scale"):
            if actual.get(key) != expected.get(key):
                fail(f"Big Vat held {java_key} {key} no longer matches Java")
        if actual.get("position", [0, 0, 0]) != expected.get("translation", [0, 0, 0]):
            fail(f"Big Vat held {java_key} translation no longer matches Java")
    return 5 + len(expected_strips) + len(mapping)


def check_script_graph():
    node = shutil.which("node")
    if not node:
        fail("node is required for canonical JavaScript syntax validation")
    files = sorted(SCRIPTS.rglob("*.js"))
    script_root = SCRIPTS.resolve()
    imports = 0
    for path in files:
        subprocess.run([node, "--check", str(path)], check=True)
        text = path.read_text(encoding="utf-8")
        for rel in IMPORT_RE.findall(text):
            target = (path.parent / rel).resolve()
            try:
                target.relative_to(script_root)
            except ValueError:
                fail(f"script import escapes canonical script tree: {path} -> {rel}")
            if not target.is_file():
                fail(f"missing script import: {path} -> {rel}")
            imports += 1
    return len(files), imports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiled", action="store_true")
    args = parser.parse_args()

    if not BP.is_dir() or not RP.is_dir():
        fail("canonical behavior_pack/resource_pack directories are missing")

    json_count = 0
    for root in (BP, RP):
        for path in root.rglob("*.json"):
            load_json(path)
            json_count += 1

    bm = load_json(BP / "manifest.json")
    rm = load_json(RP / "manifest.json")
    if bm["header"]["uuid"] != EXPECTED_BP_UUID:
        fail("behavior-pack UUID changed")
    if rm["header"]["uuid"] != EXPECTED_RP_UUID:
        fail("resource-pack UUID changed")
    version = version_tuple(bm["header"]["version"])
    if version_tuple(rm["header"]["version"]) != version:
        fail("BP/RP versions do not match")

    resource_deps = [d for d in bm.get("dependencies", []) if d.get("uuid") == EXPECTED_RP_UUID]
    if len(resource_deps) != 1 or version_tuple(resource_deps[0].get("version")) != version:
        fail("BP dependency on RP is missing or version-mismatched")
    cookery = [d for d in bm.get("dependencies", []) if d.get("uuid") == EXPECTED_COOKERY_BP_UUID]
    if len(cookery) != 1 or version_tuple(cookery[0].get("version")) != (1, 0, 6):
        fail("Cookery 1.0.6 dependency contract changed")

    script_modules = [m for m in bm.get("modules", []) if m.get("type") == "script"]
    if len(script_modules) != 1 or script_modules[0].get("entry") != "scripts/main.js":
        fail("Gameplay Core must have exactly one Script API entry: scripts/main.js")
    if not (BP / "scripts" / "main.js").is_file():
        fail("canonical scripts/main.js is missing")

    forbidden_player_overrides = (
        RP / "entity" / "player.entity.json",
        RP / "entity" / "player.json",
        BP / "entities" / "player.json",
    )
    for path in forbidden_player_overrides:
        if path.exists():
            fail(f"unexpected whole-player override in public Gameplay Core: {path.relative_to(ROOT)}")

    identifiers = check_identifiers()
    interaction_contracts = check_interaction_contracts()
    big_vat_render_contracts = check_big_vat_render_contract()
    js_files, imports = check_script_graph()

    compiled = []
    if args.compiled:
        dist = PROJECT / "builds" / "dist"
        if not dist.is_dir():
            fail("compiled verification requested but builds/dist is missing")
        for label, source, uid in (("behavior_pack", BP, EXPECTED_BP_UUID), ("resource_pack", RP, EXPECTED_RP_UUID)):
            target = find_compiled_pack(dist, uid)
            compiled.append({"pack": label, "files": compare_compiled(source, target)})

    result = {
        "version": ".".join(map(str, version)),
        "canonical_project": str(PROJECT.relative_to(ROOT)).replace("\\", "/"),
        "json_files": json_count,
        "registered_block_item_identifiers": identifiers,
        "javascript_files": js_files,
        "local_script_imports": imports,
        "interaction_contracts": interaction_contracts,
        "big_vat_render_contracts": big_vat_render_contracts,
        "script_entry": "scripts/main.js",
        "bp_uuid_preserved": True,
        "rp_uuid_preserved": True,
        "cookery_1_0_6_dependency_preserved": True,
        "compiled_checked": args.compiled,
        "compiled_packs": compiled,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"canonical release check FAILED: {exc}", file=sys.stderr)
        raise
