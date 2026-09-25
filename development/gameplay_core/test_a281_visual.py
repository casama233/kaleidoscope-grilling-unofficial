"""Pure source/image regressions; never simulates a player or claims engine QA."""
import unittest
from copy import deepcopy
import a281_visual_contract as c
class VisualContracts(unittest.TestCase):
 def test_java_native_all_seven_contexts(self):self.assertEqual(c.java_native_match(),7)
 def test_rotation_equivalence(self):self.assertEqual(c.normalized_display({'rotation':[30,-135,0]}),c.normalized_display({'rotation':[30,225,0]}))
 def test_wrong_scale_rejected_by_comparison(self):
  bad=deepcopy(c.NATIVE_DEFAULTS['firstperson_righthand']);bad['scale']=[1]*3
  self.assertNotEqual(c.normalized_display(bad),c.normalized_display(c.NATIVE_DEFAULTS['firstperson_righthand']))
 def test_native_vat_path(self):self.assertEqual(c.vat_contract(),7)
 def test_generated_icons_and_guide(self):self.assertEqual(len(c.icon_contract()),3)
 def test_empty_vs_full_icon(self):
  from PIL import Image
  empty=Image.open(c.RP/'textures/items/empty_seasoning_bottle.png').convert('RGBA')
  full=Image.open(c.RP/'textures/items/special_seasoning.png').convert('RGBA')
  self.assertNotEqual(empty.tobytes(),full.tobytes())
 def test_all_other_runtime_unchanged(self):self.assertGreater(c.baseline_contract(),1300)
 def test_existing_108_minus_vat_attachable(self):self.assertEqual(len(list((c.RP/'attachables').glob('*.json'))),107)
 def test_icon_input_sheet_still_intact(self):self.assertEqual(c.sha((c.RP/'textures/blocks/seasoning_bottle.png').read_bytes()),'9a889a96a4bb34b999ddfc5bcb42b1f1a691fc1e65c91253726b7eee6a3dc94b')
 def test_correction_changes_no_gameplay_script(self):
  # Enforced by the precise allowed-changes manifest, not a simulated interaction.
  self.assertFalse(any('/scripts/' in path for path in c.ALLOWED_CHANGED))
if __name__=='__main__':unittest.main(verbosity=2)
