from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,13]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ASSETS={
 'houttuynia':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/houttuynia.png','40afc94ae7826ddb7cb5a8cd106434a6745dfe25'),
 'minced_houttuynia':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/minced_houttuynia.png','c6653c730bb5d1fefab02db05388b0f2e6aefc30')
}
COOKERY_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.13/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.13 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.13 Houttuynia Processing BP'),(rm,'Kaleidoscope Grilling A2.7.13 Houttuynia Processing RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.13 Houttuynia Processing';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_13_Houttuynia_Processing';write(P/'config.json',cfg)

def houttuynia_item():
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:houttuynia','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:houttuynia.name'},
   'minecraft:icon':{'textures':{'default':'houttuynia'}},
   'minecraft:max_stack_size':64,
   'minecraft:allow_off_hand':True,
   'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':0.35},
   'minecraft:food':{'can_always_eat':False,'nutrition':2,'saturation_modifier':0.2},
   'minecraft:use_animation':{'value':'eat'},
   'minecraft:tags':{'tags':['minecraft:is_food']}
  }
 }}

def plain_item(id):
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:'+id,'menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:'+id+'.name'},
   'minecraft:icon':{'textures':{'default':id}},
   'minecraft:max_stack_size':64
  }
 }}

def patch_items():
 write(BP/'items/houttuynia.json',houttuynia_item())
 write(BP/'items/minced_houttuynia.json',plain_item('minced_houttuynia'))
 for id,(src,sha) in ASSETS.items():
  out=RP/f'textures/items/{id}.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(src,sha))
 atlas=load(RP/'textures/item_texture.json')
 for id in ASSETS:atlas['texture_data'][id]={'textures':f'textures/items/{id}'}
 write(RP/'textures/item_texture.json',atlas)
 labels={
  'zh_TW':{'item.kaleidoscope_grilling:houttuynia.name':'折耳根','item.kaleidoscope_grilling:minced_houttuynia.name':'折耳根沫'},
  'zh_CN':{'item.kaleidoscope_grilling:houttuynia.name':'折耳根','item.kaleidoscope_grilling:minced_houttuynia.name':'折耳根沫'},
  'en_US':{'item.kaleidoscope_grilling:houttuynia.name':'Houttuynia','item.kaleidoscope_grilling:minced_houttuynia.name':'Minced Houttuynia'}
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2713_houttuynia_processing_core.js',BP/'scripts/a2713_houttuynia_processing_core.js')
 shutil.copy2(DEV/'a2713_houttuynia_processing_runtime.js',BP/'scripts/a2713_houttuynia_processing_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2712_remaining_knife_drops_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2713_houttuynia_processing_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2713-parity.json',{
  'version':'A2.7.13',
  'scope':'houttuynia item + minced_houttuynia chopping processing',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'java_tag':{
   'id':'kaleidoscope_grilling:ingredients/houttuynia',
   'values':['kaleidoscope_grilling:houttuynia'],
   'direct_item_registration_is_exact_for_locked_baseline':True
  },
  'java_recipe':{
   'id':'kaleidoscope_grilling:chopping_board/minced_houttuynia',
   'input_tag':'kaleidoscope_grilling:ingredients/houttuynia',
   'resolved_input':'kaleidoscope_grilling:houttuynia',
   'cuts':4,'model_id':'kaleidoscope_grilling:houttuynia',
   'result':'kaleidoscope_grilling:minced_houttuynia','count':1
  },
  'items':{
   'houttuynia':{
    'java_kind':'ItemNameBlockItem','max_stack_size':64,'nutrition':2,'saturation_modifier':0.2,
    'texture_git_blob_sha1':ASSETS['houttuynia'][1],
    'bedrock_crop_placer':False
   },
   'minced_houttuynia':{
    'plain_item':True,'max_stack_size':64,'texture_git_blob_sha1':ASSETS['minced_houttuynia'][1]
   }
  },
  'cookery_bedrock':{
   'version':'1.0.6','exact_public_archive_sha256':COOKERY_SHA,'extension_api':1,
   'built_in_houttuynia_board_recipe':False,
   'registration':'public register_recipe event, gated by chopping_board capability',
   'private_scripts_modified':False
  },
  'deferred_acquisition':{
   'fortress_chest_bonus':{
    'java':'chests/nether_bridge extra pool: rolls 1..2, 65% pool chance, houttuynia count 1..3 per successful roll',
    'bedrock':'not implemented in this slice; stable 2.9.0 LootTable/LootPool inspection is read-only and replacing the whole vanilla table is intentionally avoided'
   },
   'fortress_wart_replacement':{
    'java':'new Nether Fortress chunks replace 25% of fortress-bounds nether wart with red-variant houttuynia crop',
    'bedrock':'deferred with crop/worldgen slice'
   },
   'survival_houttuynia_acquisition_complete':False
  },
  'visual_difference':{
   'java_model_id':'kaleidoscope_grilling:houttuynia',
   'exact_java_staged_board_visual':False
  },
  'downstream':{
   'raw_slime_skewer_uses_houttuynia':True,
   'raw_sweet_potato_sheet_skewer_uses_minced_houttuynia':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,12]:raise RuntimeError('A2.7.13 must augment verified A2.7.12')
 patch_versions();patch_items();patch_runtime();report();print('A2.7.13 houttuynia processing complete')
if __name__=='__main__':main()
