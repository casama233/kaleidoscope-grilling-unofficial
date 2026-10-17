from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,12]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
TEX_PATH='common/src/main/resources/assets/kaleidoscope_grilling/textures/item/squid_tentacle.png'
TEX_SHA='60aab20cf2c9c4b250780430f7114c22ae7b9dff'
JAVA_KNIFE_SHA='4acd1490f9302e3698795c291e2907bdafaf14c8'
COOKERY_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.12/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.12 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.12 Remaining Knife Drops BP'),(rm,'Kaleidoscope Grilling A2.7.12 Remaining Knife Drops RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.12 Remaining Knife Drops';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_12_Remaining_Knife_Drops';write(P/'config.json',cfg)

def patch_item():
 item={'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:squid_tentacle','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:squid_tentacle.name'},
   'minecraft:icon':{'textures':{'default':'squid_tentacle'}},
   'minecraft:max_stack_size':64
  }
 }}
 write(BP/'items/squid_tentacle.json',item)
 out=RP/'textures/items/squid_tentacle.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(TEX_PATH,TEX_SHA))
 atlas=load(RP/'textures/item_texture.json');atlas['texture_data']['squid_tentacle']={'textures':'textures/items/squid_tentacle'};write(RP/'textures/item_texture.json',atlas)
 labels={'zh_TW':'魷魚鬚','zh_CN':'鱿鱼须','en_US':'Squid Tentacle'}
 for lang,value in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8');key='item.kaleidoscope_grilling:squid_tentacle.name'
  if key+'=' not in text:text+='\n'+key+'='+value
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2712_remaining_knife_drops_core.js',BP/'scripts/a2712_remaining_knife_drops_core.js')
 shutil.copy2(DEV/'a2712_remaining_knife_drops_runtime.js',BP/'scripts/a2712_remaining_knife_drops_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2711_mantou_chopping_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2712_remaining_knife_drops_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2712-parity.json',{
  'version':'A2.7.12',
  'scope':'remaining Java KnifeDropHandler parity: cow raw offal + squid tentacle',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'java_source':{
   'path':'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/KnifeDropHandler.java',
   'git_blob_sha1':JAVA_KNIFE_SHA
  },
  'cookery_bedrock':{
   'version':'1.0.6','exact_public_archive_sha256':COOKERY_SHA,
   'knife_ids_owned_by_a2710_contract':True,
   'raw_cow_offal_item_required':True,
   'private_scripts_modified':False
  },
  'items':{
   'raw_cow_offal':{'namespace':'kaleidoscope_cookery','owned_by_grilling':False},
   'squid_tentacle':{'plain_item':True,'max_stack_size':64,'texture_git_blob_sha1':TEX_SHA}
  },
  'drops':{
   'cow':{
    'entity':'minecraft:cow','result':'kaleidoscope_cookery:raw_cow_offal',
    'chance':1.0,'base_count':'1 + random(0..1)','looting_bonus':'random(0..Looting level)'
   },
   'squid':{
    'entity':'minecraft:squid','result':'kaleidoscope_grilling:squid_tentacle',
    'chance':0.5,'base_count':'2 + random(0..1)','looting_bonus':'random(0..Looting level)'
   }
  },
  'trigger_semantics':{
   'killer':'damageSource.damagingEntity must be minecraft:player',
   'weapon':'player current main hand must be one of the Cookery kitchen knife ids pinned by A2.7.10',
   'projectile_note':'no explicit projectile rejection, matching Java causing-player/current-main-hand logic'
  },
  'downstream':{
   'raw_squid_tentacle_skewer_recipe_already_references_squid_tentacle':True,
   'squid_fixed_skewer_chain_reachable':True,
   'cow_offal_restores_java_kitchen_knife_bonus_drop':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,11]:raise RuntimeError('A2.7.12 must augment verified A2.7.11')
 patch_versions();patch_item();patch_runtime();report();print('A2.7.12 remaining knife drops complete')
if __name__=='__main__':main()
