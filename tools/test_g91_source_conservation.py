"""Only the three Cloud reads and paired identity can follow frozen G90."""
import copy,json
from pathlib import Path
import unittest
from unittest.mock import patch
import g91_source_conservation as witness
import g92_source_conservation as current

class CloudSourceConservation(unittest.TestCase):
 def test_frozen_g90_is_validated_before_the_exact_current_delta(self):
  self.assertEqual(witness.previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)['runtime_files'],4155)
  result=witness.verify_snapshot(current.FROZEN_SOURCE_BASE);self.assertEqual(result['reviewed_paths'],5)
  self.assertEqual(witness.verify_current()['reviewed_paths'],6)
  self.assertEqual(set(witness.metadata()['files']),witness.DELTA_PATHS)

 def test_cloud_changes_only_the_three_inherited_coalescers(self):
  before=witness.source(witness.CLOUD_PATH);after=(witness.ROOT/witness.CLOUD_PATH).read_bytes()
  self.assertEqual(after,witness.corrected_cloud(before))
  for axis in 'xyz':
   self.assertEqual(before.count(('((variable.kg_velocity.'+axis+' ?? 0)/20)').encode()),1)
   self.assertEqual(after.count(('(variable.kg_velocity.'+axis+'/20)').encode()),1)
  self.assertNotIn(b'??',after)
  path=witness.PROJECT+'behavior_pack/scripts/immersion_particles_runtime.js'
  self.assertEqual((witness.ROOT/path).read_bytes(),witness.source(path))

 def test_cloud_other_runtime_and_manifest_mutations_are_rejected(self):
  original=Path.read_bytes
  for path in [witness.CLOUD_PATH,*witness.MANIFESTS,witness.PROJECT+'behavior_pack/scripts/main.js',witness.PROJECT+'resource_pack/attachables/skewer_plate.attachable.json']:
   with patch.object(Path,'read_bytes',lambda p:original(p)+b'\n' if p==witness.ROOT/path else original(p)):
    with self.assertRaisesRegex(AssertionError,'Runtime source drift'):witness.verify_current()

 def test_reviewed_metadata_cannot_admit_wrong_divisor_or_extra_scope(self):
  original=Path.read_text;meta=witness.metadata();before=witness.source(witness.CLOUD_PATH)
  changed=copy.deepcopy(meta);after=witness.corrected_cloud(before).replace(b'variable.kg_velocity.x/20',b'variable.kg_velocity.x/10')
  changed['files'][witness.CLOUD_PATH]['operations']=[{'start':0,'end':len(before.decode()),'before':before.decode(),'after':after.decode()}]
  changed['files'][witness.CLOUD_PATH]['after_sha256']=witness.sha(after)
  variants=[changed]
  changed=copy.deepcopy(meta);changed['files'][witness.HELD_WRITER_PATH]['after_sha256']='0'*64;variants.append(changed)
  changed=copy.deepcopy(meta);changed['held_review']['patch_sha256']='0'*64;variants.append(changed)
  changed=copy.deepcopy(meta);changed['files'][witness.PROJECT+'behavior_pack/scripts/main.js']=copy.deepcopy(changed['files'][witness.CLOUD_PATH]);variants.append(changed)
  changed=copy.deepcopy(meta);changed['base_commit']='0'*40;variants.append(changed)
  for changed in variants:
   def read(path,*args,**kwargs):return json.dumps(changed) if path.name=='g91-cloud-reviewed-delta.json' else original(path,*args,**kwargs)
   with patch.object(Path,'read_text',read):
    with self.assertRaises(AssertionError):witness.apply_delta(witness.CLOUD_PATH)

 def test_held_diagnostic_and_fp_deltas_are_exact_reviewed_patch_bytes(self):
  for path,digest in witness.HELD_REVIEWED_AFTER.items():
   after=witness.apply_delta(path);self.assertEqual(witness.sha(after),digest)
   self.assertEqual(current.source(path),after)
  path=witness.PROJECT+'resource_pack/models/entity/plate_held.geo.json'
  self.assertEqual((witness.ROOT/path).read_bytes(),witness.source(path))

 def test_manifest_delta_cannot_change_other_fields(self):
  original=Path.read_text;changed=copy.deepcopy(witness.metadata());path=next(iter(witness.MANIFESTS));before=witness.source(path)
  after=json.loads(witness.apply_delta(path));after['header']['uuid']='00000000-0000-0000-0000-000000000000'
  after=(json.dumps(after,ensure_ascii=False,indent=2)+'\n').encode()
  changed['files'][path]['operations']=[{'start':0,'end':len(before.decode()),'before':before.decode(),'after':after.decode()}]
  changed['files'][path]['after_sha256']=witness.sha(after)
  def read(p,*args,**kwargs):return json.dumps(changed) if p.name=='g91-cloud-reviewed-delta.json' else original(p,*args,**kwargs)
  with patch.object(Path,'read_text',read):
   with self.assertRaisesRegex(AssertionError,'paired G91 identity'):witness.apply_delta(path)

if __name__=='__main__':unittest.main()
