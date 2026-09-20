import assert from 'node:assert/strict';
import {
  PLATE_CAPACITY,PLATE_ITEM_ID,PLATE_BLOCK_ID,RECIPE_BOOK_ID,RECIPE_BLOCK_ID,
  isPlateSkewerId,isRecordableSkewer,addToPlate,removeLastFromPlate,highestNutritionIndex,takeHighestNutrition,
  recordBook,bookIngredients,planBookCraft,plateLore,bookLore
} from './a25_plate_core.js';

let n=0;const t=(name,fn)=>{fn();n++;console.log('PASS',name)};

t('A2.5 public/internal identifiers are stable',()=>{
 assert.equal(PLATE_ITEM_ID,'kaleidoscope_grilling:skewer_plate');
 assert.equal(PLATE_BLOCK_ID,'kaleidoscope_grilling:skewer_plate_block');
 assert.equal(RECIPE_BOOK_ID,'kaleidoscope_grilling:skewer_recipe_book');
 assert.equal(RECIPE_BLOCK_ID,'kaleidoscope_grilling:skewer_recipe');
});
t('plate accepts Java skewer families and rejects unrelated items',()=>{
 for(const id of [
  'kaleidoscope_grilling:raw_beef_skewer','kaleidoscope_grilling:grilled_beef_skewer',
  'kaleidoscope_grilling:ordinary_skewer','kaleidoscope_grilling:secret_skewer',
  'kaleidoscope_grilling:mysterious_skewer','kaleidoscope_grilling:dark_grilling'
 ])assert.equal(isPlateSkewerId(id),true,id);
 assert.equal(isPlateSkewerId('minecraft:stick'),false);
});
t('plate capacity is five',()=>{
 let rows=[];for(let i=0;i<PLATE_CAPACITY;i++){const x=addToPlate(rows,{id:'kaleidoscope_grilling:raw_beef_skewer',n:i});assert.equal(x.ok,true);rows=x.rows}
 assert.equal(rows.length,5);assert.equal(addToPlate(rows,{id:'kaleidoscope_grilling:raw_beef_skewer'}).ok,false);
});
t('plate removes last skewer and compacts',()=>{
 const rows=[1,2,3].map(n=>({id:'kaleidoscope_grilling:raw_beef_skewer',n}));
 const x=removeLastFromPlate(rows);assert.equal(x.ok,true);assert.equal(x.stack.n,3);assert.deepEqual(x.rows.map(y=>y.n),[1,2]);
});
t('plate eating selects first highest nutrition',()=>{
 const rows=[{id:'a',nutrition:3},{id:'b',nutrition:8},{id:'c',nutrition:8},{id:'d',nutrition:1}];
 assert.equal(highestNutritionIndex(rows,x=>x.nutrition),1);
 const x=takeHighestNutrition(rows,r=>r.nutrition);assert.equal(x.stack.id,'b');assert.deepEqual(x.rows.map(r=>r.id),['a','c','d']);
});
t('recordable set is raw fixed, ordinary, or complete raw secret',()=>{
 assert.equal(isRecordableSkewer('kaleidoscope_grilling:raw_beef_skewer'),true);
 assert.equal(isRecordableSkewer('kaleidoscope_grilling:ordinary_skewer'),true);
 assert.equal(isRecordableSkewer('kaleidoscope_grilling:grilled_beef_skewer'),false);
 assert.equal(isRecordableSkewer('kaleidoscope_grilling:secret_skewer',[{},{},{}]),true);
 assert.equal(isRecordableSkewer('kaleidoscope_grilling:secret_skewer',[{},{}]),false);
});
t('fixed recipe book preserves Java selector alternatives',()=>{
 const b=recordBook({id:'kaleidoscope_grilling:raw_fish_skewer'});
 assert.equal(b.resultId,'kaleidoscope_grilling:raw_fish_skewer');assert.equal(b.stack,null);
 assert.deepEqual(bookIngredients(b),[['minecraft:cod','minecraft:salmon','minecraft:tropical_fish','minecraft:pufferfish']]);
});
t('secret recipe book stores three exact ingredient ids',()=>{
 const b=recordBook({id:'kaleidoscope_grilling:secret_skewer',ingredients:[{id:'minecraft:apple'},{id:'minecraft:bread'},{id:'minecraft:carrot'}],creator:'A'});
 assert.deepEqual(bookIngredients(b),[['minecraft:apple'],['minecraft:bread'],['minecraft:carrot']]);
 assert.equal(b.stack.creator,'A');
});
t('recipe-book plan reserves repeated ingredients from one stack',()=>{
 const b=recordBook({id:'kaleidoscope_grilling:raw_potato_slice_skewer'});
 const p=planBookCraft(b,[{slot:5,id:'kaleidoscope_grilling:potato_slice',count:3}]);
 assert.equal(p.ok,true);assert.deepEqual(p.consumption,[{slot:5,count:3}]);
});
t('recipe-book plan can split repeated ingredients across stacks',()=>{
 const b=recordBook({id:'kaleidoscope_grilling:raw_meatball_skewer'});
 const p=planBookCraft(b,[
  {slot:0,id:'kaleidoscope_cookery:raw_meatball',count:1},
  {slot:1,id:'kaleidoscope_cookery:raw_meatball',count:2}
 ]);
 assert.equal(p.ok,true);assert.deepEqual(p.consumption,[{slot:0,count:1},{slot:1,count:2}]);
});
t('recipe-book plan skips selected/offhand entries and reports missing selector',()=>{
 const b=recordBook({id:'kaleidoscope_grilling:raw_beef_skewer'});
 const p=planBookCraft(b,[
  {slot:0,id:'kaleidoscope_grilling:beef_chunks',count:2,skip:true},
  {slot:1,id:'kaleidoscope_cookery:red_chili',count:1}
 ]);
 assert.equal(p.ok,false);assert.equal(p.reason,'missing');assert.deepEqual(p.missing,['kaleidoscope_grilling:beef_chunks']);
});
t('recipe-book alternatives choose available selector',()=>{
 const b=recordBook({id:'kaleidoscope_grilling:raw_mushroom_skewer'});
 const p=planBookCraft(b,[
  {slot:1,id:'minecraft:red_mushroom',count:2},
  {slot:2,id:'kaleidoscope_grilling:carrot_dice',count:1}
 ]);
 assert.equal(p.ok,true);
});
t('lore summarizes count and recipe inputs',()=>{
 assert.match(plateLore([{id:'x'}])[0],/1\/5/);
 assert.match(bookLore(recordBook({id:'kaleidoscope_grilling:raw_beef_skewer'}))[0],/raw beef skewer|raw_beef_skewer/);
});

console.log(JSON.stringify({passed:n,failed:0,scope:'A2.5 Skewer Plate and Recipe Book Java 1.1.1 semantics'}));
