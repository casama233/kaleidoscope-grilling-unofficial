// Pure source/data regressions. No Minecraft player, host API or UI is simulated.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {SKEWER_RECIPES} from '../../history/integrated-pr/pr1/projects/grilling/gameplay_core/behavior_pack/scripts/a24_skewer_rules.js';
import {A27_ITEMS as old5} from '../../history/integrated-pr/pr5/development/gameplay_core/a27_items_core.js';
import {A27_ITEMS as old6,A27_FOOD} from '../../history/integrated-pr/pr6/development/gameplay_core/a27_content_core.js';
import {recipeTable} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a24_skewering_core.js';
const BP=new URL('../../projects/grilling/gameplay_core/behavior_pack/',import.meta.url);
let n=0;const test=(name,fn)=>{fn();n++;console.log('PASS',name)};
const item=(name)=>JSON.parse(fs.readFileSync(new URL('items/'+name+'.json',BP)))['minecraft:item'];
test('PR1 twenty fixed threading recipes retained by current implementation',()=>{
 const current=recipeTable();assert.equal(SKEWER_RECIPES.length,20);assert.equal(current.length,20);
 for(const old of SKEWER_RECIPES){
  const now=current.find(r=>r.id===old.result);assert.ok(now,old.result);assert.deepEqual(now.slots,old.slots,old.result);
 }
});
test('PR5 all 27 previously missing item identifiers are registered',()=>{
 assert.equal(old5.length,27);
 for(const old of old5)assert.equal(item(old.id).description.identifier,'kaleidoscope_grilling:'+old.id);
});
test('PR6 all 27 item identifiers are registered without duplicate aliases',()=>{
 assert.equal(new Set(old6).size,27);
 assert.deepEqual([...old6].sort(),old5.map(r=>r.id).sort());
 for(const id of old6)assert.equal(item(id).description.identifier,'kaleidoscope_grilling:'+id);
});
test('PR5 food values are preserved',()=>{
 for(const old of old5){
  if(!old.food)continue;const food=item(old.id).components['minecraft:food'];
  assert.equal(food.nutrition,old.food.nutrition,old.id);
  assert.ok(Math.abs(food.saturation_modifier-old.food.saturation)<1e-6,old.id);
 }
});
test('PR6 food values and stack limits are preserved',()=>{
 for(const [id,old] of Object.entries(A27_FOOD)){
  const c=item(id.split(':')[1]).components;assert.equal(c['minecraft:food'].nutrition,old.nutrition,id);
  assert.ok(Math.abs(c['minecraft:food'].saturation_modifier-old.saturation)<1e-6,id);
  assert.equal(c['minecraft:max_stack_size']??64,old.maxStack,id);
 }
});
test('Secret skewer remains on the newer metadata-aware executor',()=>{
 const main=fs.readFileSync(new URL('scripts/main.js',BP),'utf8');
 assert.ok(main.includes('scheduleSkewerAction'));
 assert.ok(!main.includes("from './a24_skewering.js'"));
 assert.ok(!main.includes("from './a24_skewer_rules.js'"));
});
test('Guide and display runtime are each imported once',()=>{
 const main=fs.readFileSync(new URL('scripts/main.js',BP),'utf8');
 for(const name of ['guide/main.js','a2770_placed_visual_runtime.js'])assert.equal(main.split("import './"+name+"';").length-1,1);
});
test('Typed oil-pot event writes retain the A2769 compensation path',()=>{
 const runtime=fs.readFileSync(new URL('scripts/a2736_typed_oil_pot_block_runtime.js',BP),'utf8');
 for(const token of ['interactionIntentStillCurrent(player,intent)','placedOilPotSnapshotMatches(block,snapshot)','handRestored','potRestored'])assert.ok(runtime.includes(token));
});
test('Cuisine accepts event hand but never loses materialized seasoning states',()=>{
 const runtime=fs.readFileSync(new URL('scripts/a2750_cookery_cuisine_runtime.js',BP),'utf8');
 for(const token of ['captureInteractionIntent(player,event.itemStack)',"hand==='main'&&isSpecialSeasoningId(used?.typeId)",'retargetSpecialSeasoningStack','commitTwoParty','typedHeldOil(used)'])assert.ok(runtime.includes(token),token);
});
console.log('Integrated PR preservation: '+n+'/'+n);
