import {world,system} from '@minecraft/server';
import {FX_KEY,activeEffects} from './effect_lifecycle_core.js';
import {writeEffects} from './effect_state_runtime.js';
import {definitelyLethalProvisionalHealth,sameHeavyMetalEffect,planHeavyMetalTransition} from './heavy_metal_damage_core.js';

// One claim per entity. An already canceled hit cannot refund its claim merely
// because the later storage acknowledgement failed. Quarantine lasts while the
// same raw effect remains, including expiry/clock rollback; it is session-local.
const rescues=new Map();
function snapshot(entity){
 const time=world.getAbsoluteTime();
 if(!Number.isFinite(time))throw Error('Heavy Metal absolute clock is unavailable');
 const raw=entity.getDynamicProperty(FX_KEY);
 if(raw!==undefined&&typeof raw!=='string')throw Error('Heavy Metal effect state is unreadable');
 const value=raw===undefined?{}:JSON.parse(raw);
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('Heavy Metal effect state is invalid');
 return {time,raw,hasMetal:Object.hasOwn(value,'heavy_metal'),effects:activeEffects(value,time),rawMetal:activeEffects({heavy_metal:value.heavy_metal},-Infinity).heavy_metal};
}
function release(id,token){if(rescues.get(id)===token)rescues.delete(id)}
export function forgetHeavyMetalRescue(entityOrId){
 try{rescues.delete(typeof entityOrId==='string'?entityOrId:entityOrId.id)}catch{}
}
function settle(entity,id,token){
 if(rescues.get(id)!==token||token.phase!=='pending')return;
 try{
  if(entity.isValid===false){release(id,token);return}
  const state=snapshot(entity);
  if(state.time<token.time)throw Error('Heavy Metal absolute clock moved backwards');
  const next=planHeavyMetalTransition(state.effects,token,state.time);
  if(!next){
   if(sameHeavyMetalEffect(state.rawMetal,token))token.phase='quarantined';
   else release(id,token);
   return;
  }
  const health=entity.getComponent('minecraft:health'),value=health?.currentValue;
  if(!Number.isFinite(value))throw Error('Heavy Metal health is unreadable');
  if(value<=0){release(id,token);return} // Never resurrect a later death.

  // Use the actual acknowledged effect writer once. main's legacy fxClear /
  // fxSet wrappers swallow storage errors and cannot establish this receipt.
  token.phase='committing';
  writeEffects(entity,next,{expectedRaw:state.raw});
  const saved=snapshot(entity);
  if(saved.hasMetal||!sameHeavyMetalEffect(saved.effects.heavy_metal_poisoning,next.heavy_metal_poisoning))
   throw Error('Heavy Metal transition was not acknowledged');
  token.phase='paid';
  if(rescues.get(id)!==token||entity.isValid===false)return;
  let healthError;try{health.setCurrentValue(1)}catch(error){healthError=error}
  if(entity.getComponent('minecraft:health')?.currentValue!==1)
   throw healthError??Error('Heavy Metal rescue health was not acknowledged');
  entity.dimension.playSound('kg_java21.heavy_metal',entity.location);
 }catch(error){
  // A canceled hit is already protection. Do not grant another one on an
  // unchanged/unreadable effect, retry unknown writes, or replay native damage.
  if(token.phase!=='paid')token.phase='quarantined';
  console.warn('[Grilling heavy metal] '+error);
 }finally{if(token.phase==='paid')release(id,token)}
}

/** Called only by main's existing before-hurt subscriber, after dodge and
 * invincibility. This module adds no competing event subscription.
 */
export function handleHeavyMetalBeforeHurt(event){
 if(event.cancel||!(event.damage>0))return false;
 let id,token;
 try{
  const entity=event.hurtEntity;id=entity.id;
  if(typeof id!=='string'||entity.isValid===false)return false;
  const state=snapshot(entity),old=rescues.get(id);
  if(old){
   if(old.phase==='quarantined'&&!sameHeavyMetalEffect(state.rawMetal,old))release(id,old);
   else return false;
  }
  const metal=state.effects.heavy_metal;
  if(!sameHeavyMetalEffect(metal,metal)||state.effects.heavy_metal_poisoning)return false;
  const health=entity.getComponent('minecraft:health');
  if(!health||!definitelyLethalProvisionalHealth(health.currentValue,entity.getEffect?.('absorption')))return false;
  token={...metal,time:state.time,phase:'pending'};rescues.set(id,token);
  // A throwing scheduler may already have queued its callback. Releasing this
  // exact token makes that callback inert before native damage is allowed on.
  system.run(()=>settle(entity,id,token));
  event.cancel=true;return true;
 }catch(error){
  if(token)release(id,token);
  console.warn('[Grilling heavy metal admission] '+error);return false;
 }
}
