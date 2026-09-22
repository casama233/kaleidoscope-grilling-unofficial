import assert from 'node:assert/strict';
import {
 FIREWORKS_FEAST,FIREWORKS_FEAST_FOODS,FIREWORKS_FEAST_PROGRESS_KEY,
 normalizeFireworksFeastProgress,nextFireworksFeastProgress
} from './a2759_fireworks_feast_core.js';

assert.equal(FIREWORKS_FEAST.id,'fireworks_feast');
assert.equal(FIREWORKS_FEAST.parent,'eat_it_hot');
assert.equal(FIREWORKS_FEAST.frame,'challenge');
assert.equal(FIREWORKS_FEAST.xp,100);
assert.equal(FIREWORKS_FEAST.propertyKey,'kaleidoscope_grilling:adv_fireworks_feast');
assert.equal(FIREWORKS_FEAST_PROGRESS_KEY,'kaleidoscope_grilling:advancement_foods');
assert.equal(FIREWORKS_FEAST_FOODS.length,29);
assert.equal(new Set(FIREWORKS_FEAST_FOODS).size,29);
assert.ok(FIREWORKS_FEAST_FOODS.includes('kaleidoscope_grilling:ordinary_skewer'));
assert.ok(!FIREWORKS_FEAST_FOODS.includes('kaleidoscope_grilling:secret_skewer'));

assert.deepEqual(
 normalizeFireworksFeastProgress('["grilled_beef_skewer","kaleidoscope_grilling:grilled_beef_skewer","minecraft:apple"]'),
 ['kaleidoscope_grilling:grilled_beef_skewer']
);
assert.deepEqual(
 normalizeFireworksFeastProgress('grilled_beef_skewer,cold_houttuynia'),
 ['kaleidoscope_grilling:grilled_beef_skewer','kaleidoscope_grilling:cold_houttuynia']
);

const ignored=nextFireworksFeastProgress([], 'minecraft:apple');
assert.equal(ignored.eligible,false);
assert.equal(ignored.changed,false);

let state=[];
for(let i=0;i<FIREWORKS_FEAST_FOODS.length;i++){
 const result=nextFireworksFeastProgress(state,FIREWORKS_FEAST_FOODS[i]);
 assert.equal(result.eligible,true);
 assert.equal(result.changed,true);
 assert.equal(result.count,i+1);
 assert.equal(result.complete,i===FIREWORKS_FEAST_FOODS.length-1);
 state=result.eaten;
}
const duplicate=nextFireworksFeastProgress(state,FIREWORKS_FEAST_FOODS[0]);
assert.equal(duplicate.changed,false);
assert.equal(duplicate.complete,true);
assert.equal(duplicate.count,29);

console.log('A2.7.59 Fireworks Feast core: PASS');
