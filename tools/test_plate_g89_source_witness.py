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
  version=tuple(json.loads((witness.ROOT/'baseline.json').read_text())['version'])
  if version>=(2,8,90):
   from g90_source_conservation import assert_history,PLATE_SOURCE_BASE,expected_runtime_bytes,source
   assert_history(self,current,witness.DIRECTION_SOURCE_BASE)
  else:
   for label,value in json.loads(witness.source('release-history.json')).items():self.assertEqual(current[label],value)
  for name in ('main.js','bottle_held_visual_runtime.js','a25_plate_recipe_runtime.js','station_contents_visual_runtime.js'):
   path=witness.PROJECT+'behavior_pack/scripts/'+name
   if version>=(2,8,90):
    self.assertEqual(source(PLATE_SOURCE_BASE,path),witness.source(path),path)
    self.assertEqual((witness.ROOT/path).read_bytes(),expected_runtime_bytes(path),path)
   else:self.assertEqual((witness.ROOT/path).read_bytes(),witness.source(path),path)
if __name__=='__main__':unittest.main()
