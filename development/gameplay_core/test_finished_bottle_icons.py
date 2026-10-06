"""Pinned-model inventory regressions; these do not certify native rendering."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

import a2766_build_special_seasoning_visuals as special_items
import build_finished_bottle_icons as icons


class FinishedBottleIcons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.images = icons.images()

    def test_exact_pinned_java_sources_and_palette(self):
        self.assertEqual(icons.source_contract(), {
            "model_set_sha256": "8f2d794f4b61b541866a13fe191bb8eb68ec09323b3ee3e9cb44bc94b8572497",
            "texture_sha256": "d2a4d3b0e081cf145b8bc54ff5fba6b4b12a754dfd7dc80972c1d26646932f33",
        })
        self.assertEqual(len(icons.sprites.INPUTS), 65)
        self.assertEqual(set(icons.sprites.INPUTS), {
            path.relative_to(icons.ROOT).as_posix()
            for path in [icons.TEXTURE, *(icons.source_for(r, v) for r, v in icons.STATES)]
        })

    def test_java_models_keep_shell_and_exact_fill_geometry_uv(self):
        representative = icons.load(icons.source_for(8, 0))
        shell = [element for element in representative["elements"] if not element["name"].startswith("spice_fill")]
        palette_uv = ((0, 4), (0, 8), (4, 8), (12, 8), (0, 12), (4, 12), (8, 12), (12, 12))
        for remaining, variant in icons.STATES:
            with self.subTest(remaining=remaining, variant=variant):
                model = icons.load(icons.source_for(remaining, variant))
                self.assertEqual(model["display"], representative["display"])
                self.assertEqual(model["textures"], representative["textures"])
                self.assertEqual([e for e in model["elements"] if not e["name"].startswith("spice_fill")], shell)
                fill = [e for e in model["elements"] if e["name"].startswith("spice_fill")]
                self.assertEqual(len(fill), 1)
                self.assertEqual(fill[0]["from"], [5.5, .5, 5.5])
                self.assertEqual(fill[0]["to"], [10.5, .5 + 5 * remaining / 8, 10.5])
                u, v = palette_uv[variant]
                for direction, face in fill[0]["faces"].items():
                    top = v if direction in ("up", "down") else v + 4 - remaining / 2
                    self.assertEqual(face["uv"], [u, top, u + 4, v + 4])
                    self.assertEqual(face["texture"], "#0")

    def test_all_64_images_and_item_atlas_bindings_reproduce(self):
        icons.verify(self.images)
        self.assertEqual(len(self.images), 64)
        self.assertEqual(len({image.tobytes() for image in self.images.values()}), 64)

    def test_representative_and_existing_base_icons_stay_unchanged(self):
        expected = {
            "special_seasoning": "911dd1a62942cd48171f9f39d7df4164d4adf821c7a69662c072c6269d6e6f11",
            "empty_seasoning_bottle": "e0bd1e10011502c7b30503646475113df0200b2f4c344b9ad301ed220d121650",
            "pending_seasoning": "e0bd1e10011502c7b30503646475113df0200b2f4c344b9ad301ed220d121650",
        }
        for name, digest in expected.items():
            path = icons.RP / "textures/items" / (name + ".png")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest, name)
        self.assertEqual((icons.RP / "textures/items/special_seasoning.png").read_bytes(),
                         (icons.RP / "textures/items/special_seasoning_r8_v0.png").read_bytes())

    def test_every_icon_keeps_framing_transparency_and_upper_shell(self):
        base = self.images["special_seasoning_r8_v0"]
        for name, image in self.images.items():
            with self.subTest(name=name):
                self.assertEqual(image.size, (64, 64))
                self.assertEqual(image.getbbox(), (11, 5, 53, 59))
                self.assertEqual(image.crop((0, 0, 64, 28)).tobytes(), base.crop((0, 0, 64, 28)).tobytes())
                alpha = image.getchannel("A")
                self.assertTrue(any(0 < value < 255 for value in alpha.tobytes()))
                for x in range(64):
                    self.assertEqual(image.getpixel((x, 0))[3], 0)
                    self.assertEqual(image.getpixel((x, 63))[3], 0)

    def test_original_special_item_generator_uses_state_icon(self):
        for remaining, variant in icons.STATES:
            item = special_items.item_doc(variant, remaining)["minecraft:item"]
            self.assertEqual(item["components"]["minecraft:icon"]["textures"]["default"],
                             icons.name_for(remaining, variant))

    def test_invalid_state_is_rejected(self):
        for remaining, variant in ((0, 0), (9, 0), (1, -1), (1, 8)):
            with self.assertRaises(ValueError):
                icons.name_for(remaining, variant)

    def temporary_packs(self, root):
        root = Path(root)
        bp, rp = root / "bp", root / "rp"
        (bp / "items").mkdir(parents=True)
        (rp / "textures/items").mkdir(parents=True)
        for path in icons.item_paths().values():
            shutil.copyfile(path, bp / "items" / path.name)
        shutil.copyfile(icons.RP / "textures/item_texture.json", rp / "textures/item_texture.json")
        for name in self.images:
            path = Path("textures/items") / (name + ".png")
            shutil.copyfile(icons.RP / path, rp / path)
        return bp, rp

    def test_binding_update_preserves_unrelated_item_fields_and_atlas_rows(self):
        with tempfile.TemporaryDirectory() as root:
            bp, rp = self.temporary_packs(root)
            atlas_path = rp / "textures/item_texture.json"
            atlas = icons.load(atlas_path)
            atlas["texture_data"]["pending_seasoning_fill_8"] = {"textures": "textures/items/pending_seasoning_fill_8"}
            atlas_path.write_text(json.dumps(atlas))
            expected = deepcopy(atlas)
            docs = icons.binding_documents(bp, rp)
            self.assertEqual(docs[atlas_path], expected)
            for path in icons.item_paths(bp).values():
                self.assertEqual(docs[path], icons.load(path))

    def test_wrong_full_icon_binding_and_wrong_atlas_target_are_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            bp, rp = self.temporary_packs(root)
            path = bp / "items/special_seasoning_r1_v7.json"
            item = icons.load(path)
            old = deepcopy(item)
            item["minecraft:item"]["components"]["minecraft:icon"]["textures"]["default"] = "special_seasoning"
            path.write_text(json.dumps(item))
            with self.assertRaisesRegex(AssertionError, "binding drift"):
                icons.verify(self.images, bp, rp)
            path.write_text(json.dumps(old))
            atlas_path = rp / "textures/item_texture.json"
            atlas = icons.load(atlas_path)
            atlas["texture_data"]["special_seasoning_r1_v7"]["textures"] = "textures/items/special_seasoning"
            atlas_path.write_text(json.dumps(atlas))
            with self.assertRaisesRegex(AssertionError, "binding drift"):
                icons.verify(self.images, bp, rp)

    def test_wrong_image_and_missing_image_are_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            bp, rp = self.temporary_packs(root)
            target = rp / "textures/items/special_seasoning_r1_v7.png"
            self.images["special_seasoning_r8_v0"].save(target)
            with self.assertRaisesRegex(AssertionError, "sprite drift"):
                icons.verify(self.images, bp, rp)
            target.unlink()
            with self.assertRaisesRegex(AssertionError, "texture set drift"):
                icons.verify(self.images, bp, rp)

    def test_changed_source_palette_is_rejected_before_generation(self):
        with tempfile.TemporaryDirectory() as root:
            palette = Path(root) / "spice_jar.png"
            with Image.open(icons.TEXTURE) as image:
                image = image.convert("RGBA")
            image.putpixel((1, 9), (255, 0, 255, 255))
            image.save(palette)
            with patch.object(icons, "TEXTURE", palette):
                with self.assertRaisesRegex(AssertionError, "palette changed"):
                    icons.source_contract()


if __name__ == "__main__":
    unittest.main(verbosity=2)
