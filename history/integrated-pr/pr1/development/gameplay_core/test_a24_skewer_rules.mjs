import assert from 'node:assert/strict';
import {SKEWER_RECIPES,expectedSize,fixedResult,canAppend,isRawFixedId,hasDuplicateIngredients} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a24_skewer_rules.js';

let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('Java 1.1.1 exposes twenty fixed threading recipes',()=>assert.equal(SKEWER_RECIPES.length,20));
t('beef order resolves to raw beef skewer',()=>assert.equal(
 fixedResult(['kaleidoscope_grilling:beef_chunks','kaleidoscope_cookery:red_chili','kaleidoscope_grilling:beef_chunks']),
 'kaleidoscope_grilling:raw_beef_skewer'));
t('fish accepts all four Java fish alternatives',()=>{
 for(const id of ['minecraft:cod','minecraft:salmon','minecraft:tropical_fish','minecraft:pufferfish'])
  assert.equal(fixedResult([id]),'kaleidoscope_grilling:raw_fish_skewer');
});
t('ordinary skewer is a direct threading result',()=>assert.equal(
 fixedResult(['minecraft:poisonous_potato','minecraft:spider_eye','minecraft:pufferfish']),
 'kaleidoscope_grilling:ordinary_skewer'));
t('two dough pieces resolve to gluten skewer',()=>assert.equal(
 fixedResult(['kaleidoscope_cookery:raw_dough','kaleidoscope_cookery:raw_dough']),
 'kaleidoscope_grilling:raw_gluten_skewer'));
t('golden skewer uses apple totem carrot order',()=>assert.equal(
 fixedResult(['minecraft:golden_apple','minecraft:totem_of_undying','minecraft:golden_carrot']),
 'kaleidoscope_grilling:raw_golden_skewer'));
t('configured ingredient can start a secret mix even off recipe',()=>assert.equal(
 canAppend([], 'minecraft:bone', false), true));
t('edible compatibility fallback accepts external food',()=>assert.equal(
 canAppend([], 'example:food', true), true));
t('non-food unconfigured item is rejected',()=>assert.equal(
 canAppend([], 'minecraft:cobblestone', false), false));
t('three ingredients is the hard append cap',()=>assert.equal(
 canAppend(['minecraft:apple','minecraft:apple','minecraft:apple'],'minecraft:apple',true),false));
t('prefix expected size follows Java recipe length',()=>{
 assert.equal(expectedSize(['kaleidoscope_grilling:chicken_skin']),2);
 assert.equal(expectedSize(['kaleidoscope_grilling:beef_chunks']),3);
 assert.equal(expectedSize(['minecraft:cod']),1);
});
t('raw fixed set excludes direct ordinary skewer result',()=>{
 assert.equal(isRawFixedId('kaleidoscope_grilling:raw_gluten_skewer'),true);
 assert.equal(isRawFixedId('kaleidoscope_grilling:ordinary_skewer'),false);
});
t('duplicate detection drives secret nutrition coefficient',()=>{
 assert.equal(hasDuplicateIngredients(['a','a','b']),true);
 assert.equal(hasDuplicateIngredients(['a','b','c']),false);
});
console.log(JSON.stringify({passed:n,failed:0,scope:'A2.4 Java 1.1.1 hand-threading rules'}));
