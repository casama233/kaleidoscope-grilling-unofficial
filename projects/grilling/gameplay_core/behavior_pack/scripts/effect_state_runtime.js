import {world,system} from '@minecraft/server';
import {nativeDragonHealth} from './dragon_native_health.js';
import {FX_KEY,activeEffects,effectPayload,milkEffects} from './effect_lifecycle_core.js';
const snapshots=new WeakMap(),identities=new Map();let identityTick=-1;
const copyEffects=fx=>Object.fromEntries(Object.entries(fx).map(([k,v])=>[k,{...v}]));
function identity(entity){if(identityTick!==system.currentTick){identities.clear();identityTick=system.currentTick}try{if(typeof entity.id==='string')return entity.id}catch{}return undefined;}
function snapshot(entity){const id=identity(entity);return id===undefined?snapshots.get(entity):identities.get(id);}
function save(entity,value){const id=identity(entity);if(id===undefined)snapshots.set(entity,value);else identities.set(id,value);}
function discard(entity){const id=identity(entity);if(id===undefined)snapshots.delete(entity);else identities.delete(id);}
export function effectTime(){try{return world.getAbsoluteTime()}catch{return system.currentTick}}
export function readEffects(entity){
 const cached=snapshot(entity);if(cached?.tick===system.currentTick)return copyEffects(cached.effects);
 let raw,value;try{raw=entity.getDynamicProperty(FX_KEY);value=typeof raw==='string'?JSON.parse(raw):{}}catch{value={}}
 const effects=activeEffects(value,effectTime());save(entity,{tick:system.currentTick,raw,effects});return copyEffects(effects);
}
export function writeEffects(entity,value){
 const effects=activeEffects(value,effectTime()),raw=effectPayload(effects,effectTime());
 let old=snapshot(entity);if(old?.tick!==system.currentTick){readEffects(entity);old=snapshot(entity)}
 // Events can supply distinct wrappers for the same actor. Share by native ID,
 // and do not let an uncommitted caller mutation change the cached snapshot.
 if(raw!==old?.raw)try{entity.setDynamicProperty(FX_KEY,raw)}catch(error){discard(entity);throw error}
 save(entity,{tick:system.currentTick,raw,effects});return copyEffects(effects);
}
export function clearEffects(entity,{milk=false}={}){
 if(readEffects(entity).dragon_blood)nativeDragonHealth(entity,undefined);
 writeEffects(entity,milk?milkEffects(readEffects(entity),effectTime()):{});
 entity.setDynamicProperty('kaleidoscope_grilling:dragon_pool',undefined);
 discard(entity);
}
