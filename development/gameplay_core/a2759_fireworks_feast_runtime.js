import {awardOneShotAdvancement} from './a2753_advancement_runtime.js';
import {
 FIREWORKS_FEAST,FIREWORKS_FEAST_PROGRESS_KEY,nextFireworksFeastProgress
} from './a2759_fireworks_feast_core.js';

function readProgress(player){
 try{return player?.getDynamicProperty(FIREWORKS_FEAST_PROGRESS_KEY)}
 catch{return undefined}
}
function writeProgress(player,eaten){
 try{player.setDynamicProperty(FIREWORKS_FEAST_PROGRESS_KEY,JSON.stringify(eaten));return true}
 catch{return false}
}

export function recordFireworksFeastFood(player,itemId){
 if(!player)return false;
 const plan=nextFireworksFeastProgress(readProgress(player),itemId);
 if(!plan.eligible)return false;
 if(plan.changed&&!writeProgress(player,plan.eaten))return false;
 if(plan.complete)return awardOneShotAdvancement(player,FIREWORKS_FEAST);
 return plan.changed;
}
