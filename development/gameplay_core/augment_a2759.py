from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,58]
CORE='a2759_pepper_worldgen_fruiting_core.js'
RUNTIME='a2759_pepper_worldgen_fruiting_runtime.js'
BLOCK='a2759_pepper_leaves_fruiting_bridge.block.json'
FEATURE='a2759_pepper_tree_worldgen.feature.json'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.59 P1 Completion BP'),
  (rm,'Kaleidoscope Grilling A2.7.59 P1 Completion RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.59 P1 Completion'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_58_P1_Completion'
 write(P/'config.json',cfg)

def patch_content():
 shutil.copy2(DEV/CORE,BP/'scripts'/CORE)
 shutil.copy2(DEV/RUNTIME,BP/'scripts'/RUNTIME)
 shutil.copy2(DEV/BLOCK,BP/'blocks'/'pepper_leaves_fruiting_bridge.json')
 shutil.copy2(DEV/FEATURE,BP/'features'/'pepper_tree_worldgen.json')
 main=BP/'scripts/main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2748_pepper_tree_runtime.js';\n"
 add=anchor+"import './a2759_pepper_worldgen_fruiting_runtime.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.59 Pepper runtime anchor drift')
 if 'a2759_pepper_worldgen_fruiting_runtime.js' in s:raise RuntimeError('A2.7.59 runtime already active')
 main.write_text(s.replace(anchor,add,1),encoding='utf-8')

def report():
 write(P/'reports/a2759-p1-completion.json',{
  'version':'A2.7.59',
  'scope':'close remaining actionable P1 parity after auditing Advanced Rack and Pepper Tree',
  'advanced_rack':{
   'complete':True,'version':'A2.7.46',
   'compartments':9,'seasoning_slots':5,'tool_slots':4,
   'persistent_filters':True,'deposit_matching':True,'hotbar_binding':True,
   'break_preserves_contents':True,'automation_borrow_return':True,
   'bedrock_equivalent_ui':'ActionFormData + namespaced nearby-rack command'
  },
  'pepper_tree':{
   'lifecycle_complete':True,'lifecycle_version':'A2.7.48',
   'forest_worldgen':True,'worldgen_version':'A2.7.51',
   'village_acquisition':True,'village_version':'A2.7.54',
   'pepper_picked_advancement':True,'advancement_version':'A2.7.53',
   'worldgen_initial_fruiting_probability':0.25,
   'worldgen_leaf_weights':[3,1],
   'worldgen_bridge_is_internal':True,
   'worldgen_bridge_canonicalizes_after_ticks':1
  },
  'platform_limit':{
   'java_entity_inside_continuous_leaf_sting':True,
   'bedrock_stable_on_entity_inside':False,
   'bedrock_mapping':'onStepOn + short slowness + 20-tick damage throttle',
   'global_entity_leaf_polling_added':False
  },
  'p1_actionable_complete':True,
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,58]:
  raise RuntimeError('A2.7.59 must augment published A2.7.58')
 patch_content();patch_versions();report()
 print('A2.7.59 P1 completion applied')

if __name__=='__main__':main()
