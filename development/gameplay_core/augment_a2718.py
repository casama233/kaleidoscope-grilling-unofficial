from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,18]
COOKERY_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if old not in s:raise RuntimeError('A2.7.18 patch anchor missing: '+label)
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.18 Onion Processing BP'),(rm,'Kaleidoscope Grilling A2.7.18 Onion Processing RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.18 Onion Processing';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_18_Onion_Processing';write(P/'config.json',cfg)

def patch_runtime():
 shutil.copy2(DEV/'a2718_onion_processing_core.js',BP/'scripts/a2718_onion_processing_core.js')
 shutil.copy2(DEV/'a2718_onion_processing_runtime.js',BP/'scripts/a2718_onion_processing_runtime.js')
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 anchor="import './a2717_onion_crop_runtime.js';"
 s=replace_once(s,anchor,anchor+"\nimport './a2718_onion_processing_runtime.js';",'runtime import')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2718-parity.json',{
  'version':'A2.7.18','scope':'Onion -> Cookery Millstone -> Onion Powder',
  'java_baseline':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
  'java_recipe':{
   'id':'kaleidoscope_grilling:millstone/onion_powder',
   'type':'kaleidoscope_cookery:millstone',
   'input_tag':'kaleidoscope_grilling:ingredients/onions',
   'tag_chain':['#c:crops/onion','kaleidoscope_grilling:onion'],
   'locked_baseline_resolved_inputs':['kaleidoscope_grilling:onion'],
   'result':'kaleidoscope_grilling:onion_powder','count':1,'chance':1.0
  },
  'cookery_bedrock':{
   'version':'1.0.6','exact_public_archive_sha256':COOKERY_SHA,'extension_api':1,
   'registration':'public register_recipe event, gated by millstone capability',
   'additional_api_ping':False,'private_scripts_modified':False
  },
  'common_tag_compatibility':{
   'java_common_tag_extensible':True,
   'bedrock_third_party_common_tag_expansion':False,
   'locked_baseline_native_input_exact':True,
   'reason':'Cookery Bedrock extension recipe input is an item identifier; the locked Java baseline resolves to Grilling Onion only, but Java modpacks may add third-party onions to c:crops/onion.'
  },
  'chain':{
   'straw_hat_short_grass_to_onion':'A2.7.17',
   'onion_crop_reproduction':'A2.7.17',
   'onion_to_powder':'A2.7.18',
   'survival_onion_processing_chain_complete':True
  },
  'create_optional_processing':{
   'java_milling_recipe_exists':True,
   'bedrock_create_ported':False,
   'required_for_cookery_survival_chain':False
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,17]:raise RuntimeError('A2.7.18 must augment verified A2.7.17')
 patch_versions();patch_runtime();report();print('A2.7.18 onion processing complete')
if __name__=='__main__':main()
