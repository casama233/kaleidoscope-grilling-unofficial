import assert from 'node:assert/strict';
import {
 FX_KEY,SUGARED_TOMATO_ID,PEPPER_HONEY_ID,PEPPER_HONEY_NUMB_TICKS,
 standaloneFoodEffectTable,effectsForStandaloneFood,nextPersistentUntil
} from './a2742_standalone_food_effect_core.js';

assert.equal(FX_KEY,'kaleidoscope_grilling:a21_fx');
assert.equal(SUGARED_TOMATO_ID,'kaleidoscope_grilling:sugared_tomato');
assert.equal(PEPPER_HONEY_ID,'kaleidoscope_grilling:pepper_honey');
assert.equal(PEPPER_HONEY_NUMB_TICKS,1200);
const rows=standaloneFoodEffectTable();
assert.equal(rows.length,3);
const pepper=effectsForStandaloneFood(PEPPER_HONEY_ID);
assert.deepEqual(pepper,[{
 kind:'persistent_fx',effect:'numb',ticks:1200,amplifier:0,stacking:'max_until'
}]);
assert.deepEqual(effectsForStandaloneFood(SUGARED_TOMATO_ID),[]);
assert.equal(nextPersistentUntil(100,0,1200),1300);
assert.equal(nextPersistentUntil(100,2000,1200),2000);
rows[0].effects[0].ticks=1;
assert.notEqual(standaloneFoodEffectTable()[0].effects[0].ticks,1);
console.log('A2.7.42 standalone food effect core: PASS');
