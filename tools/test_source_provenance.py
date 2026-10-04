from pathlib import Path
import json,shutil,subprocess,tempfile,unittest
from source_provenance import ensure_provenance,ROOT
class SelectedSourceProvenanceTests(unittest.TestCase):
 def fixture(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);r=Path(t.name);(r/'tools/fixtures').mkdir(parents=True);subprocess.run(['git','init','-q',str(r)],check=True)
  for name in ('g66-selected-source.pack','g66-selected-source.json'):shutil.copy2(ROOT/'tools/fixtures'/name,r/'tools/fixtures'/name)
  return r
 def test_selected_original_blobs_import_exactly_without_refs(self):
  r=self.fixture();result=ensure_provenance(r);self.assertEqual(result['commits'],1);self.assertEqual(result['objects'],12);self.assertFalse(result['refs_changed']);self.assertEqual(subprocess.run(['git','-C',str(r),'show-ref'],capture_output=True).stdout,b'');self.assertEqual(ensure_provenance(r),result)
 def test_changed_pack_rejected_before_import(self):
  r=self.fixture();p=r/'tools/fixtures/g66-selected-source.pack';p.write_bytes(p.read_bytes()+b'X')
  with self.assertRaisesRegex(AssertionError,'Corrupt'):ensure_provenance(r)
 def test_wrong_object_inventory_rejected(self):
  r=self.fixture();p=r/'tools/fixtures/g66-selected-source.json';x=json.loads(p.read_text());x['object_count']+=1;p.write_text(json.dumps(x))
  with self.assertRaisesRegex(AssertionError,'Wrong source object inventory'):ensure_provenance(r)
 def test_wrong_selected_blob_hash_rejected(self):
  r=self.fixture();p=r/'tools/fixtures/g66-selected-source.json';x=json.loads(p.read_text());row=next(iter(next(iter(x['selected_blobs'].values())).values()));row['sha256']='0'*64;p.write_text(json.dumps(x))
  with self.assertRaises(AssertionError):ensure_provenance(r)
 def test_exact_object_set_rejected_if_metadata_would_hide_an_object(self):
  r=self.fixture();p=r/'tools/fixtures/g66-selected-source.json';x=json.loads(p.read_text());x['exact_object_ids'][0]='0'*40;p.write_text(json.dumps(x))
  with self.assertRaisesRegex(AssertionError,'Unexpected selected source objects'):ensure_provenance(r)
if __name__=='__main__':unittest.main()
