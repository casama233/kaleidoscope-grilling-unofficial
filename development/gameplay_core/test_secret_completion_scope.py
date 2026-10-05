"""Bound the completion repair to visual ownership, not eating mechanics."""
from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
BASE = '93c2fa2a4de5155f7810c3c6289e7bee6ef17857'
RUNTIME = 'projects/grilling/gameplay_core/'
sys.path.insert(0, str(ROOT / 'tools'))
from secret_terminal_visibility import apply as apply_terminal_visibility


def old(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT).decode()


class SecretCompletionScope(unittest.TestCase):
    def test_only_two_visual_sync_bp_files_and_two_owned_attachables_change(self):
        changed = subprocess.check_output(['git', 'diff', '--name-only', BASE, '--', RUNTIME], cwd=ROOT).decode().splitlines()
        self.assertEqual(changed, [
            RUNTIME + 'behavior_pack/scripts/main.js',
            RUNTIME + 'behavior_pack/scripts/secret_held_runtime.js',
            RUNTIME + 'resource_pack/attachables/secret_skewer.attachable.json',
            RUNTIME + 'resource_pack/attachables/secret_skewer_java_three_alt.attachable.json',
        ])
        for name in ('secret_skewer', 'secret_skewer_java_three_alt'):
            path = RUNTIME + 'resource_pack/attachables/' + name + '.attachable.json'
            before, after = json.loads(old(path)), json.loads((ROOT / path).read_text())
            before_rows = before['minecraft:attachable']['description']['scripts']['pre_animation']
            # Preserve the historical single owner-expression change, followed
            # by the independently bounded 6714 client-only terminal boundary.
            from build_secret_held import owner_occupancy
            before_description = before['minecraft:attachable']['description']
            before_description['scripts']['pre_animation'] = [owner_occupancy(before_description['identifier']) if row.startswith('v.kg_secret_owner_occupied = ') else row for row in before_rows]
            apply_terminal_visibility(before_description)
            self.assertEqual(after, before)

    def test_all_native_debit_reward_checkpoint_and_cleanup_code_is_identical(self):
        path = RUNTIME + 'behavior_pack/scripts/main.js'
        expected = old(path)
        begin = "  try{syncSecretHeld(e.source)}catch(error){console.warn('[Grilling held ingredients] '+error)}\n"
        self.assertEqual(expected.count(begin), 1)
        expected = expected.replace(begin, '')
        requested = next(row for row in expected.splitlines(True) if row.startswith('  const requested=PROFILE_BY_ITEM[id]'))
        expected = expected.replace(requested, requested + begin.replace('syncSecretHeld(e.source)', 'syncSecretHeld(e.source,{beginHand:hand})'))
        expected = expected.replace(
            ' // Native debit is already complete. Refresh owner mesh indices before the\n // eating presentation clears; never show yesterday\'s full ingredient rows.\n',
            ' // Publish completion ownership before presentation reset, even if the held\n // snapshot still contains the just-consumed single serving this callback.\n')
        expected = expected.replace("if(id===SECRET_ID)try{syncSecretHeld(e.source)}catch(error){console.warn('[Grilling held completion] '+error)}", "if(id===SECRET_ID)try{syncSecretHeld(e.source,{completedUse:a.use})}catch(error){console.warn('[Grilling held completion] '+error)}")
        self.assertTrue((ROOT / path).read_text() == expected, 'Main runtime changed outside visual sync calls')


if __name__ == '__main__':
    unittest.main()
