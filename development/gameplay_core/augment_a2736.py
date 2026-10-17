from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,36]
CORE='a2736_typed_oil_pot_block_core.js';RUNTIME='a2736_typed_oil_pot_block_runtime.js'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.36 Typed Cookery Oil Pot Block BP'),(rm,'Kaleidoscope Grilling A2.7.36 Typed Cookery Oil Pot Block RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.36 Typed Cookery Oil Pot Block'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_36_Typed_Cookery_Oil_Pot_Block'
 write(P/'config.json',cfg)

def patch_runtime():
 shutil.copy2(DEV/CORE,BP/'scripts'/CORE);shutil.copy2(DEV/RUNTIME,BP/'scripts'/RUNTIME)
 main=BP/'scripts/main.js';s=main.read_text(encoding='utf-8')
 anchor="import {playerInventory as mainContainer,getMainHand as heldMain,setMainHand as setMain,getOffHand as heldOff,setOffHand as setOff,getHand as heldByHand,findHandEntry as handFor,setHand,isCreative as creative} from './a2735_player_io.js';\n"
 add=anchor+"import './a2736_typed_oil_pot_block_runtime.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.36 main import anchor drift')
 if "a2736_typed_oil_pot_block_runtime.js" in s:raise RuntimeError('A2.7.36 runtime already active')
 main.write_text(s.replace(anchor,add,1),encoding='utf-8')

def report():
 write(P/'reports/a2736-typed-oil-pot-block.json',{
  'version':'A2.7.36','scope':'reuse Cookery oil-pot block while preserving Java Grilling typed-oil block lifecycle semantics',
  'java_1_1_1':{
   'placement_copies_oil_type':True,'block_entity_persists_oil_type':True,'typed_capacity':64,
   'typed_pot_blocks_empty_hand_extraction':True,'typed_pot_blocks_cookery_fat_insertion':True,
   'drops_copy_oil_type':True,'typed_bucket_points':8
  },
  'bedrock_host_1_0_6':{
   'block_id':'kaleidoscope_cookery:oil_pot','block_count_prefix':'kc_oilpot:',
   'host_capacity':256,'host_item_count_key':'kc_oil_count','host_has_oil_state':'kaleidoscope_cookery:has_oil',
   'player_break_drop_event':'afterEvents.playerBreakBlock','explosion_drop_event':'afterEvents.blockExplode'
  },
  'reuse':{'a2734_oil_adapter':True,'a2735_shared_player_io':True,'new_grilling_oil_pot_block':False},
  'after':{
   'uses_host_block':True,'placement_type_bridge':True,'typed_capacity_clamped_to_64':True,
   'native_fat_and_empty_hand_blocked_when_typed':True,'placed_bucket_fill':True,
   'player_break_preserves_type':True,'explosion_preserves_type':True,'host_duplicate_drop_avoided':True
  },
  'known_visual_gap':'Cookery Bedrock block schema has no Grilling oil-type visual state; semantic lifecycle is ported but placed oil color/model parity remains separate',
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,35]:raise RuntimeError('A2.7.36 must augment verified A2.7.35')
 patch_versions();patch_runtime();report();print('A2.7.36 typed Cookery oil-pot block bridge complete')
if __name__=='__main__':main()
