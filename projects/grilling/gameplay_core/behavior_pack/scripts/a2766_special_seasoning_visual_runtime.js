import {ItemStack} from '@minecraft/server';
import {SEASONING_USES_KEY,SEASONING_VARIANT_KEY} from './a2743_seasoning_contract_core.js';
import {isSpecialSeasoningId,specialSeasoningVisualId,SPECIAL_SEASONING_VARIANT_MAX} from './a2766_special_seasoning_visual_core.js';

export function specialSeasoningVariant(stack){
 try{return Math.max(0,Math.min(SPECIAL_SEASONING_VARIANT_MAX,Number(stack?.getDynamicProperty(SEASONING_VARIANT_KEY)??0)|0))}catch{return 0}
}

function copyMetadata(from,to){
 try{if(from?.nameTag)to.nameTag=from.nameTag}catch{}
 let lore=[];try{lore=from?.getLore?.()??[]}catch{}
 let ids=[];try{ids=from?.getDynamicPropertyIds?.()??[]}catch{}
 try{if(lore.length)to.setLore(lore);else if(ids.length)to.setLore(['§r'])}catch{}
 for(const id of ids)try{to.setDynamicProperty(id,from.getDynamicProperty(id))}catch{}
 return to;
}

export function retargetSpecialSeasoningStack(stack,uses,variant=specialSeasoningVariant(stack)){
 if(!stack||!isSpecialSeasoningId(stack.typeId))return undefined;
 const id=specialSeasoningVisualId(uses,variant);
 const out=copyMetadata(stack,new ItemStack(id,1));
 try{out.setDynamicProperty(SEASONING_USES_KEY,Math.max(0,Math.min(16,Number(uses)||0))|0)}catch{}
 try{out.setDynamicProperty(SEASONING_VARIANT_KEY,Math.max(0,Math.min(SPECIAL_SEASONING_VARIANT_MAX,Number(variant)||0))|0)}catch{}
 return out;
}
