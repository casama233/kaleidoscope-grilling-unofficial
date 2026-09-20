export const UNFINISHED_ID='kaleidoscope_grilling:unfinished_skewer';
export const SECRET_ID='kaleidoscope_grilling:secret_skewer';
export const SKEWER_INGREDIENTS_KEY='kaleidoscope_grilling:skewer_ingredients';
export const SECRET_COOKED_KEY='kaleidoscope_grilling:secret_cooked';
export const SECRET_COOKED_INGREDIENTS_KEY='kaleidoscope_grilling:secret_cooked_ingredients';
export const SECRET_CREATOR_KEY='kaleidoscope_grilling:secret_creator';
export const FAT_CAPACITY=256;
export const FLUID_CAPACITY=64;
export const OIL_BUCKET_POINTS=8;

const RECIPES=Object.freeze([
 {id:'kaleidoscope_grilling:raw_beef_skewer',cooked:'kaleidoscope_grilling:grilled_beef_skewer',slots:[['kaleidoscope_grilling:beef_chunks'],['kaleidoscope_cookery:red_chili'],['kaleidoscope_grilling:beef_chunks']]},
 {id:'kaleidoscope_grilling:raw_pork_belly_skewer',cooked:'kaleidoscope_grilling:grilled_pork_belly_skewer',slots:[['kaleidoscope_cookery:raw_pork_belly'],['kaleidoscope_cookery:green_chili'],['kaleidoscope_cookery:raw_pork_belly']]},
 {id:'kaleidoscope_grilling:raw_chicken_skin_skewer',cooked:'kaleidoscope_grilling:grilled_chicken_skin_skewer',slots:[['kaleidoscope_grilling:chicken_skin'],['kaleidoscope_grilling:chicken_skin']]},
 {id:'kaleidoscope_grilling:raw_mid_wing_skewer',cooked:'kaleidoscope_grilling:grilled_mid_wing_skewer',slots:[['kaleidoscope_grilling:chicken_wing'],['kaleidoscope_cookery:red_chili'],['kaleidoscope_grilling:chicken_wing']]},
 {id:'kaleidoscope_grilling:raw_squid_tentacle_skewer',cooked:'kaleidoscope_grilling:grilled_squid_tentacle_skewer',slots:[['kaleidoscope_grilling:squid_tentacle'],['kaleidoscope_grilling:squid_tentacle'],['kaleidoscope_grilling:squid_tentacle']]},
 {id:'kaleidoscope_grilling:raw_fish_skewer',cooked:'kaleidoscope_grilling:grilled_fish_skewer',slots:[['minecraft:cod','minecraft:salmon','minecraft:tropical_fish','minecraft:pufferfish']]},
 {id:'kaleidoscope_grilling:raw_sweet_potato_sheet_skewer',cooked:'kaleidoscope_grilling:grilled_sweet_potato_sheet_skewer',slots:[['kaleidoscope_grilling:raw_sweet_potato_sheet'],['kaleidoscope_grilling:minced_houttuynia'],['kaleidoscope_grilling:minced_houttuynia']]},
 {id:'kaleidoscope_grilling:raw_potato_slice_skewer',cooked:'kaleidoscope_grilling:grilled_potato_slice_skewer',slots:[['kaleidoscope_grilling:potato_slice'],['kaleidoscope_grilling:potato_slice'],['kaleidoscope_grilling:potato_slice']]},
 {id:'kaleidoscope_grilling:raw_caterpillar_skewer',cooked:'kaleidoscope_grilling:grilled_caterpillar_skewer',slots:[['kaleidoscope_cookery:caterpillar']]},
 {id:'kaleidoscope_grilling:raw_mushroom_skewer',cooked:'kaleidoscope_grilling:grilled_mushroom_skewer',slots:[['minecraft:brown_mushroom','minecraft:red_mushroom'],['kaleidoscope_grilling:carrot_dice'],['minecraft:brown_mushroom','minecraft:red_mushroom']]},
 {id:'kaleidoscope_grilling:raw_bun_slice_skewer',cooked:'kaleidoscope_grilling:grilled_bun_slice_skewer',slots:[['kaleidoscope_grilling:raw_mantou_slice'],['kaleidoscope_grilling:raw_mantou_slice'],['kaleidoscope_grilling:raw_mantou_slice']]},
 {id:'kaleidoscope_grilling:raw_ender_pearl_skewer',cooked:'kaleidoscope_grilling:grilled_ender_pearl_skewer',slots:[['minecraft:ender_pearl'],['minecraft:beetroot'],['minecraft:ender_pearl']]},
 {id:'kaleidoscope_grilling:raw_meatball_skewer',cooked:'kaleidoscope_grilling:grilled_meatball_skewer',slots:[['kaleidoscope_cookery:raw_meatball'],['kaleidoscope_cookery:raw_meatball'],['kaleidoscope_cookery:raw_meatball']]},
 {id:'kaleidoscope_grilling:raw_slime_skewer',cooked:'kaleidoscope_grilling:grilled_slime_skewer',slots:[['minecraft:slime_ball'],['kaleidoscope_grilling:houttuynia'],['minecraft:slime_ball']]},
 {id:'kaleidoscope_grilling:raw_meat_and_bone_skewer',cooked:'kaleidoscope_grilling:grilled_meat_and_bone_skewer',slots:[['kaleidoscope_cookery:raw_cut_small_meats'],['minecraft:bone'],['kaleidoscope_cookery:raw_cut_small_meats']]},
 {id:'kaleidoscope_grilling:raw_fried_egg_skewer',cooked:'kaleidoscope_grilling:grilled_fried_egg_skewer',slots:[['kaleidoscope_cookery:fried_egg'],['kaleidoscope_cookery:fried_egg']]},
 {id:'kaleidoscope_grilling:raw_gluten_skewer',cooked:'kaleidoscope_grilling:grilled_gluten_skewer',slots:[['kaleidoscope_cookery:raw_dough'],['kaleidoscope_cookery:raw_dough']]},
 {id:'kaleidoscope_grilling:raw_lamb_skewer',cooked:'kaleidoscope_grilling:grilled_lamb_skewer',slots:[['kaleidoscope_cookery:raw_lamb_chops'],['kaleidoscope_cookery:oil'],['kaleidoscope_cookery:raw_lamb_chops']]},
 {id:'kaleidoscope_grilling:raw_golden_skewer',cooked:'kaleidoscope_grilling:grilled_golden_skewer',slots:[['minecraft:golden_apple'],['minecraft:totem_of_undying'],['minecraft:golden_carrot']]},
 {id:'kaleidoscope_grilling:ordinary_skewer',cooked:null,slots:[['minecraft:poisonous_potato'],['minecraft:spider_eye'],['minecraft:pufferfish']]}
]);

function ids(rows){return rows.map(x=>typeof x==='string'?x:x?.id).filter(x=>typeof x==='string')}
function slotMatches(id,selectors){return selectors.includes(id)}
function matches(recipe,values){return recipe.slots.length===values.length&&values.every((id,i)=>slotMatches(id,recipe.slots[i]))}
function prefix(recipe,values){return values.length<=recipe.slots.length&&values.every((id,i)=>slotMatches(id,recipe.slots[i]))}

export function recipeTable(){return RECIPES.map(r=>({id:r.id,cooked:r.cooked,slots:r.slots.map(s=>[...s])}))}
export function completedRecipe(rows){const values=ids(rows);return RECIPES.find(r=>matches(r,values))??null}
export function canAppendConfigured(rows,nextId){const values=[...ids(rows),nextId];return RECIPES.some(r=>prefix(r,values))}
export function isConfiguredIngredient(id){return RECIPES.some(r=>r.slots.some(slot=>slotMatches(id,slot)))}
export function expectedSize(rows){const values=ids(rows);return RECIPES.filter(r=>prefix(r,values)).reduce((m,r)=>Math.max(m,r.slots.length),3)}
export function appendOutcome(rows,nextId,edible=false,explicitAllow=false){
 const current=ids(rows);
 if(!nextId||current.length>=3)return {ok:false,reason:'full'};
 if(!canAppendConfigured(current,nextId)&&!isConfiguredIngredient(nextId)&&!edible&&!explicitAllow)return {ok:false,reason:'not_skewerable'};
 const values=[...current,nextId],recipe=completedRecipe(values);
 if(recipe)return {ok:true,kind:'fixed',id:recipe.id,cooked:recipe.cooked,ingredients:values};
 if(values.length>=3)return {ok:true,kind:'secret',id:SECRET_ID,ingredients:values};
 return {ok:true,kind:'unfinished',id:UNFINISHED_ID,ingredients:values};
}
export function cookedResultFor(id){return RECIPES.find(r=>r.id===id)?.cooked??null}
export function isFixedRaw(id){return RECIPES.some(r=>r.id===id&&r.cooked)}
export function isDisassemblableRaw(id,cooked=false){return id===UNFINISHED_ID||isFixedRaw(id)||(id===SECRET_ID&&!cooked)}
export function canonicalIngredients(id){
 const r=RECIPES.find(x=>x.id===id);return r?r.slots.map(slot=>slot[0]):[];
}

export function secretFood(rows,cooked=false){
 const foods=(rows??[]).map(x=>({
  id:String(x?.id??''),
  signature:String(x?.signature??x?.id??''),
  nutrition:Math.max(0,Number(x?.nutrition)||0),
  saturation:Math.max(0,Number(x?.saturation)||0)
 })).filter(x=>x.nutrition>0);
 if(!foods.length)return {nutrition:1,saturation:0,duplicate:false};
 let total=0,weighted=0,duplicate=false;
 const seen=new Set();
 for(const x of foods){total+=x.nutrition;weighted+=x.nutrition*x.saturation;if(seen.has(x.signature))duplicate=true;seen.add(x.signature)}
 let nutrition=Math.max(1,Math.floor(total*.6*(duplicate?.8:1))),saturation=Math.max(0,weighted/Math.max(1,total));
 if(!cooked){nutrition=Math.max(1,Math.floor(nutrition*.5));saturation*=.5}
 return {nutrition,saturation,duplicate};
}

export function oilPotCapacity(type){return type?FLUID_CAPACITY:FAT_CAPACITY}
export function clampOilCount(type,count){return Math.max(0,Math.min(oilPotCapacity(type),Number(count)||0))}
export function canFillTypedOil(currentType,currentCount,nextType,points=OIL_BUCKET_POINTS){
 const type=String(currentType??''),next=String(nextType??''),count=clampOilCount(type,currentCount),amount=Math.max(0,Number(points)||0);
 if(!next||amount<=0)return false;
 if((type===''&&count>0)||(type!==''&&type!==next))return false;
 return count+amount<=FLUID_CAPACITY;
}
