"""Build static native inventory fallbacks from the original Java GUI templates.

Templates: breezeth / Kaleidoscope Official Production Team, CC-BY-NC-SA-4.0.
See development/gameplay_core/fixtures/java-custom-skewer-gui-9a1acdab.
This does not resolve per-stack ingredients, cooking state or random variants.
"""
import argparse
import struct
import zlib
from pathlib import Path

from PIL import Image
from java_custom_skewer_gui import TEMPLATES, mask_tone

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'projects/grilling/gameplay_core/resource_pack/textures/items'
HELD_UV = (ROOT / 'development/gameplay_core/fixtures/java-secret-skewer-9a1acdab'
           / 'common/src/main/resources/assets/kaleidoscope_grilling/textures/item/secret_skewer_stick.png')
# Both maintained Java branches: SkewerColorProvider.FALLBACK.
FALLBACK_RGB = (0xB8, 0x6B, 0x45)


def completed_icon():
    with Image.open(TEMPLATES / 'stick.png') as original:
        result = original.convert('RGBA')
    # CustomSkewerGuiTexture.bake paints the front slot last.
    for slot in (3, 2, 1):
        with Image.open(TEMPLATES / f'food_{slot}_1.png') as original:
            mask = original.convert('RGBA')
        for y in range(16):
            for x in range(16):
                marker, _, _, alpha = mask.getpixel((x, y))
                if alpha:
                    result.putpixel((x, y), (*mask_tone(FALLBACK_RGB, marker), alpha))
    return result


def png_bytes(image):
    """Fixed RGBA PNG with one uncompressed DEFLATE block; no encoder drift."""
    if image.mode != 'RGBA' or image.size != (16, 16):
        raise ValueError('Expected original 16x16 RGBA GUI icon')
    pixels = image.tobytes()
    raw = b''.join(b'\0' + pixels[y * 64:(y + 1) * 64] for y in range(16))
    packed = (b'\x78\x01\x01' + struct.pack('<HH', len(raw), len(raw) ^ 0xFFFF)
              + raw + struct.pack('>I', zlib.adler32(raw) & 0xFFFFFFFF))

    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF))

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', 16, 16, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', packed) + chunk(b'IEND', b''))


def expected_icons():
    return {
        # Existing raw-last helper references retain the original UV sprite.
        'unfinished_skewer.png': HELD_UV.read_bytes(),
        'secret_skewer.png': HELD_UV.read_bytes(),
        'unfinished_skewer_gui.png': (TEMPLATES / 'stick.png').read_bytes(),
        'secret_skewer_gui.png': png_bytes(completed_icon()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, expected in expected_icons().items():
        path = OUTPUT / name
        if args.check:
            if not path.exists() or path.read_bytes() != expected:
                raise SystemExit('Native GUI fallback differs: ' + name)
        else:
            path.write_bytes(expected)
    print('Native skewer inventory fallback icons ' + ('verified' if args.check else 'written'))


if __name__ == '__main__':
    main()
