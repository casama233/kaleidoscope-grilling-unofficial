from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,22]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
TEX_PATH='common/src/main/resources/assets/kaleidoscope_grilling/textures/item/cold_houttuynia.png'
TEX_SHA='98d59596cc06892e78d6d90d3e8ed2303151f841'
FIRE_RESISTANCE_TICKS=1200

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.22/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.22 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.22 Cold Houttuynia BP'),(rm,'Kaleidoscope Grilling A2.7.22 Cold Houttuynia RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.22 Cold Houttuynia';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_22_Cold_Houttuynia';write(P/'config.json',cfg)

def item_doc():
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:cold_houttuynia','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:cold_houttuynia.name'},
   'minecraft:icon':{'textures':{'default':'cold_houttuynia'}},
   'minecraft:max_stack_size':64,
   'minecraft:allow_off_hand':True,
   'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':0.35},
   'minecraft:food':{'can_always_eat':False,'nutrition':6,'saturation_modifier':1.0},
   'minecraft:use_animation':{'value':'eat'},
   'minecraft:tags':{'tags':['minecraft:is_food']}
  }
 }}

def patch_assets():
 write(BP/'items/cold_houttuynia.json',item_doc())
 out=RP/'textures/items/cold_houttuynia.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(TEX_PATH,TEX_SHA))
 atlas=load(RP/'textures/item_texture.json');atlas['texture_data']['cold_houttuynia']={'textures':'textures/items/cold_houttuynia'};write(RP/'textures/item_texture.json',atlas)
 labels={
  'zh_TW':{'item.kaleidoscope_grilling:cold_houttuynia.name':'涼拌折耳根'},
  'zh_CN':{'item.kaleidoscope_grilling:cold_houttuynia.name':'凉拌折耳根'},
  'en_US':{'item.kaleidoscope_grilling:cold_houttuynia.name':'Dressed Houttuynia'}
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2722_cold_houttuynia_core.js',BP/'scripts/a2722_cold_houttuynia_core.js')
 shutil.copy2(DEV/'a2722_cold_houttuynia_runtime.js',BP/'scripts/a2722_cold_houttuynia_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2720_roasted_sweet_potato_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2722_cold_houttuynia_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2722-parity.json',{
  'version':'A2.7.22','scope':'Cold Houttuynia item + exact ingredient/oil semantics + Fire Resistance',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'item':{
   'id':'kaleidoscope_grilling:cold_houttuynia','nutrition':6,'saturation_modifier':1.0,
   'base_effect':'minecraft:fire_resistance','base_effect_ticks':FIRE_RESISTANCE_TICKS,
   'texture_git_blob_sha1':TEX_SHA
  },
  'java_recipe':{
   'custom_serializer':'kaleidoscope_grilling:cold_houttuynia',
   'houttuynia_tag_resolves_to':['kaleidoscope_grilling:houttuynia'],
   'houttuynia_count':3,'oil_type':'premium_chili','oil_points':2,'occupied_slots':4
  },
  'bedrock_recipe_equivalent':{
   'surface':'sneak + interact crafting table; main hand >=3 Houttuynia; offhand Cookery premium chili oil pot',
   'native_recipe_json_used':False,
   'ingredient_count_exact':True,'oil_type_exact':True,'partial_oil_consumption_exact':True,
   'zero_oil_returns_empty_pot':True,'crafting_grid_surface_exact':False
  },
  'effect':{
   'native_food_consumption_preserved':True,'base_fire_resistance_1200_ticks':True,
   'cuisine_quality_duration_scaling_ported':False,'maxim_tooltip_ported':False
  },
  'survival_chain':{
   'houttuynia_crop_and_processing':'A2.7.13-A2.7.14',
   'premium_chili_oil_world_and_pot_support':'A2.3/A2.6',
   'cold_houttuynia_obtainable_in_survival':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,21]:raise RuntimeError('A2.7.22 must augment verified A2.7.21')
 patch_versions();patch_assets();patch_runtime();report();print('A2.7.22 cold houttuynia complete')
if __name__=='__main__':main()
