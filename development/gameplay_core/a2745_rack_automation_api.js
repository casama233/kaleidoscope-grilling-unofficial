import {
 ADVANCED_RACK_BLOCK_ID,RACK_COMPARTMENTS,rackCanPlace,rackCanonicalFilter,rackFilterMatches
} from './a2745_advanced_rack_core.js';
import {
 rackContainer,readRackFilters,writeRackFilters,syncRackDisplay
} from './a2745_rack_state_adapter.js';

function tags(stack){try{return stack?.getTags?.()??[]}catch{return []}}
function cloneAmount(stack,amount){const out=stack.clone();out.amount=amount;return out}

function canReturn(block,slot,stack){
 const c=rackContainer(block);if(!c||slot<0||slot>=RACK_COMPARTMENTS)return false;
 const filters=readRackFilters(block),filter=filters[slot];
 if(!rackCanPlace(slot,stack.typeId,tags(stack),filter))return false;
 const stored=c.getItem(slot);
 return !stored||(stored.isStackableWith(stack)&&stored.amount+stack.amount<=stored.maxAmount);
}

export function borrowAdvancedRackItem(dimension,location,predicate=()=>true,simulate=false){
 const block=dimension?.getBlock?.(location);
 if(!block||block.typeId!==ADVANCED_RACK_BLOCK_ID)return {stack:undefined,receipt:undefined,success:false};
 const c=rackContainer(block);if(!c)return {stack:undefined,receipt:undefined,success:false};
 for(let slot=0;slot<RACK_COMPARTMENTS;slot++){
  const stored=c.getItem(slot);
  if(!stored||!predicate(stored))continue;
  const borrowed=cloneAmount(stored,1);
  if(!simulate){
   if(stored.amount<=1)c.setItem(slot,undefined);
   else{const next=stored.clone();next.amount=stored.amount-1;c.setItem(slot,next)}
   syncRackDisplay(block);
  }
  return {
   stack:borrowed,
   receipt:{dimension:block.dimension.id,x:block.x,y:block.y,z:block.z,slot},
   success:true
  };
 }
 return {stack:undefined,receipt:undefined,success:false};
}

export function returnAdvancedRackItem(dimension,receipt,returned,simulate=false){
 if(!receipt||!returned||dimension?.id!==receipt.dimension)return {success:false,remainder:returned?.clone?.()};
 const block=dimension.getBlock({x:receipt.x,y:receipt.y,z:receipt.z});
 if(!block||block.typeId!==ADVANCED_RACK_BLOCK_ID)return {success:false,remainder:returned.clone()};
 const preferred=Math.floor(Number(receipt.slot));
 const slots=[preferred,...Array.from({length:RACK_COMPARTMENTS},(_,i)=>i).filter(i=>i!==preferred)];
 for(const slot of slots){
  if(!canReturn(block,slot,returned))continue;
  if(!simulate){
   const c=rackContainer(block),stored=c.getItem(slot),filters=readRackFilters(block);
   if(!filters[slot]){filters[slot]=rackCanonicalFilter(returned.typeId,tags(returned));writeRackFilters(block,filters)}
   if(!stored)c.setItem(slot,returned.clone());
   else{const next=stored.clone();next.amount=stored.amount+returned.amount;c.setItem(slot,next)}
   syncRackDisplay(block);
  }
  return {success:true,remainder:undefined};
 }
 return {success:false,remainder:returned.clone()};
}
