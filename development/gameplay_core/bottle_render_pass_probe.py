"""Generate RP-only native diagnostics; never write canonical RP or gameplay.

No matrix projection can certify these experiments. Copy one output overlay to
a private exact-source RP, restart its client, and compare actual rendering.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image
import a2861_bottle_held_visual_assets as held

CASES = ('shell-first', 'shell-only', 'rebuild-true', 'single-rc-two-layer', 'one-rc-audit')


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def run(source, out, case):
    source, out = source.resolve(), out.resolve()
    if out.is_relative_to(source) or source.is_relative_to(out):
        raise ValueError('Probe output must be separate from source RP')
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh output directory for each case')
    out.mkdir(parents=True, exist_ok=True)
    outputs, inputs = {}, {}

    def read(relative):
        path = source / relative
        inputs[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        return load(path)

    def write(relative, doc):
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8', newline='\n')
        outputs[relative] = hashlib.sha256(path.read_bytes()).hexdigest()

    attachables = {}
    for path in sorted((source / 'attachables').glob('*.json')):
        doc = load(path)
        d = doc['minecraft:attachable']['description']
        if d.get('animations', {}).get('fp_right') == 'animation.kg_a286.bottle_fp_right':
            relative = path.relative_to(source).as_posix()
            attachables[relative] = read(relative)

    if case == 'one-rc-audit':
        assert len(attachables) == 67
        for doc in attachables.values():
            d = doc['minecraft:attachable']['description']
            assert len(d['render_controllers']) == 1
            assert set(d['geometry']) == {'default'}
            assert set(d['textures']) == {'default'}
            assert d['materials']['default'] == 'entity_alphablend'
            assert d['materials']['contents'] == 'entity'
        controllers = read('render_controllers/bottle_held_contents.render_controllers.json')['render_controllers']
        used = {doc['minecraft:attachable']['description']['render_controllers'][0]
                for doc in attachables.values()}
        assert used == set(controllers) == {'controller.render.kg_bottle_held.dynamic',
                                            'controller.render.kg_bottle_held.fixed'}
        for rc in controllers.values():
            assert rc['geometry'] == 'Geometry.default'
            assert rc['textures'] == ['Texture.default']
            assert 'uv_anim' not in rc
        g = read('models/entity/bottle_held_contents.geo.json')['minecraft:geometry']
        assert len(g) == 65 and len(g[0]['bones']) == 146
    elif case in ('shell-first', 'shell-only'):
        for relative, doc in attachables.items():
            d = doc['minecraft:attachable']['description']
            rc = d['render_controllers']
            if len(rc) == 1:
                raise ValueError('Order probes require the archived multipass RP; use one-rc-audit for the expanded RP')
            assert isinstance(rc[-1], str) and rc[-1] in (
                'controller.render.kg_bottle_held.shell',
                'controller.render.kg_a2733.seasoning_bottle_hand')
            d['render_controllers'] = [rc[-1]] + (rc[:-1] if case == 'shell-first' else [])
            write(relative, doc)
    elif case == 'rebuild-true':
        used = {next(iter(rc)) if isinstance(rc, dict) else rc
                for doc in attachables.values()
                for rc in doc['minecraft:attachable']['description']['render_controllers']}
        seen = set()
        for path in sorted((source / 'render_controllers').glob('*.json')):
            doc = load(path)
            changed = used.intersection(doc.get('render_controllers', {}))
            if changed:
                relative = path.relative_to(source).as_posix()
                inputs[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
                for name in changed:
                    doc['render_controllers'][name]['rebuild_animation_matrices'] = True
                seen.update(changed)
                write(relative, doc)
        assert seen == used, used - seen
    else:
        # Limited native test: EMPTY/PENDING first two ingredient layers only,
        # plus the QA default SPECIAL finished8. Variant routes are not changed.
        combined = read('models/entity/bottle_held_contents.geo.json')['minecraft:geometry'][0]
        assert combined['description']['identifier'] == 'geometry.kg_bottle_held.combined'
        bones = {bone['name']: bone for bone in combined['bones']}
        texture_path = source / 'textures/blocks/seasoning_bottle.png'
        inputs['textures/blocks/seasoning_bottle.png'] = hashlib.sha256(texture_path.read_bytes()).hexdigest()
        with Image.open(texture_path) as im:
            original = im.convert('RGBA')
        assert original.size == (32, 32)
        atlas = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        atlas.paste(original, (0, 0))
        # Use the existing generated texture arrays as the exact palette contract.
        rc_source = read('render_controllers/bottle_held_contents.render_controllers.json')['render_controllers']
        palette_locations, pixels = {}, {}
        free_tiles = [(x * 16, y * 16) for y in range(8) for x in range(8)
                      if not (x < 2 and y < 2)]
        partial = deepcopy(combined)
        partial['description'].update(identifier='geometry.kg_bottle_probe.partial2',
                                      texture_width=128, texture_height=128)
        partial['bones'] = [deepcopy(bones['grip']), deepcopy(bones['shell'])]
        visibility = [{'*': False}, {'grip': True}, {'shell': True}]
        for tint in range(4):
            choices = rc_source[f'controller.render.kg_bottle_held.pending_{tint}']['arrays']['textures']['Array.colors']
            assert len(choices) == 10
            for value in range(1, 10):
                alias = choices[value].removeprefix('Texture.')
                relative = f'textures/a2770_placed/{alias}.png'
                png = source / relative
                inputs[relative] = hashlib.sha256(png.read_bytes()).hexdigest()
                with Image.open(png) as im:
                    tile = im.convert('RGBA')
                samples = tile.getcolors()
                assert tile.size == (16, 16) and samples and len(samples) == 1
                assert samples[0][0] == 256 and samples[0][1][3] == 255
                if alias not in palette_locations:
                    location = free_tiles.pop(0)
                    palette_locations[alias] = location
                    pixels[alias] = samples[0][1]
                    atlas.paste(tile, location)
                x, y = palette_locations[alias]
                bone = deepcopy(bones[f'pending_{tint}'])
                bone['name'] = f'probe_half_{tint}_color_{value}'
                for cube in bone['cubes']:
                    # Static, inset UVs sample a uniform region with a gutter.
                    # No per-pass UV animation or runtime atlas offset is used.
                    cube['uv'] = {face: {'uv': [x + 4, y + 4], 'uv_size': [8, 8]}
                                  for face in cube['uv']}
                partial['bones'].append(bone)
                visibility.append({bone['name']: f'v.kg_bottle_layer_{tint // 2} == {value}'})

        assert atlas.crop((0, 0, 32, 32)).tobytes() == original.tobytes()
        for alias, (x, y) in palette_locations.items():
            assert atlas.crop((x, y, x + 16, y + 16)).getcolors() == [(256, pixels[alias])]
        atlas_relative = 'textures/bottle_probe/shell_palette.png'
        atlas_path = out / atlas_relative
        atlas_path.parent.mkdir(parents=True, exist_ok=True)
        atlas.save(atlas_path)
        outputs[atlas_relative] = hashlib.sha256(atlas_path.read_bytes()).hexdigest()
        geometries = [partial]
        controllers = {'controller.render.kg_bottle_probe.partial2': {
            'geometry': 'Geometry.default',
            'materials': [{'*': 'Material.contents'}, {'shell': 'Material.default'}],
            'textures': ['Texture.probe_atlas'], 'part_visibility': visibility}}
        for item in ('empty_seasoning_bottle', 'pending_seasoning'):
            relative = f'attachables/{item}.attachable.json'
            doc = read(relative)
            d = doc['minecraft:attachable']['description']
            d['geometry'] = {'default': 'geometry.kg_bottle_probe.partial2'}
            d['textures']['probe_atlas'] = atlas_relative.removesuffix('.png')
            d['materials']['contents'] = 'entity'
            d['render_controllers'] = ['controller.render.kg_bottle_probe.partial2']
            write(relative, doc)

        # The default QA finished8 uses the original shell and contents texture.
        relative = 'attachables/special_seasoning.attachable.json'
        doc = read(relative)
        d = doc['minecraft:attachable']['description']
        refs = set(d['geometry'].values())
        index = {}
        for path in sorted((source / 'models').rglob('*.geo.json')):
            for g in load(path)['minecraft:geometry']:
                if g['description']['identifier'] in refs:
                    inputs[path.relative_to(source).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
                    index[g['description']['identifier']] = g
        assert set(index) == refs
        shell, fill = index[d['geometry']['default']], index[d['geometry']['contents']]
        assert all(g['description']['texture_width'] == 32 and g['description']['texture_height'] == 32
                   for g in (shell, fill))
        special = deepcopy(shell)
        special['description'].update(identifier='geometry.kg_bottle_probe.finished8',
                                      texture_width=128, texture_height=128)
        special['bones'] = [deepcopy(bones['grip'])]
        for name, geometry in (('shell', shell), ('contents', fill)):
            assert len(geometry['bones']) == 1
            bone = deepcopy(geometry['bones'][0])
            bone.update(name=name, parent='grip', pivot=[0, 24, 0])
            bone.pop('binding', None)
            special['bones'].append(bone)
        geometries.append(special)
        d['geometry'] = {'default': 'geometry.kg_bottle_probe.finished8'}
        d['textures']['probe_atlas'] = atlas_relative.removesuffix('.png')
        d['materials']['contents'] = 'entity'
        d['render_controllers'] = ['controller.render.kg_bottle_probe.finished8']
        controllers['controller.render.kg_bottle_probe.finished8'] = {
            'geometry': 'Geometry.default', 'textures': ['Texture.probe_atlas'],
            'materials': [{'*': 'Material.contents'}, {'shell': 'Material.default'}]}
        write(relative, doc)
        write('models/entity/bottle_probe.geo.json', {'format_version': '1.16.0', 'minecraft:geometry': geometries})
        write('render_controllers/bottle_probe.render_controllers.json',
              {'format_version': '1.8.0', 'render_controllers': controllers})

    # All poses, animation dispatch/pre_animation and item identities are exact
    # source copies. Record equality without pretending it proves native output.
    for relative in outputs:
        if relative.startswith('attachables/'):
            before = load(source / relative)['minecraft:attachable']['description']
            after = load(out / relative)['minecraft:attachable']['description']
            for key in ('identifier', 'animations', 'scripts'):
                assert before[key] == after[key], (relative, key)
    for relative, digest in inputs.items():
        assert hashlib.sha256((source / relative).read_bytes()).hexdigest() == digest
    receipt = {'case': case, 'scope': 'private RP overlay; not a production candidate',
               'inputs_sha256': inputs, 'outputs_sha256': outputs,
               'native_tested': False, 'source_unchanged': True,
               'single_rc_partial_layer_limit': 2 if case == 'single-rc-two-layer' else None}
    (out / 'probe-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'case': case, 'overlay_files': len(outputs), 'native_tested': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-rp', type=Path, default=held.RP)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=CASES, required=True)
    args = parser.parse_args()
    run(args.source_rp, args.output, args.case)
