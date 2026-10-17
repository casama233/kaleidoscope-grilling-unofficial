from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,10]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ASSETS={
 'chicken_skin':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/chicken_skin.png','5a8517468ed9da877b219047e1032d3a4c728bfc'),
 'chicken_wing':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/chicken_wing.png','4adb1a131eb7f0dda0ed43f616e1dd561c7b3e71')
}
COOKERY_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.10/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.10 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.10 Chicken Acquisition BP'),(rm,'Kaleidoscope Grilling A2.7.10 Chicken Acquisition RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.10 Chicken Acquisition';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_10_Chicken_Acquisition';write(P/'config.json',cfg)

def skin_item():
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:chicken_skin','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:chicken_skin.name'},
   'minecraft:icon':{'textures':{'default':'chicken_skin'}},
   'minecraft:max_stack_size':64
  }
 }}

def wing_item():
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:chicken_wing','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:chicken_wing.name'},
   'minecraft:icon':{'textures':{'default':'chicken_wing'}},
   'minecraft:max_stack_size':64,
   'minecraft:allow_off_hand':True,
   'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':0.35},
   'minecraft:food':{'can_always_eat':False,'nutrition':2,'saturation_modifier':0.06},
   'minecraft:use_animation':{'value':'eat'},
   'minecraft:tags':{'tags':['minecraft:is_food']}
  }
 }}

def patch_items():
 write(BP/'items/chicken_skin.json',skin_item())
 write(BP/'items/chicken_wing.json',wing_item())
 for id,(src,sha) in ASSETS.items():
  out=RP/f'textures/items/{id}.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(src,sha))
 tex=load(RP/'textures/item_texture.json')
 for id in ASSETS:tex['texture_data'][id]={'textures':f'textures/items/{id}'}
 write(RP/'textures/item_texture.json',tex)
 labels={
  'zh_TW':{
   'item.kaleidoscope_grilling:chicken_skin.name':'雞皮',
   'item.kaleidoscope_grilling:chicken_wing.name':'雞翅'
  },
  'zh_CN':{
   'item.kaleidoscope_grilling:chicken_skin.name':'鸡皮',
   'item.kaleidoscope_grilling:chicken_wing.name':'鸡翅'
  },
  'en_US':{
   'item.kaleidoscope_grilling:chicken_skin.name':'Chicken Skin',
   'item.kaleidoscope_grilling:chicken_wing.name':'Chicken Wing'
  }
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2710_chicken_acquisition_core.js',BP/'scripts/a2710_chicken_acquisition_core.js')
 shutil.copy2(DEV/'a2710_chicken_acquisition_runtime.js',BP/'scripts/a2710_chicken_acquisition_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import {tryScheduleBeefBoardOverride} from './a279_beef_board_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2710_chicken_acquisition_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2710-parity.json',{
  'version':'A2.7.10',
  'scope':'chicken_skin and chicken_wing survival acquisition parity',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'java_sources':{
   'chopping_board_mixin_blob_sha1':'3b201faf83c2b8aa29008d1d63185d7738f6a2f1',
   'knife_drop_handler_blob_sha1':'8a6e2705d46ec9535dc35b8baf203d3411c84e6e'
  },
  'items':{
   'chicken_skin':{'plain_item':True,'max_stack_size':64,'texture_git_blob_sha1':ASSETS['chicken_skin'][1]},
   'chicken_wing':{'food':True,'max_stack_size':64,'nutrition':2,'saturation_modifier':0.06,'texture_git_blob_sha1':ASSETS['chicken_wing'][1]}
  },
  'chicken_skin':{
   'cookery_base_recipe':'minecraft:chicken -> kaleidoscope_cookery:raw_cut_small_meats x2, 4 cuts',
   'java_extra_drop':'on successful release action when current cuts >= max: chicken_skin x(1..3)',
   'bedrock_strategy':'observe first knife interaction at completed Cookery chicken-board state; after Cookery clears/advances state, spawn bonus skin without replacing Cookery output',
   'duplicate_guard':'one pending completion watch per station key per callback window'
  },
  'chicken_wing':{
   'java_drop':'when DamageSource causing entity is Player and player current main hand is in kaleidoscope_cookery:kitchen_knife tag',
   'chance':1.0,
   'base_count':'1 + random(0..1)',
   'looting_bonus':'random(0..Looting level)',
   'bedrock_knife_ids':[
    'kaleidoscope_cookery:iron_kitchen_knife','kaleidoscope_cookery:gold_kitchen_knife',
    'kaleidoscope_cookery:diamond_kitchen_knife','kaleidoscope_cookery:netherite_kitchen_knife'
   ],
   'projectile_note':'no explicit projectile rejection, mirroring Java causing-player/current-main-hand implementation'
  },
  'cookery_bedrock':{
   'version':'1.0.6','exact_public_archive_sha256':COOKERY_SHA,
   'chicken_board_model':2,
   'private_scripts_modified':False
  },
  'downstream':{
   'raw_chicken_skin_skewer_recipe_already_references_chicken_skin':True,
   'raw_mid_wing_skewer_recipe_already_references_chicken_wing':True
  },
  'minecraft_tested':False,'bds_tested':False,'engine_rendering_verified':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,9]:raise RuntimeError('A2.7.10 must augment verified A2.7.9')
 patch_versions();patch_items();patch_runtime();report();print('A2.7.10 chicken acquisition complete')
if __name__=='__main__':main()
