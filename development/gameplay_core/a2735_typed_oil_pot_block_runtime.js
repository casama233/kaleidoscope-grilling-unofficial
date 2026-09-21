import {world,system,ItemStack,EquipmentSlot,GameMode} from '@minecraft/server';
import {
 COOKERY_FILLED_ID,readCookeryOilPotForPlacement,buildCookeryOilPot
} from './a2734_cookery_oil_pot_adapter.js';
import {
 HOST_BLOCK_ID,HOST_FAT_ITEM_ID,OIL_BUCKET_POINTS,hostBlockCountKey,typedOilBlockKey,
 placementCandidateLocations,normalizePlacedOilCount,planPlacedTypedOilAddition,blocksNativeCookeryInteraction
} from './a2735_typed_oil_pot_block_core.js';

const BUCKET_TO_TYPE=Object.freeze({
 'kaleidoscope_grilling:canola_oil_bucket':'canola',
 'kaleidoscope_grilling:secret_chili_oil_bucket':'secret_chili',
 'kaleidoscope_grilling:premium_chili_oil_bucket':'premium_chili'
});

function blockLoc(block){return {x:block.x,y:block.y,z:block.z}}
function typeKeyAt(d,l){return typedOilBlockKey(d.id,l.x,l.y,l.z)}
function countKeyAt(d,l){return hostBlockCountKey(d.id,l.x,l.y,l.z)}
function readTypeAt(d,l){try{return String(world.getDynamicProperty(typeKeyAt(d,l))??'')}catch{return ''}}
function readCountAt(d,l,type=''){try{return normalizePlacedOilCount(type,world.getDynamicProperty(countKeyAt(d,l))??0)}catch{return 0}}
function clearAt(d,l){
 try{world.setDynamicProperty(typeKeyAt(d,l),undefined)}catch{}
 try{world.setDynamicProperty(countKeyAt(d,l),undefined)}catch{}
}
function writeAt(block,type,count){
 if(!block||block.typeId!==HOST_BLOCK_ID)return false;
 const d=block.dimension,l=blockLoc(block),next=normalizePlacedOilCount(type,count);
 try{
  world.setDynamicProperty(typeKeyAt(d,l),type||undefined);
  world.setDynamicProperty(countKeyAt(d,l),next);
 }catch{return false}
 try{block.setPermutation(block.permutation.withState('kaleidoscope_cookery:has_oil',next>0))}catch{}
 return true;
}
function inventory(p){return p.getComponent('minecraft:inventory')?.container}
function main(p){return inventory(p)?.getItem(p.selectedSlotIndex)}
function off(p){return p.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function findHand(p,id){if(main(p)?.typeId===id)return 'main';if(off(p)?.typeId===id)return 'off';return null}
function setHand(p,hand,stack){if(hand==='off')return p.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack);return inventory(p)?.setItem(p.selectedSlotIndex,stack)}
function creative(p){try{return p.getGameMode()===GameMode.Creative}catch{return false}}
function mismatch(p){try{p.onScreenDisplay.setActionBar('§c油壺內已有不同內容')}catch{}}
function playPour(p,type,count){try{p.playSound(type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',{volume:.9,pitch:.8+.5*Math.min(64,count)/64})}catch{}}

function scheduleTypedPlacement(e){
 if(e.isFirstEvent===false||e.block.typeId===HOST_BLOCK_ID)return;
 const item=e.itemStack;
 if(item?.typeId!==COOKERY_FILLED_ID)return;
 const state=readCookeryOilPotForPlacement(item);
 if(!state.type||state.count<=0)return;
 const d=e.block.dimension,candidates=placementCandidateLocations(e.block.location,e.blockFace).map(l=>({l,wasPot:d.getBlock(l)?.typeId===HOST_BLOCK_ID}));
 system.run(()=>{
  for(const c of candidates){
   if(c.wasPot)continue;
   const block=d.getBlock(c.l);
   if(block?.typeId===HOST_BLOCK_ID){writeAt(block,state.type,state.count);break}
  }
 });
}

function fillPlacedPot(player,dimension,location,bucketId,incomingType,hand){
 const block=dimension.getBlock(location);if(!block||block.typeId!==HOST_BLOCK_ID)return;
 const type=readTypeAt(dimension,location),count=readCountAt(dimension,location,type);
 const plan=planPlacedTypedOilAddition(type,count,incomingType,OIL_BUCKET_POINTS);
 if(!plan.ok){mismatch(player);return}
 if(!writeAt(block,plan.type,plan.nextCount))return;
 if(!creative(player)&&hand)setHand(player,hand,new ItemStack('minecraft:bucket',1));
 playPour(player,plan.type,plan.nextCount);
}

function manuallyBreakTypedPot(d,l,type,count,drop){
 const block=d.getBlock(l);if(!block||block.typeId!==HOST_BLOCK_ID)return false;
 const liveType=readTypeAt(d,l);if(liveType!==type)return false;
 clearAt(d,l);
 try{block.setType('minecraft:air')}catch{return false}
 if(drop){
  const stack=buildCookeryOilPot(type,count);
  if(stack)try{d.spawnItem(stack,{x:l.x+.5,y:l.y+.35,z:l.z+.5})}catch{}
 }
 return true;
}

world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 try{scheduleTypedPlacement(e)}catch{}
 if(e.block.typeId!==HOST_BLOCK_ID)return;
 const d=e.block.dimension,l=blockLoc(e.block),type=readTypeAt(d,l),itemId=e.itemStack?.typeId;
 const incoming=BUCKET_TO_TYPE[itemId];
 if(incoming){
  e.cancel=true;if(e.isFirstEvent===false)return;
  const p=e.player,hand=findHand(p,itemId);
  system.run(()=>fillPlacedPot(p,d,l,itemId,incoming,hand));
  return;
 }
 if(blocksNativeCookeryInteraction(type,itemId)){
  e.cancel=true;
  if(itemId===HOST_FAT_ITEM_ID&&e.isFirstEvent!==false){const p=e.player;system.run(()=>mismatch(p))}
 }
});

world.beforeEvents.playerBreakBlock.subscribe(e=>{
 if(e.block.typeId!==HOST_BLOCK_ID)return;
 const d=e.block.dimension,l=blockLoc(e.block),type=readTypeAt(d,l);if(!type)return;
 const count=readCountAt(d,l,type),drop=!creative(e.player);e.cancel=true;
 system.run(()=>manuallyBreakTypedPot(d,l,type,count,drop));
});

world.beforeEvents.explosion.subscribe(e=>{
 const impacted=e.getImpactedBlocks(),keep=[],typed=[];
 for(const block of impacted){
  if(block.typeId!==HOST_BLOCK_ID){keep.push(block);continue}
  const d=block.dimension,l=blockLoc(block),type=readTypeAt(d,l);
  if(!type){keep.push(block);continue}
  typed.push({d,l,type,count:readCountAt(d,l,type)});
 }
 if(!typed.length)return;
 e.setImpactedBlocks(keep);
 system.run(()=>{for(const row of typed)manuallyBreakTypedPot(row.d,row.l,row.type,row.count,true)});
});
