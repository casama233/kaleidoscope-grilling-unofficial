from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def body(text,name):
 marker=f'export function {name}'
 start=text.index(marker)
 brace=text.index('{',start)
 depth=0
 for i in range(brace,len(text)):
  if text[i]=='{':depth+=1
  elif text[i]=='}':
   depth-=1
   if depth==0:return text[brace:i+1]
 raise AssertionError(name)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,56] and rm['header']['version']==[2,7,56]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.56 P0 Official API Hardening BP'

 adapter=(BP/'scripts/a2750_food_state_adapter.js').read_text(encoding='utf-8')
 expected=(DEV/'a2756_refactored_a2750_food_state_adapter.js').read_text(encoding='utf-8')
 assert adapter==expected

 apply=body(adapter,'applyFoodMetadata')
 hot_i=apply.index('setHotFood(stack,hotTicks)')
 season_i=apply.index('setFoodSeasonings(stack,seasoning)')
 assert hot_i<season_i,(hot_i,season_i)
 hot=body(adapter,'setHotFood')
 assert hot.index('stack.setLore(lore)')<hot.index('stack.setDynamicProperty(HOT_UNTIL_KEY,until)')
 assert 'Official stable API' in apply

 cuisine=(BP/'scripts/a2750_cookery_cuisine_runtime.js').read_text(encoding='utf-8')
 assert 'applyFoodMetadata(custom,plan)' in cuisine
 assert 'world.beforeEvents.playerInteractWithBlock.subscribe' in cuisine
 assert 'system.run(()=>finishHostInteraction' in cuisine
 assert 'kc_station:' not in cuisine
 assert 'register_recipe' not in cuisine

 main_text=(BP/'scripts/main.js').read_text(encoding='utf-8')
 for token in (
  "import {WOK_FOOD_IDS} from './a2750_wok_food_core.js';",
  "import {STOCKPOT_FOOD_IDS} from './a2752_stockpot_food_core.js';",
  'const CUISINE_FOOD_SET=new Set([...WOK_FOOD_IDS,...STOCKPOT_FOOD_IDS]);',
  'CUISINE_EATS.set(','CUISINE_EATS.delete(',
  'afterCommitted(e.source,id,a.meta,a,true);return;'
 ):
  assert token in main_text,token

 host=(BP/'scripts/a2727_cookery_host_recipes_core.js').read_text(encoding='utf-8')
 assert "import {wokRecipes} from './a2750_wok_food_core.js';" in host
 assert "import {stockpotRecipes} from './a2752_stockpot_food_core.js';" in host
 assert "...wokRecipes().map(wok)" in host
 assert "...stockpotRecipes().map(stockpot)" in host
 assert 'kc_station:' not in host

 wok=(BP/'scripts/a2750_wok_food_core.js').read_text(encoding='utf-8')
 stock=(BP/'scripts/a2752_stockpot_food_core.js').read_text(encoding='utf-8')
 assert wok.count("id:'kaleidoscope_grilling:wok/")==3
 assert stock.count("row('stockpot_exact'")==3
 assert stock.count("row('stockpot_flex'")==3

 for name in (
  'houttuynia_stir_fried_pork','green_pepper_squid_tentacles','braised_chicken_wings',
  'potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles'
 ):
  assert (BP/'items'/f'{name}.json').is_file(),name
  assert (RP/'textures/items'/f'{name}.png').is_file(),name

 report=load(P/'reports/a2756-p0-official-api-hardening.json')
 assert report['version']=='A2.7.56'
 assert report['architecture_audit']['before_event_mutation_deferred_with_system_run'] is True
 assert report['architecture_audit']['world_json_dynamic_property_pattern_matches_official_sample'] is True
 assert report['architecture_audit']['cookery_private_kc_station_access'] is False
 assert report['p0_regression_guard']['wok_foods']==3
 assert report['p0_regression_guard']['stockpot_foods']==3
 assert len(report['official_references'])==5
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

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
  'version':'A2.7.56','p0_official_api_hardening':True,
  'hot_before_seasoning_dynamic_property':True,
  'official_samples_pinned':True,
  'p0_wok_foods':3,'p0_stockpot_foods':3,
  'private_host_state_access':False,'duplicate_host_station':False,
  'compiled':a.compiled,'compiled_packs':compiled,
  'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2756-dash-verification.json' if a.compiled else 'a2756-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
