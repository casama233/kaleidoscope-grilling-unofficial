from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,20]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
TEX_PATH='common/src/main/resources/assets/kaleidoscope_grilling/textures/item/roasted_sweet_potato.png'
TEX_SHA='cc8bda808a99d38ecdae90a78a3acf6b7c0dea9a'
WARMTH_TICKS=600

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.20/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.20 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.20 Roasted Sweet Potato BP'),(rm,'Kaleidoscope Grilling A2.7.20 Roasted Sweet Potato RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.20 Roasted Sweet Potato';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_20_Roasted_Sweet_Potato';write(P/'config.json',cfg)

def item_doc():
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:roasted_sweet_potato','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:roasted_sweet_potato.name'},
   'minecraft:icon':{'textures':{'default':'roasted_sweet_potato'}},
   'minecraft:max_stack_size':64,
   'minecraft:allow_off_hand':True,
   'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':0.35},
   'minecraft:food':{'can_always_eat':False,'nutrition':6,'saturation_modifier':0.2},
   'minecraft:use_animation':{'value':'eat'},
   'minecraft:tags':{'tags':['minecraft:is_food']}
  }
 }}

def recipe_doc():
 return {'format_version':'1.20.10','minecraft:recipe_furnace':{
  'description':{'identifier':'kaleidoscope_grilling:roasted_sweet_potato'},
  'tags':['furnace','smoker','campfire','soul_campfire'],
  'input':'kaleidoscope_grilling:sweet_potato',
  'output':'kaleidoscope_grilling:roasted_sweet_potato'
 }}

def patch_assets():
 write(BP/'items/roasted_sweet_potato.json',item_doc())
 write(BP/'recipes/roasted_sweet_potato.json',recipe_doc())
 out=RP/'textures/items/roasted_sweet_potato.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(TEX_PATH,TEX_SHA))
 atlas=load(RP/'textures/item_texture.json');atlas['texture_data']['roasted_sweet_potato']={'textures':'textures/items/roasted_sweet_potato'};write(RP/'textures/item_texture.json',atlas)
 labels={
  'zh_TW':{'item.kaleidoscope_grilling:roasted_sweet_potato.name':'烤番薯'},
  'zh_CN':{'item.kaleidoscope_grilling:roasted_sweet_potato.name':'烤红薯'},
  'en_US':{'item.kaleidoscope_grilling:roasted_sweet_potato.name':'Roasted Sweet Potato'}
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2720_roasted_sweet_potato_core.js',BP/'scripts/a2720_roasted_sweet_potato_core.js')
 shutil.copy2(DEV/'a2720_roasted_sweet_potato_runtime.js',BP/'scripts/a2720_roasted_sweet_potato_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2719_sweet_potato_crop_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2720_roasted_sweet_potato_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2720-parity.json',{
  'version':'A2.7.20','scope':'Roasted Sweet Potato item + native cooking + base Warmth',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'item':{
   'id':'kaleidoscope_grilling:roasted_sweet_potato','nutrition':6,'saturation_modifier':0.2,
   'base_effect':'kaleidoscope_cookery:warmth','base_effect_ticks':WARMTH_TICKS,
   'texture_git_blob_sha1':TEX_SHA
  },
  'recipes':{
   'input':'kaleidoscope_grilling:sweet_potato','output':'kaleidoscope_grilling:roasted_sweet_potato',
   'java':{
    'furnace':{'cookingtime':200,'experience':0.35},
    'smoker':{'cookingtime':100,'experience':0.35},
    'campfire':{'cookingtime':600,'experience':0.35}
   },
   'bedrock_station_tags':['furnace','smoker','campfire','soul_campfire'],
   'station_access_parity':True,
   'explicit_cookingtime_field_available':False,
   'explicit_experience_field_available':False,
   'java_experience_0_35_exact':False
  },
  'effect':{
   'native_food_consumption_preserved':True,
   'existing_a21_fx_warmth_state_reused':True,
   'base_600_tick_duration':True,
   'cuisine_quality_duration_scaling_ported':False
  },
  'survival_chain':{
   'sweet_potato_acquisition_crop':'A2.7.19',
   'roasted_sweet_potato_obtainable_in_survival':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,19]:raise RuntimeError('A2.7.20 must augment verified A2.7.19')
 patch_versions();patch_assets();patch_runtime();report();print('A2.7.20 roasted sweet potato complete')
if __name__=='__main__':main()
