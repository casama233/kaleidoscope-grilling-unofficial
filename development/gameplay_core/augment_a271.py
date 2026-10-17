from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,1]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ASSETS={
 'sweet_potato_powder':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/sweet_potato_powder.png','2e15c9ea095ff0ef7c7959b05bd9f60d79631dab'),
 'raw_sweet_potato_sheet':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/raw_sweet_potato_sheet.png','a537de022aa9cc50b99dfec6f0fedd0046cb2d2f')
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.1/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 if blob(v)!=sha:raise RuntimeError('pinned upstream mismatch '+path)
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.1 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_manifest():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.1 Gameplay BP'),(rm,'Kaleidoscope Grilling A2.7.1 Gameplay RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.1 Gameplay';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_1';write(P/'config.json',cfg)

def copy_runtime():
 shutil.copy2(DEV/'a271_sweet_potato_core.js',BP/'scripts/a271_sweet_potato_core.js')
 shutil.copy2(DEV/'a271_sweet_potato_runtime.js',BP/'scripts/a271_sweet_potato_runtime.js')
 main=BP/'scripts/main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a26_oil_machine_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a271_sweet_potato_runtime.js';",'main runtime import')
 old="function isEdible(stack){try{return !!stack?.getComponent('minecraft:food')}catch{return false}}"
 new="function isEdible(stack){if(stack?.typeId==='kaleidoscope_grilling:sweet_potato_powder')return false;try{return !!stack?.getComponent('minecraft:food')}catch{return false}}"
 s=replace_once(s,old,new,'pseudo-food skewer exclusion')
 main.write_text(s,encoding='utf-8')

def powder_item():
 return {
  'format_version':'1.26.30',
  'minecraft:item':{
   'description':{'identifier':'kaleidoscope_grilling:sweet_potato_powder','menu_category':{'category':'items'}},
   'components':{
    'minecraft:display_name':{'value':'item.kaleidoscope_grilling:sweet_potato_powder.name'},
    'minecraft:icon':{'textures':{'default':'sweet_potato_powder'}},
    'minecraft:max_stack_size':64,
    'minecraft:allow_off_hand':True,
    'minecraft:use_modifiers':{'start_using':'always','use_duration':1.5,'movement_modifier':0.2},
    'minecraft:food':{'can_always_eat':True,'nutrition':0,'saturation_modifier':0.0},
    'minecraft:use_animation':{'value':'bow'}
   }
  }
 }
def plain_item(id):
 return {
  'format_version':'1.26.30',
  'minecraft:item':{
   'description':{'identifier':'kaleidoscope_grilling:'+id,'menu_category':{'category':'items'}},
   'components':{
    'minecraft:display_name':{'value':'item.kaleidoscope_grilling:'+id+'.name'},
    'minecraft:icon':{'textures':{'default':id}},
    'minecraft:max_stack_size':64
   }
  }
 }

def patch_content():
 write(BP/'items/sweet_potato_powder.json',powder_item())
 write(BP/'items/raw_sweet_potato_sheet.json',plain_item('raw_sweet_potato_sheet'))
 for id,(path,sha) in ASSETS.items():
  out=RP/f'textures/items/{id}.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(path,sha))
 itemtex=load(RP/'textures/item_texture.json')
 for id in ASSETS:itemtex['texture_data'][id]={'textures':f'textures/items/{id}'}
 write(RP/'textures/item_texture.json',itemtex)

 labels={
  'zh_TW':{
   'item.kaleidoscope_grilling:sweet_potato_powder.name':'紅薯粉',
   'item.kaleidoscope_grilling:raw_sweet_potato_sheet.name':'生苕皮'
  },
  'zh_CN':{
   'item.kaleidoscope_grilling:sweet_potato_powder.name':'红薯粉',
   'item.kaleidoscope_grilling:raw_sweet_potato_sheet.name':'生苕皮'
  },
  'en_US':{
   'item.kaleidoscope_grilling:sweet_potato_powder.name':'Sweet Potato Powder',
   'item.kaleidoscope_grilling:raw_sweet_potato_sheet.name':'Raw Sweet Potato Sheet'
  }
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,val in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+val
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def report():
 write(P/'reports/a271-parity.json',{
  'version':'A2.7.1',
  'scope':'sweet potato powder direct kneading only; this is not the full A2.7 recipe reconciliation',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'items':['kaleidoscope_grilling:sweet_potato_powder','kaleidoscope_grilling:raw_sweet_potato_sheet'],
  'direct_knead':{
   'duration_ticks':30,'duration_seconds':1.5,'use_animation':'bow','transforms_entire_starting_stack':True,
   'completion_sound':'armor.equip_leather','volume':0.8,'pitch':1.1
  },
  'java_alternate_processing':{
   'cookery_chopping_board':{'cut_count':4,'ported_in_this_slice':False},
   'cookery_millstone_sweet_potato_to_powder':False,
   'create_milling_sweet_potato_to_powder':False
  },
  'known_platform_substitutions':[
   'Bedrock retail needs a native use-capable component to emit start/complete-use events. The powder uses a zero-nutrition always-usable food component only as an input shim, while the script performs the Java full-stack transformation.',
   'The pseudo-food input shim is explicitly excluded from Secret Skewer ingredient eligibility.',
   'Cookery chopping-board and millstone integration are intentionally deferred to the next small A2.7 processing slice instead of being reported as complete.'
  ],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,6,0]:raise RuntimeError('A2.7.1 must augment the verified A2.6 baseline')
 patch_manifest();copy_runtime();patch_content();report();print('A2.7.1 sweet-potato kneading augmentation complete')
if __name__=='__main__':main()
