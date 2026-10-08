import {world,EquipmentSlot,GameMode} from '@minecraft/server';
import {commitSteps} from './a277_grill_transaction_core.js';
import {bonemealAgeIncrease} from './a2714_houttuynia_crop_core.js';

const BONE_MEAL='minecraft:bone_meal',OIL_RESIDUE='kaleidoscope_grilling:oil_residue';
const handlers=new Map();
const faulted=new Set();
function blockKey(block){
 const p=block.location;
 return block.dimension.id+'|'+p.x+'|'+p.y+'|'+p.z;
}
function faultKey(block){return 'kaleidoscope_grilling:plant_transaction_fault_'+encodeURIComponent(blockKey(block));}
export function plantMutationAllowed(block){
 const key=faultKey(block);
 return !faulted.has(key)&&world.getDynamicProperty(key)===undefined;
}
export function commitPlantSteps(block,steps){
 if(!plantMutationAllowed(block))return false;
 const result=commitSteps(steps);
 if(result.rollbackErrors){
  const key=faultKey(block);faulted.add(key);
  try{world.setDynamicProperty(key,true)}catch{}
  console.warn('[Grilling plant] transaction requires recovery at '+blockKey(block));
 }
 return result.ok;
}
export function samePlantPermutation(a,b){
 if(a.type.id!==b.type.id)return false;
 const actual=a.getAllStates(),expected=b.getAllStates();
 return Object.keys(actual).length===Object.keys(expected).length&&Object.keys(expected).every(key=>actual[key]===expected[key]);
}
function writePermutation(block,permutation){
 block.setPermutation(permutation);
 return samePlantPermutation(block.permutation,permutation);
}
function growthJournal(){
 const writes=new Map();
 return {
  read(block){return writes.get(blockKey(block))?.after??block.permutation;},
  set(block,after){
   const key=blockKey(block),entry=writes.get(key);
   if(entry)entry.after=after;
   else writes.set(key,{block,before:block.permutation,after});
  },
  steps(){return [...writes.values()].map(({block,before,after})=>({
   apply:()=>writePermutation(block,after),rollback:()=>writePermutation(block,before)
  }));}
 };
}
export function registerPlantFertilizer(id,handler){
 if(handlers.has(id))throw Error('Duplicate plant fertilizer handler: '+id);
 handlers.set(id,handler);
}
export function hasPlantFertilizer(block){return !!block&&handlers.has(block.typeId);}
function fertilizerSlot(player,hand){
 const eq=player.getComponent('minecraft:equippable');
 const choices=hand?[hand==='off'?EquipmentSlot.Offhand:EquipmentSlot.Mainhand]:[EquipmentSlot.Mainhand,EquipmentSlot.Offhand];
 for(const choice of choices){
  const slot=eq?.getEquipmentSlot(choice),stack=slot?.hasItem()?slot.getItem():undefined;
  if(stack?.typeId===BONE_MEAL||stack?.typeId===OIL_RESIDUE)return {slot,stack:stack.clone()};
 }
 return undefined;
}
function sameStack(actual,expected){
 if(!actual||!expected)return actual===undefined&&expected===undefined;
 return actual.amount===expected.amount&&actual.typeId===expected.typeId&&actual.isStackableWith(expected);
}
function writeSlot(slot,stack){
 slot.setItem(stack?.clone());
 return sameStack(slot.hasItem()?slot.getItem():undefined,stack);
}

// Each pass calls the same plant handler as ordinary bone meal. Planning both
// passes before mutation preserves plant-specific stages, RNG and tree writes.
// An accepted sapling use consumes fertilizer even when its growth RNG misses,
// just as BoneMealItem.useOn does; an invalid/mature target does not consume it.
export function usePlantFertilizer(block,player,hand){
 try{
  if(!hasPlantFertilizer(block)||!plantMutationAllowed(block))return false;
  const entry=fertilizerSlot(player,hand);if(!entry)return false;
  const journal=growthJournal(),passes=entry.stack.typeId===OIL_RESIDUE?2:1;
  let accepted=false;
  for(let pass=0;pass<passes;pass++){
   const handler=handlers.get(journal.read(block).type.id);
   if(handler?.(block,journal,Math.random))accepted=true;
  }
  if(!accepted)return false;
  const steps=[];
  if(player.getGameMode()!==GameMode.Creative){
   const before=entry.stack,after=before.amount>1?before.clone():undefined;
   if(after)after.amount--;
   steps.push({apply:()=>writeSlot(entry.slot,after),rollback:()=>writeSlot(entry.slot,before)});
  }
  steps.push(...journal.steps());
  if(!commitPlantSteps(block,steps))return false;
  try{const p=block.location;block.dimension.spawnParticle('minecraft:crop_growth_emitter',{x:p.x+.5,y:p.y+.5,z:p.z+.5})}catch{}
  return true;
 }catch{return false}
}
export function interactWithPlantFertilizer(event){
 if(event.player)usePlantFertilizer(event.block,event.player);
}

// Stable Script API has no generic native bone-meal invocation. These explicit
// vanilla CropBlock adapters retain the Java 2..5 increase. Other vanilla
// bonemealable blocks require their own handler, never a guessed age mutation.
for(const id of ['minecraft:wheat','minecraft:carrots','minecraft:potatoes'])registerPlantFertilizer(id,(block,journal,random)=>{
 const permutation=journal.read(block),age=permutation.getState('growth');
 if(typeof age!=='number'||age>=7)return false;
 journal.set(block,permutation.withState('growth',Math.min(7,age+bonemealAgeIncrease(random()))));
 return true;
});
