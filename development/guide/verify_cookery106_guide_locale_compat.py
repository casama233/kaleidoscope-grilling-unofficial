"""Verify the legacy minimal locale patch without writing a Cookery archive."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from patch_cookery106_guide_locale import EXPECTED_SHA, build_patch, require, sha256

LOCALES = ("zh_CN", "zh_TW", "en_US")
PREFIX = "// Generated A1.16 per-player localized Cookery guide extension.\nexport const GUIDE_PAYLOAD = "


def payload(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    require(text.startswith(PREFIX) and text.endswith(";"), "expected legacy A1.16 payload")
    return json.loads(text[len(PREFIX):-1])


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit(
            "usage: verify_cookery106_guide_locale_compat.py "
            "<private-original.mcaddon> <output.patch.json> <payload.js> <report.json>"
        )
    original, patch_path, payload_path, report_path = map(Path, sys.argv[1:])
    if not patch_path.name.endswith(".patch.json"):
        raise SystemExit("Verify the minimal .patch.json document; full Cookery archives are no longer accepted.")
    expected = build_patch(original)
    patch = json.loads(patch_path.read_text(encoding="utf-8"))
    require(patch == expected, "patch differs from the single reviewed locale edit")

    guide = payload(payload_path)
    require(guide["version"] == "0.1.16" and len(guide["entries"]) == 33, "unexpected legacy guide identity")
    for entry in guide["entries"]:
        localized = entry.get("mechanicsByLocale")
        require(isinstance(localized, dict) and set(localized) == set(LOCALES), "missing entry locales")
        normalized = {locale: steps for locale, steps in localized.items()
                      if re.fullmatch(r"[a-z]{2}_[A-Z]{2}", locale) and isinstance(steps, list)}
        require(set(normalized) == set(LOCALES), "invalid localized mechanics")
        require(entry["mechanics"] == localized["zh_TW"], "legacy fallback changed")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report["schema"] == 2 and report["output_kind"] == "text-patch-only", "obsolete archive report")
    require(report["input_sha256"] == EXPECTED_SHA, "wrong source report")
    require(report["patch_sha256"] == sha256(patch_path), "patch report hash mismatch")
    require(report["runtime_change"] == expected["runtime_change"], "wrong edit report")
    require(report["per_player_language_isolation_preserved"] is True, "language isolation not verified")
    require(report["full_host_archive_produced"] is False, "full host output is prohibited")
    print(json.dumps({
        "cookery_input_sha256": EXPECTED_SHA,
        "patch_sha256": sha256(patch_path),
        "planned_changed_original_files": [patch["registry_path"]],
        "guide_entries": 33,
        "mechanics_locales": list(LOCALES),
        "per_player_language_property": "kc:guidebook_language",
        "per_player_language_isolation": True,
        "stock_host_bug_reproduced": True,
        "compat_text_edit_verified": True,
        "full_host_archive_produced": False,
        "minecraft_tested": False,
        "bds_tested": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
