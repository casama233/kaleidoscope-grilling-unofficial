"""G86 is the exact public palette/plate union, not inherited client acceptance."""
from pathlib import Path
import hashlib,json,subprocess,unittest,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PALETTE_SOURCE_BASE='c85cb34f591079c0b06878b8e565e7f262833e49'
PLATE_SOURCE_BASE='07208cd8b8a047ed3e5be9a38596054b1818dcdc'
UNION_SOURCE_BASE='6e714853d029f93f0186efa2e96e192e87735a74'
PROJECT='projects/grilling/gameplay_core/'
PALETTES={PROJECT+f'resource_pack/textures/secret_food_palette/food_100_{i}.png' for i in range(7)}
def source(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT)
def files(ref,prefix):
 return {line.split('\t',1)[1]:line.split('\t',1)[0].split()[2] for line in subprocess.check_output(['git','ls-tree','-r',ref,'--',prefix],cwd=ROOT,text=True).splitlines()}
def git_blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
# Every later runtime exception must carry an exact reviewed preimage/postimage.
G87_DELTAS={
 PROJECT+'behavior_pack/scripts/a25_plate_recipe_runtime.js':'g87-plate-use-reviewed-delta.json',
 PROJECT+'behavior_pack/scripts/station_contents_visual_runtime.js':'g87-plate-yaw-reviewed-delta.json'
}
def apply_runtime_delta(before,path,filename):
 d=json.loads((ROOT/'tools/fixtures'/filename).read_text())
 assert d['schema']==1 and d['release']==[2,8,87] and d['path']==path
 assert hashlib.sha256(before).hexdigest()==d['before_sha256']
 text=before.decode('utf-8');ops=d['operations']
 assert ops and all(0<=o['start']<=o['end']<=len(text) for o in ops)
 assert all(a['end']<=b['start'] for a,b in zip(ops,ops[1:]))
 for o in reversed(ops):
  assert text[o['start']:o['end']]==o['before']
  text=text[:o['start']]+o['after']+text[o['end']:]
 result=text.encode('utf-8');assert hashlib.sha256(result).hexdigest()==d['after_sha256']
 return result

class SourceCoherence(unittest.TestCase):
 def test_complete_runtime_is_exact_plate_source_plus_seven_palette_substitutions(self):
  version=tuple(json.loads((ROOT/'baseline.json').read_text())['version'])
  for side in ['behavior_pack','resource_pack']:
   prefix=PROJECT+side+'/'
   expected=files(PLATE_SOURCE_BASE,prefix)
   frozen=files(UNION_SOURCE_BASE,prefix) if version>(2,8,86) else None
   if frozen is not None:self.assertEqual(set(frozen),set(expected),'Frozen G86 missing/extra runtime file')
   current={p.relative_to(ROOT).as_posix():p for p in (ROOT/prefix).rglob('*') if p.is_file()}
   self.assertEqual(set(current),set(expected),'Missing/extra runtime file')
   for path,p in current.items():
    if path.endswith('/manifest.json'):continue
    ref=PALETTE_SOURCE_BASE if path in PALETTES else PLATE_SOURCE_BASE
    sha=files(ref,path)[path] if path in PALETTES else expected[path]
    self.assertEqual(frozen[path] if frozen is not None else git_blob(p.read_bytes()),sha,path)
 def test_original_palette_inputs_attribution_and_importer_survive_exactly(self):
  paths=['development/gameplay_core/fixtures/secret-food-palettes.json','projects/grilling/ATTRIBUTION.md','tools/import_java_cookery_palettes.py','docs/STATUS-A2.8.82.md']
  paths+=list(files(PALETTE_SOURCE_BASE,'development/gameplay_core/fixtures/java-cookery-palette-160/'))
  for path in paths:self.assertEqual((ROOT/path).read_bytes(),source(PALETTE_SOURCE_BASE,path),path)
 def test_retained_original_changed_sprite_proves_the_16_cell_palette(self):
  sys.path.insert(0,str(ROOT/'tools'))
  from secret_food_palette import sample_grid
  proof=json.loads((ROOT/'development/gameplay_core/fixtures/java-cookery-palette-160/source.json').read_text())
  row=next(r for r in proof['items'] if r['id']=='kaleidoscope_cookery:suspicious_stir_fry')
  image=ROOT/'development/gameplay_core/fixtures/java-cookery-palette-160/changed/suspicious_stir_fry.png'
  self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(),row['sources']['Forge1.20.1']['texture_sha256'])
  self.assertEqual(sample_grid(Image.open(image).convert('RGBA')),row['palette'])
  samples=json.loads((ROOT/'development/gameplay_core/fixtures/secret-food-palettes.json').read_text())
  actual=next(r for r in samples['items'] if r['id']==row['id'])
  self.assertEqual(actual['index'],100);self.assertEqual(actual['palette'],row['palette'])
 def test_both_histories_are_append_only_and_fresh_identity_is_86(self):
  now=json.loads((ROOT/'release-history.json').read_text())
  for ref in [PALETTE_SOURCE_BASE,PLATE_SOURCE_BASE]:
   for version,value in json.loads(source(ref,'release-history.json')).items():self.assertEqual(now[version],value,version)
  version=tuple(json.loads((ROOT/'baseline.json').read_text())['version'])
  self.assertGreaterEqual(version,(2,8,86))
  frozen=source(UNION_SOURCE_BASE,'baseline.json') if version>(2,8,86) else (ROOT/'baseline.json').read_bytes()
  self.assertEqual(json.loads(frozen)['version'],[2,8,86])
 def test_current_runtime_differs_from_frozen_g86_only_by_exact_reviewed_deltas(self):
  version=tuple(json.loads((ROOT/'baseline.json').read_text())['version'])
  if version<(2,8,87):self.skipTest('G87 runtime delta applies only after fresh release identity admission')
  for side in ['behavior_pack','resource_pack']:
   prefix=PROJECT+side+'/'
   expected=files(UNION_SOURCE_BASE,prefix)
   current={p.relative_to(ROOT).as_posix():p for p in (ROOT/prefix).rglob('*') if p.is_file()}
   self.assertEqual(set(current),set(expected),'Missing/extra runtime file after G86')
   for path,p in current.items():
    if path.endswith('/manifest.json'):continue
    if path in G87_DELTAS:
     data=apply_runtime_delta(source(UNION_SOURCE_BASE,path),path,G87_DELTAS[path])
     self.assertEqual(p.read_bytes(),data,path)
    else:self.assertEqual(git_blob(p.read_bytes()),expected[path],path)
if __name__=='__main__':unittest.main()
