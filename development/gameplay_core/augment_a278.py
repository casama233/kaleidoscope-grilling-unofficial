from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,8]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ASSETS={
 'carrot_dice':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/carrot_dice.png','c5359f186611411d51f1fe55077357d2c16efa61'),
 'potato_slice':('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/potato_slice.png','9562676753ad5e32ea0e1345236e314ad4767b85')
}
COOKERY_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.8/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.8 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.8 Basic Chopping I BP'),(rm,'Kaleidoscope Grilling A2.7.8 Basic Chopping I RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.8 Basic Chopping I';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_8_Basic_Chopping_I';write(P/'config.json',cfg)

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
 for id,(src,sha) in ASSETS.items():
  write(BP/f'items/{id}.json',plain_item(id))
  out=RP/f'textures/items/{id}.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(src,sha))
 tex=load(RP/'textures/item_texture.json')
 for id in ASSETS:tex['texture_data'][id]={'textures':f'textures/items/{id}'}
 write(RP/'textures/item_texture.json',tex)
 labels={
  'zh_TW':{
   'item.kaleidoscope_grilling:carrot_dice.name':'胡蘿蔔粒',
   'item.kaleidoscope_grilling:potato_slice.name':'馬鈴薯片'
  },
  'zh_CN':{
   'item.kaleidoscope_grilling:carrot_dice.name':'胡萝卜粒',
   'item.kaleidoscope_grilling:potato_slice.name':'土豆片'
  },
  'en_US':{
   'item.kaleidoscope_grilling:carrot_dice.name':'Carrot Dice',
   'item.kaleidoscope_grilling:potato_slice.name':'Potato Slice'
  }
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a278_basic_chopping_core.js',BP/'scripts/a278_basic_chopping_core.js')
 shutil.copy2(DEV/'a278_basic_chopping_runtime.js',BP/'scripts/a278_basic_chopping_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a272_cookery_processing_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a278_basic_chopping_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a278-parity.json',{
  'version':'A2.7.8',
  'scope':'first conflict-free basic chopping slice: carrot_dice + potato_slice',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'cookery_bedrock':{
   'version':'1.0.6','exact_public_archive_sha256':COOKERY_SHA,'extension_api':1,
   'lookup_priority_observed':'BOARD_RECIPES[input] || getExtensionBoardRecipe(input)'
  },
  'items':{
   'carrot_dice':{'plain_item':True,'max_stack_size':64,'texture_git_blob_sha1':ASSETS['carrot_dice'][1]},
   'potato_slice':{'plain_item':True,'max_stack_size':64,'texture_git_blob_sha1':ASSETS['potato_slice'][1]}
  },
  'recipes':{
   'carrot_dice':{'input':'minecraft:carrot','result':'kaleidoscope_grilling:carrot_dice','count':3,'cuts':4,'registered_through_public_api':True},
   'potato_slice':{'input':'minecraft:potato','result':'kaleidoscope_grilling:potato_slice','count':3,'cuts':4,'registered_through_public_api':True}
  },
  'explicitly_deferred_conflict':{
   'beef_chunks':{
    'java_grilling':'minecraft:beef -> kaleidoscope_grilling:beef_chunks x2, 4 cuts',
    'cookery_bedrock_builtin':'minecraft:beef -> kaleidoscope_cookery:raw_cow_offal x2',
    'reason':'Cookery 1.0.6 directStation checks built-in BOARD_RECIPES before extension recipes, so public recipe registration cannot override this input.',
    'planned_slice':'A2.7.9'
   }
  },
  'visual_difference':{
   'java_model_ids':['kaleidoscope_grilling:carrot_dice','kaleidoscope_grilling:potato_slice'],
   'bedrock':'Cookery public recipe API uses generic foreign-item display fallback unless an addon separately supplies board display/native-model assets.',
   'exact_java_staged_board_visual':False
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,7]:raise RuntimeError('A2.7.8 must augment verified A2.7.7')
 patch_versions();patch_items();patch_runtime();report();print('A2.7.8 basic chopping I complete')
if __name__=='__main__':main()
