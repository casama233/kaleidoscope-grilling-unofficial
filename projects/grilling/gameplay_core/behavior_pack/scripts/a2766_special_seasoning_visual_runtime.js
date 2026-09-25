import {ItemStack} from '@minecraft/server';
import {SEASONING_USES_KEY,SEASONING_VARIANT_KEY} from './a2743_seasoning_contract_core.js';
import {isSpecialSeasoningId,specialSeasoningVisualId,SPECIAL_SEASONING_VARIANT_MAX} from './a2766_special_seasoning_visual_core.js';

function bounded(value,max){
 const n=Number(value);
 return Math.max(0,Math.min(max,Number.isFinite(n)?Math.trunc(n):0));
}

export function specialSeasoningVariant(stack){
 try{return bounded(stack?.getDynamicProperty(SEASONING_VARIANT_KEY)??0,SPECIAL_SEASONING_VARIANT_MAX)}catch{return 0}
}

function copyMetadata(from,to){
 if(typeof from.nameTag==='string')to.nameTag=from.nameTag;
 const lore=typeof from.getRawLore==='function'?from.getRawLore():from.getLore();
 to.setLore(lore);
 if(typeof from.keepOnDeath==='boolean')to.keepOnDeath=from.keepOnDeath;
 if(from.lockMode!==undefined)to.lockMode=from.lockMode;
 to.setCanDestroy(from.getCanDestroy());
 to.setCanPlaceOn(from.getCanPlaceOn());
 // Never swallow a property failure and return a bottle with lost ingredients.
 for(const id of from.getDynamicPropertyIds())to.setDynamicProperty(id,from.getDynamicProperty(id));
 return to;
}

export function retargetSpecialSeasoningStack(stack,uses,variant=specialSeasoningVariant(stack)){
 if(!stack||stack.amount!==1||!isSpecialSeasoningId(stack.typeId))return undefined;
 try{
  const used=bounded(uses,16),v=bounded(variant,SPECIAL_SEASONING_VARIANT_MAX);
  const id=specialSeasoningVisualId(used,v);
  const out=id===stack.typeId?stack.clone():copyMetadata(stack,new ItemStack(id,1));
  out.setDynamicProperty(SEASONING_USES_KEY,used);
  out.setDynamicProperty(SEASONING_VARIANT_KEY,v);
  return out;
 }catch{return undefined}
}
