import assert from 'node:assert/strict';
import {A27_ITEMS,itemIds,foodSpec,effectsFor,stackSizeFor,qualityAware,kneadResult,deferredPlantBlock,qualityRatioFromId,qualityFood} from './a27_items_core.js';
let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('exactly 27 missing Java registry items are covered',()=>assert.equal(A27_ITEMS.length,27));
t('ids are unique',()=>assert.equal(new Set(itemIds()).size,27));
t('Java basic food values match',()=>{
 assert.deepEqual(foodSpec('kaleidoscope_grilling:chicken_wing'),{nutrition:2,saturation:.06});
 assert.deepEqual(foodSpec('kaleidoscope_grilling:houttuynia'),{nutrition:2,saturation:.2});
 assert.deepEqual(foodSpec('kaleidoscope_grilling:sweet_potato'),{nutrition:3,saturation:.1});
});
t('Java prepared food values match',()=>{
 assert.deepEqual(foodSpec('kaleidoscope_grilling:roasted_sweet_potato'),{nutrition:6,saturation:.2});
 assert.deepEqual(foodSpec('kaleidoscope_grilling:cold_houttuynia'),{nutrition:6,saturation:1});
 assert.deepEqual(foodSpec('kaleidoscope_grilling:potato_beef_stew'),{nutrition:12,saturation:.9});
 assert.deepEqual(foodSpec('kaleidoscope_grilling:red_sweet_potato_porridge'),{nutrition:14,saturation:.071429});
});
t('dish and bowl foods use Java stack 16',()=>{
 for(const id of ['braised_chicken_wings','green_pepper_squid_tentacles','houttuynia_stir_fried_pork','potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles'])
  assert.equal(stackSizeFor('kaleidoscope_grilling:'+id),16);
});
t('wedding candy alone is always-eat among new foods',()=>assert.equal(foodSpec('kaleidoscope_grilling:wedding_candy').alwaysEat,true));
t('effects preserve Java base durations',()=>{
 assert.deepEqual(effectsFor('kaleidoscope_grilling:roasted_sweet_potato'),[{kind:'fx',id:'warmth',ticks:600}]);
 assert.deepEqual(effectsFor('kaleidoscope_grilling:cold_houttuynia'),[{kind:'native',id:'fire_resistance',ticks:1200}]);
 assert.deepEqual(effectsFor('kaleidoscope_grilling:pepper_honey'),[{kind:'fx',id:'numb',ticks:1200}]);
 assert.deepEqual(effectsFor('kaleidoscope_grilling:wedding_candy'),[{kind:'fx',id:'invincible',ticks:300}]);
});
t('porridge applies both Java Cookery effects',()=>assert.deepEqual(effectsFor('kaleidoscope_grilling:red_sweet_potato_porridge'),[{kind:'fx',id:'flatulence',ticks:900},{kind:'fx',id:'warmth',ticks:900}]));
t('quality-aware cuisine scales effect duration, wedding candy does not',()=>{
 assert.equal(qualityAware('kaleidoscope_grilling:pepper_honey'),true);
 assert.equal(effectsFor('kaleidoscope_grilling:pepper_honey',1.5)[0].ticks,1800);
 assert.equal(effectsFor('kaleidoscope_grilling:wedding_candy',2)[0].ticks,300);
});
t('eleven Java CuisineQualitySupport items are marked',()=>assert.equal(itemIds().filter(qualityAware).length,11));
t('Cookery Java quality IDs map to exact ratios',()=>assert.deepEqual([0,1,2,3].map(qualityRatioFromId),[1.2,.9,.6,.3]));
t('quality scales both nutrition and saturation modifier',()=>{
 assert.deepEqual(qualityFood('kaleidoscope_grilling:pepper_honey',0),{nutrition:5,saturation:.3});
 assert.deepEqual(qualityFood('kaleidoscope_grilling:pepper_honey',3),{nutrition:1,saturation:.075});
});
t('sweet potato powder kneads the entire stack after 30 ticks',()=>assert.deepEqual(kneadResult('kaleidoscope_grilling:sweet_potato_powder',17),{id:'kaleidoscope_grilling:raw_sweet_potato_sheet',count:17,ticks:30,animation:'bow'}));
t('crop-linked items are explicit but planting is deferred to A2.8',()=>{
 assert.equal(deferredPlantBlock('kaleidoscope_grilling:canola_seeds'),'kaleidoscope_grilling:canola_crop');
 assert.equal(deferredPlantBlock('kaleidoscope_grilling:onion'),'kaleidoscope_grilling:onion_crop');
 assert.equal(deferredPlantBlock('kaleidoscope_grilling:houttuynia'),'kaleidoscope_grilling:houttuynia_crop');
 assert.equal(deferredPlantBlock('kaleidoscope_grilling:sweet_potato'),'kaleidoscope_grilling:sweet_potato_crop');
});
console.log(JSON.stringify({passed:n,failed:0,scope:'A2.7 missing Java item registry + food/effect contracts'}));
