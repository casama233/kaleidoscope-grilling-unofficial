from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,52]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FOODS={
 'potato_beef_stew':dict(nutrition=12,saturation=.9,maxStack=16),
 'red_sweet_potato_porridge':dict(nutrition=14,saturation=.071429,maxStack=16),
 'sour_spicy_noodles':dict(nutrition=10,saturation=.6,maxStack=16),
}
TEXTURES={
 'potato_beef_stew':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/potato_beef_stew.png','b702c0e0b1960d1374d8b52aee9b81fe0c50a30c'),
 'red_sweet_potato_porridge':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/red_sweet_potato_porridge.png','3802ce2611ce23c51b6b776f0646651c79d71f47'),
 'sour_spicy_noodles':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/sour_spicy_noodles.png','026fe88aa24d0f5161c6376617d6e76aaa0e89dd'),
}
IDS=tuple('kaleidoscope_grilling:'+x for x in FOODS)
LANG={
 'en_US.lang':{
  'potato_beef_stew':('Potato Beef Stew (Grilling Edition)','Potatoes soaked in gravy and beef tender enough to need no teeth.'),
  'red_sweet_potato_porridge':('Sweet Potato Rice Porridge','Very filling, but not very nutritious. Better take it easy.'),
  'sour_spicy_noodles':('Sour and Spicy Noodles','Sour enough to wake you, hot enough to make you sweat, and impossible to stop slurping.'),
 },
 'zh_CN.lang':{
  'potato_beef_stew':('土豆炖牛肉（烟火版）','土豆吸饱了肉汁，牛肉烂到不用牙。'),
  'red_sweet_potato_porridge':('红苕稀饭','特别顶饿，但没营养，还是少涨点吧'),
  'sour_spicy_noodles':('酸辣粉','酸得醒神，辣得冒汗，嗦一口就停不下来。'),
 },
 'zh_TW.lang':{
  'potato_beef_stew':('馬鈴薯燉牛肉（煙火版）','馬鈴薯吸飽了肉汁，牛肉軟爛到不用牙。'),
  'red_sweet_potato_porridge':('紅苕稀飯','特別頂餓，但沒營養，還是少長點吧'),
  'sour_spicy_noodles':('酸辣粉','酸得醒神，辣得冒汗，嗦一口就停不下來。'),
 },
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.52/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def replace_once(s,old,new,label):
 n=s.count(old)
 if n!=1:raise RuntimeError(f'A2.7.52 patch anchor drift ({label}): {n}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.52 Cookery Stockpot Cuisine BP'),
  (rm,'Kaleidoscope Grilling A2.7.52 Cookery Stockpot Cuisine RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.52 Cookery Stockpot Cuisine'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_51_Cookery_Stockpot_Cuisine'
 write(P/'config.json',cfg)

def food_item(name,spec):
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:'+name,'menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':f'item.kaleidoscope_grilling:{name}.name'},
   'minecraft:icon':{'textures':{'default':name}},
   'minecraft:max_stack_size':spec['maxStack'],'minecraft:allow_off_hand':True,
   'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':.35},
   'minecraft:food':{'can_always_eat':False,'nutrition':spec['nutrition'],'saturation_modifier':spec['saturation']},
   'minecraft:use_animation':{'value':'eat'},'minecraft:tags':{'tags':['minecraft:is_food']}
  }
 }}

def add_content():
 for name,spec in FOODS.items():
  p=BP/'items'/f'{name}.json'
  if p.exists():raise RuntimeError(f'A2.7.52 item already exists: {p}')
  write(p,food_item(name,spec))
 atlas=load(RP/'textures/item_texture.json')
 for name,(src,sha) in TEXTURES.items():
  if name in atlas['texture_data']:raise RuntimeError(f'A2.7.52 texture key already exists: {name}')
  p=RP/'textures/items'/f'{name}.png';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(fetch(src,sha))
  atlas['texture_data'][name]={'textures':f'textures/items/{name}'}
 write(RP/'textures/item_texture.json',atlas)

 catalog_path=BP/'item_catalog/crafting_item_catalog.json';catalog=load(catalog_path)
 groups=catalog['minecraft:crafting_items_catalog']['categories'][0]['groups']
 group=next((x for x in groups if x.get('group_identifier',{}).get('name')=='kaleidoscope_grilling:itemGroup.main'),None)
 if group is None:raise RuntimeError('A2.7.52 main item catalog group missing')
 rows=group.setdefault('items',[])
 for item_id in IDS:
  if item_id in rows:raise RuntimeError(f'A2.7.52 duplicate catalog id: {item_id}')
  rows.append(item_id)
 write(catalog_path,catalog)

 for lang,entries in LANG.items():
  p=RP/'texts'/lang;s=p.read_text(encoding='utf-8');rows=s.splitlines();add=[]
  for name,(label,maxim) in entries.items():
   for key,value in (
    (f'item.kaleidoscope_grilling:{name}.name',label),
    (f'tooltip.kaleidoscope_grilling.{name}.maxim',maxim),
   ):
    if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{lang}: duplicate {key}')
    add.append(key+'='+value)
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(add)+'\n',encoding='utf-8')

def patch_host_core():
 p=BP/'scripts/a2727_cookery_host_recipes_core.js';s=p.read_text(encoding='utf-8')
 anchor="import {wokRecipes} from './a2750_wok_food_core.js';\n"
 s=replace_once(s,anchor,anchor+"import {stockpotRecipes} from './a2752_stockpot_food_core.js';\n",'stockpot import')
 helper_anchor="""function wok(recipe){
 return Object.freeze({
  capability:'wok',
  payload:Object.freeze({
   api:KC_API,kind:'wok',source:SOURCE,
   recipe:Object.freeze({
    id:recipe.id,ingredients:Object.freeze([...recipe.ingredients]),
    result:recipe.result,count:recipe.count,carrier:recipe.carrier,time:recipe.time
   })
  })
 });
}
"""
 helper_add=helper_anchor+"""
function stockpot(recipe){
 return Object.freeze({
  capability:recipe.kind,
  requiresItems:Object.freeze([...(recipe.requiresItems??[])]),
  payload:Object.freeze({
   api:KC_API,kind:recipe.kind,source:SOURCE,
   recipe:Object.freeze({
    id:recipe.id,
    ingredients:Object.freeze(recipe.ingredients.map(slot=>Object.freeze([...slot]))),
    result:recipe.result,count:recipe.count,time:recipe.time,base:recipe.base,
    carrier:recipe.carrier,finishedKind:recipe.finishedKind
   })
  })
 });
}
"""
 s=replace_once(s,helper_anchor,helper_add,'stockpot helper')
 rows_anchor=" ...wokRecipes().map(wok),\n]);"
 s=replace_once(s,rows_anchor," ...wokRecipes().map(wok),\n ...stockpotRecipes().map(stockpot),\n]);",'stockpot rows')
 table="""export function recipeTable(){
 return RECIPES.map(x=>({
  capability:x.capability,
  payload:JSON.parse(JSON.stringify(x.payload))
 }));
}
export function recipesForReady(info){
 if(!info||Number(info.api)!==KC_API)return [];
 const caps=new Set(Array.isArray(info.capabilities)?info.capabilities.map(String):[]);
 return RECIPES.filter(x=>caps.has(x.capability)).map(x=>JSON.parse(JSON.stringify(x.payload)));
}
"""
 table_new="""export function recipeTable(){
 return RECIPES.map(x=>({
  capability:x.capability,
  requiresItems:[...(x.requiresItems??[])],
  payload:JSON.parse(JSON.stringify(x.payload))
 }));
}
export function recipesForReady(info,{availableItems=[]}={}){
 if(!info||Number(info.api)!==KC_API)return [];
 const caps=new Set(Array.isArray(info.capabilities)?info.capabilities.map(String):[]);
 const available=new Set(Array.isArray(availableItems)?availableItems.map(String):[]);
 return RECIPES.filter(x=>
  caps.has(x.capability)&&(x.requiresItems??[]).every(id=>available.has(id))
 ).map(x=>JSON.parse(JSON.stringify(x.payload)));
}
"""
 s=replace_once(s,table,table_new,'requirements filter')
 p.write_text(s,encoding='utf-8')

def patch_host_runtime():
 p=BP/'scripts/a2727_cookery_host_recipes_runtime.js';s=p.read_text(encoding='utf-8')
 s=replace_once(s,"import {system} from '@minecraft/server';","import {system,ItemTypes} from '@minecraft/server';",'ItemTypes import')
 anchor="""import {
 KC_READY_EVENT,KC_PING_EVENT,KC_REGISTER_EVENT,SOURCE,recipesForReady
} from './a2727_cookery_host_recipes_core.js';
"""
 s=replace_once(s,anchor,anchor+"import {TAVERN_VINEGAR_IDS} from './a2752_stockpot_food_core.js';\n",'vinegar import')
 reg="""function registerReady(info){
 for(const payload of recipesForReady(info)){
  system.sendScriptEvent(KC_REGISTER_EVENT,JSON.stringify(payload));
 }
}
"""
 reg_new="""function optionalRecipeItems(){
 const out=[];
 for(const id of TAVERN_VINEGAR_IDS)try{if(ItemTypes.get(id))out.push(id)}catch{}
 return out;
}
function registerReady(info){
 for(const payload of recipesForReady(info,{availableItems:optionalRecipeItems()})){
  system.sendScriptEvent(KC_REGISTER_EVENT,JSON.stringify(payload));
 }
}
"""
 s=replace_once(s,reg,reg_new,'optional recipe items')
 p.write_text(s,encoding='utf-8')

def patch_effect_core():
 p=BP/'scripts/a2732_standalone_food_effect_core.js';s=p.read_text(encoding='utf-8')
 anchor="import {pepperHoneyEffectRow} from './a2749_sugared_tomato_pepper_honey_core.js';\n"
 s=replace_once(s,anchor,anchor+"import {stockpotEffectRows} from './a2752_stockpot_food_core.js';\n",'stockpot effects import')
 tail=""" }),
 pepperHoneyEffectRow()
]);
"""
 s=replace_once(s,tail,""" }),
 pepperHoneyEffectRow(),
 ...stockpotEffectRows()
]);
""",'stockpot effect rows')
 p.write_text(s,encoding='utf-8')

def patch_main():
 p=BP/'scripts/main.js';s=p.read_text(encoding='utf-8')
 anchor="import {WOK_FOOD_IDS} from './a2750_wok_food_core.js';\n"
 s=replace_once(s,anchor,anchor+"import {STOCKPOT_FOOD_IDS} from './a2752_stockpot_food_core.js';\n",'stockpot food import')
 if s.count('WOK_EATS')!=5:raise RuntimeError(f'A2.7.52 WOK_EATS drift: {s.count("WOK_EATS")}')
 if s.count('WOK_FOOD_SET')!=3:raise RuntimeError(f'A2.7.52 WOK_FOOD_SET drift: {s.count("WOK_FOOD_SET")}')
 s=s.replace('WOK_EATS','CUISINE_EATS').replace('WOK_FOOD_SET','CUISINE_FOOD_SET')
 old="const CUISINE_FOOD_SET=new Set(WOK_FOOD_IDS);"
 new="const CUISINE_FOOD_SET=new Set([...WOK_FOOD_IDS,...STOCKPOT_FOOD_IDS]);"
 s=replace_once(s,old,new,'cuisine food set')
 p.write_text(s,encoding='utf-8')

def patch_scripts():
 shutil.copy2(DEV/'a2752_stockpot_food_core.js',BP/'scripts/a2752_stockpot_food_core.js')
 patch_host_core();patch_host_runtime();patch_effect_core();patch_main()

def report():
 write(P/'reports/a2752-cookery-stockpot-cuisine.json',{
  'version':'A2.7.52',
  'scope':'three remaining Java Stockpot dishes through Cookery exact/flex host API',
  'foods':list(FOODS),
  'recipes':{'stockpot_exact':3,'stockpot_flex':3},
  'cookery_host':{
   'single_recipe_publisher':True,'stockpot_exact':True,'stockpot_flex':True,
   'private_kc_station_access':False,'existing_cuisine_bridge_reused':True
  },
  'tavern':{
   'java_optional_mod_condition_preserved':True,
   'java_vinegar_id':'kaleidoscope_tavern:vinegar',
   'bedrock_quality_ids':[f'kaleidoscope_tavern:vinegar_q{i}' for i in range(1,7)],
   'registration_requires_all_quality_ids':True,
   'duplicate_vinegar_created':False
  },
  'effects':{
   'red_sweet_potato_porridge':{'flatulence':900,'warmth':900},
   'sour_spicy_noodles':{'warmth':900},
   'shared_standalone_food_effect_runtime':True
  },
  'shared_state':{
   'cuisine_bridge':'a2750_cookery_cuisine_runtime.js',
   'cuisine_eat_map_unified':True,'new_item_complete_use_listener':False
  },
  'catalog_registered':True,'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,51]:
  raise RuntimeError('A2.7.52 must augment published A2.7.51')
 patch_scripts();add_content();patch_versions();report()
 print('A2.7.52 Cookery Stockpot Cuisine complete')

if __name__=='__main__':main()
