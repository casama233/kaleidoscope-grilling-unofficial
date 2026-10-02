import {world,system} from '@minecraft/server';
import {FX_KEY,activeEffects,effectPayload,milkEffects} from './effect_lifecycle_core.js';
const snapshots=new WeakMap();
export function effectTime(){try{return world.getAbsoluteTime()}catch{return system.currentTick}}
export function readEffects(entity){
 const cached=snapshots.get(entity);if(cached?.tick===system.currentTick)return {...cached.effects};
 let raw,value;try{raw=entity.getDynamicProperty(FX_KEY);value=typeof raw==='string'?JSON.parse(raw):{}}catch{value={}}
 const effects=activeEffects(value,effectTime());snapshots.set(entity,{tick:system.currentTick,raw,effects});return {...effects};
}
export function writeEffects(entity,value){
 const effects=activeEffects(value,effectTime()),raw=effectPayload(effects,effectTime());
 let old=snapshots.get(entity);if(old?.tick!==system.currentTick){readEffects(entity);old=snapshots.get(entity)}
 // All canonical writers share this cache. No write or JSON parse on an unchanged empty tick.
 if(raw!==old?.raw)entity.setDynamicProperty(FX_KEY,raw);
 snapshots.set(entity,{tick:system.currentTick,raw,effects});return effects;
}
export function clearEffects(entity,{milk=false}={}){
 writeEffects(entity,milk?milkEffects(readEffects(entity),effectTime()):{});
 entity.setDynamicProperty('kaleidoscope_grilling:dragon_pool',undefined);
 snapshots.delete(entity);
}
