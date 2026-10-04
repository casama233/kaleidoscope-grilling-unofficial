import {canonicalFoodId,eatingItemId,SKEWER_EATING_IDS,isPlainEatingId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_profile_ids.js';
import {FOOD_DATA as actualFoodData} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_data_lookup.js';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
const start=source.indexOf('world.beforeEvents.itemUse.subscribe(e=>{');
const end=source.indexOf('world.beforeEvents.playerInteractWithEntity.subscribe',start);
assert.ok(start>=0&&end>start);
// Execute the production callback in deterministic fixtures, not simulated players.
function fixture({id='fixed',sneak=false,full=true,allowFull=true,hot=false,action=null,cancel=false,animations=true}={}){
 const calls=[];let callback;
 const p={isSneaking:sneak,getComponent:()=>({currentValue:full?20:10,effectiveMax:20})};
 const item={typeId:id==='secret'?'kaleidoscope_grilling:secret_skewer':id,clone(){return this;}};
 vm.runInNewContext(source.slice(start,end),{canonicalFoodId,SKEWER_EATING_IDS,isPlainEatingId,world:{beforeEvents:{itemUse:{subscribe:f=>callback=f}}},FOOD_DATA:new Proxy({fixed:{}},{get:(target,key)=>target[key]??actualFoodData[key]}),SECRET_ID:'kaleidoscope_grilling:secret_skewer',PLATE_ID:'plate',grillingConfig:()=>({fullHungerEating:allowFull,enableEatingAnimations:animations}),canUseSecretSkewer:()=>true,skewerAction:()=>action,scheduleSkewerAction:(_,a)=>calls.push(a),isHot:()=>hot,heldOff:()=>undefined,isFoodStack:()=>true,captureInteractionIntent:()=>({}),system:{run:f=>f()},interactionIntentStillCurrent:()=>true,mainContainer:()=>({}),compactMatchingHotFood:()=>calls.push('merge')});
 const e={source:p,itemStack:item,cancel};callback(e);return {e,calls};
}
test('crouching blocks ordinary fixed secret and plate eating',()=>{for(const id of ['fixed','secret','plate'])assert.equal(fixture({id,sneak:true}).e.cancel,true,id);});
test('configured full-hunger restriction includes plated food',()=>{for(const id of ['fixed','secret','plate']){assert.equal(fixture({id,allowFull:false}).e.cancel,true,id);assert.equal(fixture({id,allowFull:false,full:false}).e.cancel,false,id);assert.equal(fixture({id,allowFull:true}).e.cancel,false,id);}});
test('non-eating actions take precedence even when full and crouching',()=>{for(const action of ['thread','disassemble']){const f=fixture({sneak:action==='disassemble',allowFull:false,action});assert.equal(f.e.cancel,true);assert.deepEqual(f.calls,[action]);}});
test('hot merge remains available with full-hunger eating disabled',()=>{const f=fixture({sneak:true,hot:true,allowFull:false});assert.equal(f.e.cancel,true);assert.deepEqual(f.calls,['merge']);});
test('unrelated items and already-cancelled events are untouched',()=>{assert.equal(fixture({id:'other',sneak:true,allowFull:false}).e.cancel,false);assert.deepEqual(fixture({cancel:true,action:'thread'}).calls,[]);});
const nutrition=source.slice(source.indexOf('function addSecretNutrition('),source.indexOf('function clearContainer('));
function feed(multiplier,hot,startSat=0){const h={currentValue:10,effectiveMax:20,setCurrentValue(n){this.currentValue=n;}},s={currentValue:startSat,setCurrentValue(n){this.currentValue=n;}};const ctx=vm.createContext({dynamicFood:()=>({nutrition:5,saturation:.6}),grillingConfig:()=>({saturationMultiplier:multiplier})});vm.runInContext(nutrition,ctx);ctx.addNestedNutrition({getComponent:id=>id.endsWith('hunger')?h:s},{},{hot});return {h:h.currentValue,s:s.currentValue};}
test('plated hot-food gain honors the same configured multiplier',()=>{for(const multiplier of [1,1.25,2])assert.deepEqual(feed(multiplier,true),{h:15,s:6*multiplier});});
test('cold food has no hot multiplier and saturation stays capped by hunger',()=>{assert.deepEqual(feed(2,false),{h:15,s:6});assert.deepEqual(feed(2,true,14),{h:15,s:15});});
test('thread and insertion use Java success events; oil and flip keep their own event',()=>{assert.ok(source.includes("useSound(player,'action_success',.7,1)"));assert.ok(source.includes("else blockSound(block,'action_success',.65,1)"));assert.ok(source.includes("awardGleamingWithOil(player);blockSound(block,'grill_flip',.75)"));assert.ok(source.includes("javaInteractionFeedback(player,'grill_wait_flip',[r.state.flips,4]);blockSound(block,'grill_flip',.75)"));});

const actionSource=source.slice(source.indexOf('function skewerAction('),source.indexOf('function secretRemainders('));
test('actual dispatch never threads while crouching; disassembly retains priority',()=>{const ctx=vm.createContext({canDisassembleOff:p=>p.disassemble,heldMain:()=>({typeId:'food'}),threadOutcome:()=>({ok:true})});vm.runInContext(actionSource,ctx);assert.equal(ctx.skewerAction({isSneaking:true},{typeId:'food'}),null);assert.equal(ctx.skewerAction({isSneaking:true,disassemble:true},{typeId:'food'}),'disassemble');assert.equal(ctx.skewerAction({isSneaking:false},{typeId:'food'}),'thread');});


test('actual hidden food and secret IDs retain crouch/full-hunger gates and interaction priority',()=>{
 for(const base of ['kaleidoscope_grilling:grilled_gluten_skewer','kaleidoscope_grilling:ordinary_skewer','kaleidoscope_grilling:secret_skewer'])for(const id of [base,eatingItemId(base,true)]){
  assert.equal(fixture({id,sneak:true}).e.cancel,true,id);
  assert.equal(fixture({id,allowFull:false}).e.cancel,true,id);
  assert.equal(fixture({id,allowFull:false,full:false}).e.cancel,false,id);
  assert.deepEqual(fixture({id,sneak:true,allowFull:false,action:'disassemble'}).calls,['disassemble']);
 }
});
