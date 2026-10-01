import {world} from '@minecraft/server';
import {stationContainer} from './family_station_storage.js';
import {
 ADVANCED_RACK_BLOCK_ID,RACK_COMPARTMENTS,normalizeRackFilters,rackDisplayLevel
} from './a2746_advanced_rack_core.js';

function enc(n){return n<0?'m'+Math.abs(n):'p'+n}
export function rackFiltersKey(block){
 return 'kaleidoscope_grilling:rack_filters_'+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z);
}
export function rackContainer(block){
 if(!block||block.typeId!==ADVANCED_RACK_BLOCK_ID)return undefined;
 return stationContainer(block);
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
 if(!c)throw new Error('Rack inventory unavailable; not an empty rack');
 for(let i=0;i<RACK_COMPARTMENTS;i++)out[i]=c.getItem(i)?.clone();
 return out;
}
export function writeRackItems(block,items){
 const c=rackContainer(block);if(!c)return false;
 const old=Array.from({length:RACK_COMPARTMENTS},(_,i)=>c.getItem(i)?.clone());
 const next=Array.from({length:RACK_COMPARTMENTS},(_,i)=>items?.[i]?.clone());
 try{for(let i=0;i<RACK_COMPARTMENTS;i++)c.setItem(i,next[i]);}
 catch(error){
  let restored=true;for(let i=0;i<RACK_COMPARTMENTS;i++)try{c.setItem(i,old[i])}catch{restored=false}
  if(!restored)throw new Error('Rack inventory rollback failed; manual recovery required');
  return false;
 }
 syncRackDisplay(block);return true;
}
export function clearRackItems(block){return writeRackItems(block,[]);}
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
