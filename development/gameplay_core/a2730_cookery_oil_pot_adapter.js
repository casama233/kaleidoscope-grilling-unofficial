import {ItemStack} from '@minecraft/server';
import {
 COOKERY_EMPTY_ID,COOKERY_FILLED_ID,HOST_COUNT_KEY,GRILLING_TYPE_KEY,
 normalizeOilType,oilCapacity,normalizeOilCount,planOilConsumption
} from './a2730_cookery_oil_pot_core.js';

export {COOKERY_EMPTY_ID,COOKERY_FILLED_ID,HOST_COUNT_KEY,GRILLING_TYPE_KEY};

function dynamic(stack,key){
 try{return {ok:true,value:stack?.getDynamicProperty(key)}}catch{return {ok:false,value:undefined}}
}

export function readCookeryOilPot(stack){
 const filled=stack?.typeId===COOKERY_FILLED_ID;
 const empty=stack?.typeId===COOKERY_EMPTY_ID;
 if(!filled)return {filled:false,empty,type:'',count:0,capacity:0};

 const typeProbe=dynamic(stack,GRILLING_TYPE_KEY);
 const type=normalizeOilType(typeProbe.value);
 const countProbe=dynamic(stack,HOST_COUNT_KEY);
 const count=normalizeOilCount({
  filled:true,type,raw:countProbe.value,
  hasRaw:countProbe.ok&&countProbe.value!==undefined
 });
 return {filled:true,empty:false,type,count,capacity:oilCapacity(type)};
}

export function buildCookeryOilPot(type,count,template=undefined){
 const normalizedType=normalizeOilType(type);
 const cap=oilCapacity(normalizedType);
 const normalizedCount=Math.max(0,Math.min(cap,Math.floor(Number(count)||0)));
 if(normalizedCount<=0){
  try{return new ItemStack(COOKERY_EMPTY_ID,1)}catch{return undefined}
 }

 let out;
 try{
  out=template?.typeId===COOKERY_FILLED_ID?template.clone():new ItemStack(COOKERY_FILLED_ID,1);
  out.amount=1;
 }catch{return undefined}

 try{
  out.setDynamicProperty(HOST_COUNT_KEY,normalizedCount);
  out.setDynamicProperty(GRILLING_TYPE_KEY,normalizedType||undefined);
  out.setLore(['§7Oil: '+normalizedCount+'/'+cap]);
 }catch{}
 return out;
}

export function planCookeryOilPotConsumption(stack,needed,requiredType=''){
 const state=readCookeryOilPot(stack);
 const plan=planOilConsumption(state,needed,requiredType);
 if(!plan.ok)return plan;

 let before;
 try{before=stack.clone()}catch{return {ok:false,reason:'stack_error',type:plan.type,count:plan.count}}
 const next=buildCookeryOilPot(plan.type,plan.remaining,stack);
 if(!next)return {ok:false,reason:'stack_error',type:plan.type,count:plan.count};
 return {...plan,before,next};
}
