"""Bake all 64 finished-bottle inventory states from pinned Java models.

Reuse the existing A2.8.1 projection, lighting and transparent-shell renderer so
the representative icon stays byte-for-byte unchanged. Each state reads its own
Java fill geometry and UV rectangle, including variants 5 through 7. This is a
static inventory asset contract, not evidence of native client rendering.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

import a281_bottle_icons as sprites

ROOT = Path(__file__).resolve().parents[2]
BP = ROOT / "projects/grilling/gameplay_core/behavior_pack"
RP = sprites.RP
SOURCE = sprites.ASSETS / "kaleidoscope_grilling/models/item/seasoning_special_states"
TEXTURE = sprites.ASSETS / "kaleidoscope_grilling/textures/block/spice_jar.png"
MODEL_SET_SHA256 = "8f2d794f4b61b541866a13fe191bb8eb68ec09323b3ee3e9cb44bc94b8572497"
TEXTURE_SHA256 = "d2a4d3b0e081cf145b8bc54ff5fba6b4b12a754dfd7dc80972c1d26646932f33"
STATES = tuple((remaining, variant) for remaining in range(1, 9) for variant in range(8))


def name_for(remaining: int, variant: int) -> str:
    if (remaining, variant) not in STATES:
        raise ValueError(f"invalid finished seasoning state: {remaining}, {variant}")
    return f"special_seasoning_r{remaining}_v{variant}"


def source_for(remaining: int, variant: int) -> Path:
    name_for(remaining, variant)
    return SOURCE / f"remaining_{remaining}_variant_{variant}.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def source_contract() -> dict:
    hashes = {
        name_for(r, v): hashlib.sha256(source_for(r, v).read_bytes()).hexdigest()
        for r, v in STATES
    }
    digest = hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert digest == MODEL_SET_SHA256, "pinned finished-bottle Java models changed"
    assert hashlib.sha256(TEXTURE.read_bytes()).hexdigest() == TEXTURE_SHA256, "pinned Java bottle palette changed"
    return {"model_set_sha256": digest, "texture_sha256": TEXTURE_SHA256}


def images() -> dict[str, Image.Image]:
    source_contract()
    sprites.INPUTS.clear()
    return {
        name_for(r, v): sprites.render(sprites.make_faces(sprites.model(source_for(r, v))))
        for r, v in STATES
    }


def item_paths(bp: Path = BP) -> dict[str, Path]:
    paths = {name_for(r, v): bp / "items" / f"{name_for(r, v)}.json" for r, v in STATES}
    actual = {path.stem for path in (bp / "items").glob("special_seasoning_r*_v*.json")}
    assert actual == set(paths), ("finished-bottle item set drift", actual ^ set(paths))
    return paths


def binding_documents(bp: Path = BP, rp: Path = RP) -> dict[Path, dict]:
    """Change only icon bindings; preserve later item fixes and other atlas rows."""
    documents = {}
    for name, path in item_paths(bp).items():
        doc = load(path)
        item = doc["minecraft:item"]
        assert item["description"]["identifier"] == "kaleidoscope_grilling:" + name, path
        item["components"]["minecraft:icon"] = {"textures": {"default": name}}
        documents[path] = doc
    atlas_path = rp / "textures/item_texture.json"
    atlas = load(atlas_path)
    for remaining, variant in STATES:
        name = name_for(remaining, variant)
        atlas["texture_data"][name] = {"textures": "textures/items/" + name}
    documents[atlas_path] = atlas
    return documents


def verify(result: dict[str, Image.Image], bp: Path = BP, rp: Path = RP) -> None:
    expected = {name_for(r, v) for r, v in STATES}
    assert set(result) == expected, "finished-bottle image set drift"
    actual = {path.stem for path in (rp / "textures/items").glob("special_seasoning_r*_v*.png")}
    assert actual == expected, ("finished-bottle texture set drift", actual ^ expected)
    atlas = load(rp / "textures/item_texture.json")["texture_data"]
    assert {name for name in atlas if name.startswith("special_seasoning_r")} == expected
    for path, doc in binding_documents(bp, rp).items():
        assert load(path) == doc, ("finished-bottle icon binding drift", path)
    for name, image in result.items():
        with Image.open(rp / "textures/items" / (name + ".png")) as source:
            actual_image = source.convert("RGBA")
        assert actual_image.size == image.size and actual_image.tobytes() == image.tobytes(), ("finished-bottle sprite drift", name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = images()
    if not args.check:
        # Validate every existing item before any output mutation.
        documents = binding_documents()
        for name, image in result.items():
            image.save(RP / "textures/items" / (name + ".png"), compress_level=9)
        for path, doc in documents.items():
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verify(result)
    print(json.dumps({"finished_bottle_icons": len(result), "size": sprites.SIZE,
                      **source_contract(), "minecraft_tested": False,
                      "client_visuals_tested": False}, indent=2))


if __name__ == "__main__":
    main()
