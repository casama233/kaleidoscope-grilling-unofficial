"""Focused palette regressions; no pack generation or engine-rendering claims.

Optional pinned Java differential oracle:
  KG_PINNED_SKEWER_PROVIDER=/path/to/SkewerColorProvider.java \
    python -m unittest discover -s tools -p test_secret_food_palette.py
"""

from pathlib import Path
import hashlib
import os
import random
import shutil
import subprocess
import tempfile
import unittest

from PIL import Image

import secret_food_palette as palette


class SecretFoodPaletteTests(unittest.TestCase):
    def test_alpha_boundary_and_fully_transparent_fallback(self):
        self.assertEqual(palette.sample_grid(Image.new("RGBA", (1, 1), (10, 20, 30, 47))),
                         [palette.FALLBACK] * 16)
        self.assertEqual(palette.sample_grid(Image.new("RGBA", (1, 1), (10, 20, 30, 48))),
                         [0x0A141E] * 16)

    def test_center_crop_and_source_y_inversion(self):
        image = Image.new("RGBA", (8, 8), (0, 255, 0, 255))
        for y in range(2, 6):
            for x in range(2, 6):
                image.putpixel((x, y), (255, 0, 0, 255) if y < 4 else (0, 0, 255, 255))
        self.assertEqual(palette.sample_grid(image), [0x0000FF] * 8 + [0xFF0000] * 8)

    def test_empty_center_samples_whole_sprite(self):
        image = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        image.putpixel((0, 0), (31, 127, 239, 255))
        self.assertEqual(palette.sample_grid(image), [0x1F7FEF] * 16)

    def test_dark_pixels_are_filtered_with_per_cell_fallback(self):
        image = Image.new("RGBA", (16, 16), (200, 200, 200, 255))
        for y in range(4, 12, 2):
            for x in range(4, 12, 2):
                image.putpixel((x, y), (0, 0, 0, 255))
        self.assertEqual(palette.sample_grid(image), [0xC8C8C8] * 16)
        self.assertEqual(palette.sample_grid(Image.new("RGB", (16, 16), (0, 0, 0))), [0] * 16)

    def test_transparent_fill_is_in_place_with_ascending_ties(self):
        colors = [None] * 16
        colors[3], colors[12] = 0xFF0000, 0x0000FF
        palette._fill_transparent_cells(colors, palette.FALLBACK)
        # Cell zero ties between the two initial sources; the earlier red
        # source wins. Already filled cells then propagate the same red.
        self.assertEqual(colors, [0xFF0000] * 12 + [0x0000FF, 0xFF0000, 0xFF0000, 0xFF0000])

    def test_tint_uses_integer_division_and_java_signed_int(self):
        image = Image.new("RGB", (4, 4), (196, 100, 25))
        self.assertEqual(palette.sample_grid(image, 0x739AD1), [0x583C14] * 16)
        self.assertEqual(palette.sample_grid(image, 0), [0] * 16)
        self.assertEqual(palette.sample_grid(image, 0x80000000), [0xC46419] * 16)

    def test_quantization_fixture_retains_java_cluster_order(self):
        image = Image.new("RGBA", (8, 8))
        image.putdata([((i * 37) % 256, (i * 53) % 256, (i * 83) % 256, 255)
                       for i in range(64)])
        expected = [0x24CCC7, 0x24CCC7, 0x5A246B, 0x5A246B,
                    0xEA0A06, 0x0F3F59, 0x629DD5, 0x629DD5,
                    0xD95F8E, 0xD95F8E, 0x65DD1E, 0x5A246B,
                    0x629DD5, 0x65DD1E, 0xD95F8E, 0x0959CF]
        self.assertEqual(palette.sample_grid(image), expected)
        self.assertLessEqual(len(set(expected)), 8)

    def test_cleanup_two_vs_two_tie_uses_java_hash_buckets(self):
        colors = [0x00FF00] * 16
        colors[4] = colors[1] = 0xFF0000
        colors[5] = 0
        palette._clean_isolated_cells(colors)
        self.assertEqual(colors[5], 0x00FF00)

    def test_face_shading_then_all_six_stage_styles(self):
        colors = [0xB86B45] * 16
        edge = [0xCD774D, 0xE69058, 0xC06F43, 0xA45836, 0x9D5738, 0x130C09]
        inner = [0xCD774D, 0xE69058, 0xC97548, 0xB4633E, 0xB66441, 0x23160F]
        for stage in range(6):
            self.assertEqual(palette.color_at(colors, 0, 0, stage), edge[stage])
            self.assertEqual(palette.color_at(colors, 0, 5, stage), inner[stage])
        self.assertEqual([palette.color_at(colors, face, 0, 0) for face in range(6)],
                         [0xCD774D, 0x925537, 0x9C5B3B, 0xB06642, 0xAC6440, 0xA45F3D])

    def test_snapshot_only_changes_stage_four_glaze(self):
        colors = [0xB86B45] * 16
        self.assertEqual(palette.color_at(colors, 0, 0, 4, True), 0xBE6C46)
        self.assertEqual(palette.color_at(colors, 0, 5, 4, True), 0xCB724A)
        for stage in (0, 1, 2, 3, 5):
            self.assertEqual(palette.color_at(colors, 0, 5, stage, True),
                             palette.color_at(colors, 0, 5, stage))

    def test_atlas_layout_is_opaque_face_by_cell(self):
        colors = [index * 0x0F0F0F for index in range(16)]
        atlas = palette.render_atlas(colors, 4, True)
        self.assertEqual((atlas.mode, atlas.size), ("RGBA", (16, 6)))
        for face in range(6):
            for cell in range(16):
                rgb = palette.color_at(colors, face, cell, 4, True)
                self.assertEqual(atlas.getpixel((cell, face)),
                                 (rgb >> 16 & 255, rgb >> 8 & 255, rgb & 255, 255))

    def test_bounded_api_rejects_invalid_indices_and_palettes(self):
        for args in (([0] * 15, 0, 0, 0), ([0] * 16, 6, 0, 0),
                     ([0] * 16, 0, 16, 0), ([0] * 16, 0, 0, 6),
                     ([-1] * 16, 0, 0, 0)):
            with self.assertRaises(ValueError):
                palette.color_at(*args)


@unittest.skipUnless(os.environ.get("KG_PINNED_SKEWER_PROVIDER") and shutil.which("java"),
                     "set KG_PINNED_SKEWER_PROVIDER and install Java for pinned differential oracle")
class PinnedJavaOracleTests(unittest.TestCase):
    def test_exact_pinned_java_differential(self):
        source_path = Path(os.environ["KG_PINNED_SKEWER_PROVIDER"])
        self.assertEqual(hashlib.sha256(source_path.read_bytes()).hexdigest(),
                         palette.PINNED_PROVIDER_SHA256)
        source = source_path.read_text()
        methods = source[source.index("  private static int[] sampleGrid("):
                         source.index("  private record PaletteKey")]
        start = methods.index("  private static int stageColor(")
        end = methods.index("    if (stage == 0) return rgb;", start)
        methods = (methods[:start]
                   + "  private static int stageColor(int rgb, int cell, int stage, boolean cooked) {\n"
                   + methods[end:])
        methods = methods.replace("SkeweringHandler.hasCookedIngredientStacks(stack)", "cooked")
        methods = methods.replace("SkewerColorProvider::luminance", "SecretPaletteOracle::luminance")
        cluster = source[source.index("  private static final class ColorCluster"):
                         source.index("  private SkewerColorProvider()")]
        oracle = _JAVA_HARNESS + methods + cluster + "}\n"
        rng = random.Random(20261005)
        commands, expected = [], []
        for i in range(200):
            width = rng.choice([1, 2, 3, 4, 5, 7, 8, 9, 16, 17, 32])
            height = rng.choice([1, 2, 3, 4, 5, 7, 8, 9, 16, 17, 32])
            pixels = [(rng.randrange(256), rng.randrange(256), rng.randrange(256),
                       rng.choice([0, 1, 47, 48, 49, 128, 255])) for _ in range(width * height)]
            if i % 10 == 0:
                pixels = [(r, g, b, 0) for r, g, b, a in pixels]
            if i % 10 == 1:
                pixels = [(r // 16, g // 16, b // 16, a) for r, g, b, a in pixels]
            image = Image.new("RGBA", (width, height))
            image.putdata(pixels)
            tint = rng.choice([-1, -2147483648, 0, 0xFFFFFF, 0x739AD1, rng.randrange(0xFFFFFF)])
            abgr = " ".join(f"{a << 24 | b << 16 | g << 8 | r:08x}" for r, g, b, a in pixels)
            commands.append(f"sample {width} {height} {tint} {abgr}")
            expected.append(" ".join(f"{rgb:06x}" for rgb in palette.sample_grid(image, tint)))
        for rgb in [0, 0xFFFFFF, 0xB86B45, 0x010101, 0x161616, 0x595959, 0x5A5A5A] + [
                rng.randrange(0xFFFFFF) for _ in range(20)]:
            for face in range(6):
                for cell in range(16):
                    for stage in range(6):
                        for cooked in (False, True):
                            commands.append(f"color {rgb:06x} {face} {cell} {stage} {int(cooked)}")
                            expected.append(f"{palette.color_at([rgb] * 16, face, cell, stage, cooked):06x}")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "SecretPaletteOracle.java"
            target.write_text(oracle)
            result = subprocess.run(["java", str(target)], input="\n".join(commands) + "\n",
                                    text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = [line.strip() for line in result.stdout.splitlines()]
        self.assertEqual(len(actual), 31304)
        for index, (java, python) in enumerate(zip(actual, expected)):
            self.assertEqual(java, python, commands[index])


_JAVA_HARNESS = """import java.util.*;
class SecretPaletteOracle {
  static final int GRID_SIZE=4,CELL_COUNT=16,FALLBACK=0xB86B45;
  static class NativeImage {
    int width,height; int[] pixels;
    NativeImage(int width,int height,int[] pixels) {this.width=width;this.height=height;this.pixels=pixels;}
    int getWidth(){return width;} int getHeight(){return height;}
    int getPixelRGBA(int x,int y){return pixels[y*width+x];}
  }
  static class Mth {
    static float clamp(float v,float min,float max){return Math.min(max,Math.max(min,v));}
    static int clamp(int v,int min,int max){return Math.min(max,Math.max(min,v));}
  }
  public static void main(String[] args) {
    Scanner scanner = new Scanner(System.in);
    while(scanner.hasNext()) {
      String mode=scanner.next();
      if(mode.equals("sample")) {
        int width=scanner.nextInt(),height=scanner.nextInt(),tint=scanner.nextInt();
        int[] pixels=new int[width*height];
        for(int i=0;i<pixels.length;i++) pixels[i]=(int)Long.parseLong(scanner.next(),16);
        for(int rgb:sampleGrid(new NativeImage(width,height,pixels),width,height,tint))
          System.out.printf("%06x ",rgb);
        System.out.println();
      } else if(mode.equals("color")) {
        int rgb=(int)Long.parseLong(scanner.next(),16),face=scanner.nextInt(),cell=scanner.nextInt(),stage=scanner.nextInt();
        boolean cooked=scanner.nextInt()!=0;
        System.out.printf("%06x%n",stageColor(shadeForFace(rgb,face),cell,stage,cooked));
      }
    }
  }
"""


if __name__ == "__main__":
    unittest.main()
