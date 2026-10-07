"""Review default generated-item particle samples from both official Java loaders.

Read Git objects, not Bedrock artwork or arbitrary item-name texture guesses.
Only single-layer minecraft:item/generated models with identical derived palettes
on both maintained loaders qualify. Missing models retain their recorded scope.
This cannot certify dynamic item tint/resource overrides or native rendering.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import subprocess

from PIL import Image
from secret_food_palette import sample_grid

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / 'development/gameplay_core/fixtures/secret-food-palettes.json'
PROOF = ROOT / 'development/gameplay_core/fixtures/java-cookery-palette-160/source.json'
PREFIXES = ('src/generated/resources/assets/', 'src/main/resources/assets/')
REPOSITORY = 'KaleidoscopeMods/KaleidoscopeCookery'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def resolve(repo, commit, paths, identifier):
    namespace, name = identifier.split(':', 1)
    candidates = [prefix + namespace + '/models/item/' + name + '.json'
                  for prefix in PREFIXES
                  if prefix + namespace + '/models/item/' + name + '.json' in paths]
    if len(candidates) != 1:
        return None
    model_path = candidates[0]
    model_raw = git(repo, 'show', commit + ':' + model_path)
    model = json.loads(model_raw)
    if model.get('parent') != 'minecraft:item/generated' or set(model.get('textures', {})) != {'layer0'}:
        return None
    sprite = model['textures']['layer0']
    texture_ns, texture = sprite.split(':', 1)
    textures = [prefix + texture_ns + '/textures/' + texture + '.png'
                for prefix in PREFIXES
                if prefix + texture_ns + '/textures/' + texture + '.png' in paths]
    if len(textures) != 1:
        return None
    texture_path = textures[0]
    raw = git(repo, 'show', commit + ':' + texture_path)
    image = Image.open(io.BytesIO(raw)).convert('RGBA')
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Not a source PNG: ' + texture_path)
    return {
        'model_path': model_path,
        'model_sha256': hashlib.sha256(model_raw).hexdigest(),
        'model_git_blob': git(repo, 'rev-parse', commit + ':' + model_path).decode().strip(),
        'particle_sprite': sprite,
        'texture_path': texture_path,
        'texture_sha256': hashlib.sha256(raw).hexdigest(),
        'texture_git_blob': git(repo, 'rev-parse', commit + ':' + texture_path).decode().strip(),
        'palette': sample_grid(image),
        'raw': raw,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--forge-commit', required=True)
    parser.add_argument('--neoforge-commit', required=True)
    args = parser.parse_args()
    remote = git(args.source, 'remote', 'get-url', 'origin').decode().strip().removesuffix('.git')
    assert remote == 'https://github.com/' + REPOSITORY, 'Only reviewed official Java source'
    commits = {'Forge1.20.1': args.forge_commit, 'NeoForge1.21.1': args.neoforge_commit}
    paths = {}
    for loader, commit in commits.items():
        assert git(args.source, 'rev-parse', commit + '^{commit}').decode().strip() == commit
        paths[loader] = set(git(args.source, 'ls-tree', '-r', '--name-only', commit).decode().splitlines())
    proof = {'schema': 1, 'repository': REPOSITORY, 'commits': commits,
             'license': 'CC BY-NC-SA 4.0',
             'scope': 'Default single-layer generated particle source; no dynamic tint/resource override or client acceptance',
             'items': [], 'unresolved': [], 'changed_palettes': []}
    samples = json.loads(SAMPLES.read_text())
    for row in samples['items']:
        if not row['id'].startswith('kaleidoscope_cookery:'):
            continue
        resolved = {loader: resolve(args.source, commit, paths[loader], row['id'])
                    for loader, commit in commits.items()}
        if any(value is None for value in resolved.values()):
            proof['unresolved'].append(row['id'])
            continue
        first, second = resolved.values()
        # Original encodings and dimensions can differ across loaders. The
        # exported tint needs equality of the actual Java sampling result;
        # keep each distinct source image's provenance instead of conflating it.
        assert first['palette'] == second['palette'], 'Loader-specific palette needs explicit adaptation: ' + row['id']
        if row['palette'] != first['palette']:
            proof['changed_palettes'].append(row['id'])
            # Retain only the changed public sprite as an independent regression input.
            fixture = PROOF.parent / 'changed' / (row['id'].split(':', 1)[1] + '.png')
            fixture.parent.mkdir(parents=True, exist_ok=True)
            fixture.write_bytes(first['raw'])
        row['palette'] = first['palette']
        source = {loader: {k: v for k, v in value.items() if k not in ('raw', 'palette')}
                  for loader, value in resolved.items()}
        row['source'] = {'kind': 'pinned_java_cookery_generated_particle_sprite',
                         'repository': REPOSITORY, 'commits': commits, 'loaders': source,
                         'static_default_tint': -1, 'java_particle_parity': False,
                         'static_particle_source_reviewed': True, 'native_renderer_accepted': False}
        proof['items'].append({'id': row['id'], 'index': row['index'], 'palette': row['palette'], 'sources': source})
    assert proof['items'], 'No qualifying original sources'
    PROOF.parent.mkdir(parents=True, exist_ok=True)
    PROOF.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    SAMPLES.write_text(json.dumps(samples, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'reviewed': len(proof['items']), 'changed': proof['changed_palettes'],
                      'unresolved': len(proof['unresolved']), 'client': False}))


if __name__ == '__main__':
    main()
