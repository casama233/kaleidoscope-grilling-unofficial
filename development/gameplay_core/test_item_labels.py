"""Cover inventory attribution without polluting plain names or item behaviour."""
from pathlib import Path
import json
import subprocess
from copy import deepcopy
import re
PROFILE_SOURCE=json.loads(re.search(r"PROFILE_BY_ITEM=Object.freeze\((\{.*?\})\)",subprocess.check_output(["git","show","d795c0e:projects/grilling/gameplay_core/behavior_pack/scripts/data.js"],cwd=Path(__file__).resolve().parents[2]).decode()).group(1))
ALL_EATING_ITEMS={k.split(':')[1] for k in PROFILE_SOURCE}|{'secret_skewer'}
RANDOM_ITEMS={k.split(":")[1] for k,v in PROFILE_SOURCE.items() if v=="THREE_RANDOM"}|{"secret_skewer"}
from test_bottle_item_offhand_sources import BOTTLES, check_authoring

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


def current_behavior_expectation(before, kind, stem, version):
    expected = deepcopy(before)
    if version >= (2, 8, 62) and kind == 'item' and stem in RANDOM_ITEMS:
        c=expected['minecraft:item']['components']
        c['minecraft:use_modifiers']['use_duration']=5.0
        tags=c.setdefault('minecraft:tags',{'tags':[]})['tags']
        tag='kaleidoscope_grilling:food_'+stem
        if tag not in tags:tags.append(tag)
    if version >= (2, 8, 67) and kind == 'item' and stem in ALL_EATING_ITEMS:
        tags=expected['minecraft:item']['components'].setdefault('minecraft:tags',{'tags':[]})['tags']
        tag='kaleidoscope_grilling:food_'+stem
        if tag not in tags:tags.append(tag)
    if version >= (2, 8, 61) and kind == 'item' and stem in BOTTLES:
        expected['minecraft:item']['components']['minecraft:allow_off_hand'] = True
    if version >= (2, 8, 71) and kind == 'item' and stem in {
            f'special_seasoning_r{r}_v{v}' for r in range(1, 9) for v in range(8)}:
        expected['minecraft:item']['components']['minecraft:icon'] = {'textures': {'default': stem}}
    if version >= (2,8,68) and kind=='block' and stem=='pepper_leaves':
        expected['minecraft:block']['components']['minecraft:tick']={'interval_range':[5,5],'looping':True}
    return expected


def main():
    aliases = {}
    version = tuple(json.loads((PROJECT / 'behavior_pack/manifest.json').read_bytes())['header']['version'])
    counts = {}
    bottle_eligibility = set()
    for folder, kind in [('items', 'item'), ('blocks', 'block')]:
        count = 0
        for path in sorted((PROJECT / 'behavior_pack' / folder).glob('*.json')):
            if kind == 'item' and path.stem.endswith('_native_plain'):
                assert version >= (2,8,67) and path.stem.removesuffix('_native_plain') in ALL_EATING_ITEMS
                plain=json.loads(path.read_bytes())['minecraft:item']
                expected=json.loads(path.with_name(path.name.replace('_native_plain','')).read_bytes())['minecraft:item']
                expected['description']['identifier']+='_native_plain';expected['description'].pop('menu_category',None)
                expected['components']['minecraft:use_modifiers']['use_duration']=1.25
                expected['components']['minecraft:use_animation']={'value':'eat'}
                assert plain==expected,path
                continue
            if kind == 'item' and path.stem.endswith('_java_three_alt'):
                assert version >= (2, 8, 62) and path.stem.removesuffix('_java_three_alt') in RANDOM_ITEMS
                alt=json.loads(path.read_bytes())['minecraft:item']
                base=json.loads(path.with_name(path.name.replace('_java_three_alt','')).read_bytes())['minecraft:item']
                assert alt['components']['minecraft:display_name']==base['components']['minecraft:display_name'],path
                assert 'menu_category' not in alt['description'],path
                continue
            if path.name == 'pepper_worldgen_seed.json':
                assert folder == 'blocks' and version >= (2, 8, 60)
                seed = json.loads(path.read_bytes())['minecraft:block']
                assert seed['description'] == {'identifier':'kaleidoscope_grilling:pepper_worldgen_seed'}
                assert seed['components']['minecraft:display_name'] == 'kaleidoscope_grilling.display.block.pepper_log'
                assert not (PROJECT / 'behavior_pack/items/pepper_worldgen_seed.json').exists()
                # This later hidden worldgen carrier reuses an existing label;
                # it is not part of the historical label-only release count.
                continue
            proxy = re.fullmatch(r'(partial|pending)_seasoning_f([1-8])', path.stem) if kind == 'item' else None
            if proxy:
                assert version >= (2,8,71)
                base = 'empty_seasoning_bottle' if proxy.group(1) == 'partial' else 'pending_seasoning'
                expected = json.loads(path.with_name(base+'.json').read_bytes())
                expected['minecraft:item']['description'].update(identifier='kaleidoscope_grilling:'+path.stem,menu_category={'category':'none'})
                expected['minecraft:item']['components']['minecraft:icon']['textures']['default']=path.stem
                assert json.loads(path.read_bytes()) == expected, path
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
            # Keep the historical label-only release fully immutable. Its
            # item/block gate still allows no non-display differences at all.
            historical = json.loads(subprocess.check_output(['git', 'show', LABEL_BASE + ':' + path.relative_to(ROOT).as_posix()], cwd=ROOT))
            historical['minecraft:' + kind]['components']['minecraft:display_name'] = old
            assert historical == before, 'Historical label release changed non-display behaviour: ' + str(path)
            expected = current_behavior_expectation(before, kind, path.stem, version)
            if version >= (2, 8, 61) and kind == 'item' and path.stem in BOTTLES:
                assert after['minecraft:item']['components']['minecraft:allow_off_hand'] is True, path
                bottle_eligibility.add(path.stem)
            assert after == expected, 'Non-display item/block behaviour changed: ' + str(path)
            aliases[key] = value
            count += 1
        counts[kind] = count
    assert counts == {'item': 156, 'block': 18}, counts
    if version >= (2, 8, 61):
        assert bottle_eligibility == BOTTLES, 'Missing/unexpected bottle eligibility route'
        assert check_authoring() == 67
    version = tuple(json.loads((PROJECT / 'behavior_pack/manifest.json').read_bytes())['header']['version'])
    public_keys = {'senluo.public.projection.v1'} if version >= (2, 8, 49) else set()
    for locale, label in LABELS.items():
        path = PROJECT / 'resource_pack/texts' / (locale + '.lang')
        old = language(prior(path))
        current = language(path.read_bytes())
        assert all(current.get(k) == v for k, v in old.items()), 'Plain names/guide text changed'
        config_keys=set(['guide.kg.body.kaleidoscope_grilling:skewer_plate.5', 'guide.kg.body.kaleidoscope_grilling:special_seasoning.8', 'guide.kg.body.kaleidoscope_grilling:grill.8', 'message.kaleidoscope_grilling.cookery_integration_disabled']) if version >= (2,8,67) else set()
        assert set(current) - set(old) == set(aliases) | public_keys | config_keys, 'Unexpected localization override'
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
