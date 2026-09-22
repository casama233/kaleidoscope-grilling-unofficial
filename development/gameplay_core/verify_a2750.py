from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
FOODS={
 'houttuynia_stir_fried_pork':(9,.7,16,'12c3d37ecee6b20598265e0511e391bd39330a4f'),
 'green_pepper_squid_tentacles':(8,.6,16,'cd66ab879f3c1818ea2f149955945ce6e6bb22ff'),
 'braised_chicken_wings':(10,.8,16,'849984b12af4346a276ed1db03ee0ff70a6ef62c'),
}
NEW=(
 'a2750_wok_food_core.js','a2750_food_state_adapter.js',
 'a2750_cookery_cuisine_core.js','a2750_cookery_cuisine_runtime.js',
)
LANG_KEYS=tuple(
 key for name in FOODS
 for key in (f'item.kaleidoscope_grilling:{name}.name',f'tooltip.kaleidoscope_grilling.{name}.maxim')
)

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,50] and rm['header']['version']==[2,7,50]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.50 Cookery Wok Cuisine BP'

 for name in NEW:assert (BP/'scripts'/name).read_bytes()==(DEV/name).read_bytes(),name

 for name,(nutrition,sat,max_stack,sha) in FOODS.items():
  item=load(BP/f'items/{name}.json')['minecraft:item'];c=item['components']
  assert item['description']['identifier']=='kaleidoscope_grilling:'+name
  assert c['minecraft:max_stack_size']==max_stack
  assert c['minecraft:food']=={'can_always_eat':False,'nutrition':nutrition,'saturation_modifier':sat}
  tex=RP/f'textures/items/{name}.png';assert tex.is_file() and blob(tex)==sha,(name,blob(tex),sha)
  assert load(RP/'textures/item_texture.json')['texture_data'][name]['textures']=='textures/items/'+name

 catalog=load(BP/'item_catalog/crafting_item_catalog.json')
 rows=catalog['minecraft:crafting_items_catalog']['categories'][0]['groups'][0]['items']
 for name in FOODS:assert rows.count('kaleidoscope_grilling:'+name)==1,name

 host=(BP/'scripts/a2727_cookery_host_recipes_core.js').read_text(encoding='utf-8')
 assert host.count("import {wokRecipes} from './a2750_wok_food_core.js';")==1
 assert host.count("capability:'wok'")==1
 assert host.count('...wokRecipes().map(wok)')==1
 assert 'wok_flex' not in host
 publisher=(BP/'scripts/a2727_cookery_host_recipes_runtime.js').read_text(encoding='utf-8')
 assert publisher.count('system.afterEvents.scriptEventReceive.subscribe')==1
 assert publisher.count('system.sendScriptEvent(KC_PING_EVENT,SOURCE)')==1

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 for token in (
  "from './a2750_food_state_adapter.js';","import {WOK_FOOD_IDS} from './a2750_wok_food_core.js';",
  "import './a2750_cookery_cuisine_runtime.js';",'WOK_EATS=new Map()','WOK_FOOD_SET=new Set(WOK_FOOD_IDS)',
  'WOK_EATS.set(','WOK_EATS.delete(','afterCommitted(e.source,id,a.meta,a,true);return;'
 ):assert token in main,token
 for forbidden in (
  "const HOT_UNTIL_KEY='kaleidoscope_grilling:hot_until'",
  'function readSeasonings(stack)','function setSeasonings(stack,list)','function bucketHot(until)',
  'function setHot(stack,ticks)','function hotUntil(stack)','function isHot(stack)','function refreshHotLore(stack)'
 ):assert forbidden not in main,forbidden
 assert "itemId:WEDDING_CANDY_ID" in (BP/'scripts/a2732_standalone_food_effect_core.js').read_text(encoding='utf-8')
 assert 'pepperHoneyEffectRow()' in (BP/'scripts/a2732_standalone_food_effect_core.js').read_text(encoding='utf-8')
 assert (BP/'blocks/pepper_log.json').is_file() and (BP/'blocks/pepper_leaves.json').is_file()

 adapter=(BP/'scripts/a2750_food_state_adapter.js').read_text(encoding='utf-8')
 for token in ('HOT_UNTIL_KEY','readFoodSeasonings','setFoodSeasonings','setHotFood','hotUntil','isHotFood','refreshHotLore','applyFoodMetadata'):
  assert token in adapter,token
 cuisine=(BP/'scripts/a2750_cookery_cuisine_runtime.js').read_text(encoding='utf-8')
 for token in ('COOKERY_POT_ID','planSeasoningUse','readCookeryOilPot','inventoryGains','applyFoodMetadata','hostHasOil'):
  assert token in cuisine,token
 for forbidden in ('kc_station:','register_recipe','api_ready','itemCompleteUse.subscribe','system.afterEvents.scriptEventReceive.subscribe'):
  assert forbidden not in cuisine,forbidden

 standalone=(BP/'scripts/a2732_standalone_food_effect_runtime.js').read_text(encoding='utf-8')
 assert standalone.count('itemCompleteUse.subscribe')==1

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  lines=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in lines if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2750_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2750-cookery-wok-cuisine.json')
 assert report['version']=='A2.7.50'
 assert len(report['foods'])==3
 assert report['cookery_host']['public_wok_extension_api'] is True
 assert report['cookery_host']['private_kc_station_access'] is False
 assert report['cookery_host']['duplicate_wok_station'] is False
 assert report['cookery_host']['java_flex_wok_exactly_available'] is False
 assert report['shared_state']['main_local_hot_parser_removed'] is True
 assert report['shared_state']['main_local_seasoning_parser_removed'] is True
 assert report['shared_state']['new_item_complete_use_listener'] is False
 assert report['shared_state']['hot_saturation_and_seasoning_eat_path_reused'] is True
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
  'version':'A2.7.50','cookery_wok_cuisine':True,'wok_foods':3,
  'single_recipe_publisher':True,'shared_food_state_adapter':True,
  'private_host_state_access':False,'wok_flex_faked':False,
  'wedding_candy_preserved':True,'pepper_honey_preserved':True,'pepper_tree_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2750-dash-verification.json' if a.compiled else 'a2750-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
