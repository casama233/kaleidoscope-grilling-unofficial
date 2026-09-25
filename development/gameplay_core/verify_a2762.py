from __future__ import annotations

from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'projects/grilling/gameplay_core'
BP = PROJECT / 'behavior_pack'
RP = PROJECT / 'resource_pack'
DEV = Path(__file__).resolve().parent
VERSION = [2, 7, 62]

def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--compiled', action='store_true')
    args = parser.parse_args()

    for path in PROJECT.rglob('*.json'):
        load(path)

    bp = load(BP / 'manifest.json')
    rp = load(RP / 'manifest.json')
    assert bp['header']['version'] == VERSION
    assert rp['header']['version'] == VERSION
    assert bp['header']['uuid'] == 'c68005c5-23ff-54e8-a3ff-da6349ad43c2'
    assert rp['header']['uuid'] == 'bbbd2d60-52e5-53a6-8b9a-c09b0f516389'
    assert bp['header']['name'] == 'Kaleidoscope Grilling A2.7.62 Runtime Split BP'
    assert rp['header']['name'] == 'Kaleidoscope Grilling A2.7.62 Runtime Split RP'

    main_text = (BP / 'scripts/main.js').read_text(encoding='utf-8')
    assert "from './a2762_interaction_intent_adapter.js'" in main_text
    for forbidden in (
        'function primitiveProps(stack)',
        'function stackIntentSignature(stack)',
        'function stackIntentDescriptor(stack)',
        'function captureInteractionIntent(player,eventStack)',
        'function interactionIntentStillCurrent(player,intent)',
    ):
        assert forbidden not in main_text, forbidden
    assert 'primitiveStackProps(stack)' in main_text

    core = (BP / 'scripts/a2762_interaction_intent_core.js').read_text(encoding='utf-8')
    adapter = (BP / 'scripts/a2762_interaction_intent_adapter.js').read_text(encoding='utf-8')
    for token in (
        "from './a276_grill_intent_core.js'",
        'export function primitiveStackProps',
        'export function stackIntentSignature',
        'export function stackIntentDescriptor',
        'export function captureInteractionIntentFromStacks',
        'export function interactionIntentMatchesStacks',
    ):
        assert token in core, token
    assert '@minecraft/server' not in core
    for token in (
        "from './a2735_player_io.js'",
        "from './a2762_interaction_intent_core.js'",
        'getMainHand(player)',
        'getOffHand(player)',
        'captureInteractionIntentFromStacks',
        'interactionIntentMatchesStacks',
    ):
        assert token in adapter, token

    active = sorted((ROOT / '.github/workflows').glob('gameplay-core-a*.yml'))
    archived = sorted((ROOT / 'docs/legacy_workflows').glob('gameplay-core-a*.yml'))
    assert active == [], active
    assert len(archived) == 65, len(archived)
    assert (ROOT / '.github/workflows/gameplay-core.yml').is_file()
    assert (ROOT / 'docs/legacy_workflows/README.md').is_file()

    for test in ('test_a275_core.mjs', 'test_a276_core.mjs', 'test_a277_core.mjs', 'test_a2762_core.mjs'):
        subprocess.run(['node', str(DEV / test)], check=True)
    subprocess.run([sys.executable, str(DEV / 'verify_a2761_java_interaction_contract.py')], check=True)
    for path in (BP / 'scripts').glob('*.js'):
        subprocess.run(['node', '--check', str(path)], check=True)

    report = load(PROJECT / 'reports/a2762-runtime-split.json')
    assert report['version'] == 'A2.7.62'
    assert report['runtime_refactor']['main_local_intent_helpers_removed'] is True
    assert report['runtime_refactor']['gameplay_rule_changes'] is False
    assert report['legacy_workflow_retirement']['active_versioned_workflows'] == 0
    assert report['legacy_workflow_retirement']['archived_versioned_workflows'] == 65
    assert report['compatibility']['identifiers_preserved'] is True
    assert report['compatibility']['uuids_preserved'] is True
    assert report['compatibility']['dynamic_property_keys_preserved'] is True
    assert report['minecraft_tested'] is False
    assert report['bds_tested'] is False
    assert report['client_visuals_tested'] is False

    print(json.dumps({
        'version': 'A2.7.62',
        'runtime_intent_split': True,
        'legacy_workflows_archived': len(archived),
        'compiled_requested': args.compiled,
        'minecraft_tested': False,
        'bds_tested': False,
        'client_visuals_tested': False,
    }, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
