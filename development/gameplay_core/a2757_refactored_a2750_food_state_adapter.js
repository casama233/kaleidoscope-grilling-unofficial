import {world,system} from '@minecraft/server';
import {
 SEASONING_LIST_KEY,normalizeSeasoningList
} from './a2743_seasoning_contract_core.js';

export const HOT_UNTIL_KEY='kaleidoscope_grilling:hot_until';

function now(){
 try{return Number(world.getAbsoluteTime())||system.currentTick}catch{return system.currentTick}
}
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
export function hotUntil(stack){
 try{return Number(stack?.getDynamicProperty(HOT_UNTIL_KEY)??0)}catch{return 0}
}
export function isHotFood(stack){return hotUntil(stack)>now()}
export function refreshHotLore(stack){
 if(!stack)return stack;
 const until=hotUntil(stack);
 try{
  const base=stack.getLore().filter(x=>!String(x).startsWith('§c🔥'));
  if(until<=0)return stack;
  const left=Math.max(0,until-now());
  if(left<=0){
   stack.setDynamicProperty(HOT_UNTIL_KEY,undefined);stack.setLore(base);return stack;
  }
  const sec=Math.max(1,Math.ceil(left/20)),m=Math.floor(sec/60),ss=String(sec%60).padStart(2,'0');
  base.push('§c🔥 煙火氣 '+m+':'+ss);stack.setLore(base);
 }catch{}
 return stack;
}
export function setHotFood(stack,ticks){
 if(!stack||ticks<=0)return stack;
 try{
  const until=bucketHot(now()+Math.max(1,Math.floor(Number(ticks)||0)));
  const left=Math.max(1,until-now()),sec=Math.max(1,Math.ceil(left/20)),m=Math.floor(sec/60),ss=String(sec%60).padStart(2,'0');
  const lore=stack.getLore().filter(x=>!String(x).startsWith('§c🔥'));
  lore.push('§c🔥 煙火氣 '+m+':'+ss);
  stack.setLore(lore);
  stack.setDynamicProperty(HOT_UNTIL_KEY,until);
 }catch{}
 return stack;
}
export function applyFoodMetadata(stack,{seasoning=[],hotTicks=0}={}){
 if(!stack)return stack;
 // Official stable API: ItemStack dynamic properties require a non-stackable/custom item.
 // HotFood lore is therefore committed first; that customizes the serving before the
 // seasoning dynamic property is written. All Cookery Pot/Stockpot outputs reach this
 // adapter with a positive hot duration, matching Java's HotFood integration.
 setHotFood(stack,hotTicks);setFoodSeasonings(stack,seasoning);return stack;
}
