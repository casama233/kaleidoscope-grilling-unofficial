"""Exact fail-closed helper-removal delta; no ownership or gameplay exception."""
import hashlib,json,unittest
from test_g86_source_coherence import ROOT,HARDENING_SOURCE_BASE,G88_DELTAS,source,apply_runtime_delta
PATH='projects/grilling/gameplay_core/behavior_pack/scripts/station_contents_visual_runtime.js'
class CleanupSourceWitness(unittest.TestCase):
 def test_only_failed_removal_check_is_added_to_frozen_renderer(self):
  before=source(HARDENING_SOURCE_BASE,PATH)
  after=apply_runtime_delta(before,PATH,G88_DELTAS[PATH],(2,8,88),HARDENING_SOURCE_BASE)
  self.assertEqual(after,(ROOT/PATH).read_bytes())
  d=json.loads((ROOT/'tools/fixtures'/G88_DELTAS[PATH]).read_text());self.assertEqual(len(d['operations']),1)
  op=d['operations'][0];self.assertEqual(before.count(op['before'].encode()),1)
  self.assertEqual(op['before'].replace('discard(row,k);old=undefined;','discard(row,k);if(row.parts.has(k))return;old=undefined;'),op['after'])
  self.assertEqual(before.replace(op['before'].encode(),op['after'].encode()),after)
  self.assertEqual(hashlib.sha256(before).hexdigest(),'e1d303dcc8bf8855d001b6b0a13800ad5d04efed8db7060f2a2b6dafb36059f4')
 def test_failed_removal_bypass_and_other_source_changes_are_rejected(self):
  after=apply_runtime_delta(source(HARDENING_SOURCE_BASE,PATH),PATH,G88_DELTAS[PATH],(2,8,88),HARDENING_SOURCE_BASE)
  for changed in (after+b'\n',after.replace(b'if(row.parts.has(k))return;',b''),after.replace(b'initialRotation:-at.angle',b'initialRotation:0')):
   self.assertNotEqual(changed,after)
if __name__=='__main__':unittest.main()
