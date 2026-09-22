export const KC_API=1;
export const KC_READY_EVENT='kaleidoscope_cookery:api_ready';
export const KC_PING_EVENT='kaleidoscope_cookery:api_ping';
export const KC_REGISTER_EVENT='kaleidoscope_cookery:register_recipe';
export const SOURCE='kaleidoscope_grilling';

function board(id,input,result,count=1,cuts=4){
 return Object.freeze({capability:'chopping_board',payload:Object.freeze({
  api:KC_API,kind:'chopping_board',source:SOURCE,
  recipe:Object.freeze({id,input,result,count,cuts})
 })});
}
function millstone(id,input,result,count=1,chance=1.0){
 return Object.freeze({capability:'millstone',payload:Object.freeze({
  api:KC_API,kind:'millstone',source:SOURCE,
  recipe:Object.freeze({id,input,outputs:Object.freeze([Object.freeze({id:result,count,chance})])})
 })});
}
function wok(id,ingredients,result,{count=1,carrier='minecraft:bowl',time=200}={}){
 return Object.freeze({capability:'wok',payload:Object.freeze({
  api:KC_API,kind:'wok',source:SOURCE,
  recipe:Object.freeze({id,ingredients:Object.freeze([...ingredients]),result,count,carrier,time})
 })});
}
function stockpot(kind,id,ingredients,result,{count=1,time=300,base='minecraft:water',carrier='minecraft:bowl',finishedKind='default'}={}){
 return Object.freeze({capability:kind,payload:Object.freeze({
  api:KC_API,kind,source:SOURCE,
  recipe:Object.freeze({
   id,ingredients:Object.freeze(ingredients.map(slot=>Object.freeze(Array.isArray(slot)?[...slot]:[slot]))),
   result,count,time,base,carrier,finishedKind
  })
 })});
}

const RECIPES=Object.freeze([
 board('kaleidoscope_grilling:chopping_board/raw_sweet_potato_sheet',
  'kaleidoscope_grilling:sweet_potato_powder','kaleidoscope_grilling:raw_sweet_potato_sheet',1,4),
 millstone('kaleidoscope_grilling:millstone/sweet_potato_powder',
  'kaleidoscope_grilling:sweet_potato','kaleidoscope_grilling:sweet_potato_powder',1,1.0),
 board('kaleidoscope_grilling:chopping_board/carrot_dice',
  'minecraft:carrot','kaleidoscope_grilling:carrot_dice',3,4),
 board('kaleidoscope_grilling:chopping_board/potato_slice',
  'minecraft:potato','kaleidoscope_grilling:potato_slice',3,4),
 board('kaleidoscope_grilling:chopping_board/raw_mantou_slice',
  'kaleidoscope_cookery:mantou','kaleidoscope_grilling:raw_mantou_slice',3,4),
 board('kaleidoscope_grilling:chopping_board/minced_houttuynia',
  'kaleidoscope_grilling:houttuynia','kaleidoscope_grilling:minced_houttuynia',1,4),
 millstone('kaleidoscope_grilling:millstone/canola_powder',
  'kaleidoscope_grilling:canola_seeds','kaleidoscope_grilling:canola_powder',1,1.0),
 millstone('kaleidoscope_grilling:millstone/onion_powder',
  'kaleidoscope_grilling:onion','kaleidoscope_grilling:onion_powder',1,1.0),
 millstone('kaleidoscope_grilling:millstone/red_chili_powder',
  'kaleidoscope_cookery:red_chili','kaleidoscope_grilling:red_chili_powder',1,1.0),

 // Java strict Pot recipes. Cookery Bedrock public v1 Wok API has no flex-Wok kind;
 // do not counterfeit Java FlexPot semantics with host batching.
 wok('kaleidoscope_grilling:wok/houttuynia_stir_fried_pork',[
  'kaleidoscope_grilling:houttuynia','kaleidoscope_grilling:houttuynia','kaleidoscope_grilling:houttuynia',
  'minecraft:porkchop','minecraft:porkchop','minecraft:porkchop'
 ],'kaleidoscope_grilling:houttuynia_stir_fried_pork'),
 wok('kaleidoscope_grilling:wok/green_pepper_squid_tentacles',[
  'kaleidoscope_cookery:green_chili','kaleidoscope_cookery:green_chili',
  'kaleidoscope_grilling:squid_tentacle','kaleidoscope_grilling:squid_tentacle',
  'kaleidoscope_grilling:onion'
 ],'kaleidoscope_grilling:green_pepper_squid_tentacles'),
 wok('kaleidoscope_grilling:wok/braised_chicken_wings',[
  'kaleidoscope_grilling:chicken_wing','kaleidoscope_grilling:chicken_wing','kaleidoscope_grilling:chicken_wing',
  'minecraft:sugar','minecraft:sugar','minecraft:sugar'
 ],'kaleidoscope_grilling:braised_chicken_wings'),

 stockpot('stockpot_exact','kaleidoscope_grilling:stockpot/potato_beef_stew',[
  'kaleidoscope_grilling:beef_chunks','kaleidoscope_grilling:beef_chunks','minecraft:potato',
  'kaleidoscope_grilling:carrot_dice','kaleidoscope_grilling:onion'
 ],'kaleidoscope_grilling:potato_beef_stew'),
 stockpot('stockpot_flex','kaleidoscope_grilling:flex_stockpot/potato_beef_stew',[
  'kaleidoscope_grilling:beef_chunks','minecraft:potato','kaleidoscope_grilling:carrot_dice','kaleidoscope_grilling:onion'
 ],'kaleidoscope_grilling:potato_beef_stew'),

 stockpot('stockpot_exact','kaleidoscope_grilling:stockpot/red_sweet_potato_porridge',[
  'kaleidoscope_grilling:sweet_potato','kaleidoscope_grilling:sweet_potato','kaleidoscope_grilling:sweet_potato',
  'kaleidoscope_cookery:rice','kaleidoscope_cookery:rice','kaleidoscope_cookery:rice'
 ],'kaleidoscope_grilling:red_sweet_potato_porridge'),
 stockpot('stockpot_flex','kaleidoscope_grilling:flex_stockpot/red_sweet_potato_porridge',[
  'kaleidoscope_grilling:sweet_potato','kaleidoscope_cookery:rice'
 ],'kaleidoscope_grilling:red_sweet_potato_porridge'),

 stockpot('stockpot_exact','kaleidoscope_grilling:stockpot/sour_spicy_noodles',[
  'kaleidoscope_tavern:vinegar','kaleidoscope_cookery:red_chili','kaleidoscope_cookery:red_chili',
  'kaleidoscope_grilling:raw_sweet_potato_sheet','kaleidoscope_grilling:raw_sweet_potato_sheet',
  'kaleidoscope_cookery:lettuce'
 ],'kaleidoscope_grilling:sour_spicy_noodles'),
 stockpot('stockpot_flex','kaleidoscope_grilling:flex_stockpot/sour_spicy_noodles',[
  'kaleidoscope_tavern:vinegar','kaleidoscope_cookery:red_chili',
  'kaleidoscope_grilling:raw_sweet_potato_sheet','kaleidoscope_cookery:lettuce'
 ],'kaleidoscope_grilling:sour_spicy_noodles')
]);

export function recipeTable(){
 return RECIPES.map(x=>({capability:x.capability,payload:JSON.parse(JSON.stringify(x.payload))}));
}
export function recipesForReady(info){
 if(!info||Number(info.api)!==KC_API)return [];
 const caps=new Set(Array.isArray(info.capabilities)?info.capabilities.map(String):[]);
 // Wok/Stockpot are part of the original v1 baseline; old hosts may omit the capability list.
 const oldV1=!caps.size;
 return RECIPES.filter(x=>oldV1||caps.has(x.capability)).map(x=>JSON.parse(JSON.stringify(x.payload)));
}
