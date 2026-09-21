from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,10]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
TEX_PATH='common/src/main/resources/assets/kaleidoscope_grilling/textures/item/raw_mantou_slice.png'
TEX_SHA='c89c916e0611d7de9d821e122b2d88c099809cbf'
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
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.10 Mantou Chopping BP'),(rm,'Kaleidoscope Grilling A2.7.10 Mantou Chopping RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.10 Mantou Chopping';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_10_Mantou_Chopping';write(P/'config.json',cfg)

def patch_item():
 item={'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:raw_mantou_slice','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:raw_mantou_slice.name'},
   'minecraft:icon':{'textures':{'default':'raw_mantou_slice'}},
   'minecraft:max_stack_size':64
  }
 }}
 write(BP/'items/raw_mantou_slice.json',item)
 out=RP/'textures/items/raw_mantou_slice.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(TEX_PATH,TEX_SHA))
 atlas=load(RP/'textures/item_texture.json');atlas['texture_data']['raw_mantou_slice']={'textures':'textures/items/raw_mantou_slice'};write(RP/'textures/item_texture.json',atlas)
 labels={'zh_TW':'生饅頭片','zh_CN':'生馒头片','en_US':'Raw Mantou Slice'}
 for lang,value in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8');key='item.kaleidoscope_grilling:raw_mantou_slice.name'
  if key+'=' not in text:text+='\n'+key+'='+value
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2710_mantou_chopping_core.js',BP/'scripts/a2710_mantou_chopping_core.js')
 shutil.copy2(DEV/'a2710_mantou_chopping_runtime.js',BP/'scripts/a2710_mantou_chopping_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import {tryScheduleBeefBoardOverride} from './a279_beef_board_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2710_mantou_chopping_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2710-parity.json',{
  'version':'A2.7.10',
  'scope':'raw_mantou_slice item plus conflict-free Cookery mantou chopping recipe',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'java_recipe':{
   'id':'kaleidoscope_grilling:chopping_board/raw_mantou_slice',
   'input':'kaleidoscope_cookery:mantou','cuts':4,
   'model_id':'kaleidoscope_grilling:raw_mantou_slice',
   'result':'kaleidoscope_grilling:raw_mantou_slice','count':3
  },
  'raw_mantou_slice':{'plain_item':True,'max_stack_size':64,'texture_git_blob_sha1':TEX_SHA},
  'cookery_bedrock':{
   'version':'1.0.6','exact_public_archive_sha256':COOKERY_SHA,'extension_api':1,
   'built_in_mantou_board_recipe':False,
   'registration':'public register_recipe event, gated by chopping_board capability',
   'initial_ping_owner':'A2.7.8 runtime; A2.7.10 only adds an api_ready listener to avoid duplicate pings'
  },
  'downstream':{
   'raw_bun_slice_skewer_recipe_already_exists':True,
   'required_raw_mantou_slices':3,
   'mantou_to_fixed_bun_skewer_chain_reachable':True
  },
  'visual_difference':{
   'java_model_id':'kaleidoscope_grilling:raw_mantou_slice',
   'bedrock':'Cookery extension recipe uses its generic foreign-item board display fallback.',
   'exact_java_staged_board_visual':False
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,9]:raise RuntimeError('A2.7.10 must augment verified A2.7.9')
 patch_versions();patch_item();patch_runtime();report();print('A2.7.10 mantou chopping complete')
if __name__=='__main__':main()
