"""Verify actual Dash output, separately from Minecraft or editor UI acceptance."""
from pathlib import Path
import hashlib, json

root = Path(__file__).resolve().parents[1]
project = root / 'projects/grilling'
checks = []
for rel in ('resource_pack', 'integration/cookery106/resource_pack', 'integration/cookery106/behavior_pack'):
    source = project / rel
    manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8-sig'))
    build_root = source.parent / 'builds/dist'
    matches = []
    for path in build_root.rglob('manifest.json'):
        candidate = json.loads(path.read_text(encoding='utf-8-sig'))
        if candidate.get('header', {}).get('uuid') == manifest['header']['uuid']:
            matches.append(path.parent)
    if len(matches) != 1:
        raise RuntimeError(f'{rel}: expected one compiled pack, found {len(matches)}')
    compiled = matches[0]
    checked = 0
    for path in source.rglob('*'):
        if not path.is_file() or path.suffix not in ('.json', '.png', '.js'):
            continue
        dest = compiled / path.relative_to(source)
        if not dest.is_file():
            raise RuntimeError('Dash omitted required file: ' + str(path))
        if path.suffix == '.json':
            equal = json.loads(path.read_text(encoding='utf-8-sig')) == json.loads(dest.read_text(encoding='utf-8-sig'))
        else:
            equal = path.read_bytes() == dest.read_bytes()
        if not equal:
            raise RuntimeError('Unexpected Dash transformation: ' + str(path))
        checked += 1
    checks.append({'pack': rel, 'uuid': manifest['header']['uuid'], 'checked_files': checked, 'matches_source': True})
result = {'compiler': 'bridge. standalone Dash v1.2.0', 'packs': checks,
          'editor_ui_tested': False, 'minecraft_tested': False,
          'scope': 'Real CLI compilation; JSON structure and PNG/JS bytes compared with source'}
print(json.dumps(result, ensure_ascii=False, indent=2))
