from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path
from a27_recipe_build import build_all as build_recipes

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,0]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ASSETS={
'beef_chunks':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/beef_chunks.png','6b9a7d3f3b153ab42c0f725abc34b4b56003c5e1'),
'braised_chicken_wings':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/braised_chicken_wings.png','849984b12af4346a276ed1db03ee0ff70a6ef62c'),
'canola_seeds':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/canola_seeds.png','89a7008164006a16dcd194ce27b6e5c165b14987'),
'carrot_dice':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/carrot_dice.png','c5359f186611411d51f1fe55077357d2c16efa61'),
'chicken_skin':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/chicken_skin.png','5a8517468ed9da877b219047e1032d3a4c728bfc'),
'chicken_wing':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/chicken_wing.png','4adb1a131eb7f0dda0ed43f616e1dd561c7b3e71'),
'cold_houttuynia':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/cold_houttuynia.png','98d59596cc06892e78d6d90d3e8ed2303151f841'),
'green_pepper_squid_tentacles':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/green_pepper_squid_tentacles.png','cd66ab879f3c1818ea2f149955945ce6e6bb22ff'),
'houttuynia':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/houttuynia.png','40afc94ae7826ddb7cb5a8cd106434a6745dfe25'),
'houttuynia_stir_fried_pork':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/houttuynia_stir_fried_pork.png','12c3d37ecee6b20598265e0511e391bd39330a4f'),
'minced_houttuynia':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/minced_houttuynia.png','c6653c730bb5d1fefab02db05388b0f2e6aefc30'),
'onion':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/onion.png','103aa78661bf35aa6b3a42989a398573056faff1'),
'pepper_honey':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/pepper_honey.png','0a629329dce3bd29c7d56baa5d2ebbf5693d6f6a'),
'potato_beef_stew':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/potato_beef_stew.png','b702c0e0b1960d1374d8b52aee9b81fe0c50a30c'),
'potato_slice':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/potato_slice.png','9562676753ad5e32ea0e1345236e314ad4767b85'),
'raw_mantou_slice':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/raw_mantou_slice.png','c89c916e0611d7de9d821e122b2d88c099809cbf'),
'raw_sweet_potato_sheet':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/raw_sweet_potato_sheet.png','a537de022aa9cc50b99dfec6f0fedd0046cb2d2f'),
'red_chili_powder':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/red_chili_powder.png','57936897efae12b743a539f0bf1dac54d45dda39'),
'red_sweet_potato_porridge':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/red_sweet_potato_porridge.png','3802ce2611ce23c51b6b776f0646651c79d71f47'),
'roasted_chicken_wing':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/roasted_chicken_wing.png','88d0b45b57a7958f185f9b292eda18d5b57dac42'),
'roasted_sweet_potato':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/roasted_sweet_potato.png','cc8bda808a99d38ecdae90a78a3acf6b7c0dea9a'),
'sour_spicy_noodles':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/sour_spicy_noodles.png','026fe88aa24d0f5161c6376617d6e76aaa0e89dd'),
'squid_tentacle':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/squid_tentacle.png','60aab20cf2c9c4b250780430f7114c22ae7b9dff'),
'sugared_tomato':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/sugared_tomato.png','da58483560e98eaeb3abc24973f0c1b247931c65'),
'sweet_potato':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/sweet_potato.png','6761c2d89d46df2e536dd6df3fe9fdb7c2262259'),
'sweet_potato_powder':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/sweet_potato_powder.png','2e15c9ea095ff0ef7c7959b05bd9f60d79631dab'),
'wedding_candy':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/wedding_candy.png','d7ca9f5dfa61d6658372d8e181283fb5bf756d78'),
}
ITEMS=json.loads(r'''[
{"id":"beef_chunks"},{"id":"braised_chicken_wings","stack":16,"food":[10,0.8]},{"id":"canola_seeds"},{"id":"carrot_dice"},{"id":"chicken_skin"},{"id":"chicken_wing","food":[2,0.06]},{"id":"cold_houttuynia","food":[6,1.0]},{"id":"green_pepper_squid_tentacles","stack":16,"food":[8,0.6]},{"id":"houttuynia","food":[2,0.2]},{"id":"houttuynia_stir_fried_pork","stack":16,"food":[9,0.7]},{"id":"minced_houttuynia"},{"id":"onion"},{"id":"pepper_honey","food":[4,0.25]},{"id":"potato_beef_stew","stack":16,"food":[12,0.9]},{"id":"potato_slice"},{"id":"raw_mantou_slice"},{"id":"raw_sweet_potato_sheet"},{"id":"red_chili_powder"},{"id":"red_sweet_potato_porridge","stack":16,"food":[14,0.071429]},{"id":"roasted_chicken_wing","food":[5,0.12]},{"id":"roasted_sweet_potato","food":[6,0.2]},{"id":"sour_spicy_noodles","stack":16,"food":[10,0.6]},{"id":"squid_tentacle"},{"id":"sugared_tomato","food":[6,0.65]},{"id":"sweet_potato","food":[3,0.1]},{"id":"sweet_potato_powder","use":true},{"id":"wedding_candy","food":[20,0.5],"always":true}
]''')

NAMES={
'zh_CN':{
'beef_chunks':'牛肉块','braised_chicken_wings':'红烧鸡翅','canola_seeds':'油菜籽','carrot_dice':'胡萝卜粒','chicken_skin':'鸡皮','chicken_wing':'鸡翅','cold_houttuynia':'凉拌折耳根','green_pepper_squid_tentacles':'青椒炒鱿鱼须','houttuynia':'折耳根','houttuynia_stir_fried_pork':'折耳根炒肉','minced_houttuynia':'折耳根沫','onion':'洋葱','pepper_honey':'花椒蜂蜜','potato_beef_stew':'土豆炖牛肉（烟火版）','potato_slice':'土豆片','raw_mantou_slice':'生馒头片','raw_sweet_potato_sheet':'生苕皮','red_chili_powder':'红辣椒粉','red_sweet_potato_porridge':'红苕稀饭','roasted_chicken_wing':'烤鸡翅','roasted_sweet_potato':'烤红薯','sour_spicy_noodles':'酸辣粉','squid_tentacle':'鱿鱼须','sugared_tomato':'糖拌番茄','sweet_potato':'红薯','sweet_potato_powder':'红薯粉','wedding_candy':'喜糖'},
'zh_TW':{
'beef_chunks':'牛肉塊','braised_chicken_wings':'紅燒雞翅','canola_seeds':'油菜籽','carrot_dice':'胡蘿蔔粒','chicken_skin':'雞皮','chicken_wing':'雞翅','cold_houttuynia':'涼拌折耳根','green_pepper_squid_tentacles':'青椒炒魷魚鬚','houttuynia':'折耳根','houttuynia_stir_fried_pork':'折耳根炒肉','minced_houttuynia':'折耳根末','onion':'洋蔥','pepper_honey':'花椒蜂蜜','potato_beef_stew':'土豆燉牛肉（煙火版）','potato_slice':'土豆片','raw_mantou_slice':'生饅頭片','raw_sweet_potato_sheet':'生苕皮','red_chili_powder':'紅辣椒粉','red_sweet_potato_porridge':'紅苕稀飯','roasted_chicken_wing':'烤雞翅','roasted_sweet_potato':'烤紅薯','sour_spicy_noodles':'酸辣粉','squid_tentacle':'魷魚鬚','sugared_tomato':'糖拌番茄','sweet_potato':'紅薯','sweet_potato_powder':'紅薯粉','wedding_candy':'喜糖'},
'en_US':{
'beef_chunks':'Beef Chunks','braised_chicken_wings':'Braised Chicken Wings','canola_seeds':'Canola Seeds','carrot_dice':'Carrot Dice','chicken_skin':'Chicken Skin','chicken_wing':'Chicken Wing','cold_houttuynia':'Dressed Houttuynia','green_pepper_squid_tentacles':'Green Pepper Squid Tentacles','houttuynia':'Houttuynia','houttuynia_stir_fried_pork':'Houttuynia Stir-fried Pork','minced_houttuynia':'Minced Houttuynia','onion':'Onion','pepper_honey':'Pepper Honey','potato_beef_stew':'Potato Beef Stew (Grilling Edition)','potato_slice':'Potato Slice','raw_mantou_slice':'Raw Mantou Slice','raw_sweet_potato_sheet':'Raw Sweet Potato Sheet','red_chili_powder':'Red Chili Powder','red_sweet_potato_porridge':'Sweet Potato Rice Porridge','roasted_chicken_wing':'Roasted Chicken Wing','roasted_sweet_potato':'Roasted Sweet Potato','sour_spicy_noodles':'Sour and Spicy Noodles','squid_tentacle':'Squid Tentacle','sugared_tomato':'Sugared Tomato','sweet_potato':'Sweet Potato','sweet_potato_powder':'Sweet Potato Powder','wedding_candy':'Wedding Candy'}
}

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 if blob(v)!=sha:raise RuntimeError('pinned upstream mismatch '+path)
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_manifest():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7 Gameplay BP'),(rm,'Kaleidoscope Grilling A2.7 Gameplay RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7 Gameplay';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7';write(P/'config.json',cfg)

def item_doc(spec):
 id=spec['id'];c={
  'minecraft:display_name':{'value':f'item.kaleidoscope_grilling:{id}.name'},
  'minecraft:icon':{'textures':{'default':id}},
  'minecraft:max_stack_size':spec.get('stack',64)
 }
 if 'food' in spec:
  n,s=spec['food'];c['minecraft:food']={'can_always_eat':bool(spec.get('always',False)),'nutrition':n,'saturation_modifier':s}
  c['minecraft:use_animation']={'value':'eat'}
  c['minecraft:tags']={'tags':['minecraft:is_food']}
 if spec.get('use'):
  c['minecraft:use_modifiers']={'start_using':'always','use_duration':1.5,'movement_modifier':0.35}
  c['minecraft:use_animation']={'value':'bow'}
 return {'format_version':'1.26.30','minecraft:item':{'description':{'identifier':'kaleidoscope_grilling:'+id,'menu_category':{'category':'items'}},'components':c}}

def add_items():
 tex=load(RP/'textures/item_texture.json')
 for spec in ITEMS:
  id=spec['id'];write(BP/f'items/{id}.json',item_doc(spec))
  path,sha=ASSETS[id];out=RP/f'textures/items/{id}.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(path,sha))
  tex['texture_data'][id]={'textures':f'textures/items/{id}'}
 write(RP/'textures/item_texture.json',tex)
 for lang,names in NAMES.items():
  p=RP/f'texts/{lang}.lang';s=p.read_text(encoding='utf-8')
  for id,name in names.items():
   k=f'item.kaleidoscope_grilling:{id}.name'
   if k+'=' not in s:s+='\n'+k+'='+name
  p.write_text(s.rstrip()+'\n',encoding='utf-8')

def patch_scripts():
 shutil.copy2(DEV/'a27_items_core.js',BP/'scripts/a27_items_core.js')
 shutil.copy2(DEV/'a27_food_runtime.js',BP/'scripts/a27_food_runtime.js')
 shutil.copy2(DEV/'a27_recipe_core.js',BP/'scripts/a27_recipe_core.js')
 shutil.copy2(DEV/'a27_dynamic_recipe_runtime.js',BP/'scripts/a27_dynamic_recipe_runtime.js')
 p=BP/'scripts/main.js';s=p.read_text(encoding='utf-8')
 anchor="import './a26_oil_machine_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a27_food_runtime.js';\nimport './a27_dynamic_recipe_runtime.js';",'A2.7 runtime imports')
 p.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a27-items.json',{
  'version':'A2.7.0','java_registry_missing_before':27,'java_registry_items_added':27,'java_registry_missing_after':0,
  'food_contracts':{
   'chicken_wing':[2,.06],'houttuynia':[2,.2],'sweet_potato':[3,.1],
   'roasted_sweet_potato':[6,.2],'roasted_chicken_wing':[5,.12],'cold_houttuynia':[6,1.0],
   'sugared_tomato':[6,.65],'pepper_honey':[4,.25],'wedding_candy':[20,.5],
   'houttuynia_stir_fried_pork':[9,.7],'green_pepper_squid_tentacles':[8,.6],
   'braised_chicken_wings':[10,.8],'potato_beef_stew':[12,.9],
   'red_sweet_potato_porridge':[14,.071429],'sour_spicy_noodles':[10,.6]
  },
  'specials':{'sweet_potato_powder_whole_stack_knead_ticks':30,'wedding_candy_invincible_ticks':300},
  'quality_aware_java_items':11,
  'cookery_quality_storage_bound':False,
  'crop_planting_deferred_to':'A2.8',
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,6,0]:raise RuntimeError('A2.7 must augment verified A2.6')
 patch_manifest();add_items();patch_scripts();build_recipes(DEV,BP,P);report();print('A2.7 item + recipe augmentation complete')
if __name__=='__main__':main()
