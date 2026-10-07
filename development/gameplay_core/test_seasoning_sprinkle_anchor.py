"""Narrow source/math gate after native G64 clipping; candidate is unaccepted."""
import json
import re
import math
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'development/gameplay_core'))
import build_seasoning_held as held
FROZEN_PLATE_SOURCE_BASE='fdc9892edcb714c22e1b014943b4ce86c4a2570d'
from test_native_bottle_fp import projected


class SprinkleAnchor(unittest.TestCase):
    def test_only_main_sprinkle_positions_change_and_pending_remains_exact(self):
        path = held.RP / 'animations/seasoning_held.animation.json'
        before = json.loads(subprocess.check_output(['git', 'show', 'cba67124:' + path.relative_to(ROOT).as_posix()], cwd=ROOT))['animations']
        after = json.loads(path.read_text())['animations']
        changed = {key for key in after if before[key] != after[key]}
        self.assertEqual(changed, {'animation.kg_seasoning.item.sprinkle.right'})
        key = next(iter(changed))
        for channel in ['rotation', 'scale']:
            self.assertEqual(after[key]['bones']['grip'][channel], before[key]['bones']['grip'][channel])
        self.assertEqual(after[key]['animation_length'], .5)
        self.assertFalse(after[key]['loop'])
        offsets = []
        for time, position in after[key]['bones']['grip']['position'].items():
            offsets.append([a - b for a, b in zip(position, before[key]['bones']['grip']['position'][time])])
        for offset in offsets:
            for first, second in zip(offset, offsets[0]):
                self.assertAlmostEqual(first, second, places=8)

    def test_exact_native_empty_hand_basis_and_strict_action_scope(self):
        source = json.loads((ROOT / 'development/gameplay_core/fixtures/seasoning-native-sprinkle-frame-1.26.50.4.json').read_text())
        self.assertEqual(source['sources']['player_firstperson']['blob'], '1b664aa21eae5f2bd994a2fad53a7f42f235af50')
        path = held.RP / 'animations/seasoning_sprinkle_anchor.animation.json'
        clips = json.loads(path.read_text())['animations']
        self.assertEqual(set(clips), {'animation.kg_seasoning.player.sprinkle_anchor.right'})
        clip = next(iter(clips.values()))
        self.assertEqual(clip['animation_length'], .5)
        self.assertNotIn('loop', clip)
        self.assertTrue(clip['override_previous_animation'])
        self.assertEqual(set(clip['bones']), {'rightarm', 'rightitem'})
        for bone, data in clip['bones'].items():
            self.assertEqual(data, source['empty_hand']['bones'][bone])
            self.assertNotIn('scale', data)
        gate = clip['blend_weight']
        self.assertTrue(gate.startswith('variable.is_first_person && '))
        self.assertIn("q.property('kaleidoscope_grilling:season_hand') == 1", gate)
        self.assertIn("q.property('kaleidoscope_grilling:season_phase') > 0", gate)
        self.assertIn("q.is_item_name_any('slot.weapon.mainhand',", gate)
        self.assertNotIn('pending_seasoning', gate)
        self.assertNotIn('empty_seasoning_bottle', gate)
        self.assertNotIn('offhand', gate)
        self.assertNotIn('eat_', gate)
        self.assertIn('q.is_sneaking == 0', gate)
        self.assertIn('q.is_swimming == 0', gate)
        self.assertIn('variable.is_using_vr == 0', gate)

    def test_inverted_complete_mesh_fits_fov60_math_with_hud_clearance(self):
        # This is the finite settled native frame, not a rendered client test.
        geometries = json.loads((held.RP / 'models/entity/bottle_held_contents.geo.json').read_text())['minecraft:geometry']
        largest = geometries[0]
        for i in range(61):
            pose = held.motion('right', i / 120, False)
            points = projected(largest, {'bones': {'grip': pose}}, 'right')
            for x, y, z in points:
                self.assertLess(z, -.1)
                self.assertLess(abs(x / -z), 1.489 * math.tan(math.radians(30)))
                self.assertGreater(y / -z, -.45)
                self.assertLess(y / -z, .52)

    def test_existing_native_player_and_idle_assets_remain_unchanged(self):
        paths = [held.BP / 'entities/player.json', held.RP / 'animations/a286_held.animation.json',
                 held.RP / 'animations/a21_shake.animation.json', held.RP / 'animations/player_binding.animation.json']
        paths += list((held.RP / 'attachables').glob('*seasoning*.json'))
        version=tuple(json.loads((held.BP/'manifest.json').read_text())['header']['version'])
        if version >= (2,8,90):
            from g90_source_conservation import verify_current,expected_runtime_bytes
            verify_current()
        for path in paths:
            actual=path.read_bytes()
            if version >= (2,8,90):
                # Preserve the old physical/idle assertions on frozen G89;
                # current ranges/owner guards require exact reviewed source bytes.
                self.assertEqual(actual,expected_runtime_bytes(path.relative_to(ROOT).as_posix()),path)
                actual=subprocess.check_output(['git','show',FROZEN_PLATE_SOURCE_BASE+':'+path.relative_to(ROOT).as_posix()],cwd=ROOT)
            proxy=re.fullmatch(r'(partial|pending)_seasoning_f[1-8]\.attachable',path.stem) if path.parent==held.RP/'attachables' else None
            if proxy:
                self.assertGreaterEqual(version,(2,8,71))
                base='empty_seasoning_bottle' if proxy.group(1)=='partial' else 'pending_seasoning'
                original=path.with_name(base+'.attachable.json')
                before=json.loads(subprocess.check_output(['git','show','cba67124:'+original.relative_to(ROOT).as_posix()],cwd=ROOT))
                before['minecraft:attachable']['description']['identifier']='kaleidoscope_grilling:'+path.name.removesuffix('.attachable.json')
                self.assertEqual(json.loads(actual),before,path)
                continue
            prior=subprocess.check_output(['git','show','cba67124:'+path.relative_to(ROOT).as_posix()],cwd=ROOT)
            if version>=(2,8,68) and path==held.BP/'entities/player.json':
                before=json.loads(prior)
                props=before['minecraft:entity']['description']['properties']
                for hand in ('main','off'):
                    for index in range(3):
                        row=props['kaleidoscope_grilling:secret_'+hand+'_'+str(index)]
                        self.assertEqual(row,{'type':'int','range':[0,255],'default':0,'client_sync':True})
                        row['range']=[0,5333]
                    props['kaleidoscope_grilling:secret_'+hand+'_piece']={'type':'int','range':[0,255],'default':0,'client_sync':True}
                self.assertEqual(json.loads(actual),before,path)
            else:self.assertEqual(actual,prior,path)


if __name__ == '__main__':
    unittest.main()
