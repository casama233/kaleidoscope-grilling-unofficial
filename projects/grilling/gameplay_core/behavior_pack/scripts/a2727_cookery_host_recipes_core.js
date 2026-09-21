export const KC_API=1;
export const KC_READY_EVENT='kaleidoscope_cookery:api_ready';
export const KC_PING_EVENT='kaleidoscope_cookery:api_ping';
export const KC_REGISTER_EVENT='kaleidoscope_cookery:register_recipe';
export const SOURCE='kaleidoscope_grilling';

function board(id,input,result,count=1,cuts=4){
 return Object.freeze({
  capability:'chopping_board',
  payload:Object.freeze({
   api:KC_API,kind:'chopping_board',source:SOURCE,
   recipe:Object.freeze({id,input,result,count,cuts})
  })
 });
}
function millstone(id,input,result,count=1,chance=1.0){
 return Object.freeze({
  capability:'millstone',
  payload:Object.freeze({
   api:KC_API,kind:'millstone',source:SOURCE,
   recipe:Object.freeze({
    id,input,
    outputs:Object.freeze([Object.freeze({id:result,count,chance})])
   })
  })
 });
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
]);

export function recipeTable(){
 return RECIPES.map(x=>({
  capability:x.capability,
  payload:JSON.parse(JSON.stringify(x.payload))
 }));
}
export function recipesForReady(info){
 if(!info||Number(info.api)!==KC_API)return [];
 const caps=new Set(Array.isArray(info.capabilities)?info.capabilities.map(String):[]);
 return RECIPES.filter(x=>caps.has(x.capability)).map(x=>JSON.parse(JSON.stringify(x.payload)));
}
