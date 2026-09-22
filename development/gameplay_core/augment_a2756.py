from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,56]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_adapter():
 src=DEV/'a2756_refactored_a2750_food_state_adapter.js'
 dst=BP/'scripts/a2750_food_state_adapter.js'
 shutil.copy2(src,dst)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.56 P0 Official API Hardening BP'),
  (rm,'Kaleidoscope Grilling A2.7.56 P0 Official API Hardening RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.56 P0 Official API Hardening'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_56_P0_Official_API_Hardening'
 write(P/'config.json',cfg)

def report():
 write(P/'reports/a2756-p0-official-api-hardening.json',{
  'version':'A2.7.56',
  'scope':'P0 Cookery cuisine metadata hardening against official Bedrock stable Script API behavior',
  'bug':{
   'previous_order':['seasoning_dynamic_property','hot_lore_and_dynamic_property'],
   'fixed_order':['hot_lore_and_dynamic_property','seasoning_dynamic_property'],
   'impact':'seasoning metadata on stackable Cookery servings could be rejected before HotFood lore customized the ItemStack'
  },
  'official_samples_commit':'73a171fc8393a1052b4ca0669dc82231f775d8b1',
  'official_references':[
   {
    'source':'Microsoft Learn - ItemStack',
    'url':'https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable',
    'contract':'ItemStack.setDynamicProperty only works with non-stackable items'
   },
   {
    'source':'Microsoft Learn - ContainerSlot',
    'url':'https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/containerslot?view=minecraft-bedrock-stable',
    'contract':'isStackable is false when an item contains custom data or properties'
   },
   {
    'source':'Microsoft Learn - Working With Events',
    'url':'https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/events?view=minecraft-bedrock-stable',
    'contract':'WorldBeforeEvents listeners must not directly modify gameplay state'
   },
   {
    'source':'Microsoft minecraft-scripting-samples - Containers',
    'url':'https://github.com/microsoft/minecraft-scripting-samples/blob/73a171fc8393a1052b4ca0669dc82231f775d8b1/howto-gallery/scripts/Containers.ts',
    'contract':'Container.setItem is the canonical exact-slot replacement path'
   },
   {
    'source':'Microsoft minecraft-scripting-samples - DynamicProperties',
    'url':'https://github.com/microsoft/minecraft-scripting-samples/blob/73a171fc8393a1052b4ca0669dc82231f775d8b1/howto-gallery/scripts/DynamicProperties.ts',
    'contract':'world dynamic properties can persist JSON strings for structured state'
   }
  ],
  'architecture_audit':{
   'before_event_mutation_deferred_with_system_run':True,
   'world_json_dynamic_property_pattern_matches_official_sample':True,
   'exact_slot_rewrite_uses_container_api':True,
   'cookery_public_extension_api_preserved':True,
   'cookery_private_kc_station_access':False,
   'duplicate_wok_or_stockpot':False
  },
  'p0_regression_guard':{
   'wok_foods':3,'stockpot_foods':3,
   'special_seasoning':True,'typed_oil':True,'hot_food':True,
   'shared_cuisine_eat_path':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,55]:
  raise RuntimeError('A2.7.56 must augment published A2.7.55')
 patch_adapter();patch_versions();report()
 print('A2.7.56 P0 Official API Hardening complete')

if __name__=='__main__':main()
