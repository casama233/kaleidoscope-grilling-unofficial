export const A27_ITEMS=Object.freeze([
 'beef_chunks','canola_seeds','carrot_dice','chicken_skin','chicken_wing','houttuynia',
 'minced_houttuynia','onion','potato_slice','raw_mantou_slice','raw_sweet_potato_sheet',
 'red_chili_powder','squid_tentacle','sweet_potato','sweet_potato_powder',
 'cold_houttuynia','pepper_honey','roasted_chicken_wing','roasted_sweet_potato',
 'sugared_tomato','wedding_candy','houttuynia_stir_fried_pork',
 'green_pepper_squid_tentacles','braised_chicken_wings','potato_beef_stew',
 'red_sweet_potato_porridge','sour_spicy_noodles'
]);

export const A27_FOOD=Object.freeze({
 'kaleidoscope_grilling:chicken_wing':{nutrition:2,saturation:0.06,maxStack:64},
 'kaleidoscope_grilling:houttuynia':{nutrition:2,saturation:0.2,maxStack:64},
 'kaleidoscope_grilling:sweet_potato':{nutrition:3,saturation:0.1,maxStack:64},
 'kaleidoscope_grilling:roasted_sweet_potato':{nutrition:6,saturation:0.2,maxStack:64},
 'kaleidoscope_grilling:roasted_chicken_wing':{nutrition:5,saturation:0.12,maxStack:64},
 'kaleidoscope_grilling:cold_houttuynia':{nutrition:6,saturation:1.0,maxStack:64},
 'kaleidoscope_grilling:sugared_tomato':{nutrition:6,saturation:0.65,maxStack:64},
 'kaleidoscope_grilling:pepper_honey':{nutrition:4,saturation:0.25,maxStack:64},
 'kaleidoscope_grilling:wedding_candy':{nutrition:20,saturation:0.5,maxStack:64,alwaysEat:true},
 'kaleidoscope_grilling:houttuynia_stir_fried_pork':{nutrition:9,saturation:0.7,maxStack:16},
 'kaleidoscope_grilling:green_pepper_squid_tentacles':{nutrition:8,saturation:0.6,maxStack:16},
 'kaleidoscope_grilling:braised_chicken_wings':{nutrition:10,saturation:0.8,maxStack:16},
 'kaleidoscope_grilling:potato_beef_stew':{nutrition:12,saturation:0.9,maxStack:16},
 'kaleidoscope_grilling:red_sweet_potato_porridge':{nutrition:14,saturation:0.071429,maxStack:16},
 'kaleidoscope_grilling:sour_spicy_noodles':{nutrition:10,saturation:0.6,maxStack:16}
});

export const A27_EFFECTS=Object.freeze({
 'kaleidoscope_grilling:roasted_sweet_potato':[{kind:'fx',name:'warmth',ticks:600}],
 'kaleidoscope_grilling:cold_houttuynia':[{kind:'native',name:'fire_resistance',ticks:1200}],
 'kaleidoscope_grilling:pepper_honey':[{kind:'fx',name:'numb',ticks:1200}],
 'kaleidoscope_grilling:wedding_candy':[{kind:'fx',name:'invincible',ticks:300}],
 'kaleidoscope_grilling:red_sweet_potato_porridge':[
  {kind:'fx',name:'flatulence',ticks:900},{kind:'fx',name:'warmth',ticks:900}
 ],
 'kaleidoscope_grilling:sour_spicy_noodles':[{kind:'fx',name:'warmth',ticks:900}]
});

export const A27_RECIPE_SCOPE=Object.freeze({
 nativeExact:8,
 compatibilityFallback:17,
 dynamicDeferred:['cold_houttuynia'],
 optionalDependencyDeferred:['sour_spicy_noodles'],
 workstationFamilies:['chopping_board','milling','pot','stockpot']
});

export function effectsFor(id){return A27_EFFECTS[id]??[]}
export function foodFor(id){return A27_FOOD[id]??null}
