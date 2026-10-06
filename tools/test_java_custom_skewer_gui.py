import hashlib
import json
import unittest
from PIL import Image
import java_custom_skewer_gui as gui

class JavaCustomGuiTests(unittest.TestCase):
    def test_pinned_source_and_templates(self):
        for row in json.loads((gui.FIXTURE / 'source-manifest.json').read_text())['files']:
            self.assertEqual(hashlib.sha256((gui.FIXTURE / row['path']).read_bytes()).hexdigest(), row['sha256'])

    def test_empty_exact_stick(self):
        with Image.open(gui.TEMPLATES / 'stick.png') as image:
            self.assertEqual(gui.compose([]).tobytes(), image.convert('RGBA').tobytes())

    def test_mask_tones_and_rounding(self):
        self.assertEqual([gui.mask_tone((100, 100, 100), marker)[0] for marker in (48, 96, 144, 192, 240)], [56, 76, 100, 128, 156])
        self.assertEqual(gui.mask_tone((1, 1, 1), 48), (1, 1, 1))

    def test_missing_slots_and_variant_bits(self):
        red = [0xFF0000] * 16
        self.assertEqual(gui.compose([red], 0).tobytes(), gui.compose([red], 6).tobytes())
        self.assertNotEqual(gui.compose([red], 0).tobytes(), gui.compose([red], 1).tobytes())
        self.assertNotEqual(gui.compose([red], 0).tobytes(), gui.compose([red, red], 0).tobytes())

    def test_front_slot_overwrites_back_slot(self):
        rows = [[0xFF0000] * 16, [0x00FF00] * 16, [0x0000FF] * 16]
        result = gui.compose(rows)
        with Image.open(gui.TEMPLATES / 'food_1_1.png') as image:
            mask = image.convert('RGBA')
        for y in range(16):
            for x in range(16):
                pixel = mask.getpixel((x, y))
                if pixel[3]:
                    self.assertEqual(result.getpixel((x, y)), (*gui.mask_tone(gui.ingredient_color(rows[0]), pixel[0]), pixel[3]))

    def test_cooked_snapshot_differs_from_raw_and_legacy(self):
        row = [0xCC7722] * 16
        self.assertNotEqual(gui.ingredient_color(row), gui.ingredient_color(row, 4, True))
        self.assertNotEqual(gui.ingredient_color(row, 4, False), gui.ingredient_color(row, 4, True))
        self.assertEqual(row, [0xCC7722] * 16)

    def test_invalid_shape(self):
        with self.assertRaises(ValueError): gui.compose([[0] * 16] * 4)
        with self.assertRaises(ValueError): gui.compose([], 8)
        with self.assertRaises(ValueError): gui.compose([[0] * 15])

if __name__ == '__main__': unittest.main()
