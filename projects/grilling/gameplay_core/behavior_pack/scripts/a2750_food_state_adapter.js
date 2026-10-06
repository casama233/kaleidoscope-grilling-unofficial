import {getItemProperty,setItemProperty,getItemPropertyIds,getItemLore,getItemRawLore,setItemLore} from './itemData.js';
import {world,system} from '@minecraft/server';
import {SEASONING_LIST_KEY,normalizeSeasoningList} from './a2743_seasoning_contract_core.js';
import {readRawFoodLore,isHeatLore,applyFoodMaxim} from './a2769_food_tooltip_core.js';
import './a2769_food_tooltip_runtime.js';
import {heatLore} from './localized_lore_core.js';
import {readPublicFood,writePublicFood,bucketHotUntil} from './host_api/food_api_core.js';

export const HOT_UNTIL_KEY='kaleidoscope_grilling:hot_until';
function now(){try{return Number(world.getAbsoluteTime())||system.currentTick}catch{return system.currentTick}}
export function readFoodSeasonings(stack){
 const portable=readPublicFood(stack);if(portable.present)return portable.valid?normalizeSeasoningList(portable.state.seasoning):[];
 try{
  const raw=getItemProperty(stack,SEASONING_LIST_KEY);
  return typeof raw==='string'?normalizeSeasoningList(JSON.parse(raw)):[];
 }catch{return []}
}
export function setFoodSeasonings(stack,list){
 if(!stack)return stack;
 try{
  const values=normalizeSeasoningList(list);
  const portable=readPublicFood(stack);if(portable.present){if(!portable.valid)throw Error('public food unreadable');writePublicFood(stack,{...portable.state,seasoning:values});}
  setItemProperty(stack,SEASONING_LIST_KEY,values.length?JSON.stringify(values):undefined);
 }catch{}
 return stack;
}
export function hotUntil(stack){const p=readPublicFood(stack);if(p.present)return p.valid?p.state.hotUntil:0;try{return Number(getItemProperty(stack,HOT_UNTIL_KEY)??0)}catch{return 0}}
export function isHotFood(stack){return hotUntil(stack)>now()}
export function refreshHotLore(stack){
 if(!stack)return stack;
 const until=hotUntil(stack);
 try{
  const base=getItemRawLore(stack).filter(line=>!isHeatLore(line));
  if(until<=0)return stack;
  const left=Math.max(0,until-now());
  if(left<=0){const p=readPublicFood(stack);setItemProperty(stack,HOT_UNTIL_KEY,undefined);setItemLore(stack,base.filter(x=>!x||typeof x!=='object'||x.translate!=='senluo.public.food.v1'));if(p.present&&p.valid)writePublicFood(stack,{...p.state,hotUntil:0});return stack}
  const sec=Math.max(1,Math.ceil(left/20));
  // A full custom lore is not permission to discard a user's line.
  if(base.length>=(stack.maxAmount>1?19:20))return stack;
  base.push(heatLore(sec));setItemLore(stack,base);
 }catch{}
 return stack;
}
export function setHotFood(stack,ticks){
 if(!stack||!Number.isFinite(ticks)||ticks<=0)return stack;
 let before,priorHot;
 try{
  const portable=readPublicFood(stack);if(portable.present&&!portable.valid)return stack;
  before=stack.getRawLore();priorHot=getItemProperty(stack,HOT_UNTIL_KEY);
  const time=now(),until=bucketHotUntil(time+Math.max(1,Math.floor(ticks)));
  const left=Math.max(0,until-time),sec=Math.ceil(left/20);
  const lore=getItemRawLore(stack).filter(line=>!isHeatLore(line));
  // Stackable metadata needs a carrier. A cosmetic badge must not consume its line.
  const limit=stack.maxAmount>1?19:20;
  if(lore.length>limit)return stack;
  if(left>0&&lore.length<limit)lore.push(heatLore(sec));
  setItemLore(stack,lore);
  setItemProperty(stack,HOT_UNTIL_KEY,until);
  if(portable.valid)writePublicFood(stack,{...portable.state,hotUntil:until});
 }catch{
  // Restore the original carrier or native property after any partial write.
  if(before)try{if(stack.maxAmount<=1)stack.setDynamicProperty(HOT_UNTIL_KEY,priorHot);stack.setLore(before)}catch{}
 }
 return stack;
}
export function applyFoodMetadata(stack,{seasoning=[],hotTicks=0}={}){
 if(!stack)return stack;
 // Customize before writing dynamic properties; all cuisine outputs retain their
 // original hot duration. A tooltip failure must not suppress gameplay metadata.
 setHotFood(stack,hotTicks);setFoodSeasonings(stack,seasoning);
 try{applyFoodMaxim(stack)}catch{}
 return stack;
}
