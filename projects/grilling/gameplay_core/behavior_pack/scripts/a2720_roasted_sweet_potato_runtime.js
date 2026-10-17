import {readEffects,writeEffects} from './effect_state_runtime.js';
import {world,system} from '@minecraft/server';
import {ROASTED_ID,WARMTH_EFFECT,WARMTH_TICKS,nextWarmthUntil} from './a2720_roasted_sweet_potato_core.js';

const FX_KEY='kaleidoscope_grilling:a21_fx';

function now(){
 try{return Number(world.getAbsoluteTime())||system.currentTick}catch{return system.currentTick}
}
const readFx=readEffects,writeFx=writeEffects;
export function applyRoastedSweetPotatoWarmth(entity){
 const t=now(),fx=readFx(entity),current=Number(fx[WARMTH_EFFECT]?.until)||0;
 fx[WARMTH_EFFECT]={until:nextWarmthUntil(t,current,WARMTH_TICKS),amp:0};
 writeFx(entity,fx);
}

world.afterEvents.itemCompleteUse.subscribe(ev=>{
 if(ev.itemStack?.typeId!==ROASTED_ID)return;
 try{applyRoastedSweetPotatoWarmth(ev.source)}catch{}
});
