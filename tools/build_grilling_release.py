from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects" / "grilling" / "gameplay_core"
BP = PROJECT / "behavior_pack"
RP = PROJECT / "resource_pack"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def add_file(zf: zipfile.ZipFile, source: Path, arcname: str):
    info = zipfile.ZipInfo(arcname, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    zf.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    bm = load_json(BP / "manifest.json")
    rm = load_json(RP / "manifest.json")
    version = tuple(int(x) for x in bm["header"]["version"])
    if tuple(int(x) for x in rm["header"]["version"]) != version:
        raise RuntimeError("BP/RP version mismatch")

    output = args.output
    if output is None:
        label = "_".join(map(str, version))
        output = ROOT / "artifacts" / "candidates" / f"Kaleidoscope_Grilling_A{label}_Canonical.mcaddon"
    if not output.is_absolute():
        output = (ROOT / output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w") as zf:
        for pack_name, pack in (("behavior_pack", BP), ("resource_pack", RP)):
            for path in sorted(pack.rglob("*"), key=lambda p: p.relative_to(pack).as_posix()):
                if not path.is_file() or path.name.startswith("."):
                    continue
                add_file(zf, path, pack_name + "/" + path.relative_to(pack).as_posix())

    with zipfile.ZipFile(output) as zf:
        if zf.testzip() is not None:
            raise RuntimeError("candidate archive failed zip integrity")
        bp_inside = json.loads(zf.read("behavior_pack/manifest.json").decode("utf-8-sig"))
        rp_inside = json.loads(zf.read("resource_pack/manifest.json").decode("utf-8-sig"))
        if tuple(bp_inside["header"]["version"]) != version or tuple(rp_inside["header"]["version"]) != version:
            raise RuntimeError("packaged manifest version mismatch")
        if "behavior_pack/scripts/main.js" not in zf.namelist():
            raise RuntimeError("packaged Script API entry is missing")

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = output.with_name(output.name + ".sha256")
    checksum.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "sha256": digest,
        "version": ".".join(map(str, version)),
        "deterministic_file_order": True,
        "fixed_zip_timestamps": True,
        "contains_canonical_bp_rp": True,
    }, indent=2))


if __name__ == "__main__":
    main()
