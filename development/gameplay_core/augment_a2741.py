from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,41]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
TEXTURES={
 'sugared_tomato':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/sugared_tomato.png','da58483560e98eaeb3abc24973f0c1b247931c65'),
 'pepper_honey':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/pepper_honey.png','0a629329dce3bd29c7d56baa5d2ebbf5693d6f6a'),
}

LANG={
 'en_US.lang':{
  'item.kaleidoscope_grilling:sugared_tomato.name':'Sugared Tomato',
  'tooltip.kaleidoscope_grilling.sugared_tomato.maxim':'Sweet, tart, and ready to close out a barbecue.',
  'item.kaleidoscope_grilling:pepper_honey.name':'Pepper Honey',
  'tooltip.kaleidoscope_grilling.pepper_honey.maxim':'Eating this... how is it different from chewing an electric wire?',
 },
 'zh_CN.lang':{
  'item.kaleidoscope_grilling:sugared_tomato.name':'糖拌番茄',
  'tooltip.kaleidoscope_grilling.sugared_tomato.maxim':'酸甜清爽，适合把一顿烧烤收个尾。',
  'item.kaleidoscope_grilling:pepper_honey.name':'花椒蜂蜜',
  'tooltip.kaleidoscope_grilling.pepper_honey.maxim':'吃这个...和吃电线有什么区别？',
 },
 'zh_TW.lang':{
  'item.kaleidoscope_grilling:sugared_tomato.name':'糖拌番茄',
  'tooltip.kaleidoscope_grilling.sugared_tomato.maxim':'酸甜清爽，適合把一頓燒烤收個尾。',
  'item.kaleidoscope_grilling:pepper_honey.name':'花椒蜂蜜',
  'tooltip.kaleidoscope_grilling.pepper_honey.maxim':'吃這個...和吃電線有什麼區別？',
 },
}

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.41/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.41 Sugared Tomato + Pepper Honey BP'),(rm,'Kaleidoscope Grilling A2.7.41 Sugared Tomato + Pepper Honey RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.41 Sugared Tomato + Pepper Honey'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_41_Sugared_Tomato_Pepper_Honey'
 write(P/'config.json',cfg)

def food_item(identifier,icon,nutrition,saturation):
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':identifier,'menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.'+identifier+'.name'},
   'minecraft:icon':{'textures':{'default':icon}},
   'minecraft:max_stack_size':64,
   'minecraft:allow_off_hand':True,
   'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':0.35},
   'minecraft:food':{'can_always_eat':False,'nutrition':nutrition,'saturation_modifier':saturation},
   'minecraft:use_animation':{'value':'eat'},
   'minecraft:tags':{'tags':['minecraft:is_food']}
  }
 }}

def shapeless(identifier,ingredients,result):
 return {'format_version':'1.20.10','minecraft:recipe_shapeless':{
  'description':{'identifier':identifier},'tags':['crafting_table'],
  'ingredients':ingredients,'result':{'item':result,'count':1}
 }}

def patch_content():
 items={
  'sugared_tomato':food_item('kaleidoscope_grilling:sugared_tomato','sugared_tomato',6,0.65),
  'pepper_honey':food_item('kaleidoscope_grilling:pepper_honey','pepper_honey',4,0.25),
 }
 for name,doc in items.items():
  path=BP/f'items/{name}.json'
  if path.exists():raise RuntimeError(f'A2.7.41 item already exists: {path}')
  write(path,doc)

 recipes={
  'sugared_tomato':shapeless('kaleidoscope_grilling:sugared_tomato',[
   {'item':'kaleidoscope_cookery:tomato'},{'item':'minecraft:sugar'}
  ],'kaleidoscope_grilling:sugared_tomato'),
  'pepper_honey':shapeless('kaleidoscope_grilling:pepper_honey',[
   {'item':'kaleidoscope_grilling:sichuan_pepper'},
   {'item':'kaleidoscope_grilling:sichuan_pepper'},
   {'item':'kaleidoscope_grilling:sichuan_pepper'},
   {'item':'minecraft:honey_bottle'}
  ],'kaleidoscope_grilling:pepper_honey'),
 }
 for name,doc in recipes.items():
  path=BP/f'recipes/{name}.json'
  if path.exists():raise RuntimeError(f'A2.7.41 recipe already exists: {path}')
  write(path,doc)

 atlas=load(RP/'textures/item_texture.json')
 for name,(src,sha) in TEXTURES.items():
  if name in atlas['texture_data']:raise RuntimeError(f'A2.7.41 texture key already exists: {name}')
  out=RP/f'textures/items/{name}.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(src,sha))
  atlas['texture_data'][name]={'textures':f'textures/items/{name}'}
 write(RP/'textures/item_texture.json',atlas)

 for lang,rows in LANG.items():
  path=RP/'texts'/lang;text=path.read_text(encoding='utf-8')
  existing=text.splitlines()
  for key,value in rows.items():
   if any(row.startswith(key+'=') for row in existing):raise RuntimeError(f'{lang}: duplicate localization key {key}')
   text+='\n'+key+'='+value
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_effect_registry():
 src=DEV/'a2741_standalone_food_effect_core.js'
 dst=BP/'scripts/a2732_standalone_food_effect_core.js'
 shutil.copy2(src,dst)

def report():
 write(P/'reports/a2741-sugared-tomato-pepper-honey.json',{
  'version':'A2.7.41','scope':'two missing Java 1.1.1 cold-dessert foods',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'foods':{
   'sugared_tomato':{
    'nutrition':6,'saturation_modifier':0.65,
    'recipe':['c:crops/tomato','minecraft:sugar'],
    'bedrock_recipe':['kaleidoscope_cookery:tomato','minecraft:sugar'],
    'java_common_tomato_tag_breadth_preserved':False,
    'required_cookery_host_tomato_used':True
   },
   'pepper_honey':{
    'nutrition':4,'saturation_modifier':0.25,
    'recipe':['3x kaleidoscope_grilling:sichuan_pepper','minecraft:honey_bottle'],
    'effect':'kaleidoscope_grilling:numb','effect_ticks':1200,
    'uses_shared_standalone_food_effect_runtime':True
   }
  },
  'textures':{name:{'git_blob_sha1':sha} for name,(_,sha) in TEXTURES.items()},
  'dedupe':{
   'new_item_complete_use_listener_created':False,
   'existing_a2732_shared_effect_runtime_reused':True,
   'duplicate_cookery_tomato_created':False
  },
  'maxim_translation_keys_present':True,
  'maxim_tooltip_runtime_binding_ported':False,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,40]:raise RuntimeError('A2.7.41 must augment published A2.7.40')
 patch_content();patch_effect_registry();patch_versions();report()
 print('A2.7.41 Sugared Tomato + Pepper Honey complete')
if __name__=='__main__':main()
