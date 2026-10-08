import {world,EquipmentSlot,GameMode,BlockPermutation,ItemStack} from '@minecraft/server';
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
export function commitPlantSteps(block,steps,participants=[block]){
 const involved=new Map([[blockKey(block),block],...participants.map(target=>[blockKey(target),target])]);
 if([...involved.values()].some(target=>!plantMutationAllowed(target)))return false;
 const result=commitSteps(steps);
 if(result.rollbackErrors){
  // A double plant can be used through either half. An unknown item delivery
  // must also block its partner, otherwise the other half can repeat it.
  for(const target of involved.values()){
   const key=faultKey(target);faulted.add(key);
   try{world.setDynamicProperty(key,true)}catch{}
  }
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
 const observed=new Map(),deliveries=[];
 function observe(block){
  const key=blockKey(block);
  if(!observed.has(key))observed.set(key,{block,before:block.permutation});
  return observed.get(key);
 }
 return {
  read(block){const entry=observe(block);return entry.after??entry.before;},
  set(block,after){
   observe(block).after=after;
  },
  drop(block,id,random){
   const stack=new ItemStack(id,1),p=block.location;
   // Java Block.popResource: +/- .25 around the block centre, with the
   // item entity's half-height (.125) removed from the vertical position.
   const location={x:p.x+.25+random()*.5,y:p.y+.125+random()*.5,z:p.z+.25+random()*.5};
   if(!world.gameRules.doTileDrops)return;
   let entity,attempted=false,acknowledged=false;
   deliveries.push({
    apply(){
     attempted=true;entity=block.dimension.spawnItem(stack,location);
     const delivered=entity?.getComponent('minecraft:item')?.itemStack;
     acknowledged=entity?.isValid===true&&sameStack(delivered,stack);
     if(!acknowledged)throw Error('Plant fertilizer drop was not acknowledged');
    },
    rollback(){
     if(!attempted)return;
     if(!acknowledged)throw Error('Plant fertilizer drop outcome unknown');
     entity.remove();
     if(entity.isValid!==false)throw Error('Plant fertilizer drop removal was not acknowledged');
    }
   });
  },
  current(){return [...observed.values()].every(({block,before})=>samePlantPermutation(block.permutation,before));},
  blocks(){return [...observed.values()].map(entry=>entry.block);},
  steps(){return [...observed.values()].filter(entry=>entry.after).map(({block,before,after})=>({
   apply:()=>writePermutation(block,after),rollback:()=>writePermutation(block,before)
  })).concat(deliveries);}
 };
}
export function registerPlantFertilizer(id,handler){
 if(handlers.has(id))throw Error('Duplicate plant fertilizer handler: '+id);
 handlers.set(id,handler);
}
export function hasPlantFertilizer(block,itemId,hand='main',secondaryUse=false){
 if(!block||!handlers.has(block.typeId))return false;
 if(itemId===OIL_RESIDUE&&block.typeId==='minecraft:sweet_berry_bush'){
  // NeoForge 1.21.1's default block interaction picks berries on a normal
  // main-hand use. Sneaking skips that interaction; it is not invoked for an
  // offhand item use. Only the real BONE_MEAL item gets its own early bypass.
  const age=block.permutation.getState('growth');
  return Number.isInteger(age)&&age>=0&&age<=3&&(age<2||hand==='off'||secondaryUse===true);
 }
 return true;
}
function fertilizerSlot(player,hand){
 const eq=player.getComponent('minecraft:equippable');
 const choices=hand?[hand==='off'?EquipmentSlot.Offhand:EquipmentSlot.Mainhand]:[EquipmentSlot.Mainhand,EquipmentSlot.Offhand];
 for(const choice of choices){
  const slot=eq?.getEquipmentSlot(choice),stack=slot?.hasItem()?slot.getItem():undefined;
  if(stack?.typeId===BONE_MEAL||stack?.typeId===OIL_RESIDUE)return {slot,stack:stack.clone(),hand:choice===EquipmentSlot.Offhand?'off':'main'};
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
  if(!block||!plantMutationAllowed(block))return false;
  const entry=fertilizerSlot(player,hand),secondaryUse=player.isSneaking===true;
  if(!entry||!hasPlantFertilizer(block,entry.stack.typeId,entry.hand,secondaryUse))return false;
  const journal=growthJournal(),passes=entry.stack.typeId===OIL_RESIDUE?2:1;
  let accepted=false;
  for(let pass=0;pass<passes;pass++){
   const handler=handlers.get(journal.read(block).type.id);
   if(handler?.(block,journal,Math.random))accepted=true;
  }
  if(!accepted)return false;
  // Reads include unchanged partners/supports as well as written blocks.
  // Validate the complete native snapshots before the first debit or write.
  if((player.isSneaking===true)!==secondaryUse||!journal.current()||!sameStack(entry.slot.hasItem()?entry.slot.getItem():undefined,entry.stack))return false;
  const steps=[];
  if(player.getGameMode()!==GameMode.Creative){
   const before=entry.stack,after=before.amount>1?before.clone():undefined;
   if(after)after.amount--;
   steps.push({apply:()=>writeSlot(entry.slot,after),rollback:()=>writeSlot(entry.slot,before)});
  }
  steps.push(...journal.steps());
  if(!commitPlantSteps(block,steps,journal.blocks()))return false;
  try{const p=block.location;block.dimension.spawnParticle('minecraft:crop_growth_emitter',{x:p.x+.5,y:p.y+.5,z:p.z+.5})}catch{}
  return true;
 }catch{return false}
}
export function interactWithPlantFertilizer(event){
 if(event.player)usePlantFertilizer(event.block,event.player);
}

// @minecraft/server 2.9.0 has placeFeature, but no generic native bone-meal
// invocation or feature-write journal. Explicit handlers below reproduce each
// reviewed Java BonemealableBlock contract. Other plants remain unsupported.
// Source and state mapping: docs/evidence/vanilla-plant-fertilizer.md.
for(const id of ['minecraft:wheat','minecraft:carrots','minecraft:potatoes'])registerPlantFertilizer(id,(block,journal,random)=>{
 const permutation=journal.read(block),age=permutation.getState('growth');
 if(typeof age!=='number'||age>=7)return false;
 journal.set(block,permutation.withState('growth',Math.min(7,age+bonemealAgeIncrease(random()))));
 return true;
});

registerPlantFertilizer('minecraft:cocoa',(block,journal)=>{
 const permutation=journal.read(block),age=permutation.getState('age');
 if(!Number.isInteger(age)||age<0||age>=2)return false;
 journal.set(block,permutation.withState('age',age+1));
 return true;
});

registerPlantFertilizer('minecraft:sweet_berry_bush',(block,journal)=>{
 const permutation=journal.read(block),age=permutation.getState('growth');
 if(!Number.isInteger(age)||age<0||age>=3)return false;
 journal.set(block,permutation.withState('growth',age+1));
 return true;
});

registerPlantFertilizer('minecraft:pink_petals',(block,journal,random)=>{
 const permutation=journal.read(block),growth=permutation.getState('growth');
 if(!Number.isInteger(growth)||growth<0||growth>3)return false;
 if(growth<3)journal.set(block,permutation.withState('growth',growth+1));
 else journal.drop(block,'minecraft:pink_petals',random);
 return true;
});

function plantNeighbor(block,journal,dy){
 const p=block.location,target=block.dimension.getBlock({x:p.x,y:p.y+dy,z:p.z});
 // Missing/unloaded is not air and must not consume an unplanned attempt.
 if(!target)throw Error('Plant fertilizer neighbour unavailable');
 return {block:target,permutation:journal.read(target)};
}

const FERTILIZER_CAVE_VINES=new Set([
 'minecraft:cave_vines','minecraft:cave_vines_body_with_berries','minecraft:cave_vines_head_with_berries'
]);
registerPlantFertilizer('minecraft:cave_vines',(block,journal)=>{
 const permutation=journal.read(block),age=permutation.getState('growing_plant_age');
 if(!Number.isInteger(age)||age<0||age>25)return false;
 const below=plantNeighbor(block,journal,-1);
 const nextId=FERTILIZER_CAVE_VINES.has(below.permutation.type.id)
  ?'minecraft:cave_vines_body_with_berries':'minecraft:cave_vines_head_with_berries';
 journal.set(block,BlockPermutation.resolve(nextId,permutation.getAllStates()));
 // CaveVinesBlock and CaveVinesPlantBlock only set BERRIES=true. They do not
 // call the inherited vine-extension routine. A second pass sees berries and
 // cannot fertilize again; normal berry picking stays with the native block.
 return true;
});

// Java TallFlowerBlock is valid on either half and drops one matching item
// per accepted use. Keep both native halves in the same recovery boundary.
for(const id of ['minecraft:sunflower','minecraft:lilac','minecraft:rose_bush','minecraft:peony'])registerPlantFertilizer(id,(block,journal,random)=>{
 const permutation=journal.read(block),upper=permutation.getState('upper_block_bit');
 if(typeof upper!=='boolean')return false;
 const partner=plantNeighbor(block,journal,upper?-1:1).permutation;
 if(partner.type.id!==id||partner.getState('upper_block_bit')!==!upper)return false;
 journal.drop(block,id,random);
 return true;
});

// Both selected Java versions use #minecraft:dirt or farmland for BushBlock
// survival. Rooted dirt uses Bedrock's distinct dirt_with_roots ID.
const FERTILIZER_GRASS_SOILS=new Set([
 'minecraft:dirt','minecraft:grass_block','minecraft:podzol','minecraft:coarse_dirt',
 'minecraft:mycelium','minecraft:dirt_with_roots','minecraft:moss_block','minecraft:mud',
 'minecraft:muddy_mangrove_roots','minecraft:farmland'
]);
for(const [id,tall] of [['minecraft:short_grass','minecraft:tall_grass'],['minecraft:fern','minecraft:large_fern']])registerPlantFertilizer(id,(block,journal)=>{
 const below=plantNeighbor(block,journal,-1),above=plantNeighbor(block,journal,1);
 if(FERTILIZER_GRASS_SOILS.has(below.permutation.type.id)&&above.permutation.type.id==='minecraft:air'){
  journal.set(block,BlockPermutation.resolve(tall,{upper_block_bit:false}));
  journal.set(above.block,BlockPermutation.resolve(tall,{upper_block_bit:true}));
 }
 // TallGrassBlock.isValidBonemealTarget/isBonemealSuccess are true even if
 // performBonemeal finds blocked headroom. Such an accepted use still costs 1.
 return true;
});
