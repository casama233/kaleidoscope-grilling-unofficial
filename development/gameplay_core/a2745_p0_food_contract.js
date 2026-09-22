export const P0_FOODS=Object.freeze({
 'kaleidoscope_grilling:sugared_tomato':Object.freeze({nutrition:6,saturation:.65,maxStack:64}),
 'kaleidoscope_grilling:pepper_honey':Object.freeze({nutrition:4,saturation:.25,maxStack:64,effects:Object.freeze([{kind:'persistent_fx',effect:'numb',ticks:1200,amplifier:0,stacking:'max_until'}])}),
 'kaleidoscope_grilling:wedding_candy':Object.freeze({nutrition:20,saturation:.5,maxStack:64,alwaysEdible:true,effects:Object.freeze([{kind:'persistent_fx',effect:'invincible',ticks:300,amplifier:0,stacking:'max_until'}])}),
 'kaleidoscope_grilling:houttuynia_stir_fried_pork':Object.freeze({nutrition:9,saturation:.7,maxStack:16}),
 'kaleidoscope_grilling:green_pepper_squid_tentacles':Object.freeze({nutrition:8,saturation:.6,maxStack:16}),
 'kaleidoscope_grilling:braised_chicken_wings':Object.freeze({nutrition:10,saturation:.8,maxStack:16}),
 'kaleidoscope_grilling:potato_beef_stew':Object.freeze({nutrition:12,saturation:.9,maxStack:16}),
 'kaleidoscope_grilling:red_sweet_potato_porridge':Object.freeze({nutrition:14,saturation:.071429,maxStack:16,effects:Object.freeze([
  {kind:'persistent_fx',effect:'flatulence',ticks:900,amplifier:0,stacking:'max_until'},
  {kind:'persistent_fx',effect:'warmth',ticks:900,amplifier:0,stacking:'max_until'}
 ])}),
 'kaleidoscope_grilling:sour_spicy_noodles':Object.freeze({nutrition:10,saturation:.6,maxStack:16,effects:Object.freeze([{kind:'persistent_fx',effect:'warmth',ticks:900,amplifier:0,stacking:'max_until'}])})
});

export const P0_FOOD_IDS=Object.freeze(Object.keys(P0_FOODS));

export function p0Food(id){return P0_FOODS[String(id??'')]}

export function p0EffectRows(){
 const rows=[];
 for(const [itemId,spec] of Object.entries(P0_FOODS)){
  if(!spec.effects?.length)continue;
  rows.push({itemId,effects:spec.effects.map(x=>({...x}))});
 }
 return rows;
}
