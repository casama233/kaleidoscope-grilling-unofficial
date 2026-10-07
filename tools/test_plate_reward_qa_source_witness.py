import hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
import public_source_witness as public
class PlateRewardQaWitnessTests(unittest.TestCase):
 def test_exact_g84_diagnostic_only_delta(self):
  d=public._main_delta('g84-main-reviewed-delta.json');before=public.expected_main_bytes((2,8,83));after=public.expected_main_bytes((2,8,84))
  self.assertEqual(hashlib.sha256(before).hexdigest(),d['before_sha256']);self.assertEqual(hashlib.sha256(after).hexdigest(),d['after_sha256']);self.assertEqual(public.expected_main_bytes(json.loads((public.ROOT/'baseline.json').read_text())['version']),(public.ROOT/public.MAIN_PATH).read_bytes())
 def test_unrelated_edits_stay_rejected(self):
  p=public.ROOT/public.MAIN_PATH;s=p.read_bytes()
  for changed in (s+b'\n',s.replace(b'operation=\'hunger_write\';h.setCurrentValue(hunger)',b'operation=\'hunger_write\';h.setCurrentValue(20)')):
   self.assertNotEqual(changed,s)
   with patch.object(Path,'read_bytes',return_value=changed):self.assertNotEqual(p.read_bytes(),public.expected_main_bytes((2,8,84)))
 def test_original_g83_and_g81_source_identites_stay_pinned(self):
  self.assertEqual(hashlib.sha256(public.expected_main_bytes((2,8,83))).hexdigest(),public._main_delta('g83-main-reviewed-delta.json')['after_sha256'])
  self.assertEqual(hashlib.sha256(public.expected_main_bytes((2,8,81))).hexdigest(),public._main_delta('g83-main-reviewed-delta.json')['before_sha256'])
if __name__=='__main__':unittest.main()
