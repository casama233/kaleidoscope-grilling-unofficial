export const SKEWER_RECIPES=Object.freeze([
 {result:'kaleidoscope_grilling:raw_beef_skewer',slots:[['kaleidoscope_grilling:beef_chunks'],['kaleidoscope_cookery:red_chili'],['kaleidoscope_grilling:beef_chunks']]},
 {result:'kaleidoscope_grilling:raw_pork_belly_skewer',slots:[['kaleidoscope_cookery:raw_pork_belly'],['kaleidoscope_cookery:green_chili'],['kaleidoscope_cookery:raw_pork_belly']]},
 {result:'kaleidoscope_grilling:raw_chicken_skin_skewer',slots:[['kaleidoscope_grilling:chicken_skin'],['kaleidoscope_grilling:chicken_skin']]},
 {result:'kaleidoscope_grilling:raw_mid_wing_skewer',slots:[['kaleidoscope_grilling:chicken_wing'],['kaleidoscope_cookery:red_chili'],['kaleidoscope_grilling:chicken_wing']]},
 {result:'kaleidoscope_grilling:raw_squid_tentacle_skewer',slots:[['kaleidoscope_grilling:squid_tentacle'],['kaleidoscope_grilling:squid_tentacle'],['kaleidoscope_grilling:squid_tentacle']]},
 {result:'kaleidoscope_grilling:raw_fish_skewer',slots:[['minecraft:cod','minecraft:salmon','minecraft:tropical_fish','minecraft:pufferfish']]},
 {result:'kaleidoscope_grilling:raw_sweet_potato_sheet_skewer',slots:[['kaleidoscope_grilling:raw_sweet_potato_sheet'],['kaleidoscope_grilling:minced_houttuynia'],['kaleidoscope_grilling:minced_houttuynia']]},
 {result:'kaleidoscope_grilling:raw_potato_slice_skewer',slots:[['kaleidoscope_grilling:potato_slice'],['kaleidoscope_grilling:potato_slice'],['kaleidoscope_grilling:potato_slice']]},
 {result:'kaleidoscope_grilling:raw_caterpillar_skewer',slots:[['kaleidoscope_cookery:caterpillar']]},
 {result:'kaleidoscope_grilling:raw_mushroom_skewer',slots:[['minecraft:brown_mushroom','minecraft:red_mushroom'],['kaleidoscope_grilling:carrot_dice'],['minecraft:brown_mushroom','minecraft:red_mushroom']]},
 {result:'kaleidoscope_grilling:raw_bun_slice_skewer',slots:[['kaleidoscope_grilling:raw_mantou_slice'],['kaleidoscope_grilling:raw_mantou_slice'],['kaleidoscope_grilling:raw_mantou_slice']]},
 {result:'kaleidoscope_grilling:raw_ender_pearl_skewer',slots:[['minecraft:ender_pearl'],['minecraft:beetroot'],['minecraft:ender_pearl']]},
 {result:'kaleidoscope_grilling:raw_meatball_skewer',slots:[['kaleidoscope_cookery:raw_meatball'],['kaleidoscope_cookery:raw_meatball'],['kaleidoscope_cookery:raw_meatball']]},
 {result:'kaleidoscope_grilling:raw_slime_skewer',slots:[['minecraft:slime_ball'],['kaleidoscope_grilling:houttuynia'],['minecraft:slime_ball']]},
 {result:'kaleidoscope_grilling:raw_meat_and_bone_skewer',slots:[['kaleidoscope_cookery:raw_cut_small_meats'],['minecraft:bone'],['kaleidoscope_cookery:raw_cut_small_meats']]},
 {result:'kaleidoscope_grilling:raw_fried_egg_skewer',slots:[['kaleidoscope_cookery:fried_egg'],['kaleidoscope_cookery:fried_egg']]},
 {result:'kaleidoscope_grilling:raw_gluten_skewer',slots:[['kaleidoscope_cookery:raw_dough'],['kaleidoscope_cookery:raw_dough']]},
 {result:'kaleidoscope_grilling:raw_lamb_skewer',slots:[['kaleidoscope_cookery:raw_lamb_chops'],['kaleidoscope_cookery:oil'],['kaleidoscope_cookery:raw_lamb_chops']]},
 {result:'kaleidoscope_grilling:raw_golden_skewer',slots:[['minecraft:golden_apple'],['minecraft:totem_of_undying'],['minecraft:golden_carrot']]},
 {result:'kaleidoscope_grilling:ordinary_skewer',slots:[['minecraft:poisonous_potato'],['minecraft:spider_eye'],['minecraft:pufferfish']]}
]);

const CONFIGURED=new Set(SKEWER_RECIPES.flatMap(r=>r.slots.flat()));
const RAW_FIXED=new Set(SKEWER_RECIPES.map(r=>r.result).filter(x=>x!=='kaleidoscope_grilling:ordinary_skewer'));

export function prefixMatches(recipe,ids){
 return ids.length<=recipe.slots.length&&ids.every((id,i)=>recipe.slots[i]?.includes(id));
}
export function expectedSize(ids){
 const sizes=SKEWER_RECIPES.filter(r=>prefixMatches(r,ids)).map(r=>r.slots.length);
 return sizes.length?Math.max(...sizes):3;
}
export function fixedResult(ids){
 const r=SKEWER_RECIPES.find(x=>x.slots.length===ids.length&&prefixMatches(x,ids));
 return r?.result??null;
}
export function canAppend(ids,nextId,isEdible=false){
 if(ids.length>=3)return false;
 if(SKEWER_RECIPES.some(r=>prefixMatches(r,ids)&&r.slots.length>ids.length&&r.slots[ids.length].includes(nextId)))return true;
 return CONFIGURED.has(nextId)||!!isEdible;
}
export function isRawFixedId(id){return RAW_FIXED.has(id)}
export function hasDuplicateIngredients(ids){return ids.some((id,i)=>ids.indexOf(id)!==i)}
