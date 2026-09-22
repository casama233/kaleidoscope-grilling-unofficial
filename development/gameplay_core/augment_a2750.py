from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,50]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FOODS={
 'houttuynia_stir_fried_pork':dict(nutrition=9,saturation=.7,maxStack=16),
 'green_pepper_squid_tentacles':dict(nutrition=8,saturation=.6,maxStack=16),
 'braised_chicken_wings':dict(nutrition=10,saturation=.8,maxStack=16),
}
TEXTURES={
 'houttuynia_stir_fried_pork':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/houttuynia_stir_fried_pork.png','12c3d37ecee6b20598265e0511e391bd39330a4f'),
 'green_pepper_squid_tentacles':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/green_pepper_squid_tentacles.png','cd66ab879f3c1818ea2f149955945ce6e6bb22ff'),
 'braised_chicken_wings':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/braised_chicken_wings.png','849984b12af4346a276ed1db03ee0ff70a6ef62c'),
}
IDS=tuple('kaleidoscope_grilling:'+x for x in FOODS)
NEW_SCRIPTS=(
 'a2750_wok_food_core.js','a2750_food_state_adapter.js',
 'a2750_cookery_cuisine_core.js','a2750_cookery_cuisine_runtime.js',
)
LANG={
 'en_US.lang':{
  'houttuynia_stir_fried_pork':('Houttuynia Stir-fried Pork','Some hate its bite, others love it with rice. Houttuynia does not care.'),
  'green_pepper_squid_tentacles':('Green Pepper Squid Tentacles','Flash-fried before the squid tentacles had time to think.'),
  'braised_chicken_wings':('Braised Chicken Wings','You will not discard the bones before savoring them three times.'),
 },
 'zh_CN.lang':{
  'houttuynia_stir_fried_pork':('折耳根炒肉','有人恨它的冲，有人爱它下饭。但折耳根不在乎。'),
  'green_pepper_squid_tentacles':('青椒炒鱿鱼须','大火快炒，鱿鱼须还没来得及想就熟了。'),
  'braised_chicken_wings':('红烧鸡翅','一口下去，骨头都得嘬三遍才舍得扔。'),
 },
 'zh_TW.lang':{
  'houttuynia_stir_fried_pork':('折耳根炒肉','有人恨它的衝，有人愛它下飯。但折耳根不在乎。'),
  'green_pepper_squid_tentacles':('青椒炒魷魚鬚','大火快炒，魷魚鬚還沒來得及想就熟了。'),
  'braised_chicken_wings':('紅燒雞翅','一口下去，骨頭都得嘬三遍才捨得丟。'),
 },
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.50/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def replace_once(s,old,new,label):
 n=s.count(old)
 if n!=1:raise RuntimeError(f'A2.7.50 patch anchor drift ({label}): {n}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.50 Cookery Wok Cuisine BP'),
  (rm,'Kaleidoscope Grilling A2.7.50 Cookery Wok Cuisine RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.50 Cookery Wok Cuisine'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_50_Cookery_Wok_Cuisine'
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
  if p.exists():raise RuntimeError(f'A2.7.50 item already exists: {p}')
  write(p,food_item(name,spec))
 atlas=load(RP/'textures/item_texture.json')
 for name,(src,sha) in TEXTURES.items():
  if name in atlas['texture_data']:raise RuntimeError(f'A2.7.50 texture key already exists: {name}')
  p=RP/'textures/items'/f'{name}.png';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(fetch(src,sha))
  atlas['texture_data'][name]={'textures':f'textures/items/{name}'}
 write(RP/'textures/item_texture.json',atlas)

 catalog_path=BP/'item_catalog/crafting_item_catalog.json';catalog=load(catalog_path)
 groups=catalog['minecraft:crafting_items_catalog']['categories'][0]['groups']
 group=next((x for x in groups if x.get('group_identifier',{}).get('name')=='kaleidoscope_grilling:itemGroup.main'),None)
 if group is None:raise RuntimeError('A2.7.50 main item catalog group missing')
 rows=group.setdefault('items',[])
 for item_id in IDS:
  if item_id in rows:raise RuntimeError(f'A2.7.50 duplicate catalog id: {item_id}')
  rows.append(item_id)
 write(catalog_path,catalog)

 for lang,entries in LANG.items():
  p=RP/'texts'/lang;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  additions=[]
  for name,(label,maxim) in entries.items():
   pairs=(
    (f'item.kaleidoscope_grilling:{name}.name',label),
    (f'tooltip.kaleidoscope_grilling.{name}.maxim',maxim),
   )
   for key,value in pairs:
    if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{lang}: duplicate {key}')
    additions.append(key+'='+value)
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(additions)+'\n',encoding='utf-8')

def patch_host_recipe_core():
 p=BP/'scripts/a2727_cookery_host_recipes_core.js';s=p.read_text(encoding='utf-8')
 s=replace_once(s,"export const KC_API=1;","import {wokRecipes} from './a2750_wok_food_core.js';\n\nexport const KC_API=1;",'wok import')
 anchor="\nconst RECIPES=Object.freeze(["
 helper="""\nfunction wok(recipe){
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
 s=replace_once(s,anchor,helper+anchor,'wok helper')
 tail=""" millstone('kaleidoscope_grilling:millstone/red_chili_powder',
  'kaleidoscope_cookery:red_chili','kaleidoscope_grilling:red_chili_powder',1,1.0),
]);
"""
 add=tail.replace("]);"," ...wokRecipes().map(wok),\n]);")
 s=replace_once(s,tail,add,'wok recipe rows')
 p.write_text(s,encoding='utf-8')

def patch_main():
 p=BP/'scripts/main.js';s=p.read_text(encoding='utf-8')
 seasoning=""" SEASONING_CAPACITY,SEASONING_MAX_BOTTLES,SEASONING_MAX_USES,SEASONING_VARIANT_MAX,
 PENDING_SEASONING_ID as PENDING_SEASONING,SEASONING_PLACE_BLOCK_ID as SEASONING_BLOCK,
 SEASONING_LIST_KEY as SEASON_LIST_KEY,SEASONING_USES_KEY as SEASON_USES_KEY,
 SEASONING_VARIANT_KEY as SEASON_VARIANT_KEY,SEASONING_KINDS,
 normalizeSeasoningList,hasSeasoningBase,isSeasoningBlockId as isSeasoningBlock
"""
 seasoning_new=""" SEASONING_CAPACITY,SEASONING_MAX_BOTTLES,SEASONING_MAX_USES,SEASONING_VARIANT_MAX,
 PENDING_SEASONING_ID as PENDING_SEASONING,SEASONING_PLACE_BLOCK_ID as SEASONING_BLOCK,
 SEASONING_USES_KEY as SEASON_USES_KEY,
 SEASONING_VARIANT_KEY as SEASON_VARIANT_KEY,SEASONING_KINDS,
 hasSeasoningBase,isSeasoningBlockId as isSeasoningBlock
"""
 s=replace_once(s,seasoning,seasoning_new,'seasoning imports')
 block_adapter="""import {
 readPlacedSeasoningStack as readBottleStack,writePlacedSeasoningStack as writeBottleStack
} from './a2743_seasoning_block_adapter.js';
"""
 shared=block_adapter+"""import {
 readFoodSeasonings as readSeasonings,setFoodSeasonings as setSeasonings,
 setHotFood as setHot,hotUntil,isHotFood as isHot,refreshHotLore
} from './a2750_food_state_adapter.js';
import {WOK_FOOD_IDS} from './a2750_wok_food_core.js';
"""
 s=replace_once(s,block_adapter,shared,'food state imports')
 runtime_anchor="import './a2748_pepper_tree_runtime.js';\n"
 s=replace_once(s,runtime_anchor,runtime_anchor+"import './a2750_cookery_cuisine_runtime.js';\n",'cuisine runtime')
 s=replace_once(s,
  "const ACTIVE_EATS=new Map(),PLATE_EATS=new Map(),SETTLED=new Map(),VIGOR_LAST=new Map(),SNEAK_LAST=new Map(),SEASON_PLACE_CACHE=new Map(),THREAD_LAST=new Map();",
  "const ACTIVE_EATS=new Map(),WOK_EATS=new Map(),PLATE_EATS=new Map(),SETTLED=new Map(),VIGOR_LAST=new Map(),SNEAK_LAST=new Map(),SEASON_PLACE_CACHE=new Map(),THREAD_LAST=new Map();",
  'Wok eat map')
 s=replace_once(s,"const MAX_GRILLS=256;","const MAX_GRILLS=256;\nconst WOK_FOOD_SET=new Set(WOK_FOOD_IDS);",'Wok food set')
 s=replace_once(s,
  "const HOT_UNTIL_KEY='kaleidoscope_grilling:hot_until',FX_KEY='kaleidoscope_grilling:a21_fx';",
  "const FX_KEY='kaleidoscope_grilling:a21_fx';",
  'shared hot key')

 start=s.index('function readSeasonings(stack)')
 end=s.index('function cookedStack(raw,state)',start)
 keep="""function getUses(stack){try{return Math.max(0,Math.min(SEASONING_MAX_USES,Number(stack?.getDynamicProperty(SEASON_USES_KEY)??0)|0))}catch{return 0}}
function setUses(stack,n){try{stack.setDynamicProperty(SEASON_USES_KEY,Math.max(0,Math.min(SEASONING_MAX_USES,n|0)))}catch{}return stack}
"""
 s=s[:start]+keep+s[end:]

 start_hook="  if(!FOOD_DATA[id]&&id!==SECRET_ID)return;\n  const requested=PROFILE_BY_ITEM[id]??'THREE_RANDOM'"
 start_repl="""  if(WOK_FOOD_SET.has(id)){
   const meta=stackMeta(e.itemStack),sat=e.source.getComponent('minecraft:player.saturation');
   WOK_EATS.set(e.source.id,{id,meta,nativeBefore:meta.hot?nativeSnapshot(e.source):{},fxBefore:meta.hot?fxSnapshot(e.source):{},saturationBefore:meta.hot?sat?.currentValue:undefined});
   return;
  }
  if(!FOOD_DATA[id]&&id!==SECRET_ID)return;
  const requested=PROFILE_BY_ITEM[id]??'THREE_RANDOM'"""
 s=replace_once(s,start_hook,start_repl,'Wok itemStartUse')

 complete_hook="  dangerousPreservation(e.source,id);if(!FOOD_DATA[id]&&id!==SECRET_ID)return;"
 complete_repl="""  dangerousPreservation(e.source,id);
  if(WOK_FOOD_SET.has(id)){
   const a=WOK_EATS.get(e.source.id)??{id,meta:stackMeta(e.itemStack),nativeBefore:{},fxBefore:{},saturationBefore:undefined};
   WOK_EATS.delete(e.source.id);afterCommitted(e.source,id,a.meta,a,true);return;
  }
  if(!FOOD_DATA[id]&&id!==SECRET_ID)return;"""
 s=replace_once(s,complete_hook,complete_repl,'Wok itemCompleteUse')
 stop="world.afterEvents.itemStopUse.subscribe(e=>{const a=ACTIVE_EATS.get(e.source.id);if(!a)return;"
 s=replace_once(s,stop,"world.afterEvents.itemStopUse.subscribe(e=>{WOK_EATS.delete(e.source.id);const a=ACTIVE_EATS.get(e.source.id);if(!a)return;",'Wok stop cleanup')
 p.write_text(s,encoding='utf-8')

def patch_scripts():
 scripts=BP/'scripts'
 for name in NEW_SCRIPTS:shutil.copy2(DEV/name,scripts/name)
 patch_host_recipe_core();patch_main()

def report():
 write(P/'reports/a2750-cookery-wok-cuisine.json',{
  'version':'A2.7.50',
  'scope':'three Java strict Pot dishes through Cookery v1 Wok host + shared Grilling food metadata bridge',
  'foods':list(FOODS),
  'java_recipes':{
   'houttuynia_stir_fried_pork':'3x houttuynia + 3x porkchop',
   'green_pepper_squid_tentacles':'2x green_chili + 2x squid_tentacle + onion',
   'braised_chicken_wings':'3x chicken_wing + 3x sugar'
  },
  'cookery_host':{
   'version':'1.0.6','public_wok_extension_api':True,
   'single_recipe_publisher':'a2727_cookery_host_recipes_runtime.js',
   'private_kc_station_access':False,'duplicate_wok_station':False,
   'java_flex_wok_exactly_available':False
  },
  'shared_state':{
   'food_state_adapter':'a2750_food_state_adapter.js',
   'main_local_hot_parser_removed':True,'main_local_seasoning_parser_removed':True,
   'wok_output_metadata_bridge':'a2750_cookery_cuisine_runtime.js',
   'typed_oil_tracking':True,'special_seasoning':True,
   'hot_saturation_and_seasoning_eat_path_reused':True,
   'new_item_complete_use_listener':False
  },
  'catalog_registered':True,'maxim_translation_keys_present':True,
  'maxim_tooltip_runtime_binding_ported':False,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,49]:
  raise RuntimeError('A2.7.50 must augment published A2.7.49')
 patch_scripts();add_content();patch_versions();report()
 print('A2.7.50 Cookery Wok Cuisine complete')

if __name__=='__main__':main()
