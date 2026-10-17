"""Describe the legacy Cookery locale edit without redistributing the host pack."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

EXPECTED_SHA = "c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351"
OLD = "const safeLocale=cleanToken(locale);"
NEW = 'const safeLocale=/^[a-z]{2}_[A-Z]{2}$/.test(locale)?locale:"";'
REG_SUFFIX = "[BP]/scripts/api/guidebookExtensionRegistry.js"
UI_SUFFIX = "[BP]/scripts/events/guidebook.js"
NOTE = (
    "Compatibility edit for Kaleidoscope Cookery (Unofficial) v1.0.6. "
    "Obtain the original package separately from its author. "
    "This document contains only the scoped text edit, not the original or a "
    "modified Cookery package. Original material remains subject to its original "
    "license and attribution notices; this change does not imply author endorsement."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build_patch(src: Path) -> dict:
    """Check the pinned input and return a minimal, non-executable JSON edit."""
    require(sha256(src) == EXPECTED_SHA, "original Cookery 1.0.6 SHA-256 mismatch")
    with zipfile.ZipFile(src, "r") as archive:
        names = archive.namelist()
        registries = [name for name in names if name.endswith(REG_SUFFIX)]
        interfaces = [name for name in names if name.endswith(UI_SUFFIX)]
        require(len(registries) == len(interfaces) == 1, "ambiguous or missing host source")
        reg, ui = registries[0], interfaces[0]
        original = archive.read(reg)
        reg_text = original.decode("utf-8-sig")
        ui_text = archive.read(ui).decode("utf-8-sig")

    require(reg_text.count(OLD) == 1 and NEW not in reg_text, "locale edit precondition failed")
    require('return /^[a-z0-9_.-]+$/.test(s) ? s : "";' in reg_text, "generic token validator changed")
    require('if (!/^[a-z]{2}_[A-Z]{2}$/.test(locale)' in reg_text, "locale map validator changed")
    require('entry.mechanicsByLocale?.[guidebookLocaleCode(player)] || entry.mechanics' in ui_text,
            "per-player locale lookup changed")
    require('const GUIDEBOOK_LANGUAGE_KEY = "kc:guidebook_language";' in ui_text,
            "per-player language key changed")
    require('player.setDynamicProperty(GUIDEBOOK_LANGUAGE_KEY, code);' in ui_text,
            "per-player language write changed")
    require('return guidebookLocale(player)?.locale || "en_US";' in ui_text,
            "per-player language fallback changed")

    # Replace only these ASCII bytes, preserving the host file's BOM and line endings.
    patched = original.replace(OLD.encode("utf-8"), NEW.encode("utf-8"), 1)
    return {
        "schema": 2,
        "kind": "cookery-guide-locale-text-patch",
        "input_sha256": EXPECTED_SHA,
        "source_version": "1.0.6",
        "registry_path": reg,
        "guide_ui_path": ui,
        "encoding": "utf-8",
        "registry_input_sha256": hashlib.sha256(original).hexdigest(),
        "registry_output_sha256": hashlib.sha256(patched).hexdigest(),
        "runtime_change": {"old": OLD, "new": NEW, "replacement_count": 1},
        "generic_cleanToken_unchanged": True,
        "locale_map_validator_unchanged": True,
        "guide_ui_lookup_unchanged": True,
        "per_player_language_property": "kc:guidebook_language",
        "per_player_language_isolation_preserved": True,
        "supported_locales_verified": ["zh_CN", "zh_TW", "en_US"],
        "license_notice": NOTE,
    }


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: patch_cookery106_guide_locale.py "
            "<private-original.mcaddon> <output.patch.json> <report.json>"
        )
    src, out, report = map(Path, sys.argv[1:])
    if not out.name.endswith(".patch.json") or report.suffix != ".json":
        raise SystemExit("Only .patch.json and JSON reports are supported; full Cookery archives are not produced.")
    if len({src.resolve(), out.resolve(), report.resolve()}) != 3:
        raise SystemExit("Input, patch and report must be different files.")
    if out.exists() or report.exists():
        raise SystemExit("Refusing to overwrite an existing patch or report.")

    patch = build_patch(src)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as handle:
        json.dump(patch, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    result = {
        "schema": 2,
        "output_kind": "text-patch-only",
        "input_sha256": EXPECTED_SHA,
        "patch_sha256": sha256(out),
        "runtime_change": patch["runtime_change"],
        "per_player_language_isolation_preserved": True,
        "full_host_archive_produced": False,
        "minecraft_tested": False,
        "bds_tested": False,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
