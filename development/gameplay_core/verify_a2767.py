"""Data-only server-schema release; runtime gameplay bytes are locked to A2.7.66."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/'projects/grilling/gameplay_core'
DEV=Path(__file__).resolve().parent
BASELINE='5ea4764f782be5ff6f22fb29b16ddaa4af280830e1898db7662362d77188b9f3'
GATES={'oil_press':'minecraft:iron_ingot','advanced_rack':'minecraft:iron_ingot','oak_planks_from_pepper_log':'kaleidoscope_grilling:pepper_log','big_vat':'minecraft:brick_block','secret_chili_oil':'kaleidoscope_grilling:canola_oil_bucket','pepper_honey':'kaleidoscope_grilling:sichuan_pepper','oil_cake':'kaleidoscope_grilling:canola_powder','sugared_tomato':'kaleidoscope_cookery:tomato'}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def norm(v):
 if isinstance(v,dict):return {k:norm(x) for k,x in v.items()}
 if isinstance(v,list):return [norm(x) for x in v]
 if isinstance(v,float) and v.is_integer():return int(v)
 return v
def method(m,k,seen=frozenset()):
 assert k not in seen,('material alias cycle',k)
 row=m[k]
 return method(m,row,seen|{k}) if isinstance(row,str) else row.get('render_method','opaque')
def check_schema(project=PROJECT,expected_version=(2,7,67)):
 bp=project/'behavior_pack';rp=project/'resource_pack'
 for side in (bp,rp):assert load(side/'manifest.json')['header']['version']==list(expected_version)
 blocks={};maps=0;placers=0
 for p in sorted((bp/'blocks').glob('*.json')):
  b=load(p)['minecraft:block'];bid=b['description']['identifier']
  assert isinstance(bid,str) and ':' in bid and bid not in blocks,(p,bid)
  blocks[bid]=p
  base=b.get('components',{});variants=[base]+[dict(base,**row.get('components',{})) for row in b.get('permutations',[])]
  for c in variants:
   for m in (c.get('minecraft:material_instances'),c.get('minecraft:item_visual',{}).get('material_instances')):
    if m is not None:
     modes={method(m,k) for k in m};assert len(modes)==1,(p,modes);maps+=1
 for p in (bp/'items').glob('*.json'):
  placer=load(p)['minecraft:item']['components'].get('minecraft:block_placer')
  if placer:
   bid=placer.get('block');assert isinstance(bid,str) and ':' in bid,(p,bid)
   if bid.startswith('kaleidoscope_grilling:'):assert bid in blocks,(p,bid)
   placers+=1
 recipes=0
 for p in (bp/'recipes').glob('*.json'):
  j=load(p);r=j.get('minecraft:recipe_shaped') or j.get('minecraft:recipe_shapeless')
  if r:
   assert r.get('unlock'),('missing unlock',p);recipes+=1
   if p.stem in GATES:
    assert r['unlock']==[{'item':GATES[p.stem]}]
    ingredients=list(r.get('key',{}).values())+r.get('ingredients',[])
    assert any(row.get('item')==GATES[p.stem] for row in ingredients)
 # Prove this release changes no other runtime semantics, including scripts,
 # textures, model IDs, gameplay and saved-data formats. Formatting is ignored
 # for JSON only; every non-JSON file retains exact bytes.
 h=hashlib.sha256();count=0;vat_maps=0;unlock_count=0
 for prefix in ('behavior_pack','resource_pack'):
  for p in sorted((project/prefix).rglob('*')):
   if not p.is_file() or p.name.startswith('.') or p.name=='manifest.json':continue
   rel=p.relative_to(project).as_posix();data=p.read_bytes()
   if p.suffix=='.json':
    j=load(p)
    if rel==f'behavior_pack/recipes/{p.stem}.json' and p.stem in GATES:
     r=j.get('minecraft:recipe_shaped') or j['minecraft:recipe_shapeless'];assert r.pop('unlock')==[{'item':GATES[p.stem]}];unlock_count+=1
    if rel=='behavior_pack/blocks/big_vat.json':
     b=j['minecraft:block']
     for c in [b['components'],*[row['components'] for row in b['permutations']]]:
      if 'minecraft:material_instances' in c:
       m=c['minecraft:material_instances'];assert m['*']['render_method']==m['fluid']['render_method']=='blend'
       m['*']['render_method']='alpha_test';vat_maps+=1
    data=json.dumps(norm(j),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
   h.update((rel+'\0').encode());h.update(hashlib.sha256(data).digest());count+=1
 assert (count,vat_maps,unlock_count)==(1239,6,8),(count,vat_maps,unlock_count)
 assert h.hexdigest()==BASELINE,('unexpected runtime drift',h.hexdigest())
 return {'version':'A'+'.'.join(map(str,expected_version)),'blocks':len(blocks),'materialMaps':maps,'blockPlacers':placers,'craftingRecipesWithUnlock':recipes,'newUnlocks':8,'vatMapsCorrected':6,'baselineRuntimeFilesPreservedExceptDeclaredChanges':count,'minecraft_tested':False,'bds_tested':False,'client_visuals_tested':False,'blankRegistryErrorAttributed':False}
def main(expected_version=(2,7,67)):
 parser=argparse.ArgumentParser();parser.add_argument('--compiled',action='store_true');args=parser.parse_args()
 from verify_a2766 import check_assets
 check_assets();result=check_schema(expected_version=expected_version)
 subprocess.run([sys.executable,str(DEV/'a2764_rebake_skewer_hand_geometry.py'),'--check'],check=True)
 subprocess.run([sys.executable,str(DEV/'verify_a2761_java_interaction_contract.py')],check=True)
 for name in ('test_a275_core.mjs','test_a276_core.mjs','test_a277_core.mjs','test_a2762_core.mjs'):
  subprocess.run(['node',str(DEV/name)],check=True)
 for p in (PROJECT/'behavior_pack/scripts').rglob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
