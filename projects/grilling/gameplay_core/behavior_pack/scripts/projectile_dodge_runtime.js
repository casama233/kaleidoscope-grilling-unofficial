/** Before-hurt bookkeeping only; effect debit/teleport remain mutable-phase work.
 * One finite effect can own several pending 200-tick charges. This does not
 * reproduce Java's cancellable projectile-impact/skip-target event stage. */
import {projectileDodgeTime as effectTime,readProjectileDodgeState,debitProjectileDodge,forgetProjectileDodgeState} from './effect_state_runtime.js';
const pending=new Map(),COST=200;
const effectKey=effect=>effect?effect.until+'|'+effect.amp:'';
function discard(id){pending.delete(id);}
function actorContext(entity){
 if(entity.isValid!==true||!entity.getComponent('minecraft:health'))return undefined;
 const id=entity.id,dimensionId=entity.dimension.id;
 return typeof id==='string'&&id&&typeof dimensionId==='string'?{id,dimensionId}:undefined;
}
export function forgetProjectileDodge(entityOrId){
 let id;try{id=typeof entityOrId==='string'?entityOrId:entityOrId.id}catch{return}
 discard(id);forgetProjectileDodgeState(id);
}
export function reserveProjectileDodge(entity){
 let actor;
 try{
  const time=effectTime();if(!Number.isFinite(time))return undefined;
  actor=actorContext(entity);if(!actor)return undefined;
  let row=pending.get(actor.id);if(row?.busy)return undefined;
  const state=readProjectileDodgeState(entity);
  if(!state?.active||!state.effect){return undefined;}
  const observedTime=Math.max(time,state.observedTime);
  if(row&&(row.generation!==state.generation||row.dimensionId!==actor.dimensionId||row.expected!==effectKey(state.effect))){discard(actor.id);row=undefined;}
  if(!row){row={...actor,generation:state.generation,originalUntil:state.effect.until,expected:effectKey(state.effect),spent:0,reserved:0,claims:new Set(),busy:false,faulted:false};pending.set(actor.id,row);}
  // A native writer can reenter before it acknowledges its debit. Keep that
  // critical section closed; ordinary queued charges still have full capacity.
  if(row.faulted||row.busy||row.originalUntil-observedTime-row.spent-row.reserved<=0)return undefined;
  const claim={id:actor.id,row,phase:'reserved'};row.claims.add(claim);row.reserved+=COST;return claim;
 }catch{return undefined} // An unreadable new event must not release older protected charges.
}
export function abandonProjectileDodge(claim){
 const row=claim?.row;if(!row?.claims.has(claim))return;
 row.claims.delete(claim);row.reserved-=COST;claim.phase='abandoned';
 if(!row.claims.size&&!row.faulted&&pending.get(claim.id)===row)discard(claim.id);
}
export function settleProjectileDodge(entity,claim,teleport){
 const row=claim?.row;
 if(!row||pending.get(claim.id)!==row||!row.claims.has(claim)||claim.phase!=='reserved')return false;
 try{
  const time=effectTime();if(!Number.isFinite(time))throw Error('Projectile dodge clock is unreadable');
  const actor=actorContext(entity),health=entity.getComponent('minecraft:health');
  if(actor&&!Number.isFinite(health.currentValue))throw Error('Projectile dodge health is unreadable');
  if(!actor||actor.id!==claim.id||actor.dimensionId!==row.dimensionId||health.currentValue<=0){forgetProjectileDodge(claim.id);return false;}
  const current=readProjectileDodgeState(entity);
  // A raw, unchanged deadline may expire between admission and this callback.
  // Owned expiry pruning and acknowledged cost removal retain its generation;
  // milk/refresh/clear and lifecycle changes invalidate it instead.
  if(current?.generation!==row.generation||effectKey(current.effect)!==row.expected){discard(claim.id);return false;}
  if(row.busy)return false;
  row.busy=true;claim.phase='debiting';
  const result=debitProjectileDodge(entity,current,COST);
  if(!result.ok){
   // The hit was already canceled. An unacknowledged writer must not grant
   // repeated free protection from this same observed effect generation.
   row.faulted=true;row.generation=result.state?.generation??row.generation;row.expected=effectKey(result.state?.effect??current.effect);
   row.claims.clear();row.reserved=0;claim.phase='faulted';return false;
  }
  row.spent+=COST;row.expected=effectKey(result.state.effect);
  row.claims.delete(claim);row.reserved-=COST;claim.phase='settled';row.busy=false;
  if(!row.claims.size&&pending.get(claim.id)===row)discard(claim.id);
  // Debit is acknowledged and the claim is detached before teleport reentry.
  teleport();return true;
 }catch(error){
  if(claim.phase!=='settled'){
   // An unknown mutable read/debit failure does not undo native cancellation.
   // Keep this observed generation closed instead of refunding protected hits.
   row.faulted=true;row.claims.clear();row.reserved=0;claim.phase='faulted';
  }
  console.warn('[Grilling projectile dodge] '+error);return false;
 }
 finally{
  row.busy=false;
  if(row.claims.has(claim)){row.claims.delete(claim);row.reserved-=COST;claim.phase='abandoned';}
  if(!row.claims.size&&!row.faulted&&pending.get(claim.id)===row)discard(claim.id);
 }
}
