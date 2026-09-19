"""Reconstruct the verified A1.12 asset workspace; never execute upstream code.
The seed is exact authored tooling, not a replacement for unimported review history.
"""
from __future__ import annotations
import argparse, base64, collections, hashlib, io, json, os, re, shutil, sys, tarfile, urllib.request, zipfile
from pathlib import Path, PurePosixPath

REPOSITORY = 'casama233/kaleidoscope-grilling-unofficial'
REPOSITORY_ID = '1377218440'
CAPSULE_SHA = '9cfdb2231505cea01540615a19cb0c6edb04a42f8cb34bb6ae0e9136c0d858ef'

def digest(entries):
    h = hashlib.sha256()
    for name, value in sorted(entries.items()):
        h.update(name.encode() + b'\0' + hashlib.sha256(value).digest())
    return h.hexdigest()

def blob(value):
    return hashlib.sha1(b'blob ' + str(len(value)).encode() + b'\0' + value).hexdigest()

def safe(name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError('Unsafe archive path: ' + name)
    return p

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def archive(group):
    repo, sha = group['repository'], group['commit']
    if repo not in ('breezeth-CN/KaleidoscopeGrilling', 'Arbousier1/KaleidoscopeGrilling') or not re.fullmatch('[0-9a-f]{40}', sha):
        raise ValueError('Unapproved upstream')
    url = f'https://codeload.github.com/{repo}/zip/{sha}'
    request = urllib.request.Request(url, headers={'User-Agent': 'Grilling-verified-assets/1'})
    with urllib.request.urlopen(request, timeout=120) as response:
        raw = response.read(150_000_001)
    if len(raw) > 150_000_000:
        raise ValueError('Upstream archive too large')
    z = zipfile.ZipFile(io.BytesIO(raw))
    prefix = z.namelist()[0].split('/')[0] + '/'
    return z, prefix

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=Path('.'))
    ap.add_argument('--offline-reference', type=Path, help='Local verification only; no network')
    args = ap.parse_args()
    root = args.root.resolve()
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        if os.environ.get('GITHUB_REPOSITORY') != REPOSITORY or os.environ.get('GITHUB_REPOSITORY_ID') != REPOSITORY_ID:
            raise RuntimeError('Wrong GitHub repository')
    guard = json.loads((root / '.repo-target.json').read_text())
    if guard['repository'] != REPOSITORY or str(guard['repository_id']) != REPOSITORY_ID:
        raise RuntimeError('Wrong repository guard')
    target = root / 'projects/grilling'
    if target.exists():
        raise RuntimeError('Target already exists; no overwrite is permitted')
    parts = root / 'migration/parts'
    if sorted(p.name for p in parts.glob('*.b64')) != [f'{i:02}.b64' for i in range(5)]:
        raise RuntimeError('Capsule is incomplete')
    encoded = ''.join(''.join((parts / f'{i:02}.b64').read_text().split()) for i in range(5))
    compressed = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(compressed).hexdigest() != CAPSULE_SHA:
        raise RuntimeError('Capsule checksum mismatch')
    with tarfile.open(fileobj=io.BytesIO(compressed), mode='r:xz') as tar:
        members = tar.getmembers()
        if len(members) != 26 or sum(m.size for m in members) > 2_000_000:
            raise RuntimeError('Unexpected capsule contents')
        for item in members:
            if not item.isfile():
                raise RuntimeError('Only regular files permitted')
            name = safe(item.name)
            dest = target.joinpath(*name.parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(tar.extractfile(item).read())
    selection = json.loads((target / 'config/source-fetch.json').read_text())
    source_entries, manifest_entries = {}, []
    opened = [] if args.offline_reference else [archive(g) for g in selection['groups']]
    try:
        for item in selection['files']:
            logical, index = item[:2]
            remote = item[2] if len(item) > 2 else logical
            safe(logical); safe(remote)
            group = selection['groups'][index]
            if args.offline_reference:
                value = (args.offline_reference / 'source_snapshots' / logical).read_bytes()
            else:
                z, prefix = opened[index]
                info = z.getinfo(prefix + remote)
                if info.file_size > 10_000_000:
                    raise RuntimeError('Unexpected source size')
                value = z.read(info)
            exception = selection['canonical_exceptions'].get(logical)
            if exception:
                value = exception['text'].encode('utf-8')
                entry = exception['metadata']
            else:
                entry = {
                    'path': logical,
                    'source_url': f"https://github.com/{group['repository']}/blob/{group['commit']}/{remote}",
                    'upstream_git_blob_sha1': blob(value), 'local_git_blob_sha1': blob(value),
                    'local_sha256': hashlib.sha256(value).hexdigest(),
                    'representation': 'binary-exact' if logical.endswith('.png') else 'raw-utf8-exact',
                    'upstream_byte_match': True, 'license': 'CC-BY-NC-SA-4.0'
                }
                entry.update(selection['canonical_exceptions']['_provenance'].get(logical, {}))
            source_entries[logical] = value
            manifest_entries.append(entry)
        if len(source_entries) != selection['source_count'] or digest(source_entries) != selection['source_set_sha256']:
            raise RuntimeError('Source set differs from delivered A1.12 baseline')
        for name, value in source_entries.items():
            dest = target / 'source_snapshots' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(value)
    finally:
        for z, _ in opened:
            z.close()
    write_json(target / 'source_manifest.json', {
        'commit': selection['groups'][0]['commit'],
        'retrieval_date': '2026-09-19', 'files': manifest_entries,
        'verification': 'Aggregate ordered path + SHA256 matches delivered A1.12; individual Git blobs recomputed',
        'baseline_archive_sha256': selection['baseline_archive_sha256']
    })
    sys.path.insert(0, str(target / 'tools'))
    import build_assets
    import audit_multiview as audit
    from render_thumbnail_rgba import render_rgba
    import numpy as np
    from PIL import Image
    report = build_assets.build()
    patterns = ('resource_pack/models/entity/kg_a1/*.geo.json', 'editor/generated/*.bbmodel', 'resource_pack/textures/kg_a1/*.png')
    outputs = {p.relative_to(target).as_posix(): p.read_bytes() for pattern in patterns for p in target.glob(pattern)}
    if len(outputs) != selection['output_count'] or digest(outputs) != selection['output_set_sha256']:
        raise RuntimeError('Rebuilt geometry/editor/atlas bytes differ from delivered baseline')
    specs = {x['name']: x for x in json.loads((target / 'config/asset_specs.json').read_text())['candidates']}
    surfaces = []
    for row in report['candidates']:
        a = audit.source_faces(row, specs[row['name']]); b = audit.bedrock_faces(row)
        equal = collections.Counter(map(audit.signature, a)) == collections.Counter(map(audit.signature, b))
        surfaces.append({'name': row['name'], 'faces': len(a), 'equal': equal})
        if not equal:
            raise RuntimeError('Directed surface or UV mismatch: ' + row['name'])
    records = {x['name']: x for x in report['candidates']}
    integration = target / 'integration/cookery106'
    payload = (integration / 'behavior_pack/scripts/payload.js').read_text()
    names = sorted(set(re.findall(r'textures/ui/kg_grilling/([a-z0-9_]+)', payload)))
    for name in names:
        faces = audit.bedrock_faces(records[name])
        frame = np.concatenate([f['points'] for f in faces]).tolist()
        image = render_rgba(faces, 'front_oblique', frame)
        box = image.getbbox()
        if box:
            image = image.crop((max(0, box[0]-4), max(0, box[1]-4), min(image.width, box[2]+4), min(image.height, box[3]+4)))
        image.thumbnail((112, 112), Image.Resampling.NEAREST)
        canvas = Image.new('RGBA', (128, 128))
        canvas.paste(image, ((128-image.width)//2, (128-image.height)//2))
        dest = integration / f'resource_pack/textures/ui/kg_grilling/{name}.png'
        dest.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(dest)
    for pack in ('behavior_pack', 'resource_pack'):
        shutil.copyfile(integration / 'resource_pack/textures/ui/kg_grilling/grill_legged_lit.png', integration / pack / 'pack_icon.png')
    icons = {p.relative_to(target).as_posix(): p.read_bytes() for p in integration.rglob('*.png')}
    if len(icons) != selection['guide_png_count'] or digest(icons) != selection['guide_png_set_sha256']:
        raise RuntimeError('Guide PNG bytes differ from delivered baseline')
    result = {
        'scope': 'A1.12 runtime/editor assets and minimum rebuilding tools, not all historical reports',
        'source_files': len(source_entries), 'source_set_sha256': digest(source_entries),
        'output_files': len(outputs), 'output_set_sha256': digest(outputs),
        'guide_pngs': len(icons), 'guide_png_set_sha256': digest(icons),
        'candidates': report['candidate_count'], 'directed_surface_checks': surfaces,
        'minecraft_tested': False, 'bridge_tested': False,
        'historical_png_comparisons_reexecuted': False,
        'read_only_upstream': True, 'cookery_original_bundle_included': False
    }
    write_json(target / 'reports/migration-verification.json', result)
    write_json(root / 'migration/result.json', {k: v for k, v in result.items() if k != 'directed_surface_checks'})
    print(json.dumps({k: v for k, v in result.items() if k != 'directed_surface_checks'}, indent=2))

if __name__ == '__main__':
    main()
