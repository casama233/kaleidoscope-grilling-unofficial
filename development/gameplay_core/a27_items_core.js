export const A27_ITEMS=Object.freeze([
 {id:'beef_chunks'},
 {id:'braised_chicken_wings',stack:16,food:{nutrition:10,saturation:.8},quality:true},
 {id:'canola_seeds',plant:'canola_crop'},
 {id:'carrot_dice'},
 {id:'chicken_skin'},
 {id:'chicken_wing',food:{nutrition:2,saturation:.06}},
 {id:'cold_houttuynia',food:{nutrition:6,saturation:1.0},quality:true,effects:[{kind:'native',id:'fire_resistance',ticks:1200}]},
 {id:'green_pepper_squid_tentacles',stack:16,food:{nutrition:8,saturation:.6},quality:true},
 {id:'houttuynia',food:{nutrition:2,saturation:.2},plant:'houttuynia_crop'},
 {id:'houttuynia_stir_fried_pork',stack:16,food:{nutrition:9,saturation:.7},quality:true},
 {id:'minced_houttuynia'},
 {id:'onion',plant:'onion_crop'},
 {id:'pepper_honey',food:{nutrition:4,saturation:.25},quality:true,effects:[{kind:'fx',id:'numb',ticks:1200}]},
 {id:'potato_beef_stew',stack:16,food:{nutrition:12,saturation:.9},quality:true},
 {id:'potato_slice'},
 {id:'raw_mantou_slice'},
 {id:'raw_sweet_potato_sheet',tooltip:'tooltip.kaleidoscope_grilling.raw_sweet_potato_sheet'},
 {id:'red_chili_powder'},
 {id:'red_sweet_potato_porridge',stack:16,food:{nutrition:14,saturation:.071429},quality:true,effects:[{kind:'fx',id:'flatulence',ticks:900},{kind:'fx',id:'warmth',ticks:900}]},
 {id:'roasted_chicken_wing',food:{nutrition:5,saturation:.12},quality:true},
 {id:'roasted_sweet_potato',food:{nutrition:6,saturation:.2},quality:true,effects:[{kind:'fx',id:'warmth',ticks:600}]},
 {id:'sour_spicy_noodles',stack:16,food:{nutrition:10,saturation:.6},quality:true,effects:[{kind:'fx',id:'warmth',ticks:900}]},
 {id:'squid_tentacle'},
 {id:'sugared_tomato',food:{nutrition:6,saturation:.65},quality:true},
 {id:'sweet_potato',food:{nutrition:3,saturation:.1},plant:'sweet_potato_crop'},
 {id:'sweet_potato_powder',use:{ticks:30,animation:'bow',result:'kaleidoscope_grilling:raw_sweet_potato_sheet',wholeStack:true}},
 {id:'wedding_candy',food:{nutrition:20,saturation:.5,alwaysEat:true},effects:[{kind:'fx',id:'invincible',ticks:300}]}
]);

const BY_ID=Object.freeze(Object.fromEntries(A27_ITEMS.map(x=>['kaleidoscope_grilling:'+x.id,x])));
export function itemSpec(id){return BY_ID[String(id??'')]??null}
export function itemIds(){return A27_ITEMS.map(x=>'kaleidoscope_grilling:'+x.id)}
export function foodSpec(id){return itemSpec(id)?.food??null}
export function effectsFor(id,qualityRatio=1){
 const spec=itemSpec(id),ratio=Math.max(0,Number(qualityRatio)||1);
 return (spec?.effects??[]).map(e=>({...e,ticks:Math.max(1,Math.round(e.ticks*(spec.quality?ratio:1)))}));
}
export function stackSizeFor(id){return itemSpec(id)?.stack??64}
export function qualityAware(id){return !!itemSpec(id)?.quality}
export function kneadResult(id,count){
 const spec=itemSpec(id);if(!spec?.use?.wholeStack||!spec.use.result)return null;
 return {id:spec.use.result,count:Math.max(1,Number(count)||1)|0,ticks:spec.use.ticks,animation:spec.use.animation};
}
export function deferredPlantBlock(id){const p=itemSpec(id)?.plant;return p?'kaleidoscope_grilling:'+p:null}
