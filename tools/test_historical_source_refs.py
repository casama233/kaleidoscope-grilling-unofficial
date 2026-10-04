from pathlib import Path
import json,tempfile,unittest
from historical_source_refs import ROOT,inventory,literal_refs,verify

class HistoricalSourceRefsTests(unittest.TestCase):
 def fixture(self,text,rows):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);r=Path(t.name)
  (r/'development/gameplay_core').mkdir(parents=True);(r/'tools/fixtures').mkdir(parents=True)
  (r/'development/gameplay_core/gate.py').write_text(text)
  (r/'tools/fixtures/g66-historical-source-refs.json').write_text(json.dumps({'schema':1,'refs':rows}))
  return r
 def test_complete_original_refs_resolve_exactly(self):
  self.assertEqual(verify(),{'refs':13,'commits':13})
  self.assertEqual(set(inventory()),literal_refs())
 def test_short_literal_and_full_named_base_are_audited(self):
  full='1'*40;r=self.fixture("SOURCE_BASE='"+full+"'\nx=['git','show','abcdef12:code.json']",{full:full,'abcdef12':'a'*40})
  self.assertEqual(literal_refs(r),{full,'abcdef12'});inventory(r)
 def test_missing_short_ref_fails_closed(self):
  r=self.fixture("x=['git','show',f'abcdef12:{path}']",{'1'*40:'1'*40})
  with self.assertRaisesRegex(AssertionError,'absent'):inventory(r)
 def test_invalid_full_sha_fails_closed(self):
  r=self.fixture("BASE='abcdef12'",{'abcdef12':'a'*39})
  with self.assertRaises(AssertionError):inventory(r)

if __name__=='__main__':unittest.main()
