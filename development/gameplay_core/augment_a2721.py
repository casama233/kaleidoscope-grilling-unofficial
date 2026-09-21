from __future__ import annotations
import hashlib,json,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
VERSION=[2,7,21]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
TEX_PATH='common/src/main/resources/assets/kaleidoscope_grilling/textures/item/roasted_chicken_wing.png'
TEX_SHA='88d0b45b57a7958f185f9b292eda18d5b57dac42'

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.21/1'})
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
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.21 Roasted Chicken Wing BP'),(rm,'Kaleidoscope Grilling A2.7.21 Roasted Chicken Wing RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.21 Roasted Chicken Wing';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_21_Roasted_Chicken_Wing';write(P/'config.json',cfg)

def item_doc():
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:roasted_chicken_wing','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:roasted_chicken_wing.name'},
   'minecraft:icon':{'textures':{'default':'roasted_chicken_wing'}},
   'minecraft:max_stack_size':64,
   'minecraft:allow_off_hand':True,
   'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':0.35},
   'minecraft:food':{'can_always_eat':False,'nutrition':5,'saturation_modifier':0.12},
   'minecraft:use_animation':{'value':'eat'},
   'minecraft:tags':{'tags':['minecraft:is_food']}
  }
 }}

def recipe_doc():
 return {'format_version':'1.20.10','minecraft:recipe_furnace':{
  'description':{'identifier':'kaleidoscope_grilling:roasted_chicken_wing'},
  'tags':['furnace','smoker','campfire','soul_campfire'],
  'input':'kaleidoscope_grilling:chicken_wing',
  'output':'kaleidoscope_grilling:roasted_chicken_wing'
 }}

def patch_assets():
 write(BP/'items/roasted_chicken_wing.json',item_doc())
 write(BP/'recipes/roasted_chicken_wing.json',recipe_doc())
 out=RP/'textures/items/roasted_chicken_wing.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(TEX_PATH,TEX_SHA))
 atlas=load(RP/'textures/item_texture.json');atlas['texture_data']['roasted_chicken_wing']={'textures':'textures/items/roasted_chicken_wing'};write(RP/'textures/item_texture.json',atlas)
 labels={
  'zh_TW':{'item.kaleidoscope_grilling:roasted_chicken_wing.name':'烤雞翅'},
  'zh_CN':{'item.kaleidoscope_grilling:roasted_chicken_wing.name':'烤鸡翅'},
  'en_US':{'item.kaleidoscope_grilling:roasted_chicken_wing.name':'Roasted Chicken Wing'}
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2721-parity.json',{
  'version':'A2.7.21','scope':'Roasted Chicken Wing item + native cooking',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'item':{
   'id':'kaleidoscope_grilling:roasted_chicken_wing','nutrition':5,'saturation_modifier':0.12,
   'flavor_food_item':True,'texture_git_blob_sha1':TEX_SHA
  },
  'recipes':{
   'locked_input_tag':'kaleidoscope_grilling:ingredients/chicken_wings',
   'resolved_inputs':['kaleidoscope_grilling:chicken_wing'],
   'output':'kaleidoscope_grilling:roasted_chicken_wing',
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
  'flavor_food':{
   'base_food_properties_exact':True,
   'cuisine_quality_food_scaling_ported':False,
   'maxim_tooltip_ported':False
  },
  'survival_chain':{
   'chicken_wing_acquisition':'A2.7.10',
   'roasted_chicken_wing_obtainable_in_survival':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,20]:raise RuntimeError('A2.7.21 must augment verified A2.7.20')
 patch_versions();patch_assets();report();print('A2.7.21 roasted chicken wing complete')
if __name__=='__main__':main()
