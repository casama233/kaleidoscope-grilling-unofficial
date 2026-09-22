import {world} from '@minecraft/server';
import {
 ADVANCED_RACK_BLOCK_ID,RACK_COMPARTMENTS,normalizeRackFilters,rackDisplayLevel
} from './a2746_advanced_rack_core.js';

function enc(n){return n<0?'m'+Math.abs(n):'p'+n}
export function rackFiltersKey(block){
 return 'kaleidoscope_grilling:rack_filters_'+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z);
}
export function rackContainer(block){
 if(!block||block.typeId!==ADVANCED_RACK_BLOCK_ID)return undefined;
 try{return block.getComponent('minecraft:inventory')?.container}catch{return undefined}
}
export function readRackFilters(block){
 try{
  const raw=world.getDynamicProperty(rackFiltersKey(block));
  return normalizeRackFilters(typeof raw==='string'?JSON.parse(raw):[]);
 }catch{return normalizeRackFilters([])}
}
export function writeRackFilters(block,filters){
 try{world.setDynamicProperty(rackFiltersKey(block),JSON.stringify(normalizeRackFilters(filters)));return true}catch{return false}
}
export function clearRackFilters(block){
 try{world.setDynamicProperty(rackFiltersKey(block),undefined);return true}catch{return false}
}
export function readRackItems(block){
 const c=rackContainer(block),out=Array(RACK_COMPARTMENTS).fill(undefined);
 if(!c)return out;
 for(let i=0;i<RACK_COMPARTMENTS;i++)try{out[i]=c.getItem(i)?.clone()}catch{}
 return out;
}
export function writeRackItems(block,items){
 const c=rackContainer(block);if(!c)return false;
 for(let i=0;i<RACK_COMPARTMENTS;i++)try{c.setItem(i,items?.[i]?.clone())}catch{}
 syncRackDisplay(block);return true;
}
export function clearRackItems(block){
 const c=rackContainer(block);if(!c)return false;
 for(let i=0;i<RACK_COMPARTMENTS;i++)try{c.setItem(i,undefined)}catch{}
 syncRackDisplay(block);return true;
}
export function syncRackDisplay(block){
 if(!block||block.typeId!==ADVANCED_RACK_BLOCK_ID)return 0;
 const items=readRackItems(block),level=rackDisplayLevel(items.map(Boolean));
 try{
  const p=block.permutation;
  if(p.getState('kaleidoscope_grilling:spice_level')!==level)
   block.setPermutation(p.withState('kaleidoscope_grilling:spice_level',level));
 }catch{}
 return level;
}
