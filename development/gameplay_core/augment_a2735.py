from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,35]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')
def replace_once(s,old,new,label):
 if s.count(old)!=1:raise RuntimeError(f'A2.7.35 patch anchor drift ({label}): {s.count(old)}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.35 Shared Player IO BP'),
  (rm,'Kaleidoscope Grilling A2.7.35 Shared Player IO RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.35 Shared Player IO'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_35_Shared_Player_IO'
 write(P/'config.json',cfg)

def patch_main():
 path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
 s=replace_once(s,
  "import {world,system,ItemStack,EquipmentSlot,GameMode} from '@minecraft/server';",
  "import {world,system,ItemStack} from '@minecraft/server';",
  'main server import')
 anchor="import {COOKERY_FILLED_ID as COOKERY_FILLED,planCookeryOilPotConsumption} from './a2734_cookery_oil_pot_adapter.js';"
 addition="import {playerInventory as mainContainer,getMainHand as heldMain,setMainHand as setMain,getOffHand as heldOff,setOffHand as setOff,getHand as heldByHand,findHandEntry as handFor,setHand,isCreative as creative} from './a2735_player_io.js';"
 s=replace_once(s,anchor,anchor+'\n'+addition,'main player IO import')
 block="""function mainContainer(player){return player.getComponent('minecraft:inventory')?.container}
function heldMain(player){return mainContainer(player)?.getItem(player.selectedSlotIndex)}
function setMain(player,stack){mainContainer(player)?.setItem(player.selectedSlotIndex,stack)}
function heldOff(player){return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setOff(player,stack){return player.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}
function heldByHand(player,hand){return hand==='off'?heldOff(player):heldMain(player)}
function handFor(player,id){const m=heldMain(player);if(m?.typeId===id)return {name:'main',stack:m};const o=heldOff(player);if(o?.typeId===id)return {name:'off',stack:o};return null}
function setHand(player,hand,stack){if(hand==='off')return setOff(player,stack);return setMain(player,stack)}
function creative(player){try{return player.getGameMode()===GameMode.Creative}catch{return false}}
"""
 s=replace_once(s,block,'','main duplicated player IO')
 path.write_text(s,encoding='utf-8')

def patch_plate():
 path=BP/'scripts/a25_plate_recipe_runtime.js';s=path.read_text(encoding='utf-8')
 s=replace_once(s,
  "import {world,system,ItemStack,EquipmentSlot,GameMode} from '@minecraft/server';",
  "import {world,system,ItemStack} from '@minecraft/server';",
  'plate server import')
 anchor="} from './a25_plate_recipe_core.js';"
 addition="import {playerInventory as mainContainer,getMainHand as heldMain,setMainHand as setMain,getOffHand as heldOff,setOffHand as setOff,isCreative as creative} from './a2735_player_io.js';"
 s=replace_once(s,anchor,anchor+'\n'+addition,'plate player IO import')
 block="""function mainContainer(player){return player.getComponent('minecraft:inventory')?.container}
function heldMain(player){return mainContainer(player)?.getItem(player.selectedSlotIndex)}
function setMain(player,stack){mainContainer(player)?.setItem(player.selectedSlotIndex,stack)}
function heldOff(player){return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setOff(player,stack){return player.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}
function creative(player){try{return player.getGameMode()===GameMode.Creative}catch{return false}}
"""
 s=replace_once(s,block,'','plate duplicated player IO')
 path.write_text(s,encoding='utf-8')

def patch_oil_machine():
 path=BP/'scripts/a26_oil_machine_runtime.js';s=path.read_text(encoding='utf-8')
 s=replace_once(s,
  "import {world,system,ItemStack,EquipmentSlot,GameMode} from '@minecraft/server';",
  "import {world,system,ItemStack} from '@minecraft/server';",
  'oil machine server import')
 anchor="import {COOKERY_EMPTY_ID as COOKERY_EMPTY,COOKERY_FILLED_ID as COOKERY_FILLED,readCookeryOilPot,buildCookeryOilPot} from './a2734_cookery_oil_pot_adapter.js';"
 addition="import {playerInventory as playerContainer,getMainHand as main,getOffHand as off,setMainHand as setMain,setOffHand as setOff,findHand as handFor,getHand as held,setHand,isCreative as creative} from './a2735_player_io.js';"
 s=replace_once(s,anchor,anchor+'\n'+addition,'oil machine player IO import')
 block="""function playerContainer(p){return p.getComponent('minecraft:inventory')?.container}
function main(p){return playerContainer(p)?.getItem(p.selectedSlotIndex)}
function off(p){return p.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setMain(p,s){playerContainer(p)?.setItem(p.selectedSlotIndex,s)}
function setOff(p,s){p.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,s)}
function handFor(p,id){if(main(p)?.typeId===id)return 'main';if(off(p)?.typeId===id)return 'off';return null}
function held(p,hand){return hand==='off'?off(p):main(p)}
function setHand(p,hand,s){return hand==='off'?setOff(p,s):setMain(p,s)}
function creative(p){try{return p.getGameMode()===GameMode.Creative}catch{return false}}
"""
 s=replace_once(s,block,'','oil machine duplicated player IO')
 path.write_text(s,encoding='utf-8')

def patch_cold():
 path=BP/'scripts/a2722_cold_houttuynia_runtime.js';s=path.read_text(encoding='utf-8')
 s=replace_once(s,
  "import {world,system,ItemStack,EquipmentSlot} from '@minecraft/server';",
  "import {world,system,ItemStack} from '@minecraft/server';",
  'cold server import')
 anchor="} from './a2734_cookery_oil_pot_adapter.js';"
 addition="import {playerInventory as inventory,getMainHand as main,getOffHand as off,setMainHand as setMain,setOffHand as setOff} from './a2735_player_io.js';"
 s=replace_once(s,anchor,anchor+'\n'+addition,'cold player IO import')
 block="""function inventory(player){return player.getComponent('minecraft:inventory')?.container}
function main(player){return inventory(player)?.getItem(player.selectedSlotIndex)}
function off(player){return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setMain(player,stack){inventory(player)?.setItem(player.selectedSlotIndex,stack)}
function setOff(player,stack){player.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}
"""
 s=replace_once(s,block,'','cold duplicated player IO')
 path.write_text(s,encoding='utf-8')

def patch_oil_world():
 path=BP/'scripts/a23_oil_world.js';s=path.read_text(encoding='utf-8')
 s=replace_once(s,
  "import {world,system,ItemStack,EquipmentSlot,GameMode,BlockPermutation} from '@minecraft/server';",
  "import {world,system,ItemStack,BlockPermutation} from '@minecraft/server';",
  'oil world server import')
 anchor="import {COOKERY_EMPTY_ID as COOKERY_EMPTY,COOKERY_FILLED_ID as COOKERY_FILLED,planCookeryTypedOilAddition} from './a2734_cookery_oil_pot_adapter.js';"
 addition="import {playerInventory as playerContainer,getMainHand as main,getOffHand as off,findHand,setHand,isCreative as creative} from './a2735_player_io.js';"
 s=replace_once(s,anchor,anchor+'\n'+addition,'oil world player IO import')
 block="""function playerContainer(p){return p.getComponent('minecraft:inventory')?.container}
function main(p){return playerContainer(p)?.getItem(p.selectedSlotIndex)}
function off(p){return p.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function findHand(p,id){const m=main(p);if(m?.typeId===id)return 'main';const o=off(p);if(o?.typeId===id)return 'off';return null}
function setHand(p,hand,stack){if(hand==='off')return p.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack);return playerContainer(p)?.setItem(p.selectedSlotIndex,stack)}
function creative(p){try{return p.getGameMode()===GameMode.Creative}catch{return false}}
"""
 s=replace_once(s,block,'','oil world duplicated player IO')
 path.write_text(s,encoding='utf-8')

def report():
 write(P/'reports/a2735-player-io.json',{
  'version':'A2.7.35',
  'scope':'centralize identical selected-main/offhand/creative player IO helpers without changing transaction semantics',
  'migrated_consumers':['main.js','a25_plate_recipe_runtime.js','a26_oil_machine_runtime.js','a2722_cold_houttuynia_runtime.js','a23_oil_world.js'],
  'shared_functions':['playerInventory','getMainHand','setMainHand','getOffHand','setOffHand','getHand','setHand','findHand','findHandEntry','isCreative'],
  'before':{
   'duplicated_player_io_helper_sets':5,
   'modules_importing_EquipmentSlot_or_GameMode_only_for_basic_hand_io':5
  },
  'after':{
   'shared_player_io_modules':1,
   'migrated_consumer_local_basic_hand_io_helpers':0
  },
  'intentionally_not_migrated':{
   'a279_beef_board_runtime.js':'uses EquipmentSlot.Mainhand slot object for transactional verification',
   'a2731_farmland_crop_host_runtime.js':'bone-meal mutation needs writable equipment slot objects'
  },
  'not_generalized':['give/merge semantics','transaction rollback','durability mutation','writable equipment slots'],
  'remaining_infrastructure_duplicates':['face/offset and coordinate-key helpers','position-key/dynamic-property helpers','per-slice manifest/version/package CI boilerplate'],
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,34]:
  raise RuntimeError('A2.7.35 must augment verified A2.7.34')
 patch_versions()
 shutil.copy2(DEV/'a2735_player_io.js',BP/'scripts/a2735_player_io.js')
 patch_main();patch_plate();patch_oil_machine();patch_cold();patch_oil_world();report()
 print('A2.7.35 shared player IO refactor complete')

if __name__=='__main__':
 main()
