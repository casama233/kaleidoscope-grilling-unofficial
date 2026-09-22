from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,45]
ASSET_DIR=DEV/'assets/a2745'
SCRIPTS=(
 'a2745_p0_food_contract.js',
 'a2745_cookery_cuisine_core.js',
 'a2745_food_state_adapter.js',
 'a2745_cookery_cuisine_runtime.js',
)
FOODS={
 'sugared_tomato':dict(nutrition=6,saturation=.65,maxStack=64,always=False),
 'pepper_honey':dict(nutrition=4,saturation=.25,maxStack=64,always=False),
 'wedding_candy':dict(nutrition=20,saturation=.5,maxStack=64,always=True),
 'houttuynia_stir_fried_pork':dict(nutrition=9,saturation=.7,maxStack=16,always=False),
 'green_pepper_squid_tentacles':dict(nutrition=8,saturation=.6,maxStack=16,always=False),
 'braised_chicken_wings':dict(nutrition=10,saturation=.8,maxStack=16,always=False),
 'potato_beef_stew':dict(nutrition=12,saturation=.9,maxStack=16,always=False),
 'red_sweet_potato_porridge':dict(nutrition=14,saturation=.071429,maxStack=16,always=False),
 'sour_spicy_noodles':dict(nutrition=10,saturation=.6,maxStack=16,always=False),
}
NAMES={
 'en_US.lang':{
  'sugared_tomato':'Sugared Tomato','pepper_honey':'Pepper Honey','wedding_candy':'Wedding Candy',
  'houttuynia_stir_fried_pork':'Houttuynia Stir-fried Pork',
  'green_pepper_squid_tentacles':'Green Pepper Squid Tentacles','braised_chicken_wings':'Braised Chicken Wings',
  'potato_beef_stew':'Potato Beef Stew (Grilling Edition)','red_sweet_potato_porridge':'Sweet Potato Rice Porridge',
  'sour_spicy_noodles':'Sour and Spicy Noodles'},
 'zh_CN.lang':{
  'sugared_tomato':'糖拌番茄','pepper_honey':'花椒蜂蜜','wedding_candy':'喜糖',
  'houttuynia_stir_fried_pork':'折耳根炒肉','green_pepper_squid_tentacles':'青椒炒鱿鱼须',
  'braised_chicken_wings':'红烧鸡翅','potato_beef_stew':'土豆炖牛肉（烟火版）',
  'red_sweet_potato_porridge':'红苕稀饭','sour_spicy_noodles':'酸辣粉'},
 'zh_TW.lang':{
  'sugared_tomato':'糖拌番茄','pepper_honey':'花椒蜂蜜','wedding_candy':'喜糖',
  'houttuynia_stir_fried_pork':'折耳根炒肉','green_pepper_squid_tentacles':'青椒炒魷魚鬚',
  'braised_chicken_wings':'紅燒雞翅','potato_beef_stew':'馬鈴薯燉牛肉（煙火版）',
  'red_sweet_potato_porridge':'紅苕稀飯','sour_spicy_noodles':'酸辣粉'},
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def replace_once(s,old,new,label):
 n=s.count(old)
 if n!=1:raise RuntimeError(f'{label} drift: expected 1, got {n}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.45 P0 Cookery Cuisine BP'),(rm,'Kaleidoscope Grilling A2.7.45 P0 Cookery Cuisine RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.45 P0 Cookery Cuisine'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_45_P0_Cookery_Cuisine'
 write(P/'config.json',cfg)

def food_item(name,spec):
 return {
  'format_version':'1.26.30',
  'minecraft:item':{
   'description':{'identifier':'kaleidoscope_grilling:'+name,'menu_category':{'category':'items'}},
   'components':{
    'minecraft:display_name':{'value':f'item.kaleidoscope_grilling:{name}.name'},
    'minecraft:icon':{'textures':{'default':name}},
    'minecraft:max_stack_size':spec['maxStack'],
    'minecraft:allow_off_hand':True,
    'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':.35},
    'minecraft:food':{
     'can_always_eat':bool(spec['always']),'nutrition':spec['nutrition'],
     'saturation_modifier':spec['saturation']},
    'minecraft:use_animation':{'value':'eat'},
    'minecraft:tags':{'tags':['minecraft:is_food']}
   }
  }
 }

def add_foods():
 for name,spec in FOODS.items():
  write(BP/'items'/f'{name}.json',food_item(name,spec))
  src=ASSET_DIR/f'{name}.png'
  if not src.is_file():raise RuntimeError(f'missing pinned asset {src}')
  shutil.copy2(src,RP/'textures/items'/f'{name}.png')
 atlas=load(RP/'textures/item_texture.json')
 table=atlas.setdefault('texture_data',{})
 for name in FOODS:
  if name in table:raise RuntimeError(f'duplicate item texture key {name}')
  table[name]={'textures':f'textures/items/{name}'}
 write(RP/'textures/item_texture.json',atlas)

def add_crafting():
 write(BP/'recipes/sugared_tomato.json',{
  'format_version':'1.20.10','minecraft:recipe_shapeless':{
   'description':{'identifier':'kaleidoscope_grilling:sugared_tomato'},
   'tags':['crafting_table'],
   'ingredients':[{'item':'kaleidoscope_cookery:tomato'},{'item':'minecraft:sugar'}],
   'result':{'item':'kaleidoscope_grilling:sugared_tomato','count':1}
  }})
 write(BP/'recipes/pepper_honey.json',{
  'format_version':'1.20.10','minecraft:recipe_shapeless':{
   'description':{'identifier':'kaleidoscope_grilling:pepper_honey'},
   'tags':['crafting_table'],
   'ingredients':[
    {'item':'kaleidoscope_grilling:sichuan_pepper'},
    {'item':'kaleidoscope_grilling:sichuan_pepper'},
    {'item':'kaleidoscope_grilling:sichuan_pepper'},
    {'item':'minecraft:honey_bottle'}],
   'result':{'item':'kaleidoscope_grilling:pepper_honey','count':1}
  }})

def patch_lang():
 for lang,names in NAMES.items():
  p=RP/'texts'/lang;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  additions=[]
  for name,label in names.items():
   key=f'item.kaleidoscope_grilling:{name}.name'
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{lang}: duplicate {key}')
   additions.append(key+'='+label)
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(additions)+'\n',encoding='utf-8')

def patch_scripts():
 scripts=BP/'scripts'
 for name in SCRIPTS:shutil.copy2(DEV/name,scripts/name)
 shutil.copy2(DEV/'a2745_refactored_a2727_cookery_host_recipes_core.js',scripts/'a2727_cookery_host_recipes_core.js')
 shutil.copy2(DEV/'a2745_refactored_a2732_standalone_food_effect_core.js',scripts/'a2732_standalone_food_effect_core.js')

 p=scripts/'main.js';s=p.read_text(encoding='utf-8')
 anchor="""import {
 readPlacedSeasoningStack as readBottleStack,writePlacedSeasoningStack as writeBottleStack
} from './a2743_seasoning_block_adapter.js';
"""
 add=anchor+"""import {
 readFoodSeasonings as readSeasonings,setFoodSeasonings as setSeasonings,
 setHotFood as setHot,hotUntil,isHotFood as isHot,refreshHotLore
} from './a2745_food_state_adapter.js';
"""
 s=replace_once(s,anchor,add,'shared food-state import')
 s=replace_once(s,
  "const HOT_UNTIL_KEY='kaleidoscope_grilling:hot_until',FX_KEY='kaleidoscope_grilling:a21_fx';",
  "const FX_KEY='kaleidoscope_grilling:a21_fx';",
  'local hot key')

 h0=s.index('function readSeasonings(stack)')
 h1=s.index('function cookedStack(raw,state)',h0)
 keep="""function getUses(stack){try{return Math.max(0,Math.min(SEASONING_MAX_USES,Number(stack?.getDynamicProperty(SEASON_USES_KEY)??0)|0))}catch{return 0}}
function setUses(stack,n){try{stack.setDynamicProperty(SEASON_USES_KEY,Math.max(0,Math.min(SEASONING_MAX_USES,n|0)))}catch{}return stack}
"""
 s=s[:h0]+keep+s[h1:]

 runtime_anchor="import './a2744_skewer_plate_hud_provider.js';\n"
 if runtime_anchor not in s:runtime_anchor="import './a2743_seasoning_hud_provider.js';\n"
 s=replace_once(s,runtime_anchor,runtime_anchor+"import './a2745_cookery_cuisine_runtime.js';\n",'P0 runtime import')
 p.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2745-p0-cookery-cuisine.json',{
  'version':'A2.7.45',
  'scope':'P0 Cookery Pot/Stockpot integration + nine missing Java foods',
  'foods':list(FOODS),
  'recipes':{
   'crafting':['sugared_tomato','pepper_honey'],
   'wok_strict':['houttuynia_stir_fried_pork','green_pepper_squid_tentacles','braised_chicken_wings'],
   'stockpot_exact':['potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles'],
   'stockpot_flex':['potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles']
  },
  'cookery_host':{
   'version':'1.0.6','public_extension_api':True,
   'recipe_publisher_reused':'a2727_cookery_host_recipes_runtime.js',
   'private_kc_station_access':False,
   'duplicate_wok_or_stockpot':False
  },
  'integration':{
   'special_seasoning':True,'seasoning_use_cost':1,
   'pot_typed_oil_tracking':True,'pot_hot_output':True,
   'stockpot_hot_output':True,'output_seasoning_metadata':True,
   'inventory_delta_isolation':True
  },
  'host_boundaries':{
   'java_flex_wok_exactly_available_in_kc_v1_api':False,
   'strict_wok_registered':True,
   'stockpot_flex_registered':True,
   'wok_stirs_controlled_by_host':True,
   'grilling_oil_bucket_direct_wok_fill':False,
   'typed_oil_path':'Grilling bucket -> Cookery oil pot -> Cookery Wok'
  },
  'wedding_candy':{
   'item_and_invincible_effect':True,
   'historical_date_distribution_event_included':False,
   'reason':'dated Sep 1-12 2026 event is P2/event-layer, not the P0 cuisine item contract'
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,44]:
  raise RuntimeError('A2.7.45 must augment published A2.7.44')
 patch_scripts();add_foods();add_crafting();patch_lang();patch_versions();report()
 print('A2.7.45 P0 Cookery Cuisine complete')

if __name__=='__main__':main()
