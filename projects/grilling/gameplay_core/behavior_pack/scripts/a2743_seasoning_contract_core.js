export const SEASONING_CAPACITY=8;
export const SEASONING_MAX_BOTTLES=4;
export const SEASONING_MAX_USES=16;
export const SEASONING_VARIANT_MAX=7;

export const PENDING_SEASONING_ID='kaleidoscope_grilling:pending_seasoning';
export const SEASONING_PLACE_BLOCK_ID='kaleidoscope_grilling:seasoning_bottle_1';
export const SEASONING_BLOCK_IDS=Object.freeze([
 'kaleidoscope_grilling:seasoning_bottle',
 'kaleidoscope_grilling:seasoning_bottle_1',
 'kaleidoscope_grilling:seasoning_bottle_2',
 'kaleidoscope_grilling:seasoning_bottle_3',
 'kaleidoscope_grilling:seasoning_bottle_4'
]);

export const SEASONING_LIST_KEY='kaleidoscope_grilling:seasonings';
export const SEASONING_USES_KEY='kaleidoscope_grilling:uses';
export const SEASONING_VARIANT_KEY='kaleidoscope_grilling:variant';

export const BASE_SEASONINGS=Object.freeze([
 'kaleidoscope_grilling:green_chili_powder',
 'kaleidoscope_grilling:sichuan_pepper',
 'kaleidoscope_grilling:onion_powder'
]);

export const SEASONING_KINDS=Object.freeze({
 'minecraft:redstone':'speed',
 'minecraft:gunpowder':'strength',
 'kaleidoscope_grilling:houttuynia_powder':'duration',
 'kaleidoscope_grilling:totem_powder':'totem',
 'kaleidoscope_grilling:dragon_egg_powder':'vitality',
 'kaleidoscope_grilling:sichuan_pepper':'numbness',
 'kaleidoscope_grilling:green_chili_powder':'base',
 'kaleidoscope_grilling:onion_powder':'base'
});

const BLOCK_IDS=new Set(SEASONING_BLOCK_IDS);
const EFFECT_ORDER=Object.freeze(['speed','strength','duration','totem','vitality']);

export function isSeasoningBlockId(id){return BLOCK_IDS.has(String(id??''))}

export function normalizeSeasoningList(values){
 if(!Array.isArray(values))return [];
 return values.filter(x=>typeof x==='string').slice(0,SEASONING_CAPACITY);
}

export function hasSeasoningBase(values){
 const list=normalizeSeasoningList(values);
 return BASE_SEASONINGS.every(x=>list.includes(x));
}

export function normalizeBottleData(row={}){
 const kind=['empty','pending','special'].includes(row?.kind)?row.kind:'empty';
 return {
  kind,
  ingredients:normalizeSeasoningList(row?.ingredients),
  uses:Math.max(0,Math.min(SEASONING_MAX_USES,Number(row?.uses)||0))|0,
  variant:Math.max(0,Math.min(SEASONING_VARIANT_MAX,Number(row?.variant)||0))|0
 };
}

export function normalizeBottleStack(rows){
 if(!Array.isArray(rows))return [];
 return rows.slice(0,SEASONING_MAX_BOTTLES).map(normalizeBottleData);
}

export function remainingSeasoningUses(row={}){
 const data=normalizeBottleData(row);
 return data.kind==='special'?Math.max(0,SEASONING_MAX_USES-data.uses):0;
}

export function seasoningEffectCounts(values){
 const out={speed:0,strength:0,duration:0,totem:0,vitality:0,numbness:0};
 for(const id of normalizeSeasoningList(values)){
  const kind=SEASONING_KINDS[id];
  if(Object.hasOwn(out,kind))out[kind]++;
 }
 return out;
}

export function seasoningEffectRows(values){
 const counts=seasoningEffectCounts(values),rows=[];
 for(const kind of EFFECT_ORDER)if(counts[kind]>0)rows.push({kind,count:counts[kind],active:true});
 if(counts.numbness>0)rows.push({kind:'numbness',count:counts.numbness,active:counts.numbness>=4});
 return rows;
}
