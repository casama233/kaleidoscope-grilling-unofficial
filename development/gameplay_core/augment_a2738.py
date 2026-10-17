from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,38]
SHARED='a2738_oil_contract_core.js'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def replace_once(s,old,new,label):
 if s.count(old)!=1:raise RuntimeError(f'{label} drift: expected one match, got {s.count(old)}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.38 Shared Oil Contract BP'),(rm,'Kaleidoscope Grilling A2.7.38 Shared Oil Contract RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.38 Shared Oil Contract'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_38_Shared_Oil_Contract'
 write(P/'config.json',cfg)

def patch_a24():
 p=BP/'scripts/a24_skewering_core.js';s=p.read_text(encoding='utf-8')
 imp="import {HOST_FAT_CAPACITY as FAT_CAPACITY,GRILLING_FLUID_CAPACITY as FLUID_CAPACITY,GRILLING_OIL_BUCKET_POINTS as OIL_BUCKET_POINTS} from './a2738_oil_contract_core.js';\n"
 if imp not in s:s=imp+s
 s=replace_once(s,
  "export const FAT_CAPACITY=256;\nexport const FLUID_CAPACITY=64;\nexport const OIL_BUCKET_POINTS=8;\n",
  "export {FAT_CAPACITY,FLUID_CAPACITY,OIL_BUCKET_POINTS};\n",
  'a24 constants')
 p.write_text(s,encoding='utf-8')

def patch_a2734():
 p=BP/'scripts/a2734_cookery_oil_pot_core.js';s=p.read_text(encoding='utf-8')
 marker='export function normalizeOilCount'
 if s.count(marker)!=1:raise RuntimeError('a2734 normalize marker drift')
 rest=s[s.index(marker):]
 prefix="""import {
 HOST_FAT_CAPACITY,GRILLING_FLUID_CAPACITY,GRILLING_OIL_BUCKET_POINTS,
 GRILLING_OIL_TYPES,normalizeOilType,oilCapacity,oilTypeForBucketId
} from './a2738_oil_contract_core.js';

export {
 HOST_FAT_CAPACITY,GRILLING_FLUID_CAPACITY,GRILLING_OIL_BUCKET_POINTS,
 GRILLING_OIL_TYPES,normalizeOilType,oilCapacity,oilTypeForBucketId
};

export const COOKERY_EMPTY_ID='kaleidoscope_cookery:oil_pot';
export const COOKERY_FILLED_ID='kaleidoscope_cookery:oil_pot_filled';
export const HOST_COUNT_KEY='kc_oil_count';
export const GRILLING_TYPE_KEY='kaleidoscope_grilling:oil_type';

"""
 p.write_text(prefix+rest,encoding='utf-8')

def patch_a2736_core():
 p=BP/'scripts/a2736_typed_oil_pot_block_core.js';s=p.read_text(encoding='utf-8')
 s=replace_once(s,
  " HOST_FAT_CAPACITY,GRILLING_FLUID_CAPACITY,normalizeOilType,planTypedOilAddition\n",
  " HOST_FAT_CAPACITY,GRILLING_FLUID_CAPACITY,GRILLING_OIL_BUCKET_POINTS,normalizeOilType,planTypedOilAddition\n",
  'a2736 shared import')
 s=replace_once(s,"export const OIL_BUCKET_POINTS=8;","export const OIL_BUCKET_POINTS=GRILLING_OIL_BUCKET_POINTS;",'a2736 bucket points')
 p.write_text(s,encoding='utf-8')

def patch_a2736_runtime():
 p=BP/'scripts/a2736_typed_oil_pot_block_runtime.js';s=p.read_text(encoding='utf-8')
 s=replace_once(s,
  "import {world,system,ItemStack} from '@minecraft/server';\n",
  "import {world,system,ItemStack} from '@minecraft/server';\nimport {OIL_TYPES} from './a23_oil_world.js';\nimport {GRILLING_FLUID_CAPACITY,oilTypeForBucketId} from './a2738_oil_contract_core.js';\n",
  'a2736 runtime imports')
 mapping="""const BUCKET_TO_TYPE=Object.freeze({
 'kaleidoscope_grilling:canola_oil_bucket':'canola',
 'kaleidoscope_grilling:secret_chili_oil_bucket':'secret_chili',
 'kaleidoscope_grilling:premium_chili_oil_bucket':'premium_chili'
});

"""
 s=replace_once(s,mapping,'','a2736 duplicate bucket registry')
 s=replace_once(s,
  "function playPour(p,type,count){try{p.playSound(type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',{volume:.9,pitch:.8+.5*Math.min(64,count)/64})}catch{}}",
  "function playPour(p,type,count){try{p.playSound(type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',{volume:.9,pitch:.8+.5*Math.min(GRILLING_FLUID_CAPACITY,count)/GRILLING_FLUID_CAPACITY})}catch{}}",
  'a2736 pitch capacity')
 s=replace_once(s,
  " const incoming=BUCKET_TO_TYPE[itemId];",
  " const incoming=oilTypeForBucketId(itemId,OIL_TYPES);",
  'a2736 bucket lookup')
 p.write_text(s,encoding='utf-8')

def patch_a2737_core():
 p=BP/'scripts/a2737_offhand_oil_fill_core.js';s=p.read_text(encoding='utf-8')
 marker='export function isCookeryOilPotItemId'
 if s.count(marker)!=1:raise RuntimeError('a2737 core marker drift')
 rest=s[s.index(marker):]
 prefix="""import {
 COOKERY_EMPTY_ID,COOKERY_FILLED_ID,planTypedOilAddition
} from './a2734_cookery_oil_pot_core.js';
import {GRILLING_OIL_BUCKET_POINTS,oilTypeForBucketId} from './a2738_oil_contract_core.js';

export const ITEM_FILL_POINTS=GRILLING_OIL_BUCKET_POINTS;
export {oilTypeForBucketId};

"""
 p.write_text(prefix+rest,encoding='utf-8')

def patch_a2737_runtime():
 p=BP/'scripts/a2737_offhand_oil_fill_runtime.js';s=p.read_text(encoding='utf-8')
 s=replace_once(s,
  "try{player.playSound(type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',{volume:.9,pitch:.8+.5*plan.nextCount/64})}catch{}",
  "try{player.playSound(type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',{volume:.9,pitch:.8+.5*plan.nextCount/plan.capacity})}catch{}",
  'a2737 pitch capacity')
 s=replace_once(s,
  "message(player,'§a已向油壺加入 '+ITEM_FILL_POINTS+' 點油（'+plan.nextCount+'/64）');",
  "message(player,'§a已向油壺加入 '+ITEM_FILL_POINTS+' 點油（'+plan.nextCount+'/'+plan.capacity+'）');",
  'a2737 status capacity')
 p.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2738-shared-oil-contract.json',{
  'version':'A2.7.38',
  'scope':'remove duplicate typed-oil constants and bucket registries while auditing Java display parity',
  'shared_contract':{
   'host_fat_capacity':256,'typed_fluid_capacity':64,'bucket_points':8,
   'typed_oils':['canola','secret_chili','premium_chili'],
   'consumers':['a24_skewering_core','a2734_cookery_oil_pot_core','a2736_typed_oil_pot_block','a2737_offhand_oil_fill']
  },
  'reuse':{
   'a23_oil_world_registry_reused_by_a2736':True,
   'a2736_private_bucket_registry_removed':True,
   'a2734_duplicate_capacity_and_type_contract_removed':True,
   'a2736_duplicate_bucket_points_removed':True,
   'a2737_duplicate_bucket_points_and_lookup_removed':True
  },
  'java_display_audit':{
   'item_model_uses_java_item_property':True,
   'placed_block_uses_injected_oil_type_state':True,
   'crosshair_hud_exists':True,
   'bedrock_can_append_state_to_foreign_block':False,
   'duplicate_host_block_created':False,
   'visual_state_deferred_to_shared_host_visual_adapter':True,
   'hud_deferred_to_shared_hud_adapter':True
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,37]:raise RuntimeError('A2.7.38 must augment published A2.7.37')
 shutil.copy2(DEV/SHARED,BP/'scripts'/SHARED)
 patch_a24();patch_a2734();patch_a2736_core();patch_a2736_runtime();patch_a2737_core();patch_a2737_runtime()
 patch_versions();report();print('A2.7.38 shared oil contract complete')

if __name__=='__main__':main()
