from pathlib import Path
import json,shutil,tempfile,unittest
import verify_a2866 as gate
class G66LocalReceiptTests(unittest.TestCase):
 def fixture(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);r=Path(t.name);(r/'.github').mkdir();(r/'docs').mkdir();(r/'baseline.json').write_bytes((gate.ROOT/'baseline.json').read_bytes());(r/'.github/local-test-release-2.8.66.json').write_bytes((gate.ROOT/'.github/local-test-release-2.8.66.json').read_bytes());(r/'docs/NATIVE-SECRET-6504-20261004.json').write_bytes((gate.ROOT/'docs/NATIVE-SECRET-6504-20261004.json').read_bytes())
  config=json.loads((r/'baseline.json').read_text())
  for name in config['runtime'].values():shutil.copytree(gate.ROOT/name,r/name)
  return r
 def change(self,r,key,value):
  p=r/'.github/local-test-release-2.8.66.json';x=json.loads(p.read_text());x[key]=value;p.write_text(json.dumps(x))
 def test_exact_known_pending_receipt(self):self.assertEqual(gate.validate_local_pending_receipt()['version'],[2,8,66])
 def test_native_or_production_promotion_rejected(self):
  r=self.fixture()
  for key in ('complete_client_acceptance','java_all_view_parity','production_ready','saved_world_migration'):
   self.change(r,key,True)
   with self.assertRaises(AssertionError):gate.validate_local_pending_receipt(r)
   self.change(r,key,False)
 def test_wrong_identity_rejected(self):
  r=self.fixture();self.change(r,'version',[2,8,64])
  with self.assertRaises(AssertionError):gate.validate_local_pending_receipt(r)
 def test_stale_source_tree_rejected(self):
  r=self.fixture();self.change(r,'source_trees',{})
  with self.assertRaises(AssertionError):gate.validate_local_pending_receipt(r)
 def test_runtime_tamper_rejected(self):
  r=self.fixture();p=r/'projects/grilling/gameplay_core/behavior_pack/manifest.json';p.write_bytes(p.read_bytes()+b'\n')
  with self.assertRaises(AssertionError):gate.validate_local_pending_receipt(r)
 def test_native_evidence_tamper_rejected(self):
  r=self.fixture();p=r/'docs/NATIVE-SECRET-6504-20261004.json';p.write_bytes(p.read_bytes()+b'\n')
  with self.assertRaises(AssertionError):gate.validate_local_pending_receipt(r)
 def test_publication_claim_rejected(self):
  r=self.fixture();self.change(r,'publication_status','published')
  with self.assertRaises(AssertionError):gate.validate_local_pending_receipt(r)
 def test_mismatched_public_native_binding_rejected_even_with_updated_digest(self):
  import hashlib
  r=self.fixture();p=r/'docs/NATIVE-SECRET-6504-20261004.json';x=json.loads(p.read_text());x['release_runtime_fingerprints']={};p.write_text(json.dumps(x));self.change(r,'bounded_native_evidence_sha256',hashlib.sha256(p.read_bytes()).hexdigest())
  with self.assertRaises(AssertionError):gate.validate_local_pending_receipt(r)
if __name__=='__main__':unittest.main()
