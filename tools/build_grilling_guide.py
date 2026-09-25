from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "projects" / "grilling" / "guide" / "content.a2.json"
PROJECT = ROOT / "projects" / "grilling" / "integration" / "cookery106"
PAYLOAD = PROJECT / "behavior_pack" / "scripts" / "payload.js"
TEXTS = PROJECT / "resource_pack" / "texts"
ICON_ROOT = PROJECT / "resource_pack" / "textures" / "ui" / "kg_grilling"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def icon_path(value: str) -> str:
    value = str(value)
    return value if value.startswith("textures/") else f"textures/ui/kg_grilling/{value}"


def full_id(value: str) -> str:
    value = str(value)
    return value if ":" in value else "kg_a1:" + value


def mechanics_for(source: dict, locale: str) -> list[dict]:
    out = []
    for row in source["entries"]:
        out.append({
            "id": full_id(row["id"]),
            "kind": "mechanic",
            "category": row["category"],
            "icon": icon_path(row["icon"]),
            "lines": list(row["body"][locale]),
        })
    return out


def build_payload(source: dict) -> dict:
    locales = source["locales"]
    fallback = source["fallback_locale"]
    names = {
        loc: {full_id(row["id"]): row["title"][loc] for row in source["entries"]}
        for loc in locales
    }
    text = {}
    for loc in locales:
        ui = dict(source["ui"][loc])
        for category in source["categories"]:
            ui[category["id"]] = category["title"][loc]
        text[loc] = ui
    categories = [{
        "id": row["id"],
        "labelKey": row["id"],
        "icon": icon_path(row["icon"]),
    } for row in source["categories"]]
    localized = {loc: mechanics_for(source, loc) for loc in locales}
    return {
        "api": 1,
        "id": source["module_id"],
        "version": source["version"],
        "order": source["order"],
        "icon": icon_path(source["icon"]),
        "showAll": bool(source.get("showAll", False)),
        "showIds": bool(source.get("showIds", False)),
        "showKinds": bool(source.get("showKinds", False)),
        "showCategoryOnEntry": bool(source.get("showCategoryOnEntry", False)),
        "text": text,
        "categories": categories,
        "kinds": [],
        "names": names,
        "mechanics": localized[fallback],
        "mechanicsByLocale": localized,
    }


def payload_js(payload: dict) -> str:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return "export const GUIDEBOOK_PAYLOAD=" + body + ";\n"


def lang_text(source: dict, locale: str) -> str:
    ui = source["ui"][locale]
    rows = [
        "guide.kg.title=" + ui["title"],
        "guide.kg.intro=" + ui["intro"],
        "guide.kg.all=" + ui["all"],
        "guide.kg.select=" + ui["select"],
        "guide.kg.back=" + ui["back"],
        "guide.kg.language_note=" + ui["language_note"],
    ]
    for category in source["categories"]:
        rows.append(f"guide.kg.category.{category['id']}={category['title'][locale]}")
    for entry in source["entries"]:
        rows.append(f"guide.kg.name.{entry['id']}={entry['title'][locale]}")
        for i, line in enumerate(entry["body"][locale], 1):
            rows.append(f"guide.kg.body.{entry['id']}.{i}={line}")
    return "\n".join(rows) + "\n"


def validate_source(source: dict):
    if source.get("schema_version") != 2:
        raise RuntimeError("Guide A2 source schema must be 2")
    locales = source.get("locales")
    if locales != ["zh_CN", "zh_TW", "en_US"]:
        raise RuntimeError(f"unexpected locales: {locales}")
    if source.get("fallback_locale") not in locales:
        raise RuntimeError("fallback locale is not published")
    categories = source.get("categories", [])
    entries = source.get("entries", [])
    if len(categories) != 5 or len(entries) != 52:
        raise RuntimeError(f"expected 5 categories / 52 entries, got {len(categories)} / {len(entries)}")
    cat_ids = [x["id"] for x in categories]
    if len(cat_ids) != len(set(cat_ids)):
        raise RuntimeError("duplicate category id")
    ids = [x["id"] for x in entries]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate entry id")
    for loc in locales:
        required_ui = {"title", "intro", "all", "select", "back", "language_note"}
        if set(source["ui"][loc]) != required_ui:
            raise RuntimeError(f"{loc}: ui keys drift")
    for category in categories:
        if set(category["title"]) != set(locales):
            raise RuntimeError(f"category locale drift: {category['id']}")
        icon = category["icon"]
        if not str(icon).startswith("textures/") and not (ICON_ROOT / f"{icon}.png").is_file():
            raise RuntimeError(f"missing category icon: {icon}")
    for row in entries:
        if row["category"] not in cat_ids:
            raise RuntimeError(f"unknown category for {row['id']}: {row['category']}")
        if set(row["title"]) != set(locales) or set(row["body"]) != set(locales):
            raise RuntimeError(f"entry locale drift: {row['id']}")
        lengths = {len(row["body"][loc]) for loc in locales}
        if len(lengths) != 1 or not next(iter(lengths)):
            raise RuntimeError(f"body line count mismatch/empty: {row['id']}")
        icon = str(row["icon"])
        if not icon.startswith("textures/") and not (ICON_ROOT / f"{icon}.png").is_file():
            raise RuntimeError(f"missing guide icon for {row['id']}: {icon}")
        for loc in locales:
            for line in row["body"][loc]:
                if not isinstance(line, str) or not line.strip():
                    raise RuntimeError(f"empty body text: {row['id']} {loc}")


def write_or_check(path: Path, expected: str, check: bool):
    if check:
        actual = path.read_text(encoding="utf-8-sig") if path.is_file() else None
        if actual != expected:
            raise RuntimeError(f"generated guide output drift: {path.relative_to(ROOT)}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source = load(SOURCE)
    validate_source(source)
    payload = build_payload(source)
    write_or_check(PAYLOAD, payload_js(payload), args.check)
    for locale in source["locales"]:
        write_or_check(TEXTS / f"{locale}.lang", lang_text(source, locale), args.check)

    summary = {
        "guide_version": source["version"],
        "revision": source["revision"],
        "categories": len(source["categories"]),
        "entries": len(source["entries"]),
        "locales": source["locales"],
        "fallback_locale": source["fallback_locale"],
        "mechanics_per_locale": {loc: len(payload["mechanicsByLocale"][loc]) for loc in source["locales"]},
        "showAll": payload["showAll"],
        "mode": "check" if args.check else "write",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
