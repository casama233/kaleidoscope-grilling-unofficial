/** Production subscribers/settlement with API doubles; native proof is a separate recording. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as presentation from '../../projects/grilling/gameplay_core/behavior_pack/scripts/player_presentation_core.js';
import {captureEatingIdentity,eatingEventMatches,eatingStillCurrent,commitEating} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_eating_transaction.js';
import {finishedFoodMeta} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/food_finish_core.js';
import {FOOD_DATA,PROFILE_BY_ITEM} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/data.js';

const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
const begin=source.indexOf('world.afterEvents.itemStartUse.subscribe(e=>{');
const end=source.indexOf('// Native use poses cancel',begin);
const settleBegin=source.indexOf('function hungerSettle('),settleEnd=source.indexOf('function resolvedProfile(',settleBegin);
assert.ok(begin>=0&&end>begin&&settleBegin>=0&&settleEnd>settleBegin);
const id='kaleidoscope_grilling:grilled_beef_skewer';
class Stack{
 constructor(amount=2){this.typeId=id;this.amount=amount;this.nameTag='Same native serving';this.props={marker:'retained'};this.lore=['foreign lore'];}
 clone(){return Object.assign(new Stack(this.amount),structuredClone({...this}));}
 getLore(){return [...this.lore]}
 getRawLore(){return this.lore.map(text=>({text}))}
 getDynamicPropertyIds(){return Object.keys(this.props)}
 getDynamicProperty(key){return this.props[key]}
}
function fixture({creative=false,duration=90,profile='FOUR',start=100}={}){
 const mealId=duration===100?'kaleidoscope_grilling:grilled_ender_pearl_skewer':id;
 const callbacks={},queue=[],effects=[],properties=new Map(),nutrition={hunger:10,saturation:2};
 const counts={nativeDebits:0,manualWrites:0,nativeRewards:0,manualRewards:0};
 const state={stack:new Stack(),creative};state.stack.typeId=mealId;
 const hunger={effectiveMax:20,get currentValue(){return nutrition.hunger},setCurrentValue(n){nutrition.hunger=n}};
 const saturation={get currentValue(){return nutrition.saturation},setCurrentValue(n){nutrition.saturation=n}};
 const bag={setItem(_slot,stack){counts.manualWrites++;state.stack=stack?.clone()}};
 const player={id:'native-holder',selectedSlotIndex:3,setProperty:(key,value)=>properties.set(key,value),playAnimation(){},playSound(){return 1},addEffect:(...args)=>effects.push(args),getComponent:type=>type.endsWith('hunger')?hunger:type.endsWith('saturation')?saturation:undefined};
 const ctx={...presentation,world:{afterEvents:Object.fromEntries(['itemStartUse','itemCompleteUse','itemStopUse'].map(name=>[name,{subscribe:fn=>callbacks[name]=fn}]))},system:{currentTick:start,run:fn=>queue.push(fn)},ACTIVE_EATS:new Map(),SETTLED:new Map(),PLATE_EATS:new Map(),PENDING_USES:new Map(),CUISINE_EATS:new Map(),CUISINE_FOOD_SET:new Set(),FOOD_DATA:{[mealId]:FOOD_DATA[mealId]},PROFILE_BY_ITEM:{[mealId]:PROFILE_BY_ITEM[mealId]},JAVA_FP_EATING_ITEMS:[mealId],PENDING_SEASONING:'pending',PLATE_ID:'plate',SECRET_ID:'secret',MYSTERIOUS_ID:'mystery',DARK_ID:'dark',RAW_NAUSEA:{},captureEatingIdentity,eatingEventMatches,eatingStillCurrent,commitEating,finishedFoodMeta,
  now:()=>ctx.system.currentTick,captureInteractionIntent:()=>({hand:'main'}),syncSecretHeld(){},resolvedProfile:presentation.eatingProfile.bind(null),stackMeta:()=>({hot:false,seasonings:['salt'],hotUntil:0}),heldByHand:()=>state.stack?.clone(),copyOne:stack=>{const one=stack.clone();one.amount=1;return one},mainContainer:()=>bag,creative:()=>state.creative,grillingConfig:()=>({saturationMultiplier:1}),dangerousPreservation(){},stopSoundHandle(){},stopEatSound(){},soundFor:()=>'',secretRemainders(){},afterCommitted(_player,_id,_meta,_active,fullNative){counts[fullNative?'nativeRewards':'manualRewards']++}};
 // Production resolvedProfile returns a string, while the imported selector
 // returns its validated descriptor. Keep the real selector and source shape.
 ctx.resolvedProfile=requested=>presentation.eatingProfile(requested).profile;
 const constants=source.match(/const MINIMUM_EAT_TICKS=\d+,RELEASE_CHECKPOINT_GRACE_TICKS=\d+;/)[0]+'\n'+source.match(/const BITE_TIMES=Object.freeze\(\{[\s\S]*?\}\);/)[0];
 vm.runInNewContext(constants+'\n'+source.slice(settleBegin,settleEnd)+'\n'+source.slice(begin,end),ctx);
 let event;
 function startUse(){event={source:player,itemStack:state.stack.clone(),useDuration:duration};callbacks.itemStartUse(event);return ctx.ACTIVE_EATS.get(player.id);}
 function complete({tick=start+duration-1,remaining=0,nativeDebit=false,stack=event.itemStack}={}){
  ctx.system.currentTick=tick;
  if(nativeDebit){counts.nativeDebits++;if(!creative){state.stack=state.stack.amount>1?state.stack.clone():undefined;if(state.stack)state.stack.amount--;}nutrition.hunger=Math.min(20,nutrition.hunger+FOOD_DATA[mealId].nutrition);}
  callbacks.itemCompleteUse({source:player,itemStack:stack,useDuration:remaining});
 }
 function stop({tick=ctx.system.currentTick,remaining=0,stack=event.itemStack}={}){ctx.system.currentTick=tick;callbacks.itemStopUse({source:player,itemStack:stack,useDuration:remaining})}
 function flush(tick=ctx.system.currentTick+1){ctx.system.currentTick=tick;while(queue.length)queue.shift()()}
 return {ctx,state,counts,properties,nutrition,startUse,complete,stop,flush,get event(){return event}};
}

test('inclusive native boundary requires terminal zero and valid nonnegative ticks',()=>{
 for(const duration of [90,100]){
  assert.equal(presentation.nativeEatingCompleted(100,100+duration-2,duration,0),false);
  assert.equal(presentation.nativeEatingCompleted(100,100+duration-1,duration,0),true);
  assert.equal(presentation.nativeEatingCompleted(100,100+duration,duration,0),true);
  for(const remaining of [1,-1,undefined,NaN,'0'])assert.equal(presentation.nativeEatingCompleted(100,100+duration,duration,remaining),false);
 }
 for(const args of [[100,99,90,0],[-1,89,90,0],[NaN,100,90,0],[100,189.5,90,0],[100,190,0,0],[100,190,90.5,0]])assert.equal(presentation.nativeEatingCompleted(...args),false);
});
for(const duration of [90,100])for(const delta of [duration-1,duration])test(`production start/complete accepts native ${duration} at delta${delta}`,()=>{
 const f=fixture({duration,profile:duration===100?'THREE':'FOUR'}),a=f.startUse();
 assert.equal(a.start,100);assert.equal(a.nativeDuration,duration);
 f.complete({tick:100+delta,remaining:0});assert.equal(f.counts.nativeRewards,1);assert.equal(f.ctx.ACTIVE_EATS.size,0);
 for(const key of [presentation.EAT_PROFILE_PROPERTY,presentation.EAT_HAND_PROPERTY,presentation.EAT_NATIVE_TICKS_PROPERTY,presentation.EAT_ELAPSED_TICKS_PROPERTY])assert.equal(f.properties.get(key),0);
 assert.equal(f.properties.get(presentation.EAT_PROJECTION_PROPERTY),false);
});
for(const order of ['complete-first','stop-first'])for(const creative of [false,true])test(`inclusive completion ${order} Creative=${creative} does not debit/reward twice`,()=>{
 const f=fixture({creative});f.startUse();
 if(order==='stop-first')f.stop({tick:189});
 f.complete({tick:189,nativeDebit:true});if(order==='complete-first')f.stop({tick:189});f.flush();
 assert.deepEqual(f.counts,{nativeDebits:1,manualWrites:0,nativeRewards:1,manualRewards:0});
 assert.equal(f.state.stack.amount,creative?2:1);assert.equal(f.nutrition.hunger,15);
 assert.equal(f.state.stack.nameTag,'Same native serving');assert.deepEqual(f.state.stack.props,{marker:'retained'});assert.deepEqual(f.state.stack.lore,['foreign lore']);
 f.complete({tick:190});assert.equal(f.counts.nativeRewards,1);
});
test('early, nonterminal, negative and changed-metadata completion cannot reward current serving',()=>{
 for(const scenario of [{tick:188},{tick:189,remaining:1},{tick:99},{tick:189,remaining:-1}]){
  const f=fixture(),a=f.startUse();f.complete(scenario);assert.equal(f.counts.nativeRewards,0);assert.equal(f.ctx.ACTIVE_EATS.get('native-holder'),a);
 }
 for(const mutate of [s=>s.nameTag='replacement',s=>s.props.marker='changed',s=>s.amount--,s=>s.typeId='minecraft:apple']){
  const f=fixture(),a=f.startUse(),stale=f.event.itemStack.clone();mutate(stale);f.complete({stack:stale});assert.equal(f.counts.nativeRewards,0);assert.equal(f.ctx.ACTIVE_EATS.get('native-holder'),a);
 }
});
test('old stop callback and terminal event cannot remove next-tick auto-repeat',()=>{
 const f=fixture();f.startUse();const previous=f.event.itemStack.clone();f.stop({tick:189});f.complete({tick:189,nativeDebit:true});
 f.ctx.system.currentTick=190;const next=f.startUse();f.flush(190);
 assert.equal(f.ctx.ACTIVE_EATS.get('native-holder'),next);assert.equal(next.start,190);
 f.complete({tick:190,stack:previous});assert.equal(f.ctx.ACTIVE_EATS.get('native-holder'),next);
 assert.deepEqual(f.counts,{nativeDebits:1,manualWrites:0,nativeRewards:1,manualRewards:0});
 assert.equal(f.properties.get(presentation.EAT_NATIVE_TICKS_PROPERTY),90);
});
for(const delta of [23,24,25])test(`real hungerSettle production body retains release${delta} eligibility`,()=>{
 const f=fixture();f.startUse();f.stop({tick:100+delta,remaining:90-delta});f.flush();
 assert.deepEqual(f.counts,{nativeDebits:0,manualWrites:delta>=24?1:0,nativeRewards:0,manualRewards:delta>=24?1:0});
 assert.equal(f.state.stack.amount,delta>=24?1:2);assert.equal(f.nutrition.hunger,delta>=24?15:10);
 f.complete({tick:190});assert.equal(f.counts.nativeRewards,0);
});
