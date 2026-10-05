"""Inspect explicit local sprite sources; commit span facts, never food artwork."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
from PIL import Image
from generated_food_sprite import ROOT, FIXTURE, spans_from_alpha


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vanilla-review', type=Path, required=True)
    parser.add_argument('--cookery-addon', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    catalog_path = ROOT / 'development/gameplay_core/fixtures/secret-visual-catalog.json'
    catalog = json.loads(catalog_path.read_text())['items']
    vanilla_path = args.vanilla_review / 'alpha-mask-catalog.json'
    vanilla = json.loads(vanilla_path.read_text())
    vanilla_rows = {row['texture']: row for row in vanilla['textures']}
    output = []
    with zipfile.ZipFile(args.cookery_addon) as addon:
        for index, row in enumerate(catalog, 1):
            texture_path = row['texture'] + '.png'
            if row['id'].startswith('minecraft:'):
                source = vanilla_rows[row['texture']]
                raw = (args.vanilla_review / 'png' / Path(source['inspection_png']).name).read_bytes()
                assert sha(raw) == source['png_sha256']
                origin = {'kind': 'installed_bedrock_1.26.52.3',
                          'pack': source['selected_source_pack'], 'entry': Path(source['inspection_png']).name,
                          'archive_sha256': source['archive_sha256'], 'sha256': sha(raw)}
            elif row['id'].startswith('kaleidoscope_cookery:'):
                entry = 'Kaleidoscope Cookery v1.0.8 [RP]/' + texture_path
                raw = addon.read(entry)
                assert sha(raw) == row['texture_sha256'], row['id']
                origin = {'kind': 'catalog_hash_verified_cookery_1.0.8_sprite',
                          'entry': entry, 'sha256': sha(raw)}
            else:
                raw = (ROOT / 'projects/grilling/gameplay_core/resource_pack' / texture_path).read_bytes()
                origin = {'kind': 'canonical_grilling_runtime_sprite', 'path': texture_path, 'sha256': sha(raw)}
            with Image.open(io.BytesIO(raw)) as image:
                image = image.convert('RGBA')
                width, height = image.size
                alpha = image.getchannel('A').tobytes()
                rows = [list(alpha[y * width:(y + 1) * width]) for y in range(height)]
                spans = spans_from_alpha(rows)
                assert spans, row['id']
                output.append({'id': row['id'], 'index': index, 'texture': row['texture'],
                               'width': width, 'height': height, 'source': origin,
                               'alpha_sha256': sha(alpha), 'alpha_values': sorted(set(alpha)),
                               'solid_pixel_count': sum(value != 0 for value in alpha), 'spans': spans})
    proof = {'schema': 1, 'kind': 'derived_alpha_outline_spans_only_no_external_artwork',
             'generator_source': {'version': 'Java 1.20.1', 'official_client_sha1': '0c3ec587af28e5a785c0b4a7b8a30f9a8f78f838',
                                  'class': 'net.minecraft.client.renderer.block.model.ItemModelGenerator (fkz)',
                                  'transparency': 'alpha == 0', 'span_merge': 'min/max per direction and pixel anchor across unique frames'},
             'catalog_sha256': sha(catalog_path.read_bytes()),
             'resource_policy': 'Existing referenced texture bytes remain external or unchanged. Static source sprites only; dynamic models, overrides and resource-pack alpha changes are not represented.',
             'items': output}
    FIXTURE.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    receipt = {'fixture_sha256': sha(FIXTURE.read_bytes()), 'item_count': len(output),
               'vanilla_extraction_receipt_sha256': sha(vanilla_path.read_bytes()),
               'cookery_addon_sha256': sha(args.cookery_addon.read_bytes()),
               'source_counts': {kind: sum(row['source']['kind'] == kind for row in output) for kind in sorted({row['source']['kind'] for row in output})},
               'copied_external_pngs': 0, 'unresolved_items': [], 'fixture': str(FIXTURE)}
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
