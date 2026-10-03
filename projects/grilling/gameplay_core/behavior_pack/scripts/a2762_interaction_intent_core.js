import {getItemProperty,setItemProperty,getItemPropertyIds,getItemLore,setItemLore} from './itemDataCore.js';
import {chooseInteractionHand,makeIntent,intentMatches} from './a276_grill_intent_core.js';

export function primitiveStackProps(stack){
 const out={};let ids=[];try{ids=getItemPropertyIds(stack)??[]}catch{}
 for(const id of ids)try{
  const value=getItemProperty(stack,id);
  if(['string','number','boolean'].includes(typeof value))out[id]=value;
  else if(value&&typeof value==='object'&&Number.isFinite(value.x)&&Number.isFinite(value.y)&&Number.isFinite(value.z))out[id]={x:value.x,y:value.y,z:value.z};
 }catch{}
 return out;
}

export function stackIntentSignature(stack){
 if(!stack)return null;
 // These capabilities distinguish otherwise identical stacks. An unreadable
 // capability must reject capture, never masquerade as an empty/default value
 // or null (which represents an actually empty hand to shared intent callers).
 const keepOnDeath=stack.keepOnDeath,lockMode=stack.lockMode;
 if(typeof keepOnDeath!=='boolean'||typeof lockMode!=='string'
  ||typeof stack.getCanDestroy!=='function'||typeof stack.getCanPlaceOn!=='function')
  throw new Error('Grilling: item intent capabilities unavailable');
 const restrictions=(value)=>{
  if(!Array.isArray(value)||value.some(id=>typeof id!=='string'))
   throw new Error('Grilling: item intent restrictions unreadable');
  return [...value].sort(); // Sort only a copy; never mutate native metadata.
 };
 const canDestroy=restrictions(stack.getCanDestroy()),canPlaceOn=restrictions(stack.getCanPlaceOn());
 const raw=primitiveStackProps(stack),props=Object.fromEntries(Object.keys(raw).sort().map(k=>[k,raw[k]]));
 let lore=[];try{lore=getItemLore(stack)}catch{}
 let name='';try{name=stack.nameTag??''}catch{}
 let damage=null;try{damage=Number(stack.getComponent('minecraft:durability')?.damage??0)}catch{}
 return JSON.stringify({id:stack.typeId,amount:Number(stack.amount)||1,name,lore,props,damage,
  keepOnDeath,lockMode,canDestroy,canPlaceOn});
}

export function stackIntentDescriptor(stack){
 return stack?{empty:false,id:stack.typeId,sig:stackIntentSignature(stack)}:{empty:true,id:null,sig:null};
}

export function captureInteractionIntentFromStacks(eventStack,mainStack,offStack,selectedSlot){
 const e=stackIntentDescriptor(eventStack),m=stackIntentDescriptor(mainStack),o=stackIntentDescriptor(offStack);
 const hand=chooseInteractionHand(e,m,o),sig=hand==='off'?o.sig:m.sig;
 return makeIntent(hand,sig,selectedSlot);
}

export function interactionIntentMatchesStacks(intent,mainStack,offStack,selectedSlot){
 try{return intentMatches(intent,stackIntentSignature(mainStack),stackIntentSignature(offStack),selectedSlot)}
 catch{return false} // A deferred action cannot verify an unreadable hand.
}
