import {world,system,ItemStack,EquipmentSlot} from '@minecraft/server';
import {OIL_TYPES} from './a23_oil_world.js';
import {GRILLING_FLUID_CAPACITY,oilTypeForBucketId} from './a2738_oil_contract_core.js';
import {COOKERY_FILLED_ID,readCookeryOilPotForPlacement,readCookeryOilPot,buildCookeryOilPot} from './a2734_cookery_oil_pot_adapter.js';
import {getHand,playerInventory,isCreative as creative} from './a2735_player_io.js';
import {captureInteractionIntent,interactionIntentStillCurrent} from './a2762_interaction_intent_adapter.js';
import {stackIntentSignature} from './a2762_interaction_intent_core.js';
import {HOST_BLOCK_ID,HOST_FAT_ITEM_ID,OIL_BUCKET_POINTS,placementCandidateLocations,
 planPlacedTypedOilAddition,blocksNativeCookeryInteraction} from './a2736_typed_oil_pot_block_core.js';
import {placedOilPotLocation,readPlacedOilPotState,writePlacedOilPotState,clearPlacedOilPotState,
 capturePlacedOilPotSnapshot,placedOilPotSnapshotMatches,restorePlacedOilPotSnapshot} from './a2739_cookery_oil_pot_block_adapter.js';

function mismatch(p){try{p.onScreenDisplay.setActionBar('§c油壺內已有不同內容或容量不足')}catch{}}
function failed(p){try{p?.onScreenDisplay.setActionBar('§7油壺操作已取消：物品、容器或資料已改變')}catch{}}
function warn(text){console.warn('[Grilling A2.7.69] '+text)}
function playPour(p,type,count){try{p.playSound(type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',{volume:.9,pitch:.8+.5*Math.min(GRILLING_FLUID_CAPACITY,count)/GRILLING_FLUID_CAPACITY})}catch{}}
function livePot(d,l){try{const b=d.getBlock(l);return b?.typeId===HOST_BLOCK_ID?b:undefined}catch{return undefined}}
function sameDimension(p,d){try{return p.dimension.id===d.id}catch{return false}}
function writeHand(p,intent,stack){
 try{
  if(intent.hand==='off'){
   const eq=p.getComponent('minecraft:equippable');
   if(!eq||!eq.setEquipment(EquipmentSlot.Offhand,stack))return false;
  }else{
   if(p.selectedSlotIndex!==intent.selectedSlot)return false;
   const c=playerInventory(p);if(!c)return false;c.setItem(intent.selectedSlot,stack);
  }
  return stackIntentSignature(getHand(p,intent.hand))===stackIntentSignature(stack);
 }catch{return false}
}
function scheduleTypedPlacement(e){
 if(e.isFirstEvent===false||e.block.typeId===HOST_BLOCK_ID)return;
 const item=e.itemStack;if(item?.typeId!==COOKERY_FILLED_ID)return;
 const state=readCookeryOilPotForPlacement(item);
 if(!state.valid||!state.type||state.count<=0)return;
 const d=e.block.dimension;
 const candidates=placementCandidateLocations(e.block.location,e.blockFace).map(l=>({l,wasPot:!!livePot(d,l)}));
 system.run(()=>{
  for(const c of candidates){
   if(c.wasPot)continue;
   const block=livePot(d,c.l);
   if(block){if(!writePlacedOilPotState(block,state.type,state.count))warn('Typed placement state write failed');break}
  }
 });
}
function fillPlacedPot(player,d,l,incomingType,intent,snapshot){
 const block=livePot(d,l);
 if(!block||!sameDimension(player,d)||!interactionIntentStillCurrent(player,intent)||
  !placedOilPotSnapshotMatches(block,snapshot)){failed(player);return}
 const held=getHand(player,intent.hand),state=readPlacedOilPotState(block);
 if(!state||held?.amount!==1||oilTypeForBucketId(held.typeId,OIL_TYPES)!==incomingType){failed(player);return}
 const plan=planPlacedTypedOilAddition(state.type,state.count,incomingType,OIL_BUCKET_POINTS);
 if(!plan.ok){mismatch(player);return}
 const consume=!creative(player);
 let before,remainder;
 try{before=held.clone();if(consume)remainder=new ItemStack('minecraft:bucket',1)}catch{failed(player);return}
 if(!writePlacedOilPotState(block,plan.type,plan.nextCount)){failed(player);return}
 if(consume&&!writeHand(player,intent,remainder)){
  const handRestored=writeHand(player,intent,before);
  const potRestored=restorePlacedOilPotSnapshot(block,snapshot);
  if(!handRestored||!potRestored)warn('Bucket-fill rollback incomplete');
  failed(player);return;
 }
 playPour(player,plan.type,plan.nextCount);
}
function manuallyBreakTypedPot(d,l,snapshot,drop){
 const block=livePot(d,l);
 if(!block||!placedOilPotSnapshotMatches(block,snapshot))return false;
 const state=readPlacedOilPotState(block);if(!state?.type)return false;
 let output;
 if(drop){
  output=buildCookeryOilPot(state.type,state.count);
  if(!output)return false;
  const check=readCookeryOilPot(output);
  if(state.count>0&&(!check.valid||check.type!==state.type||check.count!==state.count))return false;
 }
 // Prepare the drop before deleting either the container or its saved data.
 if(!clearPlacedOilPotState(block))return false;
 try{
  block.setType('minecraft:air');
  if(drop&&!d.spawnItem(output,{x:l.x+.5,y:l.y+.35,z:l.z+.5}))throw new Error('drop not created');
  return true;
 }catch{
  restorePlacedOilPotSnapshot(block,snapshot);return false;
 }
}
world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 try{scheduleTypedPlacement(e)}catch(error){warn('Typed placement: '+error)}
 if(e.block.typeId!==HOST_BLOCK_ID)return;
 const d=e.block.dimension,l=placedOilPotLocation(e.block),state=readPlacedOilPotState(e.block);
 if(!state){e.cancel=true;return}
 const itemId=e.itemStack?.typeId,incoming=oilTypeForBucketId(itemId,OIL_TYPES);
 if(incoming){
  e.cancel=true;if(e.isFirstEvent===false)return;
  try{
   const p=e.player,intent=captureInteractionIntent(p,e.itemStack),snapshot=capturePlacedOilPotSnapshot(e.block);
   if(!intent||!snapshot)return;
   system.run(()=>fillPlacedPot(p,d,l,incoming,intent,snapshot));
  }catch(error){warn('Typed fill: '+error)}
  return;
 }
 if(blocksNativeCookeryInteraction(state.type,itemId)){
  e.cancel=true;
  if(itemId===HOST_FAT_ITEM_ID&&e.isFirstEvent!==false){const p=e.player;system.run(()=>mismatch(p))}
 }
});
world.beforeEvents.playerBreakBlock.subscribe(e=>{
 if(e.block.typeId!==HOST_BLOCK_ID)return;
 const state=readPlacedOilPotState(e.block);
 if(!state){e.cancel=true;return}
 if(!state.type)return;
 const d=e.block.dimension,l=placedOilPotLocation(e.block),snapshot=capturePlacedOilPotSnapshot(e.block);
 const p=e.player,drop=!creative(p);e.cancel=true;
 system.run(()=>{if(!manuallyBreakTypedPot(d,l,snapshot,drop))failed(p)});
});
world.beforeEvents.explosion.subscribe(e=>{
 const impacted=e.getImpactedBlocks(),keep=[],typed=[];
 for(const block of impacted){
  if(block.typeId!==HOST_BLOCK_ID){keep.push(block);continue}
  const state=readPlacedOilPotState(block);
  if(!state)continue; // unreadable is not an empty container
  if(!state.type){keep.push(block);continue}
  const snapshot=capturePlacedOilPotSnapshot(block);
  if(snapshot)typed.push({d:block.dimension,l:placedOilPotLocation(block),snapshot});
 }
 if(keep.length!==impacted.length)e.setImpactedBlocks(keep);
 if(typed.length)system.run(()=>{
  for(const row of typed)if(!manuallyBreakTypedPot(row.d,row.l,row.snapshot,true))warn('Explosion kept a changed or unwritable typed pot');
 });
});
