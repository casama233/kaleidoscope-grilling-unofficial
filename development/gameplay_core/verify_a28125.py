"""Retain historical gates and validate the reviewed scene/interaction repairs."""
from pathlib import Path
import json
import os
import subprocess
import sys
from verify_a28124 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session

ROOT = Path(__file__).resolve().parents[2]


def check_grill_light():
    path = ROOT / 'projects/grilling/gameplay_core/behavior_pack/blocks/grill.json'
    block = json.loads(path.read_text())['minecraft:block']
    assert block['components']['minecraft:light_emission'] == 0
    light_rows = [row for row in block['permutations']
                  if 'minecraft:light_emission' in row.get('components', {})]
    assert len(light_rows) == 4
    for row in light_rows:
        lit = "q.block_state('kaleidoscope_grilling:lit') == true" in row['condition']
        assert row['components']['minecraft:light_emission'] == (7 if lit else 0), row


def main(expected_version=(2, 8, 125)):
    previous(expected_version=expected_version)
    check_grill_light()
    subprocess.run([
        'node', '--test', 'development/gameplay_core/test_grill_destruction.mjs',
        'development/gameplay_core/test_numb_visual.mjs',
    ], cwd=ROOT, check=True)
    subprocess.run([
        sys.executable, '-B', 'tools/build_scene_visuals.py', '--check',
    ], cwd=ROOT, check=True)
    print('G125 scene, immersion and owned interaction repairs PASS; full-family/native player/client acceptance remain separate')


if __name__ == '__main__':
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
