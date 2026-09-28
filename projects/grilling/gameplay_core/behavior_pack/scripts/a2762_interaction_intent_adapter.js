import {getMainHand,getOffHand,captureWritableHand} from './a2735_player_io.js';
import {stackIntentSignature} from './a2762_interaction_intent_core.js';
import {makeTwoHandIntent,sameTwoHandIntent} from './a288_intent_core.js';
import {
 primitiveStackProps,captureInteractionIntentFromStacks,interactionIntentMatchesStacks
} from './a2762_interaction_intent_core.js';

export {primitiveStackProps};

export function captureInteractionIntent(player,eventStack){
 return captureInteractionIntentFromStacks(eventStack,getMainHand(player),getOffHand(player),player.selectedSlotIndex);
}

export function interactionIntentStillCurrent(player,intent){
 return interactionIntentMatchesStacks(intent,getMainHand(player),getOffHand(player),player.selectedSlotIndex);
}

// A threading/disassembly gesture owns BOTH hands, not just its event item.
export function captureTwoHandIntent(player){
 try{
  if(!player.isValid)return null;
  const main=captureWritableHand(player,'main'),off=captureWritableHand(player,'off');
  return makeTwoHandIntent(stackIntentSignature(main.before),stackIntentSignature(off.before),
   player.selectedSlotIndex,player.dimension.id,player.isSneaking);
 }catch{return null}
}
export function twoHandIntentStillCurrent(player,intent){
 return sameTwoHandIntent(intent,captureTwoHandIntent(player));
}
