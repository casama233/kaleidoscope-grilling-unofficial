import assert from 'node:assert/strict';
import {P0_FOODS,p0EffectRows} from './a2745_p0_food_contract.js';
import {
 COOKERY_POT_ID,COOKERY_STOCKPOT_ID,planSeasoningUse,potHotTicks,inventoryGains,metadataPlan,oilTypeFromHeld,
 stateBeforeSeasoning,planPotOilTransition
} from './a2745_cookery_cuisine_core.js';
import {recipeTable,recipesForReady} from './a2745_refactored_a2727_cookery_host_recipes_core.js';

let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('all nine missing Java food items are defined',()=>{
 assert.equal(Object.keys(P0_FOODS).length,9);
 for(const id of [
  'sugared_tomato','pepper_honey','wedding_candy','houttuynia_stir_fried_pork',
  'green_pepper_squid_tentacles','braised_chicken_wings','potato_beef_stew',
  'red_sweet_potato_porridge','sour_spicy_noodles'
 ])assert.ok(P0_FOODS['kaleidoscope_grilling:'+id]);
});

t('standalone effects preserve Java durations',()=>{
 const rows=Object.fromEntries(p0EffectRows().map(x=>[x.itemId,x.effects]));
 assert.equal(rows['kaleidoscope_grilling:pepper_honey'][0].effect,'numb');
 assert.equal(rows['kaleidoscope_grilling:pepper_honey'][0].ticks,1200);
 assert.equal(rows['kaleidoscope_grilling:wedding_candy'][0].effect,'invincible');
 assert.equal(rows['kaleidoscope_grilling:wedding_candy'][0].ticks,300);
 assert.deepEqual(rows['kaleidoscope_grilling:red_sweet_potato_porridge'].map(x=>x.effect),['flatulence','warmth']);
 assert.equal(rows['kaleidoscope_grilling:sour_spicy_noodles'][0].ticks,900);
});

t('Pot and Stockpot hot durations match Java mixins',()=>{
 assert.equal(COOKERY_POT_ID,'kaleidoscope_cookery:pot');
 assert.equal(COOKERY_STOCKPOT_ID,'kaleidoscope_cookery:stockpot');
 assert.equal(potHotTicks('default'),1200);
 assert.equal(potHotTicks('canola'),1200);
 assert.equal(potHotTicks('secret_chili'),12000);
 assert.equal(potHotTicks('premium_chili'),24000);
 assert.equal(metadataPlan('stockpot',{seasoning:['minecraft:redstone']}).hotTicks,1200);
});

 t('pre-oil seasoning survives a fresh Wok cycle but stale prior-cycle state is reset',()=>{
 const fresh=stateBeforeSeasoning('pot',{seasoning:['minecraft:redstone'],oilType:''},false);
 assert.deepEqual(fresh.seasoning,['minecraft:redstone']);
 const next=planPotOilTransition(fresh,false,true,'secret_chili');
 assert.equal(next.changed,true);assert.equal(next.state.oilType,'secret_chili');
 assert.deepEqual(next.state.seasoning,['minecraft:redstone']);
 const stale=planPotOilTransition({seasoning:['minecraft:redstone'],oilType:'canola'},false,true,'premium_chili');
 assert.equal(stale.state.oilType,'premium_chili');assert.deepEqual(stale.state.seasoning,[]);
});

t('seasoning use consumes one of Java 16 uses',()=>{
 let p=planSeasoningUse({ingredients:['minecraft:redstone'],uses:14});
 assert.equal(p.ok,true);assert.equal(p.nextUses,15);assert.equal(p.replaceEmpty,false);
 p=planSeasoningUse({ingredients:['minecraft:redstone'],uses:15});
 assert.equal(p.nextUses,16);assert.equal(p.replaceEmpty,true);
 assert.equal(planSeasoningUse({ingredients:[],uses:0}).ok,false);
});

t('typed Cookery oil pots carry Grilling oil type; native host oil is default',()=>{
 assert.equal(oilTypeFromHeld('kaleidoscope_cookery:oil_pot_filled','premium_chili'),'premium_chili');
 assert.equal(oilTypeFromHeld('kaleidoscope_cookery:oil_pot_filled',''),'default');
 assert.equal(oilTypeFromHeld('kaleidoscope_cookery:oil',''),'default');
});

t('inventory delta isolates newly gained servings',()=>{
 const b=[{id:'x',amount:3,name:'',lore:[],props:{},damage:null},null];
 const a=[{id:'x',amount:4,name:'',lore:[],props:{},damage:null},{id:'y',amount:2,name:'',lore:[],props:{},damage:null}];
 assert.deepEqual(inventoryGains(b,a),[{slot:0,id:'x',count:1},{slot:1,id:'y',count:2}]);
});

t('Cookery public API receives 3 Wok + 6 Stockpot P0 recipes without a second publisher',()=>{
 const rows=recipeTable();
 const p0=rows.filter(x=>['wok','stockpot_exact','stockpot_flex'].includes(x.capability));
 assert.equal(p0.filter(x=>x.capability==='wok').length,3);
 assert.equal(p0.filter(x=>x.capability==='stockpot_exact').length,3);
 assert.equal(p0.filter(x=>x.capability==='stockpot_flex').length,3);
 const ready=recipesForReady({api:1,capabilities:['wok','stockpot_exact','stockpot_flex']});
 assert.equal(ready.filter(x=>x.kind==='wok').length,3);
 assert.equal(ready.filter(x=>x.kind==='stockpot_exact').length,3);
 assert.equal(ready.filter(x=>x.kind==='stockpot_flex').length,3);
});

console.log('A2.7.45 P0 core: '+n+'/'+n);
