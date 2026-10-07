"""Two source/asset regressions; these do not certify client rendering."""
import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/grilling/gameplay_core'
RP = PROJECT / 'resource_pack'
TEMPLATES = (ROOT / 'development/gameplay_core/fixtures/java-custom-skewer-gui-9a1acdab'
             / 'common/src/main/resources/assets/kaleidoscope_grilling/textures/item/custom_skewer_gui_16')


def rgba(path):
    with Image.open(path) as image:
        return image.convert('RGBA')


class NativeInventoryIconTests(unittest.TestCase):
    def test_gui_changes_do_not_reassign_particle_palette(self):
        sys.path.insert(0, str(ROOT / 'development/gameplay_core'))
        import a2770_placed_visual_assets as placed
        original_open = Image.open
        gui_paths = {RP / 'textures/items/unfinished_skewer.png', RP / 'textures/items/secret_skewer.png'}

        def particle_open(path, *args, **kwargs):
            if isinstance(path, (str, Path)):
                self.assertNotIn(Path(path), gui_paths, 'GUI sprite used as a particle-color source')
            return original_open(path, *args, **kwargs)

        with patch.object(placed.Image, 'open', side_effect=particle_open):
            actual = placed.ingredient_palette()
        data = (PROJECT / 'behavior_pack/scripts/a2770_placed_visual_data.js').read_text()
        expected = json.loads(re.search(r'INGREDIENT_COLORS=Object.freeze\((\{.*?\})\)', data).group(1))
        self.assertEqual(actual, expected)

    def test_empty_gui_stick_is_not_held_uv_atlas(self):
        target = RP / 'textures/items/unfinished_skewer.png'
        source = TEMPLATES / 'stick.png'
        self.assertEqual(target.read_bytes(), source.read_bytes())
        self.assertEqual(rgba(target).size, (16, 16))
        self.assertNotEqual(rgba(target).tobytes(), rgba(RP / 'textures/secret_skewer_stick.png').tobytes())
        item = json.loads((PROJECT / 'behavior_pack/items/unfinished_skewer.json').read_text())['minecraft:item']
        self.assertEqual(item['components']['minecraft:icon']['textures']['default'], 'unfinished_skewer')
        atlas = json.loads((RP / 'textures/item_texture.json').read_text())['texture_data']
        self.assertEqual(atlas['unfinished_skewer']['textures'], 'textures/items/unfinished_skewer')

    def test_completed_three_masks_front_overlap_and_native_routes(self):
        result = rgba(RP / 'textures/items/secret_skewer.png')
        stick = rgba(TEMPLATES / 'stick.png')
        masks = [rgba(TEMPLATES / f'food_{i}_1.png') for i in (1, 2, 3)]
        # Independent literals from author fallback B8/6B/45 and Java tones.
        tones = {48: (103, 60, 39), 96: (140, 81, 52), 144: (184, 107, 69),
                 192: (197, 134, 102), 240: (210, 160, 136)}
        self.assertEqual(result.size, (16, 16))
        for y in range(16):
            for x in range(16):
                front = next((m.getpixel((x, y)) for m in masks if m.getpixel((x, y))[3]), None)
                expected = (*tones[front[0]], front[3]) if front else stick.getpixel((x, y))
                self.assertEqual(result.getpixel((x, y)), expected, (x, y))
        # Exclusive cells prove all three slots; the last cell distinguishes
        # front-slot overwrite from the incorrect forward paint order.
        for point, expected in [((4, 7), (140, 81, 52, 255)),
                                ((8, 3), (140, 81, 52, 255)),
                                ((11, 0), (210, 160, 136, 255)),
                                ((7, 7), (210, 160, 136, 255))]:
            self.assertEqual(result.getpixel(point), expected)
        atlas = json.loads((RP / 'textures/item_texture.json').read_text())['texture_data']
        for name in ('secret_skewer', 'secret_skewer_java_three_alt', 'secret_skewer_native_plain'):
            item = json.loads((PROJECT / f'behavior_pack/items/{name}.json').read_text())['minecraft:item']
            icon = item['components']['minecraft:icon']['textures']['default']
            self.assertEqual(icon, 'secret_skewer')
            self.assertEqual(atlas[icon]['textures'], 'textures/items/secret_skewer')
            self.assertTrue((RP / (atlas[icon]['textures'] + '.png')).is_file())


if __name__ == '__main__':
    unittest.main()
