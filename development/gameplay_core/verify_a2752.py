from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
FOODS={
 'potato_beef_stew':(12,.9,16,'b702c0e0b1960d1374d8b52aee9b81fe0c50a30c'),
 'red_sweet_potato_porridge':(14,.071429,16,'3802ce2611ce23c51b6b776f0646651c79d71f47'),
 'sour_spicy_noodles':(10,.6,16,'026fe88aa24d0f5161c6376617d6e76aaa0e89dd'),
}
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
 assert bm['header']['version']==[2,7,52] and rm['header']['version']==[2,7,52]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.52 Cookery Stockpot Cuisine BP'

 core=BP/'scripts/a2752_stockpot_food_core.js'
 assert core.read_bytes()==(DEV/'a2752_stockpot_food_core.js').read_bytes()

 for name,(nutrition,sat,max_stack,sha) in FOODS.items():
  item=load(BP/f'items/{name}.json')['minecraft:item'];c=item['components']
  assert item['description']['identifier']=='kaleidoscope_grilling:'+name
  assert c['minecraft:max_stack_size']==max_stack
  assert c['minecraft:food']=={'can_always_eat':False,'nutrition':nutrition,'saturation_modifier':sat}
  tex=RP/f'textures/items/{name}.png';assert tex.is_file() and blob(tex)==sha,(name,blob(tex),sha)
  assert load(RP/'textures/item_texture.json')['texture_data'][name]['textures']=='textures/items/'+name

 catalog=load(BP/'item_catalog/crafting_item_catalog.json')
 items=catalog['minecraft:crafting_items_catalog']['categories'][0]['groups'][0]['items']
 for name in FOODS:assert items.count('kaleidoscope_grilling:'+name)==1,name

 host=(BP/'scripts/a2727_cookery_host_recipes_core.js').read_text(encoding='utf-8')
 for token in (
  "import {stockpotRecipes} from './a2752_stockpot_food_core.js';",
  'function stockpot(recipe)','...stockpotRecipes().map(stockpot)',
  'requiresItems','availableItems'
 ):assert token in host,token
 assert host.count('function stockpot(recipe)')==1
 publisher=(BP/'scripts/a2727_cookery_host_recipes_runtime.js').read_text(encoding='utf-8')
 for token in ('ItemTypes','TAVERN_VINEGAR_IDS','optionalRecipeItems()','availableItems:optionalRecipeItems()'):
  assert token in publisher,token
 assert publisher.count('system.afterEvents.scriptEventReceive.subscribe')==1
 assert publisher.count('system.sendScriptEvent(KC_PING_EVENT,SOURCE)')==1

 effects=(BP/'scripts/a2732_standalone_food_effect_core.js').read_text(encoding='utf-8')
 for token in ("stockpotEffectRows","...stockpotEffectRows()","itemId:WEDDING_CANDY_ID","pepperHoneyEffectRow()"):
  assert token in effects,token
 standalone=(BP/'scripts/a2732_standalone_food_effect_runtime.js').read_text(encoding='utf-8')
 assert standalone.count('itemCompleteUse.subscribe')==1

 main=(BP/'scripts/main.js').read_text(encoding='utf-8')
 for token in (
  "import {STOCKPOT_FOOD_IDS} from './a2752_stockpot_food_core.js';",
  'CUISINE_EATS=new Map()','CUISINE_FOOD_SET=new Set([...WOK_FOOD_IDS,...STOCKPOT_FOOD_IDS])',
  'CUISINE_EATS.set(','CUISINE_EATS.delete(','CUISINE_FOOD_SET.has(id)'
 ):assert token in main,token
 assert 'WOK_EATS' not in main and 'WOK_FOOD_SET' not in main
 assert main.count('world.afterEvents.itemCompleteUse.subscribe')==1
 assert "import './a2750_cookery_cuisine_runtime.js';" in main

 cuisine=BP/'scripts/a2750_cookery_cuisine_runtime.js'
 assert cuisine.read_bytes()==(DEV/'a2750_cookery_cuisine_runtime.js').read_bytes()
 cuisine_text=cuisine.read_text(encoding='utf-8')
 assert 'COOKERY_STOCKPOT_ID' in cuisine_text and 'metadataPlan' in cuisine_text
 assert 'kc_station:' not in cuisine_text and 'itemCompleteUse.subscribe' not in cuisine_text

 # Prior slices must still be present.
 for path in (
  BP/'items/houttuynia_stir_fried_pork.json',BP/'items/green_pepper_squid_tentacles.json',
  BP/'items/braised_chicken_wings.json',BP/'items/pepper_honey.json',BP/'items/wedding_candy.json',
  BP/'blocks/pepper_log.json'
 ):assert path.is_file(),path

 for lang in ('en_US.lang','zh_CN.lang','zh_TW.lang'):
  lines=(RP/'texts'/lang).read_text(encoding='utf-8').splitlines()
  for key in LANG_KEYS:assert sum(1 for row in lines if row.startswith(key+'='))==1,(lang,key)

 subprocess.run(['node',str(DEV/'test_a2752_core.mjs')],check=True)
 subprocess.run(['node',str(DEV/'test_a2752_host_core.mjs')],check=True)
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 report=load(P/'reports/a2752-cookery-stockpot-cuisine.json')
 assert report['version']=='A2.7.52'
 assert len(report['foods'])==3
 assert report['recipes']=={'stockpot_exact':3,'stockpot_flex':3}
 assert report['cookery_host']['single_recipe_publisher'] is True
 assert report['cookery_host']['private_kc_station_access'] is False
 assert report['tavern']['java_optional_mod_condition_preserved'] is True
 assert len(report['tavern']['bedrock_quality_ids'])==6
 assert report['tavern']['duplicate_vinegar_created'] is False
 assert report['effects']['red_sweet_potato_porridge']=={'flatulence':900,'warmth':900}
 assert report['effects']['sour_spicy_noodles']=={'warmth':900}
 assert report['shared_state']['cuisine_eat_map_unified'] is True
 assert report['shared_state']['new_item_complete_use_listener'] is False
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
  'version':'A2.7.52','cookery_stockpot_cuisine':True,'stockpot_foods':3,
  'stockpot_exact':3,'stockpot_flex':3,'single_recipe_publisher':True,
  'tavern_vinegar_quality_adapter':True,'shared_cuisine_bridge':True,
  'shared_standalone_effect_runtime':True,'new_item_complete_use_listener':False,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2752-dash-verification.json' if a.compiled else 'a2752-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
