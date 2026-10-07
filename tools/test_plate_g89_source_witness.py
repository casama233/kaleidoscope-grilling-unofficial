"""Full runtime conservation, including exact new ordinary generated files."""
from pathlib import Path
import json,unittest
from unittest.mock import patch
import plate_g89_source_witness as witness
class G89SourceWitness(unittest.TestCase):
 def test_complete_current_runtime_is_exact_reviewed_plate_only_delta(self):witness.verify_current()
 def test_core_delta_and_new_assets_have_no_blanket_exception(self):
  d=witness.metadata();self.assertEqual(len(d['files']),5);self.assertEqual(len(witness.NEW),2)
  core=witness.PROJECT+'behavior_pack/scripts/plate_visual_core.js'
  self.assertEqual(len(d['files'][core]['operations']),2)
  for path in witness.ALLOWED:
   actual=(witness.ROOT/path).read_bytes();expected=witness.expected_current(path);self.assertEqual(actual,expected)
   with patch.object(Path,'read_bytes',return_value=actual+b'\n'):
    if path in witness.NEW:
     with self.assertRaises(AssertionError):witness.expected_current(path)
    else:self.assertNotEqual((witness.ROOT/path).read_bytes(),expected)
 def test_g88_history_main_and_interaction_renderer_are_conserved(self):
  current=json.loads((witness.ROOT/'release-history.json').read_text())
  for version,value in json.loads(witness.source('release-history.json')).items():self.assertEqual(current[version],value)
  for name in ('main.js','bottle_held_visual_runtime.js','a25_plate_recipe_runtime.js','station_contents_visual_runtime.js'):
   path=witness.PROJECT+'behavior_pack/scripts/'+name
   self.assertEqual((witness.ROOT/path).read_bytes(),witness.source(path),path)
if __name__=='__main__':unittest.main()
