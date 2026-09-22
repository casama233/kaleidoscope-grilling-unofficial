import {world} from '@minecraft/server';
import {
 ADVANCED_RACK_ID,RACK_COMPARTMENT_COUNT,
 normalizeRackFilters,rackCanPlaceWithFilter,rackFiltersAfterInsert,rackCanClearFilter,rackSpiceLevel
} from './a2746_advanced_rack_core.js';

const FILTER_PREFIX='kaleidoscope_grilling:a2746_rack_filters_';

function enc(n){return n<0?'m'+Math.abs(n):'p'+n}
function filterKey(block){
 return FILTER_PREFIX+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z);
}

function container(block){try{return block?.getComponent('minecraft:inventory')?.container}catch{return undefined}}

function stackDescriptor(stack){
 if(!stack)return {id:'',tags:[],damageable:false};
 let tags=[];try{tags=stack.getTags()}catch{}
 let damageable=false;try{damageable=!!stack.getComponent('minecraft:durability')}catch{}
 return {id:stack.typeId,tags,damageable};
}

export function a2746ReadRackFilters(block){
 try{
  const raw=world.getDynamicProperty(filterKey(block));
  return normalizeRackFilters(typeof raw==='string'?JSON.parse(raw):[]);
 }catch{return normalizeRackFilters([])}
}

export function a2746WriteRackFilters(block,filters){
 const clean=normalizeRackFilters(filters);
 world.setDynamicProperty(filterKey(block),JSON.stringify(clean));
 return clean;
}

export function a2746RackInventory(block){return container(block)}

export function a2746RackOccupied(block){
 const c=container(block),out=Array.from({length:RACK_COMPARTMENT_COUNT},()=>false);
 if(!c)return out;
 for(let i=0;i<RACK_COMPARTMENT_COUNT;i++)out[i]=!!c.getItem(i);
 return out;
}

export function a2746RackCanPlace(block,slot,stack){
 const filters=a2746ReadRackFilters(block);
 return rackCanPlaceWithFilter(slot,filters[slot],stackDescriptor(stack));
}

export function a2746RackSetItem(block,slot,stack){
 if(!block||block.typeId!==ADVANCED_RACK_ID)return {ok:false,reason:'not_rack'};
 const c=container(block);if(!c)return {ok:false,reason:'no_container'};
 const n=Math.floor(Number(slot));if(n<0||n>=RACK_COMPARTMENT_COUNT)return {ok:false,reason:'slot'};
 if(stack&&!a2746RackCanPlace(block,n,stack))return {ok:false,reason:'rejected'};
 let filters=a2746ReadRackFilters(block);
 if(stack)filters=rackFiltersAfterInsert(filters,n,stackDescriptor(stack));
 c.setItem(n,stack);
 a2746WriteRackFilters(block,filters);
 a2746SyncRackDisplay(block);
 return {ok:true};
}

export function a2746RackClearFilter(block,slot){
 const occupied=a2746RackOccupied(block),filters=a2746ReadRackFilters(block);
 if(!rackCanClearFilter(filters,occupied,slot))return false;
 filters[Math.floor(Number(slot))]=null;a2746WriteRackFilters(block,filters);return true;
}

export function a2746SyncRackDisplay(block){
 if(!block||block.typeId!==ADVANCED_RACK_ID)return 0;
 const level=rackSpiceLevel(a2746RackOccupied(block));
 try{
  if(block.permutation.getState('kaleidoscope_grilling:spice_level')!==level)
   block.setPermutation(block.permutation.withState('kaleidoscope_grilling:spice_level',level));
 }catch{}
 return level;
}

export function a2746RackSnapshot(block){
 const c=container(block),filters=a2746ReadRackFilters(block),items=[];
 for(let i=0;i<RACK_COMPARTMENT_COUNT;i++){
  const stack=c?.getItem(i);
  items.push(stack?{id:stack.typeId,amount:stack.amount}:null);
 }
 return {items,filters,spiceLevel:rackSpiceLevel(items.map(Boolean))};
}
