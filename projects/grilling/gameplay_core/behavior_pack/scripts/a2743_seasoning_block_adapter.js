import {markPlacedVisualDirty} from './a2770_placed_visual_queue.js';
import {world} from '@minecraft/server';
import {
 SEASONING_MAX_BOTTLES,hasSeasoningBase,normalizeBottleData,normalizeBottleStack
} from './a2743_seasoning_contract_core.js';

function enc(n){return n<0?'m'+Math.abs(n):'p'+n}

export function seasoningBlockKey(block){
 return 'kaleidoscope_grilling:sb_'+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z);
}

export function readPlacedSeasoningStack(block){
 try{
  const raw=world.getDynamicProperty(seasoningBlockKey(block));
  if(raw===undefined)return [];
  const value=JSON.parse(raw);
  if(!Array.isArray(value))return [];
  if(value.length&&typeof value[0]==='string'){
   const ingredients=value.filter(x=>typeof x==='string');
   return [normalizeBottleData({kind:hasSeasoningBase(ingredients)?'pending':'empty',ingredients,uses:0,variant:0})];
  }
  return normalizeBottleStack(value);
 }catch{return []}
}

export function writePlacedSeasoningStack(block,rows){
 const stack=normalizeBottleStack(rows).slice(0,SEASONING_MAX_BOTTLES);
 try{world.setDynamicProperty(seasoningBlockKey(block),stack.length?JSON.stringify(stack):undefined);markPlacedVisualDirty(block);return true}catch{return false}
}

export function topPlacedSeasoningBottle(block){
 const stack=readPlacedSeasoningStack(block);
 return stack.length?stack[stack.length-1]:undefined;
}
