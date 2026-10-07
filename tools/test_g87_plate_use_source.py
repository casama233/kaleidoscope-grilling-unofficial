import unittest
from pathlib import Path
from unittest.mock import patch
from test_g86_source_coherence import ROOT,UNION_SOURCE_BASE,G87_DELTAS,source,apply_runtime_delta
PATH='projects/grilling/gameplay_core/behavior_pack/scripts/a25_plate_recipe_runtime.js'
class PlateUseSourceTests(unittest.TestCase):
 def test_exact_a25_delta_from_frozen_g86(self):
  self.assertEqual(apply_runtime_delta(source(UNION_SOURCE_BASE,PATH),PATH,G87_DELTAS[PATH]),(ROOT/PATH).read_bytes())
 def test_unrelated_bytes_and_guard_removal_are_not_admitted(self):
  p=ROOT/PATH;s=p.read_bytes();expected=apply_runtime_delta(source(UNION_SOURCE_BASE,PATH),PATH,G87_DELTAS[PATH])
  for changed in (s+b'\n',s.replace(b'  if(skewerUseTargetsPlate(p,e.itemStack)){e.cancel=true;return;}\n',b'')):
   self.assertNotEqual(changed,s)
   with patch.object(Path,'read_bytes',return_value=changed):self.assertNotEqual(p.read_bytes(),expected)
if __name__=='__main__':unittest.main()
