import {world} from '@minecraft/server';
import {
 MOUNTAIN_FRAGRANCE,advancementAwardPlan
} from './a2753_advancement_core.js';
import {advancementFrameTranslationKeys} from './a2758_advancement_challenge_core.js';

function claimed(player,key){
 try{return player?.getDynamicProperty(key)===true}catch{return false}
}
function markClaimed(player,key){
 try{player.setDynamicProperty(key,true);return true}catch{return false}
}
function giveExperience(player,amount){
 const n=Math.max(0,Math.floor(Number(amount)||0));if(n<=0)return true;
 try{player.addExperience(n);return true}catch{}
 try{player.runCommand('xp '+n+' @s');return true}catch{return false}
}
function announce(player,spec){
 if(!spec.announce)return;
 const keys=advancementFrameTranslationKeys(spec.frame);
 try{
  world.sendMessage({rawtext:[
   {text:'§d'+String(player.name??'Player')+'§r'},
   {translate:keys.announce},
   {translate:spec.titleKey}
  ]});
 }catch{}
 try{
  player.sendMessage({rawtext:[
   {translate:keys.self},
   {translate:spec.titleKey},
   {text:'§r — §7'},
   {translate:spec.descriptionKey}
  ]});
 }catch{}
}

export function awardOneShotAdvancement(player,spec){
 if(!player||!spec)return false;
 const plan=advancementAwardPlan(spec,claimed(player,spec.propertyKey));
 if(!plan.grant)return false;
 if(!giveExperience(player,plan.xp))return false;
 if(!markClaimed(player,plan.propertyKey))return false;
 announce(player,{...spec,...plan});
 return true;
}

export function awardMountainFragrance(player){
 return awardOneShotAdvancement(player,MOUNTAIN_FRAGRANCE);
}
