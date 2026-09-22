import assert from 'node:assert/strict';
import {INVENTORY_ADVANCEMENTS,inventoryAdvancementIds} from './a2759_advancement_inventory_core.js';
let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('inventory advancement metadata matches Java frames and XP',()=>{
 assert.equal(INVENTORY_ADVANCEMENTS.human_fireworks.xp,10);
 assert.equal(INVENTORY_ADVANCEMENTS.better_write_it_down.xp,10);
 assert.equal(INVENTORY_ADVANCEMENTS.a_handful_of_canola.xp,10);
 assert.equal(INVENTORY_ADVANCEMENTS.strength_makes_oil.xp,25);
 assert.equal(INVENTORY_ADVANCEMENTS.sweet_potato.xp,10);
 assert.equal(INVENTORY_ADVANCEMENTS.nether_taste.xp,25);
 assert.equal(INVENTORY_ADVANCEMENTS.strength_makes_oil.frame,'goal');
 assert.equal(INVENTORY_ADVANCEMENTS.nether_taste.frame,'goal');
});

t('grill and raw skewer trigger their Java inventory milestones',()=>{
 const raw=['kaleidoscope_grilling:raw_beef_skewer'];
 assert.deepEqual(inventoryAdvancementIds(['kaleidoscope_grilling:grill'],raw,'minecraft:overworld'),['human_fireworks']);
 assert.deepEqual(inventoryAdvancementIds(['kaleidoscope_grilling:raw_beef_skewer'],raw,'minecraft:overworld'),['looking_the_part']);
});

t('recipe book, canola, residue and sweet potato map exactly',()=>{
 const ids=[
  'kaleidoscope_grilling:skewer_recipe_book','kaleidoscope_grilling:canola_seeds',
  'kaleidoscope_grilling:oil_residue','kaleidoscope_grilling:sweet_potato'
 ];
 assert.deepEqual(inventoryAdvancementIds(ids,[],'minecraft:overworld'),[
  'better_write_it_down','a_handful_of_canola','strength_makes_oil','sweet_potato'
 ]);
});

t('Nether Taste requires both Nether and houttuynia',()=>{
 const h=['kaleidoscope_grilling:houttuynia'];
 assert.equal(inventoryAdvancementIds(h,[],'minecraft:overworld').includes('nether_taste'),false);
 assert.equal(inventoryAdvancementIds([],[],'minecraft:nether').includes('nether_taste'),false);
 assert.equal(inventoryAdvancementIds(h,[],'minecraft:nether').includes('nether_taste'),true);
});

t('multiple milestones can be awarded in one one-second inventory pass',()=>{
 const raw=['kaleidoscope_grilling:raw_lamb_skewer'];
 const ids=['kaleidoscope_grilling:grill','kaleidoscope_grilling:raw_lamb_skewer','kaleidoscope_grilling:houttuynia'];
 assert.deepEqual(inventoryAdvancementIds(ids,raw,'minecraft:nether'),['human_fireworks','looking_the_part','nether_taste']);
});

console.log('A2.7.59 inventory advancement core: '+n+'/'+n);
