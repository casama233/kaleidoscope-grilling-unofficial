from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "projects" / "grilling" / "guide" / "content.a2.json"
PROJECT = ROOT / "projects" / "grilling" / "integration" / "cookery106"
BP = PROJECT / "behavior_pack"
RP = PROJECT / "resource_pack"
GAME = ROOT / "projects" / "grilling" / "gameplay_core" / "behavior_pack"
HOST_CONTRACT = ROOT / "projects" / "grilling" / "guide" / "host-contract.verified.json"

BP_UUID = "f8c367c2-84d6-5bf6-b5a8-1bbe6cdb93ab"
RP_UUID = "32baef08-6b04-5115-9d5b-2d4ba2d3a7b4"
LOCALES = ("zh_CN", "zh_TW", "en_US")
VERSION = (0, 2, 0)
EXPECTED_COUNTS = {"start": 4, "equipment": 12, "recipes": 20, "seasonings": 9, "advanced": 7}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message: str):
    raise AssertionError(message)


def payload():
    text = (BP / "scripts" / "payload.js").read_text(encoding="utf-8").strip()
    prefix = "export const GUIDEBOOK_PAYLOAD="
    if not text.startswith(prefix) or not text.endswith(";"):
        fail("payload.js is not the canonical generated export")
    return json.loads(text[len(prefix):-1])


def compare_compiled(source: Path, target: Path) -> int:
    count = 0
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel = path.relative_to(source)
        other = target / rel
        if not other.is_file():
            fail(f"compiled output missing {rel}")
        if path.suffix == ".json":
            if load(path) != load(other):
                fail(f"compiled JSON differs: {rel}")
        elif path.read_bytes() != other.read_bytes():
            fail(f"compiled file differs: {rel}")
        count += 1
    return count


def find_compiled(dist: Path, uid: str) -> Path:
    found = []
    for manifest in dist.rglob("manifest.json"):
        try:
            if load(manifest).get("header", {}).get("uuid") == uid:
                found.append(manifest.parent)
        except Exception:
            pass
    if len(found) != 1:
        fail(f"compiled pack lookup for {uid}: {found}")
    return found[0]


def source_entry(source: dict, entry_id: str) -> dict:
    rows = [x for x in source["entries"] if x["id"] == entry_id]
    if len(rows) != 1:
        fail(f"expected one source entry {entry_id}, got {len(rows)}")
    return rows[0]


def body_text(source: dict, entry_id: str, locale: str) -> str:
    return "\n".join(source_entry(source, entry_id)["body"][locale])


def require_text(source: dict, entry_id: str, locale: str, *tokens: str):
    text = body_text(source, entry_id, locale)
    for token in tokens:
        if token not in text:
            fail(f"guide fact drift: {entry_id} {locale} missing {token!r}")


def int_const(text: str, name: str) -> int:
    m = re.search(rf"export const {re.escape(name)}\s*=\s*(\d+)", text)
    if not m:
        fail(f"missing runtime constant {name}")
    return int(m.group(1))


def check_runtime_facts(source: dict) -> dict:
    core = (GAME / "scripts" / "core_logic.js").read_text(encoding="utf-8")
    press = (GAME / "scripts" / "a26_oil_machine_core.js").read_text(encoding="utf-8")
    oils = (GAME / "scripts" / "oil_types.js").read_text(encoding="utf-8")
    seasoning = (GAME / "scripts" / "a2743_seasoning_contract_core.js").read_text(encoding="utf-8")
    main = (GAME / "scripts" / "main.js").read_text(encoding="utf-8")
    hot_merge = (GAME / "scripts" / "a23_hot_merge.js").read_text(encoding="utf-8")
    skewering = (GAME / "scripts" / "a24_skewering_core.js").read_text(encoding="utf-8")
    rack = (GAME / "scripts" / "a2746_advanced_rack_core.js").read_text(encoding="utf-8")
    data = (GAME / "scripts" / "data.js").read_text(encoding="utf-8")

    finished = int_const(core, "FINISHED_TICKS")
    burnt = int_const(core, "BURNT_TICKS")
    cooldown = int_const(core, "FLIP_COOLDOWN")
    flips = int_const(core, "REQUIRED_FLIPS")
    if (finished, burnt, cooldown, flips) != (800, 400, 20, 4):
        fail("grill timing contract changed; update guide facts")
    require_text(source, "guide_grill_timing", "zh_CN", "40 秒", "20 秒")
    require_text(source, "guide_quick_start", "zh_CN", "1 秒", "4 次")

    press_values = {name: int_const(press, name) for name in (
        "PRESS_MAX_CAKES", "PRESS_REQUIRED_PROGRESS", "PRESS_ANVIL_PROGRESS",
        "PRESS_STONE_PROGRESS", "PRESS_OUTPUT_BUCKETS", "VAT_CAPACITY_BUCKETS",
        "OIL_POT_CAPACITY", "OIL_BUCKET_POINTS"
    )}
    expected_press = {
        "PRESS_MAX_CAKES": 4, "PRESS_REQUIRED_PROGRESS": 16, "PRESS_ANVIL_PROGRESS": 4,
        "PRESS_STONE_PROGRESS": 1, "PRESS_OUTPUT_BUCKETS": 4, "VAT_CAPACITY_BUCKETS": 8,
        "OIL_POT_CAPACITY": 64, "OIL_BUCKET_POINTS": 8,
    }
    if press_values != expected_press:
        fail(f"oil-machine contract changed: {press_values}")
    require_text(source, "guide_oil_press", "zh_CN", "4 个油饼", "16 点", "4 桶菜籽油", "4 个油渣")
    require_text(source, "guide_big_vat", "zh_CN", "8 桶", "8 点油")

    oil_values = {}
    for name in ("canola", "secret_chili", "premium_chili"):
        m = re.search(rf"{name}:\{{heatTicks:(\d+)", oils)
        if not m:
            fail(f"missing oil heatTicks for {name}")
        oil_values[name] = int(m.group(1))
    if oil_values != {"canola": 1200, "secret_chili": 12000, "premium_chili": 24000}:
        fail(f"oil hot-duration contract changed: {oil_values}")
    require_text(source, "guide_hot_food", "zh_CN", "60 秒", "10 分钟", "20 分钟", "25%")

    season_values = {name: int_const(seasoning, name) for name in (
        "SEASONING_CAPACITY", "SEASONING_MAX_BOTTLES", "SEASONING_MAX_USES"
    )}
    if season_values != {"SEASONING_CAPACITY": 8, "SEASONING_MAX_BOTTLES": 4, "SEASONING_MAX_USES": 16}:
        fail(f"seasoning capacity contract changed: {season_values}")
    for token in (
        "'kaleidoscope_grilling:green_chili_powder'",
        "'kaleidoscope_grilling:sichuan_pepper'",
        "'kaleidoscope_grilling:onion_powder'",
    ):
        if token not in seasoning:
            fail(f"seasoning base ingredient contract changed: {token}")
    if "let duration=3600" not in main or "fxSet(player,'numb',900*" not in main or "fxSet(target,'heavy_metal_poisoning',12000)" not in main:
        fail("seasoning runtime duration contract changed")
    require_text(source, "guide_seasoning_base", "zh_CN", "8 份", "4 瓶", "16 次")
    require_text(source, "guide_seasoning_houttuynia", "zh_CN", "3 分钟", "×2", "×4")
    require_text(source, "guide_seasoning_pepper", "zh_CN", "45 秒")
    require_text(source, "guide_seasoning_totem", "zh_CN", "10 分钟")

    if "export const NORMAL_HEAT_WINDOW=5*60*20;" not in hot_merge:
        fail("normal hot-stack merge window changed")
    require_text(source, "guide_storage_heat", "zh_CN", "5 分钟")

    recipe_segment = skewering.split("const RECIPES=Object.freeze([", 1)[1].split("]);", 1)[0]
    recipe_ids = re.findall(r"\{id:'([^']+)'", recipe_segment)
    if len(recipe_ids) != 20 or len(set(recipe_ids)) != 20:
        fail(f"fixed-skewer recipe table changed: {len(recipe_ids)} entries")
    guide_recipe_ids = [x["id"] for x in source["entries"] if x["category"] == "recipes"]
    if len(guide_recipe_ids) != 20:
        fail("guide must expose exactly 20 fixed/special recipe pages")

    if "export const RACK_COMPARTMENTS=9;" not in rack or "export const RACK_RANGE=8;" not in rack:
        fail("Advanced Rack compartment/range contract changed")
    require_text(source, "guide_advanced_rack", "zh_CN", "9 个槽位", "8 格")

    marker = "export const COOKED_EFFECTS=Object.freeze("
    effects_json = data.split(marker, 1)[1].split(");", 1)[0]
    effects = json.loads(effects_json)
    effect_pages = {
        "guide_recipe_beef": "kaleidoscope_grilling:grilled_beef_skewer",
        "guide_recipe_pork_belly": "kaleidoscope_grilling:grilled_pork_belly_skewer",
        "guide_recipe_chicken_skin": "kaleidoscope_grilling:grilled_chicken_skin_skewer",
        "guide_recipe_mid_wing": "kaleidoscope_grilling:grilled_mid_wing_skewer",
        "guide_recipe_squid_tentacle": "kaleidoscope_grilling:grilled_squid_tentacle_skewer",
        "guide_recipe_fish": "kaleidoscope_grilling:grilled_fish_skewer",
        "guide_recipe_sweet_potato_sheet": "kaleidoscope_grilling:grilled_sweet_potato_sheet_skewer",
        "guide_recipe_potato_slice": "kaleidoscope_grilling:grilled_potato_slice_skewer",
        "guide_recipe_caterpillar": "kaleidoscope_grilling:grilled_caterpillar_skewer",
        "guide_recipe_mushroom": "kaleidoscope_grilling:grilled_mushroom_skewer",
        "guide_recipe_bun_slice": "kaleidoscope_grilling:grilled_bun_slice_skewer",
        "guide_recipe_ender_pearl": "kaleidoscope_grilling:grilled_ender_pearl_skewer",
        "guide_recipe_meatball": "kaleidoscope_grilling:grilled_meatball_skewer",
        "guide_recipe_slime": "kaleidoscope_grilling:grilled_slime_skewer",
        "guide_recipe_meat_and_bone": "kaleidoscope_grilling:grilled_meat_and_bone_skewer",
        "guide_recipe_fried_egg": "kaleidoscope_grilling:grilled_fried_egg_skewer",
        "guide_recipe_gluten": "kaleidoscope_grilling:grilled_gluten_skewer",
        "guide_recipe_lamb": "kaleidoscope_grilling:grilled_lamb_skewer",
        "guide_recipe_golden": "kaleidoscope_grilling:grilled_golden_skewer",
    }
    for guide_id, item_id in effect_pages.items():
        seconds = int(effects[item_id]["seconds"])
        if seconds > 0:
            require_text(source, guide_id, "zh_CN", f"{seconds} 秒")
            require_text(source, guide_id, "en_US", f"{seconds} seconds")
    if effects["kaleidoscope_grilling:grilled_bun_slice_skewer"]["effect"] != "":
        fail("bun-slice no-fixed-effect guide claim drifted")

    return {
        "grill_constants": {"finished": finished, "burnt": burnt, "flip_cooldown": cooldown, "required_flips": flips},
        "oil_machine_constants": press_values,
        "oil_heat_ticks": oil_values,
        "seasoning_constants": season_values,
        "fixed_recipe_count": len(recipe_ids),
        "cooked_effect_pages_checked": len(effect_pages),
    }


def check_structure(source: dict, p: dict) -> dict:
    if source.get("schema_version") != 2 or source.get("version") != "0.2.0" or source.get("revision") != "a2_0_0":
        fail("Guide A2 source version/revision drift")
    if source.get("locales") != list(LOCALES) or source.get("fallback_locale") != "zh_TW":
        fail("guide locale contract drift")
    if len(source.get("categories", [])) != 5 or len(source.get("entries", [])) != 52:
        fail("Guide A2 must remain 5 sections / 52 topics")
    ids = [x["id"] for x in source["entries"]]
    if len(ids) != len(set(ids)):
        fail("duplicate guide entry ids")
    counts = Counter(x["category"] for x in source["entries"])
    if dict(counts) != EXPECTED_COUNTS:
        fail(f"guide category counts drift: {dict(counts)}")
    if p.get("api") != 1 or p.get("id") != "kg_a1:grilling" or p.get("version") != "0.2.0":
        fail("published payload identity/version drift")
    if p.get("showAll") is not False:
        fail("52-topic guide must not restore the giant flat All Entries view")
    if len(p.get("categories", [])) != 5:
        fail("published category count drift")
    if set(p.get("mechanicsByLocale", {})) != set(LOCALES):
        fail("published mechanics locales drift")
    for loc in LOCALES:
        if len(p["mechanicsByLocale"][loc]) != 52:
            fail(f"{loc}: expected 52 localized mechanics")
        if p["mechanics"] != p["mechanicsByLocale"]["zh_TW"]:
            fail("zh_TW fallback mechanics drift")
    legacy_phrase = "穿好后放上烧烤架，依刷油、翻面与调味流程烤熟"
    if legacy_phrase in json.dumps(p, ensure_ascii=False):
        fail("legacy duplicated recipe filler text returned")

    raw = json.dumps(p, ensure_ascii=True, separators=(",", ":"))
    chunks = [raw[i:i+1600] for i in range(0, len(raw), 1600)]
    if not chunks or len(chunks) > 512:
        fail(f"guide exceeds API v1 transfer capacity: {len(chunks)} chunks")
    if any(len(chunk) + 160 > 2048 for chunk in chunks):
        fail("guide chunk would exceed safe Script Event envelope")

    host = load(HOST_CONTRACT)
    if host["guidebook_extension_api"]["api"] != 1:
        fail("host Guide API version changed")
    if host["guidebook_extension_api"]["custom_callbacks_supported"] is not False:
        fail("host contract unexpectedly gained callbacks; review guide architecture")
    if host["guidebook_item"] != "kaleidoscope_cookery:guidebook":
        fail("guide host item drift")
    if host["language"]["property"] != "kc:guidebook_language":
        fail("per-player guide language property drift")

    return {
        "category_counts": dict(counts),
        "transfer_chunks": len(chunks),
        "host_api": 1,
        "host_callbacks": False,
    }


def check_project() -> dict:
    bm, rm = load(BP / "manifest.json"), load(RP / "manifest.json")
    if bm["header"]["uuid"] != BP_UUID or rm["header"]["uuid"] != RP_UUID:
        fail("guide BP/RP UUID changed")
    if tuple(bm["header"]["version"]) != VERSION or tuple(rm["header"]["version"]) != VERSION:
        fail("guide BP/RP manifest version mismatch")
    deps = [d for d in bm.get("dependencies", []) if d.get("uuid") == RP_UUID]
    if len(deps) != 1 or tuple(deps[0]["version"]) != VERSION:
        fail("guide BP dependency on RP changed")
    scripts = [m for m in bm.get("modules", []) if m.get("type") == "script"]
    if len(scripts) != 1 or scripts[0].get("entry") != "scripts/main.js":
        fail("guide must have one script entry: scripts/main.js")
    for forbidden in ("items", "blocks", "recipes", "entities"):
        if (BP / forbidden).exists():
            fail(f"guide integration must not create gameplay content: behavior_pack/{forbidden}")
    publisher = (BP / "scripts" / "publisher.js").read_text(encoding="utf-8")
    if "export const REVISION = 'a2_0_0';" not in publisher:
        fail("guide publisher revision is not A2.0")
    main = (BP / "scripts" / "main.js").read_text(encoding="utf-8")
    if "GUIDEBOOK_PAYLOAD" not in main or "installPublisher" not in main:
        fail("guide main entry no longer publishes the generated payload")
    return {"bp_uuid": BP_UUID, "rp_uuid": RP_UUID, "script_entry": "scripts/main.js"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiled", action="store_true")
    args = parser.parse_args()

    subprocess.run([sys.executable, str(ROOT / "tools" / "build_grilling_guide.py"), "--check"], check=True)
    source = load(SOURCE)
    p = payload()
    structure = check_structure(source, p)
    project = check_project()
    runtime = check_runtime_facts(source)

    compiled = []
    if args.compiled:
        dist = PROJECT / "builds" / "dist"
        if not dist.is_dir():
            fail("compiled verification requested but guide builds/dist is missing")
        for label, src, uid in (("behavior_pack", BP, BP_UUID), ("resource_pack", RP, RP_UUID)):
            dst = find_compiled(dist, uid)
            compiled.append({"pack": label, "files": compare_compiled(src, dst)})

    result = {
        "guide_version": "0.2.0",
        "canonical_source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "categories": 5,
        "entries": 52,
        "locales": list(LOCALES),
        "structure": structure,
        "project": project,
        "runtime_facts": runtime,
        "compiled_checked": args.compiled,
        "compiled_packs": compiled,
        "minecraft_tested": False,
        "bds_tested": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"canonical guide check FAILED: {exc}", file=sys.stderr)
        raise
