import {advancementPropertyKey} from './a2753_advancement_core.js';

export const FIREWORKS_FEAST=Object.freeze({
 id:'fireworks_feast',
 parent:'eat_it_hot',
 propertyKey:advancementPropertyKey('fireworks_feast'),
 titleKey:'advancement.kaleidoscope_grilling.fireworks_feast.title',
 descriptionKey:'advancement.kaleidoscope_grilling.fireworks_feast.description',
 frame:'challenge',
 xp:100,
 announce:true,
 showToast:true,
 hidden:false
});

export const FIREWORKS_FEAST_PROGRESS_KEY='kaleidoscope_grilling:advancement_foods';

export const FIREWORKS_FEAST_FOODS=Object.freeze([
 'kaleidoscope_grilling:grilled_beef_skewer',
 'kaleidoscope_grilling:grilled_pork_belly_skewer',
 'kaleidoscope_grilling:grilled_chicken_skin_skewer',
 'kaleidoscope_grilling:grilled_mid_wing_skewer',
 'kaleidoscope_grilling:grilled_squid_tentacle_skewer',
 'kaleidoscope_grilling:grilled_fish_skewer',
 'kaleidoscope_grilling:grilled_sweet_potato_sheet_skewer',
 'kaleidoscope_grilling:grilled_potato_slice_skewer',
 'kaleidoscope_grilling:grilled_caterpillar_skewer',
 'kaleidoscope_grilling:grilled_mushroom_skewer',
 'kaleidoscope_grilling:grilled_bun_slice_skewer',
 'kaleidoscope_grilling:grilled_ender_pearl_skewer',
 'kaleidoscope_grilling:grilled_meatball_skewer',
 'kaleidoscope_grilling:grilled_slime_skewer',
 'kaleidoscope_grilling:grilled_meat_and_bone_skewer',
 'kaleidoscope_grilling:grilled_fried_egg_skewer',
 'kaleidoscope_grilling:grilled_lamb_skewer',
 'kaleidoscope_grilling:grilled_gluten_skewer',
 'kaleidoscope_grilling:grilled_golden_skewer',
 'kaleidoscope_grilling:ordinary_skewer',
 'kaleidoscope_grilling:cold_houttuynia',
 'kaleidoscope_grilling:sugared_tomato',
 'kaleidoscope_grilling:pepper_honey',
 'kaleidoscope_grilling:houttuynia_stir_fried_pork',
 'kaleidoscope_grilling:green_pepper_squid_tentacles',
 'kaleidoscope_grilling:braised_chicken_wings',
 'kaleidoscope_grilling:potato_beef_stew',
 'kaleidoscope_grilling:red_sweet_potato_porridge',
 'kaleidoscope_grilling:sour_spicy_noodles'
]);

const REQUIRED=new Set(FIREWORKS_FEAST_FOODS);

function cleanId(value){
 const s=String(value??'').trim();
 if(!s)return '';
 return s.includes(':')?s:'kaleidoscope_grilling:'+s;
}

export function normalizeFireworksFeastProgress(value){
 let rows=[];
 if(Array.isArray(value))rows=value;
 else if(typeof value==='string'&&value){
  try{const parsed=JSON.parse(value);rows=Array.isArray(parsed)?parsed:value.split(',')}
  catch{rows=value.split(',')}
 }
 const seen=new Set(),out=[];
 for(const row of rows){
  const id=cleanId(row);
  if(REQUIRED.has(id)&&!seen.has(id)){seen.add(id);out.push(id)}
 }
 return out;
}

export function nextFireworksFeastProgress(previous,itemId){
 const before=normalizeFireworksFeastProgress(previous);
 const id=cleanId(itemId);
 if(!REQUIRED.has(id))return Object.freeze({
  eligible:false,changed:false,complete:false,count:before.length,total:FIREWORKS_FEAST_FOODS.length,eaten:Object.freeze(before)
 });
 const eaten=before.slice(),seen=new Set(before),changed=!seen.has(id);
 if(changed)eaten.push(id);
 return Object.freeze({
  eligible:true,
  changed,
  complete:eaten.length===FIREWORKS_FEAST_FOODS.length,
  count:eaten.length,
  total:FIREWORKS_FEAST_FOODS.length,
  eaten:Object.freeze(eaten)
 });
}
