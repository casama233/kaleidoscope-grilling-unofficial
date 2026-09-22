from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,51]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.51 Pepper Forest Worldgen BP'),(rm,'Kaleidoscope Grilling A2.7.51 Pepper Forest Worldgen RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.51 Pepper Forest Worldgen'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_51_Pepper_Forest_Worldgen'
 write(P/'config.json',cfg)

def patch_worldgen():
 features=BP/'features';rules=BP/'feature_rules'
 features.mkdir(parents=True,exist_ok=True);rules.mkdir(parents=True,exist_ok=True)
 shutil.copy2(DEV/'a2751_pepper_tree_worldgen.feature.json',features/'pepper_tree_worldgen.json')
 shutil.copy2(DEV/'a2751_pepper_tree_worldgen_rule.feature_rule.json',rules/'pepper_tree_worldgen_rule.json')

def report():
 write(P/'reports/a2751-pepper-forest-worldgen.json',{
  'version':'A2.7.51',
  'scope':'data-driven Pepper Tree generation in forest biomes',
  'java':{
   'forest_tag':'#minecraft:is_forest',
   'rarity_denominator':16,
   'surface_water_depth':0,
   'heightmap':'OCEAN_FLOOR',
   'placement_step':'vegetal_decoration'
  },
  'bedrock':{
   'tree_feature':'kaleidoscope_grilling:pepper_tree_worldgen',
   'feature_rule':'kaleidoscope_grilling:pepper_tree_worldgen_rule',
   'biome_tag':'forest',
   'scatter_chance':{'numerator':1,'denominator':16},
   'placement_pass':'surface_pass',
   'script_runtime_added':False
  },
  'reuse':{
   'pepper_log':'A2.7.48',
   'pepper_leaves':'A2.7.48',
   'pepper_lifecycle_runtime':'A2.7.48',
   'duplicate_tree_blocks':False
  },
  'known_difference':{
   'java_initial_fruiting_chance':0.25,
   'bedrock_initial_fruiting_chance':0.0,
   'reason':'Bedrock random_spread_canopy cannot weight custom permutations of the same block state; existing A2.7.48 random-tick fruiting remains active'
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,50]:raise RuntimeError('A2.7.51 must augment published A2.7.50')
 patch_worldgen();patch_versions();report()
 print('A2.7.51 Pepper forest worldgen complete')

if __name__=='__main__':main()
