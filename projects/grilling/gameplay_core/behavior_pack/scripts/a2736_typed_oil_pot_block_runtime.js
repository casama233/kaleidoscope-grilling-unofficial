import {world,system} from '@minecraft/server';
import {interactionFeedback} from './a283_interaction_feedback.js';
import {HOST_BLOCK_ID,typedOilBlockKey} from './a2736_typed_oil_pot_block_core.js';
import {COOKERY_FILLED_ID,GRILLING_TYPE_KEY} from './a2734_cookery_oil_pot_core.js';

const notices=new Map();
function notify(player){
 if(!player)return;
 const last=notices.get(player.id)??-1000;
 if(system.currentTick-last<60)return;
 notices.set(player.id,system.currentTick);
 system.run(()=>{try{interactionFeedback(player,'§c此特殊油壺暫停跨模組操作；資料與物品保留，請勿拆除。 / Typed oil-pot bridge unavailable; contents preserved.')}catch{}});
}
world.afterEvents.playerLeave.subscribe(e=>notices.delete(e.playerId));
function legacyTypedPot(block){
 if(block?.typeId!==HOST_BLOCK_ID)return false;
 try{
  const p=block.location;
  // This marker belongs to Grilling. It is NOT Cookery's oil quantity.
  const marker=world.getDynamicProperty(typedOilBlockKey(block.dimension.id,p.x,p.y,p.z));
  return marker!==undefined&&marker!==null&&marker!=='';
 }catch{return true;} // unreadable existing state is not an empty container
}
function typedHand(stack){
 if(stack?.typeId!==COOKERY_FILLED_ID)return false;
 try{const type=stack.getDynamicProperty(GRILLING_TYPE_KEY);return type!==undefined&&type!==null&&type!=='';}
 catch{return true;}
}
function typedBucket(stack){return [
 'kaleidoscope_grilling:canola_oil_bucket','kaleidoscope_grilling:secret_chili_oil_bucket',
 'kaleidoscope_grilling:premium_chili_oil_bucket'].includes(stack?.typeId);}
world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 // Untyped host pots pass through untouched, including the host's own filling.
 // Block placing a Grilling-typed host item anywhere until the host can own it.
 if(typedHand(e.itemStack)||legacyTypedPot(e.block)||(e.block?.typeId===HOST_BLOCK_ID&&typedBucket(e.itemStack))){
  e.cancel=true;if(e.isFirstEvent!==false)notify(e.player);
 }
});
world.beforeEvents.playerBreakBlock.subscribe(e=>{
 if(legacyTypedPot(e.block)){e.cancel=true;notify(e.player);}
});
world.beforeEvents.explosion.subscribe(e=>{
 const impacted=e.getImpactedBlocks(),keep=impacted.filter(block=>!legacyTypedPot(block));
 if(keep.length!==impacted.length)e.setImpactedBlocks(keep);
});
// No cleanup of old properties, block removal, item spawning, or host-state write.
// Command edits and other addons that ignore cancellation cannot be prevented.
