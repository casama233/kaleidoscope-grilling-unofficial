import assert from 'node:assert/strict';
import {A27_ITEMS,A27_FOOD,A27_EFFECTS,A27_RECIPE_SCOPE,effectsFor,foodFor} from './a27_content_core.js';

let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('27 previously missing content items are enumerated',()=>assert.equal(A27_ITEMS.length,27));
t('15 Java food registrations are preserved',()=>assert.equal(Object.keys(A27_FOOD).length,15));
t('dish stacks stay at Java 16',()=>{
 for(const id of ['houttuynia_stir_fried_pork','green_pepper_squid_tentacles','braised_chicken_wings','potato_beef_stew','red_sweet_potato_porridge','sour_spicy_noodles'])
  assert.equal(foodFor('kaleidoscope_grilling:'+id).maxStack,16);
});
t('wedding candy keeps always-eat 20/0.5',()=>{
 const f=foodFor('kaleidoscope_grilling:wedding_candy');assert.deepEqual(f,{nutrition:20,saturation:.5,maxStack:64,alwaysEat:true});
});
t('cold houttuynia keeps fire resistance 1200 ticks',()=>assert.deepEqual(effectsFor('kaleidoscope_grilling:cold_houttuynia'),[{kind:'native',name:'fire_resistance',ticks:1200}]));
t('wedding candy keeps 15 second invincible',()=>assert.deepEqual(effectsFor('kaleidoscope_grilling:wedding_candy'),[{kind:'fx',name:'invincible',ticks:300}]));
t('red sweet potato porridge keeps both 900 tick effects',()=>assert.deepEqual(effectsFor('kaleidoscope_grilling:red_sweet_potato_porridge'),[{kind:'fx',name:'flatulence',ticks:900},{kind:'fx',name:'warmth',ticks:900}]));
t('recipe boundary is explicit',()=>{assert.equal(A27_RECIPE_SCOPE.nativeExact,8);assert.equal(A27_RECIPE_SCOPE.compatibilityFallback,17);assert.deepEqual(A27_RECIPE_SCOPE.dynamicDeferred,['cold_houttuynia']);assert.deepEqual(A27_RECIPE_SCOPE.optionalDependencyDeferred,['sour_spicy_noodles'])});

console.log(JSON.stringify({passed:n,failed:0,scope:'A2.7 items/dishes/recipe reconciliation core'}));
