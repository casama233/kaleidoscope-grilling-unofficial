export const HOUTTUYNIA_PORK_ID='kaleidoscope_grilling:houttuynia_stir_fried_pork';
export const GREEN_PEPPER_SQUID_ID='kaleidoscope_grilling:green_pepper_squid_tentacles';
export const BRAISED_WINGS_ID='kaleidoscope_grilling:braised_chicken_wings';

export const WOK_FOOD_IDS=Object.freeze([
 HOUTTUYNIA_PORK_ID,GREEN_PEPPER_SQUID_ID,BRAISED_WINGS_ID
]);

export const WOK_FOODS=Object.freeze({
 [HOUTTUYNIA_PORK_ID]:Object.freeze({nutrition:9,saturation:0.7,maxStack:16}),
 [GREEN_PEPPER_SQUID_ID]:Object.freeze({nutrition:8,saturation:0.6,maxStack:16}),
 [BRAISED_WINGS_ID]:Object.freeze({nutrition:10,saturation:0.8,maxStack:16})
});

const WOK_RECIPES=Object.freeze([
 Object.freeze({
  id:'kaleidoscope_grilling:wok/houttuynia_stir_fried_pork',
  ingredients:Object.freeze([
   'kaleidoscope_grilling:houttuynia','kaleidoscope_grilling:houttuynia','kaleidoscope_grilling:houttuynia',
   'minecraft:porkchop','minecraft:porkchop','minecraft:porkchop'
  ]),
  result:HOUTTUYNIA_PORK_ID,count:1,carrier:'minecraft:bowl',time:200
 }),
 Object.freeze({
  id:'kaleidoscope_grilling:wok/green_pepper_squid_tentacles',
  ingredients:Object.freeze([
   'kaleidoscope_cookery:green_chili','kaleidoscope_cookery:green_chili',
   'kaleidoscope_grilling:squid_tentacle','kaleidoscope_grilling:squid_tentacle',
   'kaleidoscope_grilling:onion'
  ]),
  result:GREEN_PEPPER_SQUID_ID,count:1,carrier:'minecraft:bowl',time:200
 }),
 Object.freeze({
  id:'kaleidoscope_grilling:wok/braised_chicken_wings',
  ingredients:Object.freeze([
   'kaleidoscope_grilling:chicken_wing','kaleidoscope_grilling:chicken_wing','kaleidoscope_grilling:chicken_wing',
   'minecraft:sugar','minecraft:sugar','minecraft:sugar'
  ]),
  result:BRAISED_WINGS_ID,count:1,carrier:'minecraft:bowl',time:200
 })
]);

export function wokFoodSpec(id){return WOK_FOODS[String(id??'')]}
export function wokRecipes(){
 return WOK_RECIPES.map(x=>({
  id:x.id,ingredients:[...x.ingredients],result:x.result,count:x.count,carrier:x.carrier,time:x.time
 }));
}
