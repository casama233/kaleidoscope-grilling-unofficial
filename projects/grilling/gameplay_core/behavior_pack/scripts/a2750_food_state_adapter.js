import {world,system} from '@minecraft/server';
import {SEASONING_LIST_KEY,normalizeSeasoningList} from './a2743_seasoning_contract_core.js';
import {readRawFoodLore,isHeatLore,applyFoodMaxim} from './a2769_food_tooltip_core.js';
import './a2769_food_tooltip_runtime.js';

export const HOT_UNTIL_KEY='kaleidoscope_grilling:hot_until';
function now(){try{return Number(world.getAbsoluteTime())||system.currentTick}catch{return system.currentTick}}
function bucketHot(until){return until-(((until%100)+100)%100)}
export function readFoodSeasonings(stack){
 try{
  const raw=stack?.getDynamicProperty(SEASONING_LIST_KEY);
  return typeof raw==='string'?normalizeSeasoningList(JSON.parse(raw)):[];
 }catch{return []}
}
export function setFoodSeasonings(stack,list){
 if(!stack)return stack;
 try{
  const values=normalizeSeasoningList(list);
  stack.setDynamicProperty(SEASONING_LIST_KEY,values.length?JSON.stringify(values):undefined);
 }catch{}
 return stack;
}
export function hotUntil(stack){try{return Number(stack?.getDynamicProperty(HOT_UNTIL_KEY)??0)}catch{return 0}}
export function isHotFood(stack){return hotUntil(stack)>now()}
export function refreshHotLore(stack){
 if(!stack)return stack;
 const until=hotUntil(stack);
 try{
  const base=readRawFoodLore(stack).filter(line=>!isHeatLore(line));
  if(until<=0)return stack;
  const left=Math.max(0,until-now());
  if(left<=0){stack.setDynamicProperty(HOT_UNTIL_KEY,undefined);stack.setLore(base);return stack}
  const sec=Math.max(1,Math.ceil(left/20)),m=Math.floor(sec/60),ss=String(sec%60).padStart(2,'0');
  // A full custom lore is not permission to discard a user's line.
  if(base.length>=20)return stack;
  base.push('§c🔥 煙火氣 '+m+':'+ss);stack.setLore(base);
 }catch{}
 return stack;
}
export function setHotFood(stack,ticks){
 if(!stack||ticks<=0)return stack;
 try{
  const until=bucketHot(now()+Math.max(1,Math.floor(Number(ticks)||0)));
  const left=Math.max(1,until-now()),sec=Math.max(1,Math.ceil(left/20)),m=Math.floor(sec/60),ss=String(sec%60).padStart(2,'0');
  const lore=readRawFoodLore(stack).filter(line=>!isHeatLore(line));
  if(lore.length>=20)return stack;
  lore.push('§c🔥 煙火氣 '+m+':'+ss);
  stack.setLore(lore);
  stack.setDynamicProperty(HOT_UNTIL_KEY,until);
 }catch{}
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
