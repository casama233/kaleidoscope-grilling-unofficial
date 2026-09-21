import {world,system} from '@minecraft/server';
import {
 FX_KEY,effectsForStandaloneFood,nextPersistentUntil
} from './a2732_standalone_food_effect_core.js';

function now(){
 try{return Number(world.getAbsoluteTime())||system.currentTick}catch{return system.currentTick}
}
function readFx(entity){
 try{
  const raw=entity.getDynamicProperty(FX_KEY);
  if(typeof raw!=='string')return {};
  const value=JSON.parse(raw);
  return value&&typeof value==='object'?value:{};
 }catch{return {}}
}
function writeFx(entity,fx){
 try{
  const t=now(),clean={};
  for(const [name,value] of Object.entries(fx)){
   if(value&&Number(value.until)>t)clean[name]={until:Number(value.until),amp:Number(value.amp)||0};
  }
  entity.setDynamicProperty(FX_KEY,Object.keys(clean).length?JSON.stringify(clean):undefined);
 }catch{}
}
function applyPersistent(entity,effect){
 const t=now(),fx=readFx(entity),current=Number(fx[effect.effect]?.until)||0;
 fx[effect.effect]={
  until:nextPersistentUntil(t,current,effect.ticks),
  amp:Number(effect.amplifier)||0
 };
 writeFx(entity,fx);
}
function applyNative(entity,effect){
 try{entity.addEffect(effect.effect,Math.max(1,Number(effect.ticks)||1),{...(effect.options??{})})}catch{}
}

export function applyStandaloneFoodEffects(entity,itemId){
 const effects=effectsForStandaloneFood(itemId);
 if(!effects.length)return false;
 for(const effect of effects){
  if(effect.kind==='persistent_fx')applyPersistent(entity,effect);
  else if(effect.kind==='native')applyNative(entity,effect);
 }
 return true;
}

world.afterEvents.itemCompleteUse.subscribe(event=>{
 try{applyStandaloneFoodEffects(event.source,event.itemStack?.typeId)}catch{}
});
