from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
from vibrant_gate import check_pair

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "projects/grilling/gameplay_core"
BP = PROJECT / "behavior_pack"
RP = PROJECT / "resource_pack"
DEV = Path(__file__).resolve().parent

EXPECTED = {
    "bp_header_uuid": "c68005c5-23ff-54e8-a3ff-da6349ad43c2",
    "bp_data_uuid": "dcf70052-c592-56e3-84d2-2a9b86abe7ab",
    "bp_script_uuid": "d0bb6818-8187-5d20-8e1f-a2ab7b517795",
    "rp_header_uuid": "bbbd2d60-52e5-53a6-8b9a-c09b0f516389",
    "rp_module_uuid": "e7d592db-f4a0-53ce-8b0a-cab7a0cee8d7",
    "cookery_bp_uuid": "10f37ae2-9ccf-435f-b34b-0eec8191cd94",
    "cookery_rp_uuid": "c89dc8df-c3fc-4bc8-8bd0-527abba76681",
}

VERIFIERS = {
    (2, 7, 60): "verify_a2760.py",
    (2, 7, 61): "verify_a2761.py",
    (2, 7, 62): "verify_a2762.py",
    (2, 7, 63): "verify_a2763.py",
    (2, 7, 64): "verify_a2764.py",
    (2, 7, 65): "verify_a2765.py",
    (2, 7, 66): "verify_a2766.py",
    (2, 7, 67): "verify_a2767.py",
    (2, 7, 68): "verify_a2768.py",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def module_by_type(manifest: dict, kind: str) -> dict:
    rows = [m for m in manifest.get("modules", []) if m.get("type") == kind]
    assert len(rows) == 1, (kind, rows)
    return rows[0]


def dependency_by_uuid(manifest: dict, uuid: str) -> dict:
    rows = [d for d in manifest.get("dependencies", []) if d.get("uuid") == uuid]
    assert len(rows) == 1, (uuid, rows)
    return rows[0]


def verify_relative_imports() -> int:
    pattern = re.compile(r"(?:from\s+|import\s*)['\"](\.[^'\"]+)['\"]")
    checked = 0
    for path in sorted((BP / "scripts").glob("*.js")):
        text = path.read_text(encoding="utf-8")
        for spec in pattern.findall(text):
            target = (path.parent / spec).resolve()
            assert target.is_file(), f"missing relative import: {path.relative_to(ROOT)} -> {spec}"
            checked += 1
    return checked


def generic_gate() -> tuple[int, int, int, int]:
    for path in PROJECT.rglob("*.json"):
        load(path)

    bp = load(BP / "manifest.json")
    rp = load(RP / "manifest.json")
    bp_version = tuple(bp["header"]["version"])
    rp_version = tuple(rp["header"]["version"])
    assert bp_version == rp_version, (bp_version, rp_version)
    if bp_version >= (2, 7, 68):
        check_pair(bp, rp)

    assert bp["header"]["uuid"] == EXPECTED["bp_header_uuid"]
    assert rp["header"]["uuid"] == EXPECTED["rp_header_uuid"]

    data_module = module_by_type(bp, "data")
    script_module = module_by_type(bp, "script")
    resource_module = module_by_type(rp, "resources")
    assert data_module["uuid"] == EXPECTED["bp_data_uuid"]
    assert script_module["uuid"] == EXPECTED["bp_script_uuid"]
    assert resource_module["uuid"] == EXPECTED["rp_module_uuid"]
    assert tuple(data_module["version"]) == bp_version
    assert tuple(script_module["version"]) == bp_version
    assert tuple(resource_module["version"]) == rp_version

    rp_dep = dependency_by_uuid(bp, EXPECTED["rp_header_uuid"])
    assert tuple(rp_dep["version"]) == rp_version
    cookery_bp = dependency_by_uuid(bp, EXPECTED["cookery_bp_uuid"])
    cookery_rp = dependency_by_uuid(rp, EXPECTED["cookery_rp_uuid"])
    assert tuple(cookery_bp["version"]) == (1, 0, 6)
    assert tuple(cookery_rp["version"]) == (1, 0, 6)

    entry = BP / script_module["entry"]
    assert entry.is_file(), entry
    imports = verify_relative_imports()

    config = load(PROJECT / "config.json")
    assert config["type"] == "minecraftBedrock"
    assert config["namespace"] == "kaleidoscope_grilling"
    assert config["packs"] == {"behaviorPack": "./behavior_pack", "resourcePack": "./resource_pack"}

    active_legacy = sorted((ROOT / ".github/workflows").glob("gameplay-core-a*.yml"))
    archived_legacy = sorted((ROOT / "docs/legacy_workflows").glob("gameplay-core-a*.yml"))
    assert not active_legacy, f"retired gameplay workflows reactivated: {active_legacy}"
    assert len(archived_legacy) == 65, f"expected 65 archived gameplay workflows, got {len(archived_legacy)}"
    assert (ROOT / ".github/workflows/gameplay-core.yml").is_file()

    return bp_version[0], bp_version[1], bp_version[2], imports


def verify_compiled_exact() -> None:
    dist = PROJECT / "builds/dist"
    for name, source in (("behavior_pack", BP), ("resource_pack", RP)):
        manifest = load(source / "manifest.json")
        uuid = manifest["header"]["uuid"]
        matches = [p.parent for p in dist.rglob("manifest.json") if load(p).get("header", {}).get("uuid") == uuid]
        assert len(matches) == 1, (name, matches)
        target = matches[0]
        source_files = {
            p.relative_to(source).as_posix(): p
            for p in source.rglob("*")
            if p.is_file() and not p.name.startswith(".")
        }
        target_files = {
            p.relative_to(target).as_posix(): p
            for p in target.rglob("*")
            if p.is_file() and not p.name.startswith(".")
        }
        assert set(source_files) == set(target_files), {
            "pack": name,
            "missing": sorted(set(source_files) - set(target_files)),
            "extra": sorted(set(target_files) - set(source_files)),
        }
        for rel, path in source_files.items():
            compiled = target_files[rel]
            if path.suffix == ".json":
                assert load(path) == load(compiled), rel
            else:
                assert path.read_bytes() == compiled.read_bytes(), rel


def main() -> None:
    parser = argparse.ArgumentParser(description="Canonical verifier for the current Grilling gameplay core")
    parser.add_argument("--compiled", action="store_true", help="also compare the real Dash output")
    args = parser.parse_args()

    major, minor, patch, imports = generic_gate()
    subprocess.run([sys.executable, str(DEV / "verify_visual_refs.py")], check=True)
    version = (major, minor, patch)
    verifier = VERIFIERS.get(version)
    if verifier is None:
        known = ", ".join(".".join(map(str, v)) for v in sorted(VERIFIERS))
        raise SystemExit(
            f"No release verifier registered for {major}.{minor}.{patch}. "
            f"Add the new version verifier to verify_current.py before changing canonical source. Known: {known}"
        )

    command = [sys.executable, str(DEV / verifier)]
    if args.compiled:
        command.append("--compiled")
    subprocess.run(command, check=True)
    if args.compiled:
        verify_compiled_exact()
    print(
        f"Canonical gameplay-core gate PASS: {major}.{minor}.{patch}; "
        f"relative imports checked={imports}; compiled={args.compiled}"
    )


if __name__ == "__main__":
    main()
