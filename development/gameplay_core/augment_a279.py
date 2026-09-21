from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,9]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
TEX_PATH='common/src/main/resources/assets/kaleidoscope_grilling/textures/item/beef_chunks.png'
TEX_SHA='6b9a7d3f3b153ab42c0f725abc34b4b56003c5e1'
COOKERY_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.9/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.9 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.9 Beef Board Override BP'),(rm,'Kaleidoscope Grilling A2.7.9 Beef Board Override RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.9 Beef Board Override';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_9_Beef_Board_Override';write(P/'config.json',cfg)

def patch_item():
 item={'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':'kaleidoscope_grilling:beef_chunks','menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:beef_chunks.name'},
   'minecraft:icon':{'textures':{'default':'beef_chunks'}},
   'minecraft:max_stack_size':64
  }
 }}
 write(BP/'items/beef_chunks.json',item)
 out=RP/'textures/items/beef_chunks.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(TEX_PATH,TEX_SHA))
 tex=load(RP/'textures/item_texture.json');tex['texture_data']['beef_chunks']={'textures':'textures/items/beef_chunks'};write(RP/'textures/item_texture.json',tex)
 labels={'zh_TW':'牛肉塊','zh_CN':'牛肉块','en_US':'Beef Chunks'}
 for lang,value in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8');key='item.kaleidoscope_grilling:beef_chunks.name'
  if key+'=' not in text:text+='\n'+key+'='+value
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a279_beef_board_core.js',BP/'scripts/a279_beef_board_core.js')
 shutil.copy2(DEV/'a279_beef_board_runtime.js',BP/'scripts/a279_beef_board_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a278_basic_chopping_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport {tryScheduleBeefBoardOverride} from './a279_beef_board_runtime.js';",'runtime import')
 hook="world.beforeEvents.playerInteractWithBlock.subscribe(e=>{\n const skewerInput=skewerAction(e.player,e.itemStack??heldMain(e.player));"
 replacement="world.beforeEvents.playerInteractWithBlock.subscribe(e=>{\n if(tryScheduleBeefBoardOverride(e))return;\n const skewerInput=skewerAction(e.player,e.itemStack??heldMain(e.player));"
 s=replace_once(s,hook,replacement,'board override hook')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a279-parity.json',{
  'version':'A2.7.9',
  'scope':'beef_chunks item plus Java-compatible Cookery beef chopping-board override',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'java_recipe':{
   'recipe_namespace':'kaleidoscope_cookery',
   'input':'minecraft:beef','cuts':4,
   'model_id':'kaleidoscope_cookery:raw_cow_offal',
   'result':'kaleidoscope_grilling:beef_chunks','count':2
  },
  'beef_chunks':{'plain_item':True,'max_stack_size':64,'texture_git_blob_sha1':TEX_SHA},
  'cookery_bedrock':{
   'version':'1.0.6','exact_public_archive_sha256':COOKERY_SHA,
   'builtin':'minecraft:beef -> kaleidoscope_cookery:raw_cow_offal x2, 4 cuts',
   'lookup_priority':'BOARD_RECIPES[id] || getExtensionBoardRecipe(id)',
   'override_strategy':'cancel first empty-board beef interaction in Grilling before-event handler, then write Cookery canonical station state in system.run',
   'station_key':'kc_station:<dimension>:<x>,<y>,<z>',
   'native_beef_board_model':0,
   'cookery_private_scripts_modified':False
  },
  'behavior':{
   'new_insert':{'result':'beef_chunks x2','cuts':4,'survival_consumes_beef':1,'creative_consumes_beef':0},
   'in_progress_migration':'built-in beef states retain current cuts and replace only result contract; first migration interaction is intentionally consumed',
   'stale_hand_guard':True,
   'transaction_rollback':'station raw state + block permutation + main hand restored best-effort on commit exception'
  },
  'visual_parity':{
   'java_model_id':'kaleidoscope_cookery:raw_cow_offal',
   'bedrock_reuses_cookery_native_beef_model':True,
   'structural_model_mapping_verified':True,
   'engine_rendering_verified':False
  },
  'downstream':{
   'raw_beef_skewer_recipe_already_references_beef_chunks':True,
   'fixed_skewer_chain_becomes_obtainable_when_red_chili_is_available':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,8]:raise RuntimeError('A2.7.9 must augment verified A2.7.8')
 patch_versions();patch_item();patch_runtime();report();print('A2.7.9 beef board override complete')
if __name__=='__main__':main()
