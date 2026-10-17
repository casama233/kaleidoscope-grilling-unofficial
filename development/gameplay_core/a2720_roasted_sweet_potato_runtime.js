import {world,system} from '@minecraft/server';
import {ROASTED_ID,WARMTH_EFFECT,WARMTH_TICKS,nextWarmthUntil} from './a2720_roasted_sweet_potato_core.js';

const FX_KEY='kaleidoscope_grilling:a21_fx';

function now(){
 try{return Number(world.getAbsoluteTime())||system.currentTick}catch{return system.currentTick}
}
function readFx(entity){
 try{
  const raw=entity.getDynamicProperty(FX_KEY);
  if(typeof raw!=='string')return {};
  const v=JSON.parse(raw);return v&&typeof v==='object'?v:{};
 }catch{return {}}
}
function writeFx(entity,fx){
 try{
  const t=now(),clean={};
  for(const [k,v] of Object.entries(fx)){
   if(v&&Number(v.until)>t)clean[k]={until:Number(v.until),amp:Number(v.amp)||0};
  }
  entity.setDynamicProperty(FX_KEY,Object.keys(clean).length?JSON.stringify(clean):undefined);
 }catch{}
}
export function applyRoastedSweetPotatoWarmth(entity){
 const t=now(),fx=readFx(entity),current=Number(fx[WARMTH_EFFECT]?.until)||0;
 fx[WARMTH_EFFECT]={until:nextWarmthUntil(t,current,WARMTH_TICKS),amp:0};
 writeFx(entity,fx);
}

world.afterEvents.itemCompleteUse.subscribe(ev=>{
 if(ev.itemStack?.typeId!==ROASTED_ID)return;
 try{applyRoastedSweetPotatoWarmth(ev.source)}catch{}
});
