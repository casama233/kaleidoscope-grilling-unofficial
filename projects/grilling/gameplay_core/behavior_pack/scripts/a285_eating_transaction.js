import {primitiveStackProps} from './a2762_interaction_intent_core.js';

// Heat countdown lore changes while eating; authoritative heat/ingredient data must not.
export function eatingIdentity(stack){
 if(!stack)return null;
 const raw=primitiveStackProps(stack),props=Object.fromEntries(Object.keys(raw).sort().map(k=>[k,raw[k]]));
 return JSON.stringify({id:stack.typeId,amount:stack.amount,name:stack.nameTag??'',
  lore:stack.getLore().filter(x=>!String(x).startsWith('§c🔥')),props});
}
export function captureEatingIdentity(stack,hand,slot){return {identity:eatingIdentity(stack),hand,slot}}
export function eatingStillCurrent(use,current,slot){
 return !!use&&!!current&&(use.hand==='off'||use.slot===slot)&&use.identity===eatingIdentity(current);
}

// No reward before a verified debit. A failed write cannot grant free nutrition.
// Adapters throw on unavailable storage; rollback is attempted on every failure.
export function commitEating({debit,reward,restoreFood,restoreNutrition}){
 try{debit();reward();return true}catch(error){
  let rollbackError;
  try{restoreNutrition()}catch(e){rollbackError=e}
  try{restoreFood()}catch(e){rollbackError=e}
  if(rollbackError)throw new Error('Eating rollback failed: '+rollbackError);
  return false;
 }
}
