from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]
EXPECTED_ITEMS={
'beef_chunks':'6b9a7d3f3b153ab42c0f725abc34b4b56003c5e1','braised_chicken_wings':'849984b12af4346a276ed1db03ee0ff70a6ef62c',
'canola_seeds':'89a7008164006a16dcd194ce27b6e5c165b14987','carrot_dice':'c5359f186611411d51f1fe55077357d2c16efa61',
'chicken_skin':'5a8517468ed9da877b219047e1032d3a4c728bfc','chicken_wing':'4adb1a131eb7f0dda0ed43f616e1dd561c7b3e71',
'cold_houttuynia':'98d59596cc06892e78d6d90d3e8ed2303151f841','green_pepper_squid_tentacles':'cd66ab879f3c1818ea2f149955945ce6e6bb22ff',
'houttuynia':'40afc94ae7826ddb7cb5a8cd106434a6745dfe25','houttuynia_stir_fried_pork':'12c3d37ecee6b20598265e0511e391bd39330a4f',
'minced_houttuynia':'c6653c730bb5d1fefab02db05388b0f2e6aefc30','onion':'103aa78661bf35aa6b3a42989a398573056faff1',
'pepper_honey':'0a629329dce3bd29c7d56baa5d2ebbf5693d6f6a','potato_beef_stew':'b702c0e0b1960d1374d8b52aee9b81fe0c50a30c',
'potato_slice':'9562676753ad5e32ea0e1345236e314ad4767b85','raw_mantou_slice':'c89c916e0611d7de9d821e122b2d88c099809cbf',
'raw_sweet_potato_sheet':'a537de022aa9cc50b99dfec6f0fedd0046cb2d2f','red_chili_powder':'57936897efae12b743a539f0bf1dac54d45dda39',
'red_sweet_potato_porridge':'3802ce2611ce23c51b6b776f0646651c79d71f47','roasted_chicken_wing':'88d0b45b57a7958f185f9b292eda18d5b57dac42',
'roasted_sweet_potato':'cc8bda808a99d38ecdae90a78a3acf6b7c0dea9a','sour_spicy_noodles':'026fe88aa24d0f5161c6376617d6e76aaa0e89dd',
'squid_tentacle':'60aab20cf2c9c4b250780430f7114c22ae7b9dff','sugared_tomato':'da58483560e98eaeb3abc24973f0c1b247931c65',
'sweet_potato':'6761c2d89d46df2e536dd6df3fe9fdb7c2262259','sweet_potato_powder':'2e15c9ea095ff0ef7c7959b05bd9f60d79631dab',
'wedding_candy':'d7ca9f5dfa61d6658372d8e181283fb5bf756d78'
}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(p):
 v=p.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,0] and rm['header']['version']==[2,7,0]
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 for name,sha in EXPECTED_ITEMS.items():
  p=BP/f'items/{name}.json';d=load(p)['minecraft:item'];c=d['components']
  assert d['description']['identifier']=='kaleidoscope_grilling:'+name
  assert c['minecraft:max_stack_size'] in (16,64)
  if 'minecraft:food' in c:
   assert c['minecraft:use_modifiers']['start_using']=='always'
   assert c['minecraft:use_modifiers']['use_duration']==1.6
   assert c['minecraft:use_animation']['value']=='eat'
   assert 'minecraft:is_food' in c['minecraft:tags']['tags']
  assert blob(RP/f'textures/items/{name}.png')==sha,(name,blob(RP/f'textures/items/{name}.png'))

 candy=load(BP/'items/wedding_candy.json')['minecraft:item']['components']
 assert candy['minecraft:food']=={'can_always_eat':True,'nutrition':20,'saturation_modifier':0.5}
 powder=load(BP/'items/sweet_potato_powder.json')['minecraft:item']['components']
 assert powder['minecraft:use_modifiers']['use_duration']==1.5 and powder['minecraft:use_animation']['value']=='bow'

 # Native recipe reconciliation.
 big=load(BP/'recipes/big_vat.json')['minecraft:recipe_shaped'];assert big['key']['B']=={'item':'minecraft:brick'}
 grill=load(BP/'recipes/grill.json')['minecraft:recipe_shaped'];assert grill['key']['C']=={'tag':'minecraft:coals'} and grill['key']['B']=={'item':'minecraft:brick'}
 press=load(BP/'recipes/oil_press.json')['minecraft:recipe_shaped'];assert press['key']['L']=={'tag':'minecraft:logs'} and press['key']['F']=={'item':'minecraft:oak_fence'}
 pepper=load(BP/'recipes/pepper_honey.json')['minecraft:recipe_shapeless'];assert {'item':'minecraft:glass_bottle','count':1} in pepper['result']
 secret=load(BP/'recipes/secret_chili_oil.json')['minecraft:recipe_shapeless'];assert {'item':'minecraft:bucket','count':1} in secret['result']
 premium=load(BP/'recipes/premium_chili_oil.json')['minecraft:recipe_shapeless'];assert {'item':'minecraft:bucket','count':2} in premium['result']
 clear=load(BP/'recipes/clear_skewer_recipe_book.json')['minecraft:recipe_shapeless'];assert clear['result']['item']=='kaleidoscope_grilling:skewer_recipe_book'
 for q in ('clear_seasoning_pending.json','clear_seasoning_special.json','clear_seasoning_data_bottle.json'):assert (BP/'recipes'/q).is_file(),q
 for q in ('roasted_chicken_wing.json','roasted_sweet_potato.json'):
  d=load(BP/'recipes'/q)['minecraft:recipe_furnace'];assert d['tags']==['furnace','smoker','campfire','soul_campfire']

 source=load(ROOT/'development/gameplay_core/a27_recipe_sources.json');assert source['count']==61 and len(source['recipes'])==61
 report=load(P/'reports/a27-java-recipes.json')
 assert report['count']==61
 assert report['counts']=={'vanilla_direct':18,'cookery_machine':22,'tavern_conditional':2,'create_optional':16,'grilling_custom':3}
 assert report['core_cookery_catalog_count']==22 and report['cookery_runtime_registration_bound'] is False
 catalog=(BP/'scripts/a27_cookery_recipes.js').read_text(encoding='utf-8')
 prefix='export const A27_COOKERY_RECIPES=Object.freeze(';assert catalog.startswith(prefix) and catalog.endswith(');\n')
 rows=json.loads(catalog[len(prefix):-3]);assert len(rows)==22
 assert not any('sour_spicy_noodles' in x['path'] for x in rows)

 for name in ('a27_items_core.js','a27_recipe_core.js','a27_food_runtime.js','a27_dynamic_recipe_runtime.js','a27_cookery_recipes.js'):assert (BP/'scripts'/name).is_file(),name
 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert "import './a27_food_runtime.js';" in main and "import './a27_dynamic_recipe_runtime.js';" in main
 food=(BP/'scripts/a27_food_runtime.js').read_text(encoding='utf-8')
 for token in ('COOKERY_QUALITY_RATIOS','QUALITY_ID_KEY','adjustQualityFood','qualityFood'):assert token in (food+(BP/'scripts/a27_items_core.js').read_text(encoding='utf-8')),token
 dynamic=(BP/'scripts/a27_dynamic_recipe_runtime.js').read_text(encoding='utf-8')
 for token in ("premium_chili","countHout(p)>=3","consumePremiumOil(p,2)","new ItemStack(COLD,1)"):assert token in dynamic,token

 items=load(P/'reports/a27-items.json');assert items['java_registry_missing_after']==0 and items['java_registry_items_added']==27
 assert items['quality_aware_java_items']==11 and items['cookery_quality_storage_bound'] is False

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 for t in ('test_a24_core.mjs','test_a25_core.mjs','test_a26_core.mjs','test_a27_items.mjs','test_a27_recipes.mjs'):
  subprocess.run(['node',str(ROOT/'development/gameplay_core'/t)],check=True)

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source_pack in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source_pack/'manifest.json')
   matches=[p.parent for p in dist.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source_pack.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source_pack);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={'version':'A2.7.0','java_items_added':27,'java_registry_missing':0,'java_recipe_sources':61,
  'native_direct_class':18,'cookery_core_catalog':22,'tavern_conditional':2,'create_optional':16,'custom_serializers':3,
  'cookery_recipe_api_bound':False,'cookery_quality_storage_bound':False,'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a27-dash-verification.json' if a.compiled else 'a27-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
