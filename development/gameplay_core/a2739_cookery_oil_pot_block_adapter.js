import {world} from '@minecraft/server';
import {normalizeOilType,oilCapacity} from './a2738_oil_contract_core.js';
import {
 HOST_BLOCK_ID,hostBlockCountKey,typedOilBlockKey,normalizePlacedOilCount
} from './a2736_typed_oil_pot_block_core.js';

export function placedOilPotLocation(block){
 return {x:block.x,y:block.y,z:block.z};
}

function typeKeyAt(d,l){return typedOilBlockKey(d.id,l.x,l.y,l.z)}
function countKeyAt(d,l){return hostBlockCountKey(d.id,l.x,l.y,l.z)}

export function readPlacedOilPotState(block){
 if(!block||block.typeId!==HOST_BLOCK_ID)return undefined;
 const d=block.dimension,l=placedOilPotLocation(block);
 let type='';let count=0;
 try{type=normalizeOilType(world.getDynamicProperty(typeKeyAt(d,l)))}catch{}
 try{count=normalizePlacedOilCount(type,world.getDynamicProperty(countKeyAt(d,l))??0)}catch{}
 const capacity=oilCapacity(type);
 return {type,count,capacity,remaining:Math.max(0,capacity-count)};
}

export function writePlacedOilPotState(block,type,count){
 if(!block||block.typeId!==HOST_BLOCK_ID)return false;
 const d=block.dimension,l=placedOilPotLocation(block);
 const normalizedType=normalizeOilType(type);
 const next=normalizePlacedOilCount(normalizedType,count);
 try{
  world.setDynamicProperty(typeKeyAt(d,l),normalizedType||undefined);
  world.setDynamicProperty(countKeyAt(d,l),next>0?next:undefined);
 }catch{return false}
 try{block.setPermutation(block.permutation.withState('kaleidoscope_cookery:has_oil',next>0))}catch{}
 return true;
}

export function clearPlacedOilPotState(block){
 if(!block||block.typeId!==HOST_BLOCK_ID)return false;
 const d=block.dimension,l=placedOilPotLocation(block);
 try{
  world.setDynamicProperty(typeKeyAt(d,l),undefined);
  world.setDynamicProperty(countKeyAt(d,l),undefined);
 }catch{return false}
 return true;
}
