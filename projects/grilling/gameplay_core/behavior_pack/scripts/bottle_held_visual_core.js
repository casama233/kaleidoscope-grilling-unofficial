import {SEASONING_CAPACITY,SEASONING_KINDS,PENDING_SEASONING_ID,normalizeSeasoningList} from './a2743_seasoning_contract_core.js';

// Shared palette order for the held renderer and its generated color atlas.
export const BOTTLE_HELD_INGREDIENT_IDS=Object.freeze(Object.keys(SEASONING_KINDS).sort());
export const BOTTLE_HELD_INGREDIENT_INDEX=Object.freeze(Object.fromEntries(BOTTLE_HELD_INGREDIENT_IDS.map((id,index)=>[id,index+1])));
export const BOTTLE_HELD_FALLBACK_INDEX=9;

export function isBottleHeldVisualItem(typeId){
 return typeId==='kaleidoscope_grilling:empty_seasoning_bottle'||typeId===PENDING_SEASONING_ID;
}

export function bottleHeldVisualPlan(typeId,ingredients=[]){
 const values=isBottleHeldVisualItem(typeId)?normalizeSeasoningList(ingredients):[];
 return Array.from({length:SEASONING_CAPACITY},(_,index)=>{
  if(index>=values.length)return 0;
  const id=values[index];
  return Object.hasOwn(BOTTLE_HELD_INGREDIENT_INDEX,id)?BOTTLE_HELD_INGREDIENT_INDEX[id]:BOTTLE_HELD_FALLBACK_INDEX;
 });
}
