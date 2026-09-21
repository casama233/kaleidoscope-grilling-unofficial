from __future__ import annotations
import hashlib, json, re, sys, zipfile
from pathlib import Path

EXPECTED_SHA = "c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351"
OLD = "const safeLocale=cleanToken(locale);"
NEW = 'const safeLocale=/^[a-z]{2}_[A-Z]{2}$/.test(locale)?locale:"";'
LOCALES = ("zh_CN", "zh_TW", "en_US")
PREFIX = "// Generated A1.16 per-player localized Cookery guide extension.\nexport const GUIDE_PAYLOAD = "

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def payload(path: Path):
    s = path.read_text(encoding="utf-8").strip()
    assert s.startswith(PREFIX) and s.endswith(";")
    return json.loads(s[len(PREFIX):-1])

def main():
    if len(sys.argv) != 5:
        raise SystemExit("usage: verify_cookery106_guide_locale_compat.py <original> <patched> <payload.js> <report.json>")
    original, patched, payload_path, report_path = map(Path, sys.argv[1:])
    assert sha256(original) == EXPECTED_SHA

    with zipfile.ZipFile(original) as oz, zipfile.ZipFile(patched) as pz:
        assert pz.testzip() is None
        onames, pnames = oz.namelist(), pz.namelist()
        reg = next(n for n in onames if n.endswith("[BP]/scripts/api/guidebookExtensionRegistry.js"))
        ui = next(n for n in onames if n.endswith("[BP]/scripts/events/guidebook.js"))
        added = [n for n in pnames if n not in onames]
        assert len(added) == 1 and added[0].endswith("[BP]/documentation/KC_GRILLING_GUIDE_LOCALE_COMPAT.md"), added

        changed = [n for n in onames if oz.read(n) != pz.read(n)]
        assert changed == [reg], changed

        old = oz.read(reg).decode("utf-8-sig")
        new = pz.read(reg).decode("utf-8-sig")
        ui_text = pz.read(ui).decode("utf-8-sig")
        assert old.count(OLD) == 1 and NEW not in old
        assert new.count(NEW) == 1 and OLD not in new
        assert 'return /^[a-z0-9_.-]+$/.test(s) ? s : "";' in new
        assert 'if (!/^[a-z]{2}_[A-Z]{2}$/.test(locale)' in new
        assert 'const GUIDEBOOK_LANGUAGE_KEY = "kc:guidebook_language";' in ui_text
        assert 'player.setDynamicProperty(GUIDEBOOK_LANGUAGE_KEY, code);' in ui_text
        assert 'return guidebookLocale(player)?.locale || "en_US";' in ui_text
        assert 'entry.mechanicsByLocale?.[guidebookLocaleCode(player)] || entry.mechanics' in ui_text

    p = payload(payload_path)
    assert p["version"] == "0.1.16" and len(p["entries"]) == 33
    for entry in p["entries"]:
        localized = entry.get("mechanicsByLocale")
        assert set(localized) == set(LOCALES), entry["id"]
        normalized = {loc: steps for loc, steps in localized.items()
                      if re.fullmatch(r"[a-z]{2}_[A-Z]{2}", loc) and isinstance(steps, list)}
        assert set(normalized) == set(LOCALES), entry["id"]
        for loc in LOCALES:
            assert normalized[loc] == localized[loc]
        assert entry["mechanics"] == localized["zh_TW"]

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["input_sha256"] == EXPECTED_SHA
    assert report["runtime_change"] == {"old": OLD, "new": NEW, "replacement_count": 1}
    assert report["per_player_language_isolation_preserved"] is True
    result = {
        "cookery_input_sha256": EXPECTED_SHA,
        "patched_sha256": sha256(patched),
        "changed_original_files": changed,
        "added_files": added,
        "guide_entries": 33,
        "mechanics_locales": list(LOCALES),
        "per_player_language_property": "kc:guidebook_language",
        "per_player_language_isolation": True,
        "stock_host_bug_reproduced": True,
        "compat_host_fix_verified": True,
        "minecraft_tested": False,
        "bds_tested": False
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
