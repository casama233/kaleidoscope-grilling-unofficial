"""G86 is the exact public palette/plate union, not inherited client acceptance."""
from pathlib import Path
import hashlib,json,subprocess,unittest,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PALETTE_SOURCE_BASE='c85cb34f591079c0b06878b8e565e7f262833e49'
PLATE_SOURCE_BASE='07208cd8b8a047ed3e5be9a38596054b1818dcdc'
PROJECT='projects/grilling/gameplay_core/'
PALETTES={PROJECT+f'resource_pack/textures/secret_food_palette/food_100_{i}.png' for i in range(7)}
def source(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT)
def files(ref,prefix):
 return {line.split('\t',1)[1]:line.split('\t',1)[0].split()[2] for line in subprocess.check_output(['git','ls-tree','-r',ref,'--',prefix],cwd=ROOT,text=True).splitlines()}
def git_blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
class SourceCoherence(unittest.TestCase):
 def test_complete_runtime_is_exact_plate_source_plus_seven_palette_substitutions(self):
  for side in ['behavior_pack','resource_pack']:
   prefix=PROJECT+side+'/'
   expected=files(PLATE_SOURCE_BASE,prefix)
   current={p.relative_to(ROOT).as_posix():p for p in (ROOT/prefix).rglob('*') if p.is_file()}
   self.assertEqual(set(current),set(expected),'Missing/extra runtime file')
   for path,p in current.items():
    if path.endswith('/manifest.json'):continue
    ref=PALETTE_SOURCE_BASE if path in PALETTES else PLATE_SOURCE_BASE
    sha=files(ref,path)[path] if path in PALETTES else expected[path]
    self.assertEqual(git_blob(p.read_bytes()),sha,path)
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
  self.assertEqual(json.loads((ROOT/'baseline.json').read_text())['version'],[2,8,86])
if __name__=='__main__':unittest.main()
