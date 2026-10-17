"""Source-derived Java 16px GUI reference; no native Bedrock inventory routing.

Original templates: breezeth, CC-BY-NC-SA-4.0. See fixture source-manifest.
Ingredient palette resolution belongs to the caller, including cooked snapshots.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image
from secret_food_palette import color_at, _f32, _mul, _add, _sub, _round

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'development/gameplay_core/fixtures/java-custom-skewer-gui-9a1acdab'
TEMPLATES = FIXTURE / 'common/src/main/resources/assets/kaleidoscope_grilling/textures/item/custom_skewer_gui_16'


def ingredient_color(palette, stage=0, cooked_snapshot=False):
    colors = [color_at(palette, 0, cell, stage, cooked_snapshot) for cell in (5, 6, 9, 10)]
    return tuple(sum(rgb >> shift & 255 for rgb in colors) // 4 for shift in (16, 8, 0))


def mask_tone(color, marker):
    tone = min(4, max(0, _round(_f32((marker - 0x30) / _f32(48.0)))))
    if tone < 2:
        return tuple(_round(_mul(channel, _f32(0.56 if tone == 0 else 0.76))) for channel in color)
    if tone > 2:
        return tuple(_round(_add(channel, _mul(255 - channel, _f32(0.18 if tone == 3 else 0.36)))) for channel in color)
    return tuple(color)


def compose(palettes, variants=0, stage=0, cooked_snapshot=False):
    if len(palettes) > 3 or not 0 <= variants <= 7:
        raise ValueError('at most three ordered palettes and variants 0..7 required')
    with Image.open(TEMPLATES / 'stick.png') as stick:
        result = stick.convert('RGBA')
    for slot in range(len(palettes) - 1, -1, -1):
        color = ingredient_color(palettes[slot], stage, cooked_snapshot)
        with Image.open(TEMPLATES / f'food_{slot + 1}_{1 + (variants >> slot & 1)}.png') as original:
            mask = original.convert('RGBA')
        for y in range(16):
            for x in range(16):
                marker, _, _, alpha = mask.getpixel((x, y))
                if alpha:
                    result.putpixel((x, y), (*mask_tone(color, marker), alpha))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'development/gameplay_core/fixtures/secret-food-palettes.json'
    carrot = next(row for row in json.loads(source.read_text())['items'] if row['id'] == 'minecraft:carrot')
    files = []
    # Cooked partial rows are renderer probes only: ordinary unfinished assembly is raw.
    for state, stage, snapshot in [('raw', 0, False), ('cooked_snapshot', 4, True)]:
        for count in range(1, 4):
            for variant in range(8):
                name = f'carrot_{count}_{state}_v{variant}.png'
                path = args.output / name
                compose([carrot['palette']] * count, variant, stage, snapshot).save(path)
                files.append({'file': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                              'normal_gameplay_state': state == 'raw' or count == 3})
    (args.output / 'reference-receipt.json').write_text(json.dumps({
        'source_revision': '9a1acdab27698457bec16c9362678e574895a28c',
        'kind': 'source-derived reference, not a Java screenshot or Bedrock runtime result',
        'license': 'CC-BY-NC-SA-4.0', 'attribution': 'breezeth; Kaleidoscope Official Production Team',
        'palette_source': carrot['source'], 'files': files}, indent=2) + '\n')

if __name__ == '__main__':
    main()
