from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,2]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
COOKERY_ARCHIVE_SHA256='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
ASSETS={
 'sweet_potato':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/sweet_potato.png','6761c2d89d46df2e536dd6df3fe9fdb7c2262259')
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.2/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 if blob(v)!=sha:raise RuntimeError('pinned upstream mismatch '+path)
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.2 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_manifest():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.2 Gameplay BP'),(rm,'Kaleidoscope Grilling A2.7.2 Gameplay RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.2 Gameplay';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_2';write(P/'config.json',cfg)

def copy_runtime():
 shutil.copy2(DEV/'a272_cookery_processing_core.js',BP/'scripts/a272_cookery_processing_core.js')
 shutil.copy2(DEV/'a272_cookery_processing_runtime.js',BP/'scripts/a272_cookery_processing_runtime.js')
 main=BP/'scripts/main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a271_sweet_potato_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a272_cookery_processing_runtime.js';",'main runtime import')
 main.write_text(s,encoding='utf-8')

def sweet_potato_item():
 return {
  'format_version':'1.26.30',
  'minecraft:item':{
   'description':{'identifier':'kaleidoscope_grilling:sweet_potato','menu_category':{'category':'items'}},
   'components':{
    'minecraft:display_name':{'value':'item.kaleidoscope_grilling:sweet_potato.name'},
    'minecraft:icon':{'textures':{'default':'sweet_potato'}},
    'minecraft:max_stack_size':64,
    'minecraft:allow_off_hand':True,
    'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':0.35},
    'minecraft:food':{'can_always_eat':False,'nutrition':3,'saturation_modifier':0.1},
    'minecraft:use_animation':{'value':'eat'},
    'minecraft:tags':{'tags':['minecraft:is_food']}
   }
  }
 }

def patch_content():
 write(BP/'items/sweet_potato.json',sweet_potato_item())
 for id,(path,sha) in ASSETS.items():
  out=RP/f'textures/items/{id}.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(path,sha))
 itemtex=load(RP/'textures/item_texture.json')
 for id in ASSETS:itemtex['texture_data'][id]={'textures':f'textures/items/{id}'}
 write(RP/'textures/item_texture.json',itemtex)
 labels={
  'zh_TW':{'item.kaleidoscope_grilling:sweet_potato.name':'紅薯'},
  'zh_CN':{'item.kaleidoscope_grilling:sweet_potato.name':'红薯'},
  'en_US':{'item.kaleidoscope_grilling:sweet_potato.name':'Sweet Potato'}
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,val in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+val
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def report():
 write(P/'reports/a272-parity.json',{
  'version':'A2.7.2',
  'scope':'Cookery public-API adapter for the sweet-potato Millstone and Chopping Board chain only',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'cookery_bedrock':{
   'version':'1.0.6','bp_uuid':'10f37ae2-9ccf-435f-b34b-0eec8191cd94','rp_uuid':'c89dc8df-c3fc-4bc8-8bd0-527abba76681',
   'exact_public_archive_sha256':COOKERY_ARCHIVE_SHA256,'extension_recipe_api':1,
   'events':['kaleidoscope_cookery:api_ping','kaleidoscope_cookery:api_ready','kaleidoscope_cookery:register_recipe'],
   'required_capabilities':['chopping_board','millstone']
  },
  'sweet_potato_item':{'nutrition':3,'saturation_modifier':0.1,'crop_planting_ported':False},
  'recipes':{
   'chopping_board':{'input':'kaleidoscope_grilling:sweet_potato_powder','result':'kaleidoscope_grilling:raw_sweet_potato_sheet','count':1,'cuts':4,'registered_through_public_api':True},
   'millstone':{'input':'kaleidoscope_grilling:sweet_potato','result':'kaleidoscope_grilling:sweet_potato_powder','count':1,'chance':1.0,'registered_through_public_api':True}
  },
  'java_audio_difference':{
   'java_second_cut_bucket_empty_sound':True,
   'bedrock_public_api_stage_sound_hook':False,
   'status':'gameplay-equivalent recipe timing/result; second-cut sound remains an explicit audio-only difference'
  },
  'create_milling_ported':False,
  'known_boundaries':[
   'Cookery station recipes are registered only after api_ready and only when the exact advertised capability is present; the addon does not import Cookery private scripts.',
   'The Java sweet_potato ItemNameBlockItem also plants the crop. A2.7.2 adds the edible gameplay item required by the Millstone chain; Bedrock crop planting/growth remains A2.8.',
   'Java replaces the second chopping sound with BUCKET_EMPTY via a Cookery mixin. Cookery Extension Recipe API v1 has no per-cut sound field, so A2.7.2 keeps Cookery normal board audio rather than patching the host.',
   'Create Milling remains Java/Create integration and is not claimed as Bedrock Cookery parity in this slice.'
  ],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,1]:raise RuntimeError('A2.7.2 must augment the verified A2.7.1 baseline')
 patch_manifest();copy_runtime();patch_content();report();print('A2.7.2 Cookery processing augmentation complete')
if __name__=='__main__':main()
