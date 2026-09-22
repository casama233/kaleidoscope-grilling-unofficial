import {advancementPropertyKey} from './a2753_advancement_core.js';
import {LOOKING_THE_PART} from './a2756_advancement_event_core.js';

function spec(id,parent,frame,xp){
 return Object.freeze({
  id,parent,
  propertyKey:advancementPropertyKey(id),
  titleKey:'advancement.kaleidoscope_grilling.'+id+'.title',
  descriptionKey:'advancement.kaleidoscope_grilling.'+id+'.description',
  frame,xp,announce:true,showToast:true,hidden:false
 });
}

export const HUMAN_FIREWORKS=spec('human_fireworks','', 'task',10);
export const BETTER_WRITE_IT_DOWN=spec('better_write_it_down','looking_the_part','task',10);
export const A_HANDFUL_OF_CANOLA=spec('a_handful_of_canola','human_fireworks','task',10);
export const STRENGTH_MAKES_OIL=spec('strength_makes_oil','a_handful_of_canola','goal',25);
export const SWEET_POTATO=spec('sweet_potato','human_fireworks','task',10);
export const NETHER_TASTE=spec('nether_taste','human_fireworks','goal',25);

export const INVENTORY_ADVANCEMENTS=Object.freeze({
 human_fireworks:HUMAN_FIREWORKS,
 looking_the_part:LOOKING_THE_PART,
 better_write_it_down:BETTER_WRITE_IT_DOWN,
 a_handful_of_canola:A_HANDFUL_OF_CANOLA,
 strength_makes_oil:STRENGTH_MAKES_OIL,
 sweet_potato:SWEET_POTATO,
 nether_taste:NETHER_TASTE
});

export function inventoryAdvancementIds(itemIds=[],rawSkewerIds=[],dimensionId=''){
 const items=new Set((Array.isArray(itemIds)?itemIds:[]).map(String));
 const raw=new Set((Array.isArray(rawSkewerIds)?rawSkewerIds:[]).map(String));
 const out=[];
 if(items.has('kaleidoscope_grilling:grill'))out.push('human_fireworks');
 if([...raw].some(id=>items.has(id)))out.push('looking_the_part');
 if(items.has('kaleidoscope_grilling:skewer_recipe_book'))out.push('better_write_it_down');
 if(items.has('kaleidoscope_grilling:canola_seeds'))out.push('a_handful_of_canola');
 if(items.has('kaleidoscope_grilling:oil_residue'))out.push('strength_makes_oil');
 if(items.has('kaleidoscope_grilling:sweet_potato'))out.push('sweet_potato');
 if(String(dimensionId)==='minecraft:nether'&&items.has('kaleidoscope_grilling:houttuynia'))out.push('nether_taste');
 return out;
}
