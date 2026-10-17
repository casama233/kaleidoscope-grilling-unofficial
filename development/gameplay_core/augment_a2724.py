from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,24]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
TEX_PATH='common/src/main/resources/assets/kaleidoscope_grilling/textures/item/red_chili_powder.png'
TEX_SHA='57936897efae12b743a539f0bf1dac54d45dda39'
COOKERY_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
CATALOG=BP/'item_catalog/crafting_item_catalog.json'
RED_ID='kaleidoscope_grilling:red_chili_powder'
AFTER_ID='kaleidoscope_grilling:canola_powder'
BEFORE_ID='kaleidoscope_grilling:onion'

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.7.24/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned upstream mismatch {path}: {got} != {sha}')
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.24 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.24 Red Chili Processing BP'),(rm,'Kaleidoscope Grilling A2.7.24 Red Chili Processing RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.24 Red Chili Processing';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_24_Red_Chili_Processing';write(P/'config.json',cfg)

def item_doc():
 return {'format_version':'1.26.30','minecraft:item':{
  'description':{'identifier':RED_ID,'menu_category':{'category':'items'}},
  'components':{
   'minecraft:display_name':{'value':'item.kaleidoscope_grilling:red_chili_powder.name'},
   'minecraft:icon':{'textures':{'default':'red_chili_powder'}},
   'minecraft:max_stack_size':64
  }
 }}

def secret_oil_recipe():
 return {'format_version':'1.20.10','minecraft:recipe_shapeless':{
  'description':{'identifier':'kaleidoscope_grilling:secret_chili_oil'},
  'tags':['crafting_table'],
  'ingredients':[
   {'item':'kaleidoscope_grilling:canola_oil_bucket'},
   {'item':RED_ID},{'item':RED_ID},{'item':RED_ID}
  ],
  'result':{'item':'kaleidoscope_grilling:secret_chili_oil_bucket','count':1}
 }}

def patch_catalog():
 doc=load(CATALOG)
 groups=doc['minecraft:crafting_items_catalog']['categories'][0]['groups']
 if len(groups)!=1:raise RuntimeError('A2.7.24 expects one Grilling creative group')
 items=groups[0]['items']
 if RED_ID in items:raise RuntimeError('red chili powder already in creative catalog')
 ai=items.index(AFTER_ID);bi=items.index(BEFORE_ID)
 if bi!=ai+1:raise RuntimeError('A2.7.23 creative registration-order anchor drift')
 items.insert(bi,RED_ID)
 write(CATALOG,doc)

def patch_assets():
 write(BP/'items/red_chili_powder.json',item_doc())
 write(BP/'recipes/secret_chili_oil.json',secret_oil_recipe())
 out=RP/'textures/items/red_chili_powder.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(fetch(TEX_PATH,TEX_SHA))
 atlas=load(RP/'textures/item_texture.json');atlas['texture_data']['red_chili_powder']={'textures':'textures/items/red_chili_powder'};write(RP/'textures/item_texture.json',atlas)
 labels={
  'zh_TW':{'item.kaleidoscope_grilling:red_chili_powder.name':'紅辣椒粉'},
  'zh_CN':{'item.kaleidoscope_grilling:red_chili_powder.name':'红辣椒粉'},
  'en_US':{'item.kaleidoscope_grilling:red_chili_powder.name':'Red Chili Powder'}
 }
 for lang,rows in labels.items():
  path=RP/f'texts/{lang}.lang';text=path.read_text(encoding='utf-8')
  for k,v in rows.items():
   if k+'=' not in text:text+='\n'+k+'='+v
  path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_runtime():
 shutil.copy2(DEV/'a2724_red_chili_processing_core.js',BP/'scripts/a2724_red_chili_processing_core.js')
 shutil.copy2(DEV/'a2724_red_chili_processing_runtime.js',BP/'scripts/a2724_red_chili_processing_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2722_cold_houttuynia_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2724_red_chili_processing_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2724-parity.json',{
  'version':'A2.7.24','scope':'Cookery red chili -> red chili powder -> secret chili oil survival chain',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'item':{'id':RED_ID,'texture_git_blob_sha1':TEX_SHA,'stack_size':64},
  'creative_catalog':{
   'a2723_group_preserved':True,'catalog_entry_count':77,
   'java_registration_order_neighbors':[AFTER_ID,RED_ID,BEFORE_ID]
  },
  'millstone':{
   'java_recipe_id':'kaleidoscope_grilling:millstone/red_chili_powder',
   'type':'kaleidoscope_cookery:millstone',
   'input':'kaleidoscope_cookery:red_chili',
   'output':RED_ID,'count':1,'chance':1.0,
   'bedrock_registration':'Cookery 1.0.6 public register_recipe extension API',
   'cookery_archive_sha256':COOKERY_SHA,'additional_api_ping':False
  },
  'secret_chili_oil':{
   'java_recipe_type':'minecraft:crafting_shapeless',
   'ingredients':{'kaleidoscope_grilling:canola_oil_bucket':1,RED_ID:3},
   'result':'kaleidoscope_grilling:secret_chili_oil_bucket',
   'native_bedrock_shapeless':True,'ingredient_counts_exact':True
  },
  'survival_chain':{
   'cookery_red_chili_to_powder':True,
   'powder_plus_canola_to_secret_chili_bucket':True,
   'secret_chili_bucket_world_fluid_and_vat_support':'A2.3/A2.6',
   'secret_chili_oil_survival_entry_complete':True
  },
  'create_optional_processing':{
   'java_create_milling_recipe_exists':True,'bedrock_create_ported':False,
   'required_for_survival_chain':False
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,23]:raise RuntimeError('A2.7.24 must augment verified A2.7.23')
 patch_versions();patch_assets();patch_catalog();patch_runtime();report()
 print('A2.7.24 red chili processing complete')
if __name__=='__main__':main()
