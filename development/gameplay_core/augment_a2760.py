from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,60]
FEATURE='a2760_pepper_tree_worldgen.feature.json'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.60 Pepper Worldgen BDS Fix BP'),
  (rm,'Kaleidoscope Grilling A2.7.60 Pepper Worldgen BDS Fix RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)

 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.60 Pepper Worldgen BDS Fix'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_60_Pepper_Worldgen_BDS_Fix'
 write(P/'config.json',cfg)

def patch_feature():
 shutil.copy2(DEV/FEATURE,BP/'features'/'pepper_tree_worldgen.json')

def report():
 write(P/'reports/a2760-pepper-worldgen-bds-fix.json',{
  'version':'A2.7.60',
  'scope':'promote the BDS-validated Pepper Tree trunk_lean schema fix into the canonical gameplay_core pack',
  'bug':{
   'feature':'kaleidoscope_grilling:pepper_tree_worldgen',
   'previous_missing':['lean_height','lean_steps'],
   'symptom':'tree feature fails to register; feature rule reports no definition',
   'source_pack_was_affected':True,
   'server_build_shim_already_worked_around_it':True
  },
  'fix':{
   'allow_diagonal_growth':False,
   'lean_height':{'base':1,'intervals':[1],'min_height_for_canopy':2},
   'lean_steps':{'base':1,'intervals':[1]},
   'worldgen_leaf_weights':[3,1],
   'initial_fruiting_probability':0.25
  },
  'official_reference':{
   'repository':'Mojang/bedrock-samples',
   'commit':'46ba6ea985fb5a92d79a9419198f10dda14c199d',
   'path':'documentation/Features.html',
   'git_blob':'dfb66d2371e818bea6bfffb1c1785d956a76b6d6',
   'contract':'acacia_trunk.trunk_lean includes lean_height and lean_steps'
  },
  'regression':{
   'a2759_fruiting_bridge_preserved':True,
   'a2748_pepper_lifecycle_preserved':True,
   'advanced_rack_preserved':True,
   'advancement_runtime_preserved':True,
   'cookery_hardening_preserved':True
  },
  'minecraft_tested':False,
  'bds_tested':False,
  'prior_server_shim_bds_tested':True
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,59]:
  raise RuntimeError('A2.7.60 must augment published A2.7.59')
 patch_feature();patch_versions();report()
 print('A2.7.60 Pepper Worldgen BDS Fix complete')

if __name__=='__main__':main()
