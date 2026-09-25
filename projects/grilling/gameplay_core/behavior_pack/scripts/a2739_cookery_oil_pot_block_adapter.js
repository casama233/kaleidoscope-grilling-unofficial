import {markPlacedVisualDirty} from './a2770_placed_visual_queue.js';
import {world} from '@minecraft/server';
import {normalizeOilType,oilCapacity} from './a2738_oil_contract_core.js';
import {
 HOST_BLOCK_ID,hostBlockCountKey,typedOilBlockKey,normalizePlacedOilCount
} from './a2736_typed_oil_pot_block_core.js';

export function placedOilPotLocation(block){return {x:block.x,y:block.y,z:block.z}}
function typeKeyAt(d,l){return typedOilBlockKey(d.id,l.x,l.y,l.z)}
function countKeyAt(d,l){return hostBlockCountKey(d.id,l.x,l.y,l.z)}
function states(permutation){
 const raw=permutation.getAllStates();
 return JSON.stringify(Object.keys(raw).sort().map(key=>[key,raw[key]]));
}
export function capturePlacedOilPotSnapshot(block){
 try{
  if(!block||block.typeId!==HOST_BLOCK_ID)return undefined;
  const d=block.dimension,l=placedOilPotLocation(block),permutation=block.permutation;
  const typeKey=typeKeyAt(d,l),countKey=countKeyAt(d,l);
  return {dimension:d,dimensionId:d.id,location:l,typeKey,countKey,permutation,
   permutationKey:states(permutation),rawType:world.getDynamicProperty(typeKey),
   rawCount:world.getDynamicProperty(countKey)};
 }catch{return undefined}
}
export function placedOilPotSnapshotMatches(block,snapshot){
 if(!snapshot)return false;
 const live=capturePlacedOilPotSnapshot(block);
 return !!live&&live.typeKey===snapshot.typeKey&&live.countKey===snapshot.countKey&&
  live.rawType===snapshot.rawType&&live.rawCount===snapshot.rawCount&&
  live.permutationKey===snapshot.permutationKey;
}
export function restorePlacedOilPotSnapshot(block,snapshot){
 if(!snapshot)return false;
 let ok=true;
 // Each field is restored separately: one failed write must not skip the other fields.
 try{const live=snapshot.dimension.getBlock(snapshot.location);if(!live)throw new Error('block unavailable');live.setPermutation(snapshot.permutation)}catch{ok=false}
 try{world.setDynamicProperty(snapshot.typeKey,snapshot.rawType)}catch{ok=false}
 try{world.setDynamicProperty(snapshot.countKey,snapshot.rawCount)}catch{ok=false}
 if(!ok)console.warn('[Grilling A2.7.69] Oil-pot rollback incomplete at '+snapshot.countKey);
 markPlacedVisualDirty(block);return ok;
}
export function readPlacedOilPotState(block){
 const snapshot=capturePlacedOilPotSnapshot(block);if(!snapshot)return undefined;
 const type=normalizeOilType(snapshot.rawType);
 const count=normalizePlacedOilCount(type,snapshot.rawCount??0),capacity=oilCapacity(type);
 return {type,count,capacity,remaining:Math.max(0,capacity-count)};
}
export function writePlacedOilPotState(block,type,count){
 const snapshot=capturePlacedOilPotSnapshot(block);if(!snapshot)return false;
 const normalizedType=normalizeOilType(type),next=normalizePlacedOilCount(normalizedType,count);
 try{
  const permutation=block.permutation.withState('kaleidoscope_cookery:has_oil',next>0);
  world.setDynamicProperty(snapshot.typeKey,normalizedType||undefined);
  world.setDynamicProperty(snapshot.countKey,next>0?next:undefined);
  block.setPermutation(permutation);
  const result=readPlacedOilPotState(block);
  if(!result||result.type!==normalizedType||result.count!==next||block.permutation.getState('kaleidoscope_cookery:has_oil')!==(next>0))throw new Error('state readback differs');
  markPlacedVisualDirty(block);return true;
 }catch{
  restorePlacedOilPotSnapshot(block,snapshot);return false;
 }
}
export function clearPlacedOilPotState(block){return writePlacedOilPotState(block,'',0)}
