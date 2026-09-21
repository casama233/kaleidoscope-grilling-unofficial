import {world,system,ItemStack} from '@minecraft/server';
import {OIL_TYPES} from './a23_oil_world.js';
import {GRILLING_FLUID_CAPACITY,oilTypeForBucketId} from './a2738_oil_contract_core.js';
import {
 COOKERY_FILLED_ID,readCookeryOilPotForPlacement,buildCookeryOilPot
} from './a2734_cookery_oil_pot_adapter.js';
import {findHand,setHand,isCreative as creative} from './a2735_player_io.js';
import {
 HOST_BLOCK_ID,HOST_FAT_ITEM_ID,OIL_BUCKET_POINTS,
 placementCandidateLocations,planPlacedTypedOilAddition,blocksNativeCookeryInteraction
} from './a2736_typed_oil_pot_block_core.js';
import {
 placedOilPotLocation,readPlacedOilPotState,writePlacedOilPotState,clearPlacedOilPotState
} from './a2739_cookery_oil_pot_block_adapter.js';

function mismatch(p){try{p.onScreenDisplay.setActionBar('§c油壺內已有不同內容')}catch{}}
function playPour(p,type,count){try{p.playSound(type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',{volume:.9,pitch:.8+.5*Math.min(GRILLING_FLUID_CAPACITY,count)/GRILLING_FLUID_CAPACITY})}catch{}}

function scheduleTypedPlacement(e){
 if(e.isFirstEvent===false||e.block.typeId===HOST_BLOCK_ID)return;
 const item=e.itemStack;
 if(item?.typeId!==COOKERY_FILLED_ID)return;
 const state=readCookeryOilPotForPlacement(item);
 if(!state.type||state.count<=0)return;
 const d=e.block.dimension;
 const candidates=placementCandidateLocations(e.block.location,e.blockFace).map(l=>({l,wasPot:d.getBlock(l)?.typeId===HOST_BLOCK_ID}));
 system.run(()=>{
  for(const c of candidates){
   if(c.wasPot)continue;
   const block=d.getBlock(c.l);
   if(block?.typeId===HOST_BLOCK_ID){writePlacedOilPotState(block,state.type,state.count);break}
  }
 });
}

function fillPlacedPot(player,dimension,location,incomingType,hand){
 const block=dimension.getBlock(location);if(!block||block.typeId!==HOST_BLOCK_ID)return;
 const state=readPlacedOilPotState(block);if(!state)return;
 const plan=planPlacedTypedOilAddition(state.type,state.count,incomingType,OIL_BUCKET_POINTS);
 if(!plan.ok){mismatch(player);return}
 if(!writePlacedOilPotState(block,plan.type,plan.nextCount))return;
 if(!creative(player)&&hand)setHand(player,hand,new ItemStack('minecraft:bucket',1));
 playPour(player,plan.type,plan.nextCount);
}

function manuallyBreakTypedPot(d,l,type,count,drop){
 const block=d.getBlock(l);if(!block||block.typeId!==HOST_BLOCK_ID)return false;
 const state=readPlacedOilPotState(block);if(state?.type!==type)return false;
 clearPlacedOilPotState(block);
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
 const d=e.block.dimension,l=placedOilPotLocation(e.block),state=readPlacedOilPotState(e.block),type=state?.type??'',itemId=e.itemStack?.typeId;
 const incoming=oilTypeForBucketId(itemId,OIL_TYPES);
 if(incoming){
  e.cancel=true;if(e.isFirstEvent===false)return;
  const p=e.player,hand=findHand(p,itemId);
  system.run(()=>fillPlacedPot(p,d,l,incoming,hand));
  return;
 }
 if(blocksNativeCookeryInteraction(type,itemId)){
  e.cancel=true;
  if(itemId===HOST_FAT_ITEM_ID&&e.isFirstEvent!==false){const p=e.player;system.run(()=>mismatch(p))}
 }
});

world.beforeEvents.playerBreakBlock.subscribe(e=>{
 if(e.block.typeId!==HOST_BLOCK_ID)return;
 const state=readPlacedOilPotState(e.block);if(!state?.type)return;
 const d=e.block.dimension,l=placedOilPotLocation(e.block),drop=!creative(e.player);e.cancel=true;
 system.run(()=>manuallyBreakTypedPot(d,l,state.type,state.count,drop));
});

world.beforeEvents.explosion.subscribe(e=>{
 const impacted=e.getImpactedBlocks(),keep=[],typed=[];
 for(const block of impacted){
  if(block.typeId!==HOST_BLOCK_ID){keep.push(block);continue}
  const state=readPlacedOilPotState(block);
  if(!state?.type){keep.push(block);continue}
  typed.push({d:block.dimension,l:placedOilPotLocation(block),type:state.type,count:state.count});
 }
 if(!typed.length)return;
 e.setImpactedBlocks(keep);
 system.run(()=>{for(const row of typed)manuallyBreakTypedPot(row.d,row.l,row.type,row.count,true)});
});
