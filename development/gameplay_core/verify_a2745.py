from __future__ import annotations
from pathlib import Path
import argparse,json,re,subprocess,hashlib

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
FOODS=(
 'sugared_tomato','pepper_honey','wedding_candy','houttuynia_stir_fried_pork',
 'green_pepper_squid_tentacles','braised_chicken_wings','potato_beef_stew',
 'red_sweet_potato_porridge','sour_spicy_noodles',
)
EXACT_ASSET_BLOBS={
 'sugared_tomato':'da58483560e98eaeb3abc24973f0c1b247931c65',
 'pepper_honey':'0a629329dce3bd29c7d56baa5d2ebbf5693d6f6a',
 'houttuynia_stir_fried_pork':'12c3d37ecee6b20598265e0511e391bd39330a4f',
 'green_pepper_squid_tentacles':'cd66ab879f3c1818ea2f149955945ce6e6bb22ff',
 'braised_chicken_wings':'849984b12af4346a276ed1db03ee0ff70a6ef62c',
 'potato_beef_stew':'b702c0e0b1960d1374d8b52aee9b81fe0c50a30c',
 'red_sweet_potato_porridge':'3802ce2611ce23c51b6b776f0646651c79d71f47',
 'sour_spicy_noodles':'026fe88aa24d0f5161c6376617d6e76aaa0e89dd',
}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def git_blob(p):
 data=p.read_bytes()
 return hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,45] and rm['header']['version']==[2,7,45]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.45 P0 Cookery Cuisine BP'

 for name in (
  'a2745_p0_food_contract.js','a2745_cookery_cuisine_core.js',
  'a2745_food_state_adapter.js','a2745_cookery_cuisine_runtime.js',
 ):
  assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name
 assert (BP/'scripts/a2727_cookery_host_recipes_core.js').read_bytes()==(DEV/'a2745_refactored_a2727_cookery_host_recipes_core.js').read_bytes()
 assert (BP/'scripts/a2732_standalone_food_effect_core.js').read_bytes()==(DEV/'a2745_refactored_a2732_standalone_food_effect_core.js').read_bytes()

 for name in FOODS:
  item=load(BP/'items'/f'{name}.json')['minecraft:item']
  assert item['description']['identifier']=='kaleidoscope_grilling:'+name
  assert item['components']['minecraft:icon']['textures']['default']==name
  assert (RP/'textures/items'/f'{name}.png').is_file()
 for name,expected in EXACT_ASSET_BLOBS.items():
  assert git_blob(RP/'textures/items'/f'{name}.png')==expected,(name,git_blob(RP/'textures/items'/f'{name}.png'),expected)
 # Wedding Candy is intentionally a 16x16 first-frame extraction from the Java 16x48 animated strip.
 assert git_blob(RP/'textures/items/wedding_candy.png')=='59391575f81ced0e6ee40d29c8cc9aa80f6b2569'

 atlas=load(RP/'textures/item_texture.json')['texture_data']
 for name in FOODS:assert atlas[name]['textures']=='textures/items/'+name

 sugar=load(BP/'recipes/sugared_tomato.json')['minecraft:recipe_shapeless']
 assert sugar['ingredients']==[{'item':'kaleidoscope_cookery:tomato'},{'item':'minecraft:sugar'}]
 honey=load(BP/'recipes/pepper_honey.json')['minecraft:recipe_shapeless']
 assert sum(1 for x in honey['ingredients'] if x.get('item')=='kaleidoscope_grilling:sichuan_pepper')==3
 assert {'item':'minecraft:honey_bottle'} in honey['ingredients']

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 assert main_text.count("import './a2745_cookery_cuisine_runtime.js';")==1
 assert "from './a2745_food_state_adapter.js';" in main_text
 for forbidden in (
  "const HOT_UNTIL_KEY='kaleidoscope_grilling:hot_until'",
  'function readSeasonings(stack)','function setSeasonings(stack,list)',
  'function bucketHot(until)','function setHot(stack,ticks)','function hotUntil(stack)',
  'function isHot(stack)','function refreshHotLore(stack)',
 ):
  assert forbidden not in main_text,forbidden

 cuisine=(BP/'scripts/a2745_cookery_cuisine_runtime.js').read_text(encoding='utf-8')
 for token in (
  'COOKERY_POT_ID','COOKERY_STOCKPOT_ID','planSeasoningUse','readCookeryOilPot',
  'inventoryGains','applyFoodMetadata','hostHasOil','readCuisineExtensionState'
 ):
  assert token in cuisine,token
 for forbidden in ('kc_station:','register_recipe','api_ready','function wokRecipe','function stockInteract'):
  assert forbidden not in cuisine,forbidden

 publisher=(BP/'scripts/a2727_cookery_host_recipes_runtime.js').read_text(encoding='utf-8')
 assert publisher.count('system.afterEvents.scriptEventReceive.subscribe')==1
 assert publisher.count('KC_REGISTER_EVENT')>=1
 core=(BP/'scripts/a2727_cookery_host_recipes_core.js').read_text(encoding='utf-8')
 assert core.count("capability:'wok'")==1
 assert core.count("'stockpot_exact'")==3
 assert core.count("'stockpot_flex'")==3
 assert core.count("wok('kaleidoscope_grilling:wok/")==3
 assert 'wok_flex' not in core
 assert 'kaleidoscope_tavern:vinegar' in core

 effects=(BP/'scripts/a2732_standalone_food_effect_core.js').read_text(encoding='utf-8')
 assert "p0EffectRows" in effects
 for name in ('pepper_honey','wedding_candy','red_sweet_potato_porridge','sour_spicy_noodles'):
  assert name in (DEV/'a2745_p0_food_contract.js').read_text(encoding='utf-8')

 subprocess.run(['node',str(DEV/'test_a2745_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2745-p0-cookery-cuisine.json')
 assert report['version']=='A2.7.45'
 assert len(report['foods'])==9
 assert report['cookery_host']['public_extension_api'] is True
 assert report['cookery_host']['private_kc_station_access'] is False
 assert report['cookery_host']['duplicate_wok_or_stockpot'] is False
 assert report['integration']['special_seasoning'] is True
 assert report['integration']['pot_typed_oil_tracking'] is True
 assert report['integration']['output_seasoning_metadata'] is True
 assert report['host_boundaries']['java_flex_wok_exactly_available_in_kc_v1_api'] is False
 assert report['wedding_candy']['historical_date_distribution_event_included'] is False
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.45','p0_cookery_cuisine':True,'foods':9,
  'wok_strict':3,'stockpot_exact':3,'stockpot_flex':3,
  'shared_food_state_adapter':True,'special_seasoning':True,
  'typed_oil_tracking':True,'private_host_state_access':False,
  'java_flex_wok_api_boundary':True,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2745-dash-verification.json' if a.compiled else 'a2745-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
