import assert from 'node:assert/strict';
import {
 RACK_COMPARTMENT_COUNT,RACK_SEASONING_SLOTS,RACK_TOOL_SLOTS,
 COOKERY_KNIFE_TAG,COOKERY_SHOVEL_TAG,
 rackSlotKind,rackItemKind,rackCanPlace,rackFilterFor,rackFilterMatches,
 rackCanPlaceWithFilter,rackFiltersAfterInsert,rackCanClearFilter,rackSpiceLevel
} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2746_advanced_rack_core.js';

let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('Java rack compartment split is 5 seasoning + 4 tool',()=>{
 assert.equal(RACK_COMPARTMENT_COUNT,9);
 assert.equal(RACK_SEASONING_SLOTS,5);
 assert.equal(RACK_TOOL_SLOTS,4);
 assert.equal(rackSlotKind(0),'seasoning');
 assert.equal(rackSlotKind(4),'seasoning');
 assert.equal(rackSlotKind(5),'tool');
 assert.equal(rackSlotKind(8),'tool');
});

t('seasoning slots reuse oil pots and seasoning bottle family',()=>{
 for(const id of [
  'kaleidoscope_cookery:oil_pot','kaleidoscope_cookery:oil_pot_filled',
  'kaleidoscope_grilling:empty_seasoning_bottle','kaleidoscope_grilling:pending_seasoning','kaleidoscope_grilling:special_seasoning'
 ])assert.equal(rackCanPlace(0,{id}),true,id);
 assert.equal(rackCanPlace(5,{id:'kaleidoscope_grilling:special_seasoning'}),false);
});

t('tool slots accept Java Cookery tool tags and flint and steel',()=>{
 assert.equal(rackCanPlace(5,{id:'test:knife',tags:[COOKERY_KNIFE_TAG],damageable:true}),true);
 assert.equal(rackCanPlace(6,{id:'test:shovel',tags:[COOKERY_SHOVEL_TAG],damageable:true}),true);
 assert.equal(rackCanPlace(7,{id:'minecraft:flint_and_steel',damageable:true}),true);
 assert.equal(rackCanPlace(0,{id:'minecraft:flint_and_steel',damageable:true}),false);
});

t('oil pot and seasoning bottle filters share Java categories',()=>{
 const oil=rackFilterFor({id:'kaleidoscope_cookery:oil_pot'});
 assert.equal(rackFilterMatches(oil,{id:'kaleidoscope_cookery:oil_pot_filled'}),true);
 const bottle=rackFilterFor({id:'kaleidoscope_grilling:empty_seasoning_bottle'});
 assert.equal(rackFilterMatches(bottle,{id:'kaleidoscope_grilling:special_seasoning'}),true);
});

t('tool filters stay exact item id like Java durable tools',()=>{
 const filter=rackFilterFor({id:'test:knife_a',tags:[COOKERY_KNIFE_TAG],damageable:true});
 assert.equal(rackFilterMatches(filter,{id:'test:knife_a',tags:[COOKERY_KNIFE_TAG],damageable:true}),true);
 assert.equal(rackFilterMatches(filter,{id:'test:knife_b',tags:[COOKERY_KNIFE_TAG],damageable:true}),false);
});

t('first insert auto establishes filter',()=>{
 let filters=Array(9).fill(null);
 filters=rackFiltersAfterInsert(filters,0,{id:'kaleidoscope_grilling:special_seasoning'});
 assert.deepEqual(filters[0],{kind:'seasoning_bottle',id:''});
 assert.equal(rackCanPlaceWithFilter(0,filters[0],{id:'kaleidoscope_grilling:empty_seasoning_bottle'}),true);
});

t('filter clears only when stored slot is empty',()=>{
 const filters=Array(9).fill(null);filters[0]={kind:'seasoning_bottle',id:''};
 assert.equal(rackCanClearFilter(filters,[true],0),false);
 assert.equal(rackCanClearFilter(filters,[false],0),true);
});

t('spice display counts first five compartments and clamps to four',()=>{
 assert.equal(rackSpiceLevel([false,false,false,false,false,true,true]),0);
 assert.equal(rackSpiceLevel([true,true,true,false,false]),3);
 assert.equal(rackSpiceLevel([true,true,true,true,true]),4);
});

console.log('A2.7.46 Advanced Rack core: '+n+'/'+n);
