"""Placed display contracts and preserved A2.7.69 gameplay regressions. Not in-game QA."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
BASE='600219d00fee8b12048dcfb6187d1d795abdd0dc'
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def run(*args):subprocess.run(args,cwd=ROOT,check=True)
def preserved():
 if subprocess.run(['git','cat-file','-e',BASE+'^{commit}'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:run('git','fetch','--depth=1','origin',BASE)
 prefix='projects/grilling/gameplay_core/'
 tree=subprocess.check_output(['git','ls-tree','-r','-z',BASE,'--',prefix+'behavior_pack',prefix+'resource_pack'],cwd=ROOT)
 allowed={'behavior_pack/manifest.json','resource_pack/manifest.json','behavior_pack/scripts/main.js','behavior_pack/scripts/a2743_seasoning_block_adapter.js','behavior_pack/scripts/a2739_cookery_oil_pot_block_adapter.js'}
 total=0
 for row in tree.split(b'\0'):
  if not row:continue
  header,path=row.split(b'\t',1);relative=path.decode()[len(prefix):];original=header.split()[2].decode()
  assert (P/relative).is_file(),('old runtime removed',relative)
  if relative not in allowed:
   assert blob((P/relative).read_bytes())==original,('unrelated runtime changed',relative);total+=1
 # The new renderer must never substitute gameplay block IDs or write container contents.
 runtime=(BP/'scripts/a2770_placed_visual_runtime.js').read_text()
 assert 'world.setDynamicProperty' not in runtime and '.setType(' not in runtime and '.setPermutation(' not in runtime
 assert 'minecraft:air' not in runtime
 return total

def entity_contracts():
 geometry={}
 for path in RP.rglob('*.geo.json'):
  for g in load(path).get('minecraft:geometry',[]):geometry[g['description']['identifier']]=g
 rc=load(RP/'render_controllers/a2770_placed.render_controllers.json')['render_controllers']
 for name in ('seasoning','oil'):
  b=load(BP/f'entities/a2770_placed_{name}.json')['minecraft:entity']
  c=load(RP/f'entity/a2770_placed_{name}.entity.json')['minecraft:client_entity']['description']
  assert b['description']['identifier']==c['identifier']
  assert b['description']['is_spawnable'] is False
  assert 'minecraft:transient' in b['components']
  assert b['components']['minecraft:collision_box']=={'width':0,'height':0}
  assert b['components']['minecraft:physics']=={'has_gravity':False,'has_collision':False}
  assert not any(k in b['components'] for k in ('minecraft:loot','minecraft:inventory','minecraft:interact'))
  props=b['description']['properties'];assert len(props)<=32 and all(x['client_sync'] for x in props.values())
  for g in c['geometry'].values():
   assert g in geometry
   for bone in geometry[g]['bones']:
    assert 'binding' not in bone
    for cube in bone.get('cubes',[]):assert min(cube['size'])>0
  for texture in c['textures'].values():assert (RP/(texture+'.png')).is_file(),texture
  for item in c['render_controllers']:
   identifier=next(iter(item));assert identifier in rc
   text=json.dumps(rc[identifier])+json.dumps(item)
   for prop in re.findall(r"q\.property\('([^']+)'\)",text):assert prop in props,(identifier,prop)
   for alias in re.findall(r'Geometry\.([a-zA-Z0-9_]+)',text):assert alias in c['geometry'],alias
   for alias in re.findall(r'Texture\.([a-zA-Z0-9_]+)',text):assert alias in c['textures'],alias
   for alias in re.findall(r'Material\.([a-zA-Z0-9_]+)',text):assert alias in c['materials'],alias
 # No missing reference or accidental duplicated glass shell in the new filled-bottle geometry.
 special=[g for id,g in geometry.items() if id.startswith('geometry.kg_a2770.seasoning.')]
 assert len(special)==40
 for g in special:
  cubes=g['bones'][0]['cubes'];assert len(cubes)==1
  assert cubes[0]['origin']==[-2.5,.5,-2.5]
 return len(rc)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--compiled',action='store_true');args=parser.parse_args()
 assert load(BP/'manifest.json')['header']['version']==[2,7,70]
 assert load(RP/'manifest.json')['header']['version']==[2,7,70]
 assert 'pbr' in load(RP/'manifest.json')['capabilities']
 assert not (ROOT/'.github/workflows/placed-visual-bootstrap.yml').exists(),'one-shot bootstrap must be archived before integration'
 from verify_a2769 import source_guards,java_contract
 from verify_a2766 import check_assets
 kept=preserved();materials=source_guards((2,7,70));java_contract();assets=check_assets();controllers=entity_contracts()
 run(sys.executable,str(DEV/'a2770_placed_visual_assets.py'),'--check')
 run(sys.executable,str(DEV/'a2764_rebake_skewer_hand_geometry.py'),'--check')
 run(sys.executable,str(DEV/'test_vibrant_gate.py'))
 run(sys.executable,str(DEV/'verify_a2761_java_interaction_contract.py'))
 for test in ('test_a275_core.mjs','test_a276_core.mjs','test_a277_core.mjs','test_a2762_core.mjs','test_a2769_core.mjs','test_a2770_core.mjs'):run('node',str(DEV/test))
 for path in (BP/'scripts').rglob('*.js'):run('node','--check',str(path))
 report=load(P/'reports/a2770-placed-visuals.json')
 assert report['version']=='A2.7.70'
 assert not any(report[x] for x in ('minecraft_tested','bds_tested','client_visuals_tested'))
 print(json.dumps({'version':'A2.7.70','preserved_runtime_files':kept,'material_maps':materials,'placed_render_controllers':controllers,'visual_rules':16,'assets':assets,'compiled_requested':args.compiled,'minecraft_tested':False,'bds_tested':False,'client_visuals_tested':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
