import hashlib,unittest
from pathlib import Path
from unittest.mock import patch
import public_source_witness as public
class NativeSaturationWitnessTests(unittest.TestCase):
 def test_exact_g85_proven_bounds_delta(self):
  d=public._main_delta('g85-main-reviewed-delta.json');before=public.expected_main_bytes((2,8,84));after=public.expected_main_bytes((2,8,85))
  self.assertEqual(hashlib.sha256(before).hexdigest(),d['before_sha256']);self.assertEqual(hashlib.sha256(after).hexdigest(),d['after_sha256']);self.assertEqual(after,(public.ROOT/public.MAIN_PATH).read_bytes())
 def test_invented_maximum_and_unrelated_edits_remain_rejected(self):
  p=public.ROOT/public.MAIN_PATH;s=p.read_bytes()
  for changed in (s+b'\n',s.replace(b'Math.min(hunger,currentSat.effectiveMax,currentSat.currentValue+gain)',b'Math.min(hunger,20,currentSat.currentValue+gain)')):
   self.assertNotEqual(changed,s)
   with patch.object(Path,'read_bytes',return_value=changed):self.assertNotEqual(p.read_bytes(),public.expected_main_bytes((2,8,85)))
 def test_previous_g84_diagnostic_identity_stays_pinned(self):
  self.assertEqual(hashlib.sha256(public.expected_main_bytes((2,8,84))).hexdigest(),public._main_delta('g84-main-reviewed-delta.json')['after_sha256'])
if __name__=='__main__':unittest.main()
