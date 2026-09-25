import {chooseInteractionHand,makeIntent,intentMatches} from './a276_grill_intent_core.js';

export function primitiveStackProps(stack){
 const out={};let ids=[];try{ids=stack?.getDynamicPropertyIds?.()??[]}catch{}
 for(const id of ids)try{
  const value=stack.getDynamicProperty(id);
  if(['string','number','boolean'].includes(typeof value))out[id]=value;
  else if(value&&typeof value==='object'&&Number.isFinite(value.x)&&Number.isFinite(value.y)&&Number.isFinite(value.z))out[id]={x:value.x,y:value.y,z:value.z};
 }catch{}
 return out;
}

export function stackIntentSignature(stack){
 if(!stack)return null;
 const raw=primitiveStackProps(stack),props=Object.fromEntries(Object.keys(raw).sort().map(k=>[k,raw[k]]));
 let lore=[];try{lore=stack.getLore()}catch{}
 let name='';try{name=stack.nameTag??''}catch{}
 let damage=null;try{damage=Number(stack.getComponent('minecraft:durability')?.damage??0)}catch{}
 return JSON.stringify({id:stack.typeId,amount:Number(stack.amount)||1,name,lore,props,damage});
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
 return intentMatches(intent,stackIntentSignature(mainStack),stackIntentSignature(offStack),selectedSlot);
}
