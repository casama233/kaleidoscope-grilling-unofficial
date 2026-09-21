from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,37]
CORE='a2737_offhand_oil_fill_core.js';RUNTIME='a2737_offhand_oil_fill_runtime.js'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.37 Offhand Oil Pot Fill BP'),(rm,'Kaleidoscope Grilling A2.7.37 Offhand Oil Pot Fill RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.37 Offhand Oil Pot Fill'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_37_Offhand_Oil_Pot_Fill'
 write(P/'config.json',cfg)

def patch_runtime():
 shutil.copy2(DEV/CORE,BP/'scripts'/CORE);shutil.copy2(DEV/RUNTIME,BP/'scripts'/RUNTIME)
 main=BP/'scripts/main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2736_typed_oil_pot_block_runtime.js';\n"
 add=anchor+"import './a2737_offhand_oil_fill_runtime.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.37 main import anchor drift')
 if "a2737_offhand_oil_fill_runtime.js" in s:raise RuntimeError('A2.7.37 runtime already active')
 main.write_text(s.replace(anchor,add,1),encoding='utf-8')

def report():
 write(P/'reports/a2737-offhand-oil-fill.json',{
  'version':'A2.7.37',
  'scope':'port Java OilFillingHandler RightClickItem: main-hand Grilling oil bucket + offhand Cookery oil pot',
  'java_1_1_1':{
   'event':'PlayerInteractEvent.RightClickItem','main_hand_only':True,'offhand_pot_required':True,
   'bucket_points':8,'typed_capacity':64,'native_fat_retyping_blocked':True,
   'different_oil_blocked':True,'survival_bucket_replaced_with_empty_bucket':True,
   'creative_bucket_preserved':True
  },
  'reuse':{
   'oil_registry':'a23_oil_world.js OIL_TYPES',
   'oil_pot_adapter':'a2734_cookery_oil_pot_adapter.js',
   'player_io':'a2735_player_io.js',
   'new_bucket_registry':False,'direct_host_dynamic_property_access':False
  },
  'after':{
   'air_item_use_path':True,'empty_pot_supported':True,'filled_pot_supported':True,
   'same_type_stacks_by_8':True,'native_fat_blocked':True,'different_type_blocked':True,
   'full_pot_blocked':True,'post_commit_verification_and_rollback':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,36]:raise RuntimeError('A2.7.37 must augment verified A2.7.36')
 patch_versions();patch_runtime();report();print('A2.7.37 offhand oil-pot item fill complete')
if __name__=='__main__':main()
