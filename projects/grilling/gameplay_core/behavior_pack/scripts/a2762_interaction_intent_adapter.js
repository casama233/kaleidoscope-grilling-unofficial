import {getMainHand,getOffHand} from './a2735_player_io.js';
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
