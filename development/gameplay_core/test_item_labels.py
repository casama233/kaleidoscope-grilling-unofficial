"""Cover inventory attribution without polluting plain names or item behaviour."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'projects/grilling/gameplay_core'
BASE='1cf16f39f449ee5ce95190ef9088e575d133f928'  # Merged 2.8.45 runtime, including the prior repairs.
LABEL_BASE='49159e9d4dc9a88ad59dfda618146c0d7a3b9fc0'
LABELS = {'en_US': 'Kaleidoscope Grilling', 'zh_CN': '森罗物语烟火',
          'zh_TW': '森羅物語煙火'}


def prior(path):
    return subprocess.check_output(['git', 'show', BASE + ':' +
                                   path.relative_to(ROOT).as_posix()], cwd=ROOT)


def language(data):
    rows = [line.split('=', 1) for line in data.decode('utf-8-sig').splitlines()
            if '=' in line and not line.startswith('#')]
    assert len(rows) == len(dict(rows)), 'Duplicate translation key'
    return dict(rows)


def main():
    aliases = {}
    version = tuple(json.loads((PROJECT / 'behavior_pack/manifest.json').read_bytes())['header']['version'])
    counts = {}
    for folder, kind in [('items', 'item'), ('blocks', 'block')]:
        count = 0
        for path in sorted((PROJECT / 'behavior_pack' / folder).glob('*.json')):
            if path.name == 'pepper_worldgen_seed.json':
                assert folder == 'blocks' and version >= (2, 8, 60)
                seed = json.loads(path.read_bytes())['minecraft:block']
                assert seed['description'] == {'identifier':'kaleidoscope_grilling:pepper_worldgen_seed'}
                assert seed['components']['minecraft:display_name'] == 'kaleidoscope_grilling.display.block.pepper_log'
                assert not (PROJECT / 'behavior_pack/items/pepper_worldgen_seed.json').exists()
                # This later hidden worldgen carrier reuses an existing label;
                # it is not part of the historical label-only release count.
                continue
            before = json.loads(prior(path))
            after = json.loads(path.read_bytes())
            old = before['minecraft:' + kind]['components'].get('minecraft:display_name')
            if old is None:
                assert after == before, path
                continue
            value = old['value'] if isinstance(old, dict) else old
            key = ('kaleidoscope_grilling.display.' +
                   ('item' if value.startswith('item.') else 'block') + '.' +
                   value.split(':', 1)[1].removesuffix('.name'))
            display = after['minecraft:' + kind]['components']['minecraft:display_name']
            assert (display['value'] if isinstance(display, dict) else display) == key, path
            after['minecraft:' + kind]['components']['minecraft:display_name'] = old
            assert after == before, 'Non-display item/block behaviour changed: ' + str(path)
            aliases[key] = value
            count += 1
        counts[kind] = count
    assert counts == {'item': 156, 'block': 18}, counts
    version = tuple(json.loads((PROJECT / 'behavior_pack/manifest.json').read_bytes())['header']['version'])
    public_keys = {'senluo.public.projection.v1'} if version >= (2, 8, 49) else set()
    for locale, label in LABELS.items():
        path = PROJECT / 'resource_pack/texts' / (locale + '.lang')
        old = language(prior(path))
        current = language(path.read_bytes())
        assert all(current.get(k) == v for k, v in old.items()), 'Plain names/guide text changed'
        assert set(current) - set(old) == set(aliases) | public_keys, 'Unexpected localization override'
        assert all(current[k] == '' for k in public_keys), 'Public metadata must remain invisible'
        released = language(subprocess.check_output(['git','show',LABEL_BASE+':'+path.relative_to(ROOT).as_posix()],cwd=ROOT))
        assert set(released) - set(old) == set(aliases), 'Historical label-only release drift'
        for key, plain in aliases.items():
            assert current[key] == old[plain] + r'\n' + '§9§o' + label + '§r', key
            assert current[key].count(r'\n') == 1, 'Malformed tooltip newline'
    # All bottle states, existing stacks and block items resolve declaratively;
    # no inventory polling, scripted lore rewriting or host translations.
    # Check the historical label-only release itself. Later releases may add
    # scripts, which did not exist at LABEL_BASE and must not be queried there.
    released_paths = subprocess.check_output([
        'git', 'ls-tree', '-r', '--name-only', LABEL_BASE, '--',
        'projects/grilling/gameplay_core/behavior_pack/scripts',
    ], cwd=ROOT, text=True).splitlines()
    for relative in released_paths:
        path = ROOT / relative
        if path.suffix != '.js':
            continue
        if path.relative_to(PROJECT / 'behavior_pack').as_posix() in (
                'scripts/guide/payload.js', 'scripts/guide/publisher.js'):
            continue
        released = subprocess.check_output(['git', 'show', LABEL_BASE + ':' + path.relative_to(ROOT).as_posix()], cwd=ROOT)
        assert released == prior(path), 'Label release changed runtime script: ' + str(path)
    print(json.dumps({'inventory_items': counts['item'], 'named_blocks': counts['block'],
                      'display_aliases': len(aliases), 'locales': list(LABELS),
                      'plain_names_preserved': True, 'label_release_runtime_behaviour_preserved': True,
                      'client_rendering_accepted': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
