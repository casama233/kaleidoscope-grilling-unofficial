from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'projects/grilling'
P=SRC/'gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,0]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
NS='kaleidoscope_grilling'

TEXTURES={
'beef_chunks':'6b9a7d3f3b153ab42c0f725abc34b4b56003c5e1','canola_seeds':'89a7008164006a16dcd194ce27b6e5c165b14987',
'carrot_dice':'c5359f186611411d51f1fe55077357d2c16efa61','chicken_skin':'5a8517468ed9da877b219047e1032d3a4c728bfc',
'chicken_wing':'4adb1a131eb7f0dda0ed43f616e1dd561c7b3e71','houttuynia':'40afc94ae7826ddb7cb5a8cd106434a6745dfe25',
'minced_houttuynia':'c6653c730bb5d1fefab02db05388b0f2e6aefc30','onion':'103aa78661bf35aa6b3a42989a398573056faff1',
'potato_slice':'9562676753ad5e32ea0e1345236e314ad4767b85','raw_mantou_slice':'c89c916e0611d7de9d821e122b2d88c099809cbf',
'raw_sweet_potato_sheet':'a537de022aa9cc50b99dfec6f0fedd0046cb2d2f','red_chili_powder':'57936897efae12b743a539f0bf1dac54d45dda39',
'squid_tentacle':'60aab20cf2c9c4b250780430f7114c22ae7b9dff','sweet_potato':'6761c2d89d46df2e536dd6df3fe9fdb7c2262259',
'sweet_potato_powder':'2e15c9ea095ff0ef7c7959b05bd9f60d79631dab','cold_houttuynia':'98d59596cc06892e78d6d90d3e8ed2303151f841',
'pepper_honey':'0a629329dce3bd29c7d56baa5d2ebbf5693d6f6a','roasted_chicken_wing':'88d0b45b57a7958f185f9b292eda18d5b57dac42',
'roasted_sweet_potato':'cc8bda808a99d38ecdae90a78a3acf6b7c0dea9a','sugared_tomato':'da58483560e98eaeb3abc24973f0c1b247931c65',
'wedding_candy':'d7ca9f5dfa61d6658372d8e181283fb5bf756d78','houttuynia_stir_fried_pork':'12c3d37ecee6b20598265e0511e391bd39330a4f',
'green_pepper_squid_tentacles':'cd66ab879f3c1818ea2f149955945ce6e6bb22ff','braised_chicken_wings':'849984b12af4346a276ed1db03ee0ff70a6ef62c',
'potato_beef_stew':'b702c0e0b1960d1374d8b52aee9b81fe0c50a30c','red_sweet_potato_porridge':'3802ce2611ce23c51b6b776f0646651c79d71f47',
'sour_spicy_noodles':'026fe88aa24d0f5161c6376617d6e76aaa0e89dd'
}
ITEMS=list(TEXTURES)
FOOD={
'chicken_wing':(2,.06,64,False),'houttuynia':(2,.2,64,False),'sweet_potato':(3,.1,64,False),
'roasted_sweet_potato':(6,.2,64,False),'roasted_chicken_wing':(5,.12,64,False),
'cold_houttuynia':(6,1.0,64,False),'sugared_tomato':(6,.65,64,False),'pepper_honey':(4,.25,64,False),
'wedding_candy':(20,.5,64,True),'houttuynia_stir_fried_pork':(9,.7,16,False),
'green_pepper_squid_tentacles':(8,.6,16,False),'braised_chicken_wings':(10,.8,16,False),
'potato_beef_stew':(12,.9,16,False),'red_sweet_potato_porridge':(14,.071429,16,False),
'sour_spicy_noodles':(10,.6,16,False)
}
RECIPE_SHA={
'chopping_board/carrot_dice.json':'eaa04428dfbfcb1b7c44835c14f606e450468996',
'chopping_board/minced_houttuynia.json':'02c18ac0431afd347da50d0c68ed3d704f3fa154',
'chopping_board/potato_slice.json':'18539711535c3e302720a5b49b048678ab952623',
'chopping_board/raw_mantou_slice.json':'c9512e9d2cc5a1b3849fd3bf84283e5cd33749ad',
'chopping_board/raw_sweet_potato_sheet.json':'cf8f2b6687ba59b62d67d428d5f585f25a807dae',
'milling/canola_powder.json':'43215be3d0b871213805e09ef76d297f49dead9d',
'milling/green_chili_powder.json':'79483d937d5515a32fa4d5bea68698b2964225c2',
'milling/houttuynia_powder.json':'73b7f50f65235299616a49db74d15b99b0c73cac',
'milling/onion_powder.json':'9ed660c1ba2b46ec4559ba897d766a07a9066334',
'milling/red_chili_powder.json':'f5d8fe6883ebc697a232407d92f49d414243206d',
'milling/sweet_potato_powder.json':'ba730a420dae8776b57eb23060d22b712c3e1ed5',
'milling/totem_powder.json':'100d4fcdb77cebb013dd89af4fb166d91acb53ba',
'pot/braised_chicken_wings.json':'3a07fd7c9c9252db9134043b2438e10c46089d0c',
'pot/green_pepper_squid_tentacles.json':'4b7a16790f96ba00e112d3ce94c1492263d703a0',
'pot/houttuynia_stir_fried_pork.json':'31676dd8c13331aec31560df1028f21aeb77feef',
'stockpot/potato_beef_stew.json':'7596270b1a876561e70fec6afa8966d3be08c9be',
'stockpot/red_sweet_potato_porridge.json':'b8fed24b8ea41e93fdcb4611dbb61a0b12301c4c',
'pepper_honey.json':'2eeb3b30c9fd3090605c6c39c681e4d0d0b18a2e','sugared_tomato.json':'bd5dbd8d3ed3788e3637e3766d04243c32808cec'
}
LANG_SHA={'zh_cn.json':'bbc7465f6bf6ab0c698729e9800fbc3c03ae56db','en_us.json':'807c7f40618d409ca17ccb4c0a39e211a84a7b18'}
TAG_PRIMARY={
'kaleidoscope_grilling:ingredients/canola_seeds':f'{NS}:canola_seeds',
'kaleidoscope_grilling:ingredients/houttuynia':f'{NS}:houttuynia',
'kaleidoscope_grilling:ingredients/sweet_potatoes':f'{NS}:sweet_potato',
'kaleidoscope_grilling:ingredients/chicken_wings':f'{NS}:chicken_wing',
'kaleidoscope_grilling:ingredients/squid_tentacles':f'{NS}:squid_tentacle',
'kaleidoscope_grilling:ingredients/onions':f'{NS}:onion',
'kaleidoscope_grilling:ingredients/beef_chunks':f'{NS}:beef_chunks',
'kaleidoscope_grilling:ingredients/carrot_dice':f'{NS}:carrot_dice',
'kaleidoscope_grilling:ingredients/leafy_greens':'kaleidoscope_cookery:lettuce',
'c:crops/tomato':'kaleidoscope_cookery:tomato'
}
ZH_TW={
'beef_chunks':'牛肉塊','canola_seeds':'油菜籽','carrot_dice':'胡蘿蔔丁','chicken_skin':'雞皮','chicken_wing':'雞翅',
'houttuynia':'折耳根','minced_houttuynia':'碎折耳根','onion':'洋蔥','potato_slice':'馬鈴薯片','raw_mantou_slice':'生饅頭片',
'raw_sweet_potato_sheet':'生紅薯粉皮','red_chili_powder':'紅辣椒粉','squid_tentacle':'魷魚鬚','sweet_potato':'紅薯',
'sweet_potato_powder':'紅薯粉','cold_houttuynia':'涼拌折耳根','pepper_honey':'花椒蜂蜜','roasted_chicken_wing':'烤雞翅',
'roasted_sweet_potato':'烤紅薯','sugared_tomato':'糖拌番茄','wedding_candy':'喜糖','houttuynia_stir_fried_pork':'折耳根炒肉',
'green_pepper_squid_tentacles':'青椒魷魚鬚','braised_chicken_wings':'紅燒雞翅','potato_beef_stew':'馬鈴薯燉牛肉',
'red_sweet_potato_porridge':'紅薯粥','sour_spicy_noodles':'酸辣粉'
}

def blob(v:bytes)->str:return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch_bytes(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 if blob(v)!=sha:raise RuntimeError('pinned upstream mismatch '+path)
 return v
def fetch_json(path,sha):return json.loads(fetch_bytes(path,sha).decode('utf-8-sig'))
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

def item_doc(id):
 c={'minecraft:display_name':{'value':f'item.{NS}:{id}.name'},'minecraft:icon':{'textures':{'default':id}},'minecraft:max_stack_size':FOOD.get(id,(0,0,64,False))[2]}
 if id in FOOD:
  n,s,_,always=FOOD[id]
  c.update({'minecraft:allow_off_hand':True,'minecraft:use_modifiers':{'start_using':'always','use_duration':1.61,'movement_modifier':.35},
            'minecraft:food':{'can_always_eat':always,'nutrition':n,'saturation_modifier':s},
            'minecraft:use_animation':{'value':'eat'},'minecraft:tags':{'tags':['minecraft:is_food']}})
 if id=='sweet_potato_powder':
  c.update({'minecraft:allow_off_hand':True,'minecraft:use_modifiers':{'start_using':'always','use_duration':1.5,'movement_modifier':.35},
            'minecraft:use_animation':{'value':'bow'}})
 return {'format_version':'1.26.30','minecraft:item':{'description':{'identifier':f'{NS}:{id}','menu_category':{'category':'items'}},'components':c}}

def map_ing(x):
 if 'item' in x:return x['item']
 if 'tag' in x:
  if x['tag'] not in TAG_PRIMARY:raise RuntimeError('A2.7 unmapped Java tag '+x['tag'])
  return TAG_PRIMARY[x['tag']]
 raise RuntimeError('A2.7 unsupported ingredient '+repr(x))
def result_of(d):
 r=d.get('result') or (d.get('results') or [{}])[0]
 return (r.get('id') or r.get('item'),int(r.get('count',r.get('amount',1))))
def shapeless(identifier,ingredients,result,count=1):
 return {'format_version':'1.20.10','minecraft:recipe_shapeless':{'description':{'identifier':f'{NS}:{identifier}'},'tags':['crafting_table'],
   'ingredients':[{'item':x} for x in ingredients],'result':{'item':result,'count':count}}}
def furnace(identifier,tag,input_id,output_id):
 return {'format_version':'1.20.10','minecraft:recipe_furnace':{'description':{'identifier':f'{NS}:{identifier}'},'tags':[tag],'input':input_id,'output':output_id}}

def patch_items_and_textures():
 itemtex=load(RP/'textures/item_texture.json')
 for id,sha in TEXTURES.items():
  write(BP/f'items/{id}.json',item_doc(id))
  out=RP/f'textures/items/{id}.png';out.parent.mkdir(parents=True,exist_ok=True)
  out.write_bytes(fetch_bytes(f'common/src/main/resources/assets/{NS}/textures/item/{id}.png',sha))
  itemtex['texture_data'][id]={'textures':f'textures/items/{id}'}
 write(RP/'textures/item_texture.json',itemtex)

def patch_runtime():
 shutil.copy2(DEV/'a27_content_core.js',BP/'scripts/a27_content_core.js')
 shutil.copy2(DEV/'a27_food_runtime.js',BP/'scripts/a27_food_runtime.js')
 main=BP/'scripts/main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a26_oil_machine_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a27_food_runtime.js';",'main runtime import')
 main.write_text(s,encoding='utf-8')

def patch_recipes():
 recipes=BP/'recipes';recipes.mkdir(parents=True,exist_ok=True)
 modes=[]
 def source(rel):return fetch_json(f'common/src/main/resources/data/{NS}/recipe/{rel}',RECIPE_SHA[rel])
 for rel in [x for x in RECIPE_SHA if x.startswith('chopping_board/')]:
  d=source(rel);out,count=result_of(d);stem=Path(rel).stem
  write(recipes/f'a27_fallback_chop_{stem}.json',shapeless(f'a27_fallback_chop_{stem}',[map_ing(d['ingredient'])],out,count))
  modes.append({'source':rel,'mode':'crafting_table_fallback','result':out})
 for rel in [x for x in RECIPE_SHA if x.startswith('milling/')]:
  d=source(rel);out,count=result_of(d);stem=Path(rel).stem
  write(recipes/f'a27_fallback_milling_{stem}.json',shapeless(f'a27_fallback_milling_{stem}',[map_ing(x) for x in d['ingredients']],out,count))
  modes.append({'source':rel,'mode':'crafting_table_fallback','result':out})
 for family in ('pot','stockpot'):
  for rel in [x for x in RECIPE_SHA if x.startswith(family+'/')]:
   d=source(rel);out,count=result_of(d);stem=Path(rel).stem
   ings=[map_ing(x) for x in d['ingredients']]
   if family=='pot':ings=[map_ing(d['carrier'])]+ings
   else:ings=['minecraft:bowl']+ings
   write(recipes/f'a27_fallback_{family}_{stem}.json',shapeless(f'a27_fallback_{family}_{stem}',ings,out,count))
   modes.append({'source':rel,'mode':'crafting_table_fallback','result':out})
 for rel in ('pepper_honey.json','sugared_tomato.json'):
  d=source(rel);out,count=result_of(d);stem=Path(rel).stem
  write(recipes/f'a27_{stem}.json',shapeless(f'a27_{stem}',[map_ing(x) for x in d['ingredients']],out,count))
  modes.append({'source':rel,'mode':'native_shapeless','result':out})
 for stem,input_id,output_id in (
  ('roasted_chicken_wing',f'{NS}:chicken_wing',f'{NS}:roasted_chicken_wing'),
  ('roasted_sweet_potato',f'{NS}:sweet_potato',f'{NS}:roasted_sweet_potato')):
  for suffix,tag in (('smelting','furnace'),('smoking','smoker'),('campfire','campfire')):
   name=f'a27_{stem}_{suffix}';write(recipes/f'{name}.json',furnace(name,tag,input_id,output_id))
   modes.append({'source':f'{stem}_{"" if suffix=="smelting" else suffix}.json'.replace('__','_'),'mode':'native_furnace','result':output_id})
 write(P/'reports/a27-recipe-catalog.json',{'java_baseline':'9a1acdab27698457bec16c9362678e574895a28c','mapped':modes,
   'dynamic_deferred':[{'recipe':'cold_houttuynia','reason':'Java consumes exactly 2 premium_chili points from stateful Cookery oil pot and returns the pot.'}],
   'optional_deferred':[{'recipe':'sour_spicy_noodles','reason':'Java recipe is conditional on optional kaleidoscope_tavern; Bedrock has no safe pack-load conditional for an unknown item id.'}],
   'create_compat_deferred':['crushing','millstone','filling','mixing']})

def patch_languages():
 zh=fetch_json(f'common/src/main/resources/assets/{NS}/lang/zh_cn.json',LANG_SHA['zh_cn.json'])
 en=fetch_json(f'common/src/main/resources/assets/{NS}/lang/en_us.json',LANG_SHA['en_us.json'])
 tables={'zh_CN':zh,'en_US':en}
 for lang,src in tables.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for id in ITEMS:
   k=f'item.{NS}:{id}.name';value=src.get(f'item.{NS}.{id}',id.replace('_',' '))
   if k+'=' not in text:text+=f'\n{k}={value}'
  path.write_text(text.rstrip()+'\n',encoding='utf-8')
 path=RP/'texts/zh_TW.lang';text=path.read_text(encoding='utf-8')
 for id,value in ZH_TW.items():
  k=f'item.{NS}:{id}.name'
  if k+'=' not in text:text+=f'\n{k}={value}'
 path.write_text(text.rstrip()+'\n',encoding='utf-8')

def report():
 write(P/'reports/a27-parity.json',{
  'version':'A2.7.0','java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'items_added':len(ITEMS),'food_items_added':len(FOOD),
  'exact_item_food_stats':True,
  'exact_food_effects':['roasted_sweet_potato:warmth 600t','cold_houttuynia:fire_resistance 1200t','pepper_honey:numb 1200t','wedding_candy:invincible 300t','red_sweet_potato_porridge:flatulence+warmth 900t','sour_spicy_noodles:warmth 900t'],
  'sweet_potato_powder_knead_ticks':30,
  'recipe_reconciliation':{'native_exact_or_narrowed':8,'workstation_survival_fallbacks':17,'stateful_dynamic_deferred':1,'optional_dependency_deferred':1,
    'create_compat_families_deferred':['crushing','millstone','filling','mixing']},
  'known_platform_substitutions':[
   'Cookery chopping-board/pot/stockpot and Create milling custom RecipeTypes cannot be registered as Java RecipeTypes in retail Bedrock; A2.7 emits deterministic crafting-table survival fallbacks from the pinned Java ingredients/results.',
   'Stockpot fallbacks add one bowl because Java serving occurs through the workstation rather than as an input recipe carrier.',
   'c:crops/tomato is narrowed to kaleidoscope_cookery:tomato for the retail Bedrock fallback.',
   'Cold Houttuynia stays deferred rather than consuming a whole oil bucket: Java consumes exactly 2 points from a premium-chili Cookery oil pot.',
   'Sour Spicy Noodles stays deferred unless a safe optional Kaleidoscope Tavern compatibility layer is installed.'
  ],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,6,0]:raise RuntimeError('A2.7 must augment the verified A2.6 baseline')
 patch_manifest();patch_runtime();patch_items_and_textures();patch_recipes();patch_languages();report()
 print('A2.7 content + recipe reconciliation augmentation complete')
if __name__=='__main__':main()
