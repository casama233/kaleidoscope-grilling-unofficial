"""Build only reviewed original teleport samples and owned category aliases.

Offline by default. --cache uses the selected, publisher-verified source assets;
never copy a game JAR or replace author packs. Six existing feedback events stay
unchanged. Source and rendered-client acceptance remain distinct.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'development/gameplay_core/fixtures/java-projectile-dodge-audio-160.json'
RP = ROOT / 'projects/grilling/gameplay_core/resource_pack'
CORE = ROOT / 'projects/grilling/gameplay_core/behavior_pack/scripts/projectile_dodge_audio_core.js'


def event_definitions(fixture):
    sources = list(fixture['loader_sources'].values())
    assert len(sources) == 2
    assert sources[0]['original_event'] == sources[1]['original_event'], 'Review cross-loader event differences'
    assert sources[0]['samples'] == sources[1]['samples'], 'Review cross-loader sample differences'
    entries = []
    for row, sample in zip(sources[0]['original_event']['sounds'], sources[0]['samples'], strict=True):
        entry = {'name': row} if isinstance(row, str) else dict(row)
        assert entry.get('type', 'file') == 'file'
        assert entry['name'] + '.ogg' == sample['author_asset'].removeprefix('minecraft/sounds/')
        entries.append({**entry, 'name': sample['output'].removesuffix('.ogg'), 'stream': False})
    aliases = {
        fixture['origin_sound_id']: {'category': 'player', 'sounds': entries, 'max_distance': 16}
    }
    for category in ('neutral', 'hostile'):
        aliases[fixture['destination_sound_ids'][category]] = {
            'category': category, 'sounds': entries, 'max_distance': 16
        }
    # Use current Cookery sample paths, with a Grilling-owned PLAYERS alias.
    # No duplicated author audio and no author RP replacement are required.
    host = fixture['flatulence']['host_definition']
    assert host['category'] == 'neutral'
    assert fixture['flatulence']['original_java_category'] == 'PLAYERS'
    assert fixture['flatulence']['original_java_fixed_range'] == 16
    aliases[fixture['flatulence']['sound_id']] = {
        'category': 'player', 'sounds': host['sounds'],
        'max_distance': fixture['flatulence']['original_java_fixed_range']
    }
    return aliases


def build(check=False, cache=None):
    fixture = json.loads(FIXTURE.read_text())
    definitions_path = RP / 'sounds/sound_definitions.json'
    definitions = json.loads(definitions_path.read_text())
    expected_aliases = event_definitions(fixture)
    samples = []
    for sample in next(iter(fixture['loader_sources'].values()))['samples']:
        target = RP / sample['output']
        source = Path(cache) / sample['author_asset'] if cache is not None else target
        raw = source.read_bytes()
        assert len(raw) == sample['size'] and hashlib.sha1(raw).hexdigest() == sample['publisher_sha1'], 'Wrong original sample: ' + sample['author_asset']
        samples.append((target, raw))
    for alias, expected in expected_aliases.items():
        if check:
            assert definitions['sound_definitions'].get(alias) == expected, 'Stale selected audio alias: ' + alias
        else:
            definitions['sound_definitions'][alias] = expected
    if not check:
        definitions_path.write_text(json.dumps(definitions, indent=2) + '\n')
    for target, raw in samples:
        if check:
            assert target.read_bytes() == raw, 'Stale selected audio bytes'
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    by_type = {key: fixture['destination_sound_ids'][row['bedrock_category']]
               for key, row in fixture['reviewed_actor_categories'].items()}
    core = (
        '// Generated from reviewed public source; unknown actor categories use an explicit neutral adaptation.\n'
        + 'export const TELEPORT_ORIGIN_SOUND_ID=' + json.dumps(fixture['origin_sound_id']) + ';\n'
        + 'export const FLATULENCE_SOUND_ID=' + json.dumps(fixture['flatulence']['sound_id']) + ';\n'
        + 'const REVIEWED_DESTINATION_SOUNDS=Object.freeze(' + json.dumps(by_type, sort_keys=True, separators=(',', ':')) + ');\n'
        + 'export function teleportDestinationAudio(typeId){\n'
        + " const known=Object.hasOwn(REVIEWED_DESTINATION_SOUNDS,typeId);\n"
        + ' return {soundId:known?REVIEWED_DESTINATION_SOUNDS[typeId]:' + json.dumps(fixture['destination_sound_ids']['neutral']) + ',categoryReviewed:known};\n}\n'
    )
    if check:
        assert CORE.read_text() == core, 'Stale reviewed actor category adapter'
    else:
        CORE.write_text(core)
    print(('Checked' if check else 'Built') + ' two original teleport samples and selected category aliases; client=false.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--cache', type=Path)
    args = parser.parse_args()
    build(args.check, args.cache)
