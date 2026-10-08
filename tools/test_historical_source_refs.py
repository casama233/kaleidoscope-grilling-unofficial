from pathlib import Path
import io,json,tempfile,unittest
from unittest.mock import patch
from historical_source_refs import ROOT,encoded_listing,inventory,literal_refs,verify
import public_source_witness as public

class HistoricalSourceRefsTests(unittest.TestCase):
 def fixture(self,text,rows):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);r=Path(t.name)
  (r/'development/gameplay_core').mkdir(parents=True);(r/'tools/fixtures').mkdir(parents=True)
  (r/'development/gameplay_core/gate.py').write_text(text)
  (r/'tools/fixtures/g66-historical-source-refs.json').write_text(json.dumps({'schema':1,'refs':rows}))
  return r
 def test_complete_active_source_refs_resolve_exactly(self):
  self.assertEqual(verify(),{'refs':16,'commits':16})
  self.assertEqual(set(inventory()),literal_refs())
 def test_public_witness_rejects_tree_digest_and_current_source_byte_mutations(self):
  meta=public.witness();path=ROOT/'projects/grilling/gameplay_core/resource_pack/animations/java_eating_player.animation.json'
  self.assertIn(meta['commit'],inventory());self.assertEqual(meta['tree'],public.PUBLIC_SOURCE_TREE)
  source=public.public_bytes(path);self.assertEqual(path.read_bytes(),source)
  with patch.object(Path,'read_bytes',return_value=source+b'\n'):
   with self.assertRaises(AssertionError):public.assert_public_bytes(self,path)
  wrong=dict(meta,files=dict(meta['files']));wrong['files'][path.relative_to(ROOT).as_posix()]='0'*64
  with patch.object(public,'witness',return_value=wrong):
   with self.assertRaisesRegex(AssertionError,'bytes mismatch'):public.public_bytes(path)
  public.witness.cache_clear()
  try:
   with patch.object(public.subprocess,'check_output',return_value='0'*40):
    with self.assertRaisesRegex(AssertionError,'tree mismatch'):public.witness()
  finally:public.witness.cache_clear()
  with self.assertRaises(AssertionError):public.public_bytes('../outside.json')
 def test_archived_private_builders_retain_bytes_and_are_not_active_python(self):
  import subprocess
  for name in ('build_threaded_idle_private.py','build_threaded_secret_private.py'):
   path=ROOT/'docs/archive/private-builders'/(name+'.txt')
   source=subprocess.check_output(['git','show',public.PUBLIC_SOURCE_BASE+':tools/'+name],cwd=ROOT)
   self.assertEqual(path.read_bytes(),source);self.assertFalse((ROOT/'tools'/name).exists())
 def test_g73_plate_alias_delta_is_single_line_and_rejects_unrelated_mutations(self):
  path=ROOT/'projects/grilling/gameplay_core/behavior_pack/scripts/main.js'
  delta=json.loads((ROOT/'tools/fixtures/g73-plate-alias-main-delta.json').read_text())
  before=' const id=eaten.typeId;dangerousPreservation(player,id);\n'
  after=' const id=canonicalFoodId(eaten.typeId);dangerousPreservation(player,id);\n'
  self.assertEqual(delta['release'],[2,8,73]);self.assertEqual(len(delta['edits']),1)
  edit=delta['edits'][0];self.assertEqual(edit['end']-edit['start'],1)
  self.assertEqual(edit['before'],before);self.assertEqual(edit['after'],after)
  public.assert_public_bytes_with_g71_bottles(self,path)
  source=path.read_bytes()
  for changed in (source.replace(after.encode(),before.encode()),source.replace(b'MINIMUM_EAT_TICKS=25',b'MINIMUM_EAT_TICKS=1'),source+b'\n'):
   self.assertNotEqual(changed,source)
   with patch.object(Path,'read_bytes',return_value=changed):
    with self.assertRaisesRegex(AssertionError,'Source differs outside'):
     public.assert_public_bytes_with_g71_bottles(self,path)
 def test_g110_completion_and_material_lore_are_exactly_reviewed(self):
  path=ROOT/'projects/grilling/gameplay_core/behavior_pack/scripts/main.js'
  delta=json.loads((ROOT/'tools/fixtures/g110-main-reviewed-delta.json').read_text())
  self.assertEqual(delta['release'],[2,8,110]);self.assertEqual(len(delta['operations']),2)
  self.assertEqual(delta['operations'][0]['before'],'seasoningLore(16-nextUses)')
  self.assertEqual(delta['operations'][0]['after'],'seasoningLore(16-nextUses,ingredients.length)')
  self.assertIn("if(!hasSeasoningBase(list))",delta['operations'][1]['before'])
  self.assertNotIn("if(!hasSeasoningBase(list))",delta['operations'][1]['after'])
  source=path.read_bytes()
  public.assert_public_bytes_with_g71_bottles(self,path)
  for op in delta['operations']:
   changed=source.replace(op['after'].encode(),op['before'].encode())
   self.assertNotEqual(changed,source)
   with patch.object(Path,'read_bytes',return_value=changed):
    with self.assertRaisesRegex(AssertionError,'Source differs outside'):
     public.assert_public_bytes_with_g71_bottles(self,path)
  before=public.expected_main_bytes((2,8,114))
  repaired=public.expected_main_bytes((2,8,115))
  self.assertEqual(repaired,before.replace(public.NUTRITION_G114,public.NUTRITION_G115,1))
  self.assertIn(public.REVIEWED_NUTRITION_BASE,inventory())
  for changed in (repaired.replace(public.NUTRITION_G115,public.NUTRITION_G114,1),repaired.replace(b'currentSat.effectiveMax,',b'',1)):
   self.assertNotEqual(changed,repaired)
   with patch.object(Path,'read_bytes',return_value=changed):
    with self.assertRaisesRegex(AssertionError,'Source differs outside'):
     public.assert_public_bytes_with_g71_bottles(self,path)
 def test_short_literal_and_full_named_base_are_audited(self):
  full='1'*40;r=self.fixture("SOURCE_BASE='"+full+"'\nx=['git','show','abcdef12:code.json']",{full:full,'abcdef12':'a'*40})
  self.assertEqual(literal_refs(r),{full,'abcdef12'});inventory(r)
 def test_missing_short_ref_fails_closed(self):
  r=self.fixture("x=['git','show',f'abcdef12:{path}']",{'1'*40:'1'*40})
  with self.assertRaisesRegex(AssertionError,'absent'):inventory(r)
 def test_listing_has_exact_lf_bytes_through_windows_text_stdout(self):
  full='1'*40;r=self.fixture("BASE='"+full+"'",{full:full})
  raw=io.BytesIO();stdout=io.TextIOWrapper(raw,encoding='utf-8',newline='\r\n')
  stdout.buffer.write(encoded_listing(r));stdout.flush()
  self.assertEqual(raw.getvalue(),full.encode()+b'\n');self.assertNotIn(b'\r',raw.getvalue())
  stdout.detach()
 def test_invalid_full_sha_fails_closed(self):
  r=self.fixture("BASE='abcdef12'",{'abcdef12':'a'*39})
  with self.assertRaises(AssertionError):inventory(r)

if __name__=='__main__':unittest.main()
