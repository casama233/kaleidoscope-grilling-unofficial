"""Cover inventory attribution without polluting plain names or item behaviour."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'projects/grilling/gameplay_core'
BASE = '1cf16f39f449ee5ce95190ef9088e575d133f928'  # Merged 2.8.45 runtime, including the prior repairs.
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
    counts = {}
    for folder, kind in [('items', 'item'), ('blocks', 'block')]:
        count = 0
        for path in sorted((PROJECT / 'behavior_pack' / folder).glob('*.json')):
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
    for locale, label in LABELS.items():
        path = PROJECT / 'resource_pack/texts' / (locale + '.lang')
        old = language(prior(path))
        current = language(path.read_bytes())
        assert all(current.get(k) == v for k, v in old.items()), 'Plain names/guide text changed'
        assert set(current) - set(old) == set(aliases), 'Unexpected localization override'
        for key, plain in aliases.items():
            assert current[key] == old[plain] + r'\n' + '§9§o' + label + '§r', key
            assert current[key].count(r'\n') == 1, 'Malformed tooltip newline'
    # All bottle states, existing stacks and block items resolve declaratively;
    # no inventory polling, scripted lore rewriting or host translations.
    for path in (PROJECT / 'behavior_pack/scripts').rglob('*.js'):
        if path.relative_to(PROJECT / 'behavior_pack').as_posix() in (
                'scripts/guide/payload.js', 'scripts/guide/publisher.js'):
            continue
        assert path.read_bytes() == prior(path), 'Runtime script changed: ' + str(path)
    print(json.dumps({'inventory_items': counts['item'], 'named_blocks': counts['block'],
                      'display_aliases': len(aliases), 'locales': list(LABELS),
                      'plain_names_preserved': True, 'runtime_behaviour_preserved': True,
                      'client_rendering_accepted': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
