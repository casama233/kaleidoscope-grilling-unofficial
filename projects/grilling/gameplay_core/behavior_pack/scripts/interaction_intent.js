import {getMainHand,getOffHand} from './a2735_player_io.js';
import {chooseInteractionHand,makeIntent,intentMatches} from './a276_grill_intent_core.js';

function primitiveProps(stack){
 const out={};let ids=[];try{ids=stack?.getDynamicPropertyIds?.()??[]}catch{}
 for(const id of ids)try{
  const value=stack.getDynamicProperty(id);
  if(['string','number','boolean'].includes(typeof value))out[id]=value;
  else if(value&&typeof value==='object'&&Number.isFinite(value.x)&&Number.isFinite(value.y)&&Number.isFinite(value.z))out[id]={x:value.x,y:value.y,z:value.z};
 }catch{}
 return out;
}

export function interactionStackSignature(stack){
 if(!stack)return null;
 const raw=primitiveProps(stack),props=Object.fromEntries(Object.keys(raw).sort().map(k=>[k,raw[k]]));
 let lore=[];try{lore=stack.getLore()}catch{}
 let name='';try{name=stack.nameTag??''}catch{}
 let damage=null;try{damage=Number(stack.getComponent('minecraft:durability')?.damage??0)}catch{}
 return JSON.stringify({id:stack.typeId,amount:Number(stack.amount)||1,name,lore,props,damage});
}

function descriptor(stack){
 return stack?{empty:false,id:stack.typeId,sig:interactionStackSignature(stack)}:{empty:true,id:null,sig:null};
}

export function captureInteractionIntent(player,eventStack){
 const eventDesc=descriptor(eventStack),main=descriptor(getMainHand(player)),off=descriptor(getOffHand(player));
 const hand=chooseInteractionHand(eventDesc,main,off),signature=hand==='off'?off.sig:main.sig;
 return makeIntent(hand,signature,player.selectedSlotIndex);
}

export function interactionIntentStillCurrent(player,intent){
 return intentMatches(
  intent,
  interactionStackSignature(getMainHand(player)),
  interactionStackSignature(getOffHand(player)),
  player.selectedSlotIndex
 );
}
