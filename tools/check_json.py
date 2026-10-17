"""Strict JSON validation, with one byte-pinned Mojang reference header."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path('development/gameplay_core/fixtures/bedrock-fluids-1.26.50.4')
REFERENCE = FIXTURE / 'resource_pack/textures/flipbook_textures.json'
REFERENCE_SHA256 = 'bc6e227e696002bcc39ce40bde6c4133a3687d08f732b89b054cd047c4fb54d2'


def load_json(path):
    path = Path(path)
    raw = path.read_bytes()
    if path.absolute() == ROOT / REFERENCE:
        if hashlib.sha256(raw).hexdigest() != REFERENCE_SHA256:
            raise ValueError('Pinned Mojang fixture bytes changed')
        source = json.loads((ROOT / FIXTURE / 'source-manifest.json').read_text(encoding='utf-8-sig'))
        identity = {'repository': 'Mojang/bedrock-samples',
                    'source_revision': '46ba6ea985fb5a92d79a9419198f10dda14c199d',
                    'minecraft_bedrock': '1.26.50.4'}
        if not isinstance(source, dict) or any(source.get(key) != value for key, value in identity.items()):
            raise ValueError('Pinned Mojang source identity changed')
        records = source.get('files', [])
        matches = [row for row in records if isinstance(row, dict) and row.get('path') == 'resource_pack/textures/flipbook_textures.json'] if isinstance(records, list) else []
        if len(matches) != 1 or matches[0].get('sha256') != REFERENCE_SHA256 or matches[0].get('git_blob') != '9d3808a13b96ef1ca3c46e5ce8b17ca80654ddfe':
            raise ValueError('Pinned Mojang fixture record changed')
        # Preserve the official bytes: this exact reference has one initial
        # line comment. Its remaining content must still be strict JSON.
        header, newline, body = raw.partition(b'\n')
        if not newline or not header.startswith(b'//'):
            raise ValueError('Pinned Mojang reference header changed')
        raw = body
    return json.loads(raw.decode('utf-8-sig'))


def main(names):
    errors = []
    for name in names:
        try:
            load_json(name)
        except (ValueError, OSError) as error:
            errors.append(f'{name}: {error}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Validated {len(names)} JSON files; no files rewritten')


if __name__ == '__main__':
    main(sys.argv[1:])
