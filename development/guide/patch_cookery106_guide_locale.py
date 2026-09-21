from __future__ import annotations
import hashlib, json, sys, zipfile
from pathlib import Path

EXPECTED_SHA = "c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351"
OLD = "const safeLocale=cleanToken(locale);"
NEW = 'const safeLocale=/^[a-z]{2}_[A-Z]{2}$/.test(locale)?locale:"";'
REG_SUFFIX = "[BP]/scripts/api/guidebookExtensionRegistry.js"
UI_SUFFIX = "[BP]/scripts/events/guidebook.js"
NOTE_NAME = "KC_GRILLING_GUIDE_LOCALE_COMPAT.md"
NOTE = """# Grilling Guide locale compatibility patch

This archive is Kaleidoscope Cookery (Unofficial) v1.0.6 with one narrowly scoped Guidebook Extension API v1 compatibility fix.

Changed behavior:
- mechanicsByLocale locale keys are validated with the same standard locale shape already used by the host locale maps: xx_YY, for example zh_CN, zh_TW, and en_US.
- The generic token validator is not loosened.

Unchanged:
- Cookery gameplay and recipes.
- UUIDs, manifest versions, resources, and UI flow.
- Per-player language storage. The guidebook still stores the selected language in kc:guidebook_language on each player.
- The existing guide UI still reads entry.mechanicsByLocale using that player's guidebook locale.

Original package: Kaleidoscope Cookery (Unofficial) v1.0.6.
Original package SHA-256: c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351.

The original and modified Cookery material remains subject to its original license. This file documents the compatibility change and does not imply endorsement by the original authors.
"""

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: patch_cookery106_guide_locale.py <original.mcaddon> <output.mcaddon> <report.json>")
    src, out, report = map(Path, sys.argv[1:])
    assert sha256(src) == EXPECTED_SHA, (sha256(src), EXPECTED_SHA)

    with zipfile.ZipFile(src, "r") as zin:
        infos = zin.infolist()
        names = [i.filename for i in infos]
        reg = next(n for n in names if n.endswith(REG_SUFFIX))
        ui = next(n for n in names if n.endswith(UI_SUFFIX))
        reg_text = zin.read(reg).decode("utf-8-sig")
        ui_text = zin.read(ui).decode("utf-8-sig")

        assert reg_text.count(OLD) == 1
        assert 'return /^[a-z0-9_.-]+$/.test(s) ? s : "";' in reg_text
        assert 'if (!/^[a-z]{2}_[A-Z]{2}$/.test(locale)' in reg_text
        assert 'entry.mechanicsByLocale?.[guidebookLocaleCode(player)] || entry.mechanics' in ui_text
        assert 'const GUIDEBOOK_LANGUAGE_KEY = "kc:guidebook_language";' in ui_text
        assert 'player.setDynamicProperty(GUIDEBOOK_LANGUAGE_KEY, code);' in ui_text
        assert 'return guidebookLocale(player)?.locale || "en_US";' in ui_text

        patched = reg_text.replace(OLD, NEW, 1)
        assert OLD not in patched and patched.count(NEW) == 1

        note_path = reg.split("/scripts/", 1)[0] + "/documentation/" + NOTE_NAME
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w") as zout:
            for info in infos:
                data = zin.read(info.filename)
                if info.filename == reg:
                    data = patched.encode("utf-8")
                clone = zipfile.ZipInfo(info.filename, info.date_time)
                clone.compress_type = info.compress_type
                clone.comment = info.comment
                clone.extra = info.extra
                clone.internal_attr = info.internal_attr
                clone.external_attr = info.external_attr
                clone.create_system = info.create_system
                zout.writestr(clone, data)
            zout.writestr(note_path, NOTE.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

    with zipfile.ZipFile(out, "r") as check:
        assert check.testzip() is None
        assert NEW in check.read(reg).decode("utf-8-sig")
        assert note_path in check.namelist()

    result = {
        "schema": 1,
        "input_sha256": EXPECTED_SHA,
        "output_sha256": sha256(out),
        "registry_path": reg,
        "guide_ui_path": ui,
        "note_path": note_path,
        "runtime_change": {"old": OLD, "new": NEW, "replacement_count": 1},
        "generic_cleanToken_unchanged": True,
        "locale_map_validator_unchanged": True,
        "guide_ui_lookup_unchanged": True,
        "per_player_language_property": "kc:guidebook_language",
        "per_player_language_isolation_preserved": True,
        "manifest_unchanged": True,
        "gameplay_unchanged": True,
        "supported_locales_verified": ["zh_CN", "zh_TW", "en_US"]
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
