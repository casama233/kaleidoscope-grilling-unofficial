import {system} from '@minecraft/server';
import {getMainHand,getOffHand} from './a2735_player_io.js';
import {getItemProperty} from './itemDataCore.js';
import {PLATE_ID,PLATE_SKEWERS_KEY} from './a25_plate_recipe_core.js';
import {decodePlateStorage} from './plate_transaction_core.js';
import {createPlateQaLogger} from './plate_qa_core.js';
function count(stack){
 if(stack?.typeId!==PLATE_ID)return 'not_plate';
 try{return decodePlateStorage(getItemProperty(stack,PLATE_SKEWERS_KEY)).length;}catch{return 'unreadable';}
}
export const plateQaTrace=createPlateQaLogger({
 enabled:player=>player?.hasTag?.('kg_plate_qa')===true,
 key:player=>player.id, // Internal rate-limit key only. Never emitted or persisted.
 tick:()=>system.currentTick,
 snapshot:(player,eventStack)=>{
  const main=getMainHand(player),off=getOffHand(player);
  return {eventType:eventStack?.typeId,mainType:main?.typeId,offType:off?.typeId,eventRows:count(eventStack),mainRows:count(main),offRows:count(off)};
 },
 write:line=>console.warn(line)
});
