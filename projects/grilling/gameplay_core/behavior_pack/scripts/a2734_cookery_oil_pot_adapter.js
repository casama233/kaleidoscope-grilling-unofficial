import {ItemStack} from '@minecraft/server';
import {
 COOKERY_EMPTY_ID,COOKERY_FILLED_ID,HOST_COUNT_KEY,GRILLING_TYPE_KEY,
 normalizeOilType,oilCapacity,normalizeOilCount,planOilConsumption,planTypedOilAddition
} from './a2734_cookery_oil_pot_core.js';

export {COOKERY_EMPTY_ID,COOKERY_FILLED_ID,HOST_COUNT_KEY,GRILLING_TYPE_KEY};
function dynamic(stack,key){
 try{return {ok:true,value:stack?.getDynamicProperty(key)}}catch{return {ok:false,value:undefined}}
}
export function readCookeryOilPot(stack,{legacyPlacementFallback=false}={}){
 const filled=stack?.typeId===COOKERY_FILLED_ID,empty=stack?.typeId===COOKERY_EMPTY_ID;
 if(!filled)return {filled:false,empty,type:'',count:0,capacity:0,valid:true};
 const typeProbe=dynamic(stack,GRILLING_TYPE_KEY),countProbe=dynamic(stack,HOST_COUNT_KEY);
 const type=normalizeOilType(typeProbe.value);
 const count=normalizeOilCount({filled:true,type,raw:countProbe.value,
  hasRaw:countProbe.ok&&countProbe.value!==undefined,legacyPlacementFallback});
 return {filled:true,empty:false,type,count,capacity:oilCapacity(type),valid:typeProbe.ok&&countProbe.ok};
}
export function readCookeryOilPotForPlacement(stack){return readCookeryOilPot(stack,{legacyPlacementFallback:true})}
function oilLore(line){
 return typeof line==='string'?line.startsWith('§7Oil: '):
  !!line&&typeof line.text==='string'&&line.text.startsWith('§7Oil: ');
}
export function buildCookeryOilPot(type,count,template=undefined){
 const normalizedType=normalizeOilType(type),cap=oilCapacity(normalizedType);
 const normalizedCount=Math.max(0,Math.min(cap,Math.floor(Number(count)||0)));
 if(normalizedCount<=0){
  try{return new ItemStack(COOKERY_EMPTY_ID,1)}catch{return undefined}
 }
 try{
  const out=template?.typeId===COOKERY_FILLED_ID?template.clone():new ItemStack(COOKERY_FILLED_ID,1);
  out.amount=1;
  const lore=out.getRawLore().filter(line=>!oilLore(line));
  if(lore.length>=20)return undefined;
  lore.push('§7Oil: '+normalizedCount+'/'+cap);
  // Customize first, then persist. Never return an item with only half its oil payload.
  out.setLore(lore);
  out.setDynamicProperty(HOST_COUNT_KEY,normalizedCount);
  out.setDynamicProperty(GRILLING_TYPE_KEY,normalizedType||undefined);
  const result=readCookeryOilPot(out);
  if(!result.valid||result.type!==normalizedType||result.count!==normalizedCount)return undefined;
  return out;
 }catch{return undefined}
}
export function planCookeryOilPotConsumption(stack,needed,requiredType=''){
 const state=readCookeryOilPot(stack);
 if(!state.valid)return {ok:false,reason:'stack_error'};
 const plan=planOilConsumption(state,needed,requiredType);if(!plan.ok)return plan;
 let before;
 try{before=stack.clone()}catch{return {ok:false,reason:'stack_error',type:plan.type,count:plan.count}}
 const next=buildCookeryOilPot(plan.type,plan.remaining,stack);
 if(!next)return {ok:false,reason:'stack_error',type:plan.type,count:plan.count};
 return {...plan,before,next};
}
export function planCookeryTypedOilAddition(stack,incomingType,points){
 const state=readCookeryOilPot(stack);
 if(!state.valid)return {ok:false,reason:'stack_error'};
 const plan=planTypedOilAddition(state,incomingType,points);if(!plan.ok)return plan;
 const next=buildCookeryOilPot(plan.type,plan.nextCount,stack);
 if(!next)return {ok:false,reason:'stack_error',type:plan.type,count:plan.count};
 return {...plan,next};
}
