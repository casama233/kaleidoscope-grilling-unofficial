from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,16]
COOKERY_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.16 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.16 Canola Processing BP'),(rm,'Kaleidoscope Grilling A2.7.16 Canola Processing RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.16 Canola Processing';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_16_Canola_Processing';write(P/'config.json',cfg)

def patch_runtime():
 shutil.copy2(DEV/'a2716_canola_processing_core.js',BP/'scripts/a2716_canola_processing_core.js')
 shutil.copy2(DEV/'a2716_canola_processing_runtime.js',BP/'scripts/a2716_canola_processing_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2715_canola_crop_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2716_canola_processing_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2716-parity.json',{
  'version':'A2.7.16','scope':'canola seeds -> Cookery Millstone -> canola powder',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'java_recipe':{
   'id':'kaleidoscope_grilling:millstone/canola_powder',
   'type':'kaleidoscope_cookery:millstone',
   'input_tag':'kaleidoscope_grilling:ingredients/canola_seeds',
   'resolved_input':'kaleidoscope_grilling:canola_seeds',
   'tag_values':['kaleidoscope_grilling:canola_seeds'],
   'result':'kaleidoscope_grilling:canola_powder','count':1,'chance':1.0
  },
  'cookery_bedrock':{
   'version':'1.0.6','exact_public_archive_sha256':COOKERY_SHA,'extension_api':1,
   'registration':'public register_recipe event, gated by millstone capability',
   'additional_api_ping':False,'private_scripts_modified':False
  },
  'chain':{
   'straw_hat_short_grass_to_canola_seeds':'A2.7.15',
   'canola_crop_reproduction':'A2.7.15',
   'canola_seeds_to_powder':'A2.7.16',
   'oil_cake_recipe':'8 canola_powder + 1 wheat -> oil_cake',
   'oil_press_big_vat':'A2.6',
   'canola_oil_survival_chain_complete':True
  },
  'create_optional_processing':{
   'crushing_milling_java_recipes_exist':True,
   'bedrock_create_ported':False,
   'required_for_survival_chain':False
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,15]:raise RuntimeError('A2.7.16 must augment verified A2.7.15')
 patch_versions();patch_runtime();report();print('A2.7.16 canola processing complete')
if __name__=='__main__':main()
