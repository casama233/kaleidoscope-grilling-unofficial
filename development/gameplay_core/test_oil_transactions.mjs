/** Fault tests of actual production functions with storage doubles, not Minecraft players. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as core from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a26_oil_machine_core.js';
import {commitSteps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
import {createOilPressRegistry} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/oil_press_registry.js';
import {nativeItemSignature,ownedItemStep} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/owned_item_transaction_core.js';
import {captureInteractionIntentFromStacks,interactionIntentMatchesStacks} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2762_interaction_intent_core.js';
const raw=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/a26_oil_machine_runtime.js',import.meta.url),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(function|const))/g,'');
const N='kaleidoscope_grilling:';
class Stack{
 constructor(id,amount=1){this.typeId=id;this.amount=amount;this.maxAmount=id==='minecraft:bucket'?16:id.includes('bucket')?1:64;this.props={};this.lore=[];this.keepOnDeath=false;this.lockMode='none';}
 clone(){const s=Object.assign(new Stack(this.typeId,this.amount),this);s.props={...this.props};s.lore=[...this.lore];return s;}
 isStackableWith(other){return this.typeId===other.typeId;}
 getComponent(){return undefined}getRawLore(){return this.lore}getLore(){return this.lore}getCanDestroy(){return this.canDestroy??[]}getCanPlaceOn(){return this.canPlaceOn??[]}
 getDynamicPropertyIds(){return Object.keys(this.props)}getDynamicProperty(key){return this.props[key]}getTags(){return []}
}
function fixture({count=16,creative=false,full=false,off=false,potReject=false}={}){
 const dp=new Map(),blocks=new Map(),intervals=[],runs=[],timeouts=[],events={},drops=[],slots=[new Stack('minecraft:bucket',count),full?new Stack('minecraft:stone',64):undefined];
 let offhand=new Stack('minecraft:bucket',count),fault=()=>false,unloaded=false,dropSequence=0;
 function mayFail(kind,value){if(fault(kind,value))throw Error('injected '+kind);}
 const container={size:2,getItem:i=>slots[i]?.clone(),setItem(i,s){slots[i]=s?.clone();mayFail('slot'+i,s);}};
 const dimension={id:'minecraft:overworld',getBlock(at){if(unloaded)throw Error('unloaded');return blocks.get(at.x+'|'+at.y+'|'+at.z);},playSound(){},spawnItem(stack,location){
  mayFail('spawn',stack);const e={id:'drop-'+(++dropSequence),isValid:true,stack:stack.clone(),getComponent:id=>id==='minecraft:item'?{itemStack:e.stack.clone()}:undefined,
   remove(){mayFail('drop_remove_before',e);if(fault('drop_remove_noop',e))return;e.isValid=false;drops.splice(drops.indexOf(e),1);mayFail('drop_remove_after',e);}};
  drops.push(e);mayFail('spawn_after',e);if(fault('spawn_unacknowledged',e))return undefined;return e;
 }};
 const world={getDynamicProperty:k=>dp.get(k),getDynamicPropertyIds:()=>[...dp.keys()],setDynamicProperty(k,v){if(v===undefined)dp.delete(k);else dp.set(k,v);mayFail(k,v);},getDimension:()=>dimension,beforeEvents:{playerInteractWithBlock:{subscribe(fn){events.use=fn}},playerBreakBlock:{subscribe(fn){events.break=fn}}},afterEvents:{playerPlaceBlock:{subscribe(fn){events.place=fn}}}};
 const holder={id:'test-player',selectedSlotIndex:0,dimension,location:{x:0,y:64,z:0}};
 const otherHands=new WeakMap();
 const readHand=(hand,player=holder)=>otherHands.has(player)?otherHands.get(player)[hand]?.clone():hand==='off'?offhand?.clone():slots[0]?.clone();
 const context=vm.createContext({...core,commitSteps,createOilPressRegistry,nativeItemSignature,ownedItemStep,world,console:{warn(){}},ItemStack:Stack,BlockPermutation:{resolve:(id,states={})=>permutation(states,id)},system:{currentTick:0,runInterval(fn){intervals.push(fn)},run(fn){runs.push(fn)},runTimeout(fn){timeouts.push(fn)}},creative:()=>creative,playerContainer:()=>container,ensureOilHandPublished:()=>true,held:(player,hand)=>readHand(hand,player),
  getItemProperty:(stack,key)=>stack.props[key],setItemProperty(stack,key,value){if(value===undefined)delete stack.props[key];else stack.props[key]=value},getItemLore:stack=>stack.lore,setItemLore:(stack,lore)=>stack.lore=[...lore],suppressNumbVisual(){},
  captureInteractionIntent:(player,item)=>captureInteractionIntentFromStacks(item,readHand('main',player),readHand('off',player),0),interactionIntentStillCurrent:(player,intent)=>interactionIntentMatchesStacks(intent,readHand('main',player),readHand('off',player),0),isInitialBlockPress:value=>value!==false,
  captureWritableHand(player,hand){const before=readHand(hand,player);return {before,read:()=>readHand(hand,player),write(s){if(otherHands.has(player))otherHands.get(player)[hand]=s?.clone();else if(hand==='off'){offhand=s?.clone();mayFail('offhand',s);}else container.setItem(0,s);}};},
  COOKERY_EMPTY:'kaleidoscope_cookery:oil_pot',COOKERY_FILLED:'kaleidoscope_cookery:oil_pot_filled',
  readCookeryOilPot:s=>({type:s.props.type,count:s.props.count}),buildCookeryOilPot(type,count,s){if(potReject)return undefined;const out=s.clone();out.typeId='kaleidoscope_cookery:oil_pot_filled';out.props={type,count};return out;},interactionFeedback(){},javaInteractionFeedback(){}});
 vm.runInContext(raw,context);const api=vm.runInContext('({takeVatBucket,fillVatFromBucket,fillPotFromVat,finishPress,interactPress,breakPress,breakVat,vatPacked,readVat,writeVat,readPress,writePress,registerPress,registry:pressRegistry})',context);
 function permutation(states,typeId){return {type:{id:typeId},getAllStates:()=>({...states}),getState:name=>states[name],withState:(name,value)=>permutation({...states,[name]:value},typeId)}}
 function block(id,x){const b={typeId:id,x,y:64,z:0,dimension,location:{x,y:64,z:0},permutation:permutation({'minecraft:cardinal_direction':'north','kaleidoscope_grilling:cake_count':0,'kaleidoscope_grilling:press_stage':0},id),
  setPermutation(value){mayFail('permutation_before',value);this.typeId=value.type.id;this.permutation=value;mayFail('permutation',value)},
  setType(value){this.typeId=value;this.permutation=permutation({},value);mayFail('type',value)}};blocks.set(x+'|64|0',b);return b;}
 const vat=block(core.BIG_VAT_ID,1);api.writeVat(vat,{type:'canola',buckets:4});
 return {api,vat,block,slots,drops,dp,world,holder,intervals,timeouts,events,flush(){while(runs.length)runs.shift()()},hand:off?'off':'main',held:()=>off?offhand:slots[0],setHand(s){if(off)offhand=s?.clone();else slots[0]=s?.clone()},addPlayer(id,stack){const player={...holder,id};otherHands.set(player,{main:stack.clone()});return {holder:player,held:()=>readHand('main',player)}},setFault(fn){fault=fn;},unload(v){unloaded=v;},setPot(){const p=new Stack('kaleidoscope_cookery:oil_pot_filled');p.props={type:'canola',count:8};p.lore=Array.from({length:20},(_,i)=>'custom '+i);slots[0]=p;return p;}};
}
for(const off of [false,true])for(const count of [1,16])test(`${off?'off':'main'} hand bucket count ${count} preserves exact remainder`,()=>{
 const f=fixture({off,count});assert.equal(f.api.takeVatBucket(f.vat,f.holder,f.hand),true);
 assert.equal(f.held().typeId,count===1?N+'canola_oil_bucket':'minecraft:bucket');assert.equal(f.held().amount,count===1?1:15);
 if(count>1)assert.equal(f.slots[1].typeId,N+'canola_oil_bucket');assert.equal(f.api.readVat(f.vat).buckets,3);
});
test('full inventory spills one output, retains15 buckets',()=>{const f=fixture({full:true});f.api.takeVatBucket(f.vat,f.holder,'main');assert.equal(f.held().amount,15);assert.equal(f.drops.length,1);assert.equal(f.drops[0].stack.amount,1);});
test('creative drains one bucket without minting output or changing hand',()=>{const f=fixture({creative:true});f.api.takeVatBucket(f.vat,f.holder,'main');assert.equal(f.held().amount,16);assert.equal(f.slots[1],undefined);assert.equal(f.drops.length,0);assert.equal(f.api.readVat(f.vat).buckets,3);});
for(const kind of ['hand','output','spawn','vat'])test(kind+' write failure rolls back bucket, inventory, drops and vat',()=>{
 const f=fixture({full:kind==='spawn'});let once=true;f.setFault((key,value)=>{if(once&&((kind==='hand'&&key==='slot0')||(kind==='output'&&key==='slot1')||(kind==='spawn'&&key==='spawn')||(kind==='vat'&&key.startsWith(N+'a26_vat_')))){once=false;return true;}return false;});
 assert.throws(()=>f.api.takeVatBucket(f.vat,f.holder,'main'),/transaction failed/);assert.equal(f.held().amount,16);assert.equal(f.held().typeId,'minecraft:bucket');assert.equal(f.api.readVat(f.vat).buckets,4);assert.equal(f.drops.length,0);if(kind!=='spawn')assert.equal(f.slots[1],undefined);
});
test('rejected pot builder never drains oil or mutates lore',()=>{const f=fixture({potReject:true}),p=f.setPot();f.api.fillPotFromVat(f.vat,f.holder,'main',p);assert.equal(f.api.readVat(f.vat).buckets,4);assert.equal(f.held().props.count,8);assert.equal(f.held().lore.length,20);});
test('pot write failure restores both pot and vat',()=>{const f=fixture(),p=f.setPot();let once=true;f.setFault(k=>{if(once&&k.startsWith(N+'a26_vat_')){once=false;return true;}return false;});assert.throws(()=>f.api.fillPotFromVat(f.vat,f.holder,'main',p));assert.equal(f.held().props.count,8);assert.equal(f.api.readVat(f.vat).buckets,4);});
test('press reset failure cannot duplicate four buckets on retry',()=>{
 const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.api.writeVat(f.vat,{type:'',buckets:0});f.api.writePress(press,{cakes:4,progress:16,completionDelay:0});let once=true;
 f.setFault(k=>{if(once&&k.startsWith(N+'a26_press_minecraft_')){once=false;return true;}return false;});
 assert.throws(()=>f.api.finishPress(press));assert.equal(f.api.readVat(f.vat).buckets,0);assert.equal(f.api.readPress(press).cakes,4);assert.equal(f.drops.length,0);
 f.api.finishPress(press);assert.equal(f.api.readVat(f.vat).buckets,4);assert.equal(f.api.readPress(press).cakes,0);assert.equal(f.drops[0].stack.amount,4);
});
test('failed rollback quarantines vat and prevents automatic duplication retry',()=>{
 const f=fixture();f.setFault(k=>k.startsWith(N+'a26_vat_'));assert.throws(()=>f.api.takeVatBucket(f.vat,f.holder,'main'),/rollback failures=1/);f.setFault(()=>false);
 assert.ok([...f.dp.keys()].some(k=>k.startsWith(N+'oil_transaction_fault_')));assert.throws(()=>f.api.takeVatBucket(f.vat,f.holder,'main'),/requires recovery/);
});
test('unloaded chunk retains pending press then resumes once loaded',()=>{
 const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.api.writeVat(f.vat,{type:'',buckets:0});f.api.writePress(press,{cakes:4,progress:16,completionDelay:1});f.unload(true);f.intervals[0]();assert.equal(f.api.registry.rows().length,1);assert.equal(f.api.readPress(press).completionDelay,1);
 f.unload(false);f.intervals[0]();assert.equal(f.api.readVat(f.vat).buckets,4);assert.equal(f.api.registry.rows().length,0);
});
test('300 registry entries persist across independent registry reload',()=>{
 const f=fixture();for(let i=0;i<300;i++)f.api.registerPress(f.block(core.OIL_PRESS_ID,10+i));assert.equal(f.api.registry.rows().length,300);
 const reloaded=createOilPressRegistry(f.world,N+'a26_press_registry');assert.equal(reloaded.rows().length,300);
});
test('legacy registry migration is resumable when a write fails',()=>{
 const dp=new Map([[N+'a26_press_registry',JSON.stringify([{d:'minecraft:overworld',x:1,y:2,z:3},{d:'minecraft:overworld',x:2,y:2,z:3}])]]);let fail=true;
 const world={getDynamicProperty:k=>dp.get(k),getDynamicPropertyIds:()=>[...dp.keys()],setDynamicProperty(k,v){if(fail&&k.endsWith('%7C2%7C2%7C3'))throw Error('migration failure');if(v===undefined)dp.delete(k);else dp.set(k,v);}};
 assert.throws(()=>createOilPressRegistry(world,N+'a26_press_registry').rows());assert.ok(dp.has(N+'a26_press_registry'));fail=false;assert.equal(createOilPressRegistry(world,N+'a26_press_registry').rows().length,2);assert.equal(dp.has(N+'a26_press_registry'),false);
});
test('press stones accept the native addon tag and preserve anvil precedence',()=>{
 assert.equal(core.toolProgress('addon:stone',['kaleidoscope_grilling:press_stones']),1);
 assert.equal(core.toolProgress('minecraft:anvil',['kaleidoscope_grilling:press_stones']),4);
 assert.equal(core.toolProgress('addon:stone',[]),0);
});
test('residue spawn failure restores batch and oil before a retry',()=>{
 const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.api.writeVat(f.vat,{type:'',buckets:0});f.api.writePress(press,{cakes:4,progress:16,completionDelay:0});let once=true;
 f.setFault(k=>{if(once&&k==='spawn'){once=false;return true;}return false;});assert.throws(()=>f.api.finishPress(press));assert.equal(f.api.readVat(f.vat).buckets,0);assert.equal(f.api.readPress(press).cakes,4);assert.equal(f.drops.length,0);
 f.api.finishPress(press);assert.equal(f.api.readVat(f.vat).buckets,4);assert.equal(f.drops[0].stack.amount,4);
});
test('interacting throughout the normal ten-tick completion delay cannot settle early',()=>{
 const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);
 f.api.writeVat(f.vat,{type:'',buckets:0});
 f.api.writePress(press,{cakes:4,progress:16,completionDelay:10});
 for(let tick=0;tick<10;tick++){
  f.api.interactPress(press,f.holder,undefined);
  assert.equal(f.api.readVat(f.vat).buckets,0);
  assert.equal(f.drops.length,0);
  assert.equal(f.api.readPress(press).completionDelay,10-tick);
  f.intervals[0]();
 }
 assert.equal(f.api.readVat(f.vat).buckets,4);
 assert.equal(f.drops.length,1);assert.equal(f.drops[0].stack.amount,4);
 f.api.interactPress(press,f.holder,undefined);f.intervals[0]();
 assert.equal(f.api.readVat(f.vat).buckets,4);assert.equal(f.drops.length,1);
});
test('container waiting after completion still retries immediately on interaction',()=>{
 const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);
 f.api.writeVat(f.vat,{type:'',buckets:0});
 f.api.writePress(press,{cakes:4,progress:16,completionDelay:0,waiting:true});
 f.api.interactPress(press,f.holder,undefined);
 assert.equal(f.api.readVat(f.vat).buckets,4);assert.equal(f.api.readPress(press).cakes,0);
 assert.equal(f.drops.length,1);
});
function cakeGesture(f,press,participant=f){const event={block:press,player:participant.holder,itemStack:participant.held().clone(),cancel:false,isFirstEvent:true};f.events.use(event);assert.equal(event.cancel,true);return event}
test('deferred cake insertion refuses removed, replaced and already-cancelled targets',()=>{
 for(const change of ['air','same-type-placement','cancelled']){
  const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.setHand(new Stack(core.OIL_CAKE_ID,2));
  if(change==='cancelled')f.events.use({block:press,player:f.holder,itemStack:f.held().clone(),cancel:true,isFirstEvent:true});
  else{
   cakeGesture(f,press);
   if(change==='air')press.typeId='minecraft:air';
   if(change==='same-type-placement')f.events.place({block:f.block(core.OIL_PRESS_ID,0)});
  }
  const saved=[...f.dp.entries()];f.flush();assert.equal(f.held().amount,2,change);assert.deepEqual([...f.dp.entries()],saved,change);
 }
});
test('two queued players use the same press instance in order against its latest capacity',()=>{
 for(const cakes of [2,3]){
  const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.events.place({block:press});f.api.writePress(press,{cakes});
  const first=new Stack(core.OIL_CAKE_ID,2);first.nameTag='first player';f.setHand(first);
  const secondStack=new Stack(core.OIL_CAKE_ID,2);secondStack.nameTag='second player';const second=f.addPlayer('second-player',secondStack);
  cakeGesture(f,press);cakeGesture(f,press,second);f.flush();
  assert.equal(f.api.readPress(press).cakes,4);assert.equal(f.held().amount,1);
  assert.equal(second.held().amount,cakes===2?1:2,'second gesture must fill available capacity, or keep its cake when full');
  assert.equal(f.held().nameTag,'first player');assert.equal(second.held().nameTag,'second player');assert.equal(f.drops.length,0);
 }
});
test('cake insertion debits the captured main or offhand and preserves native metadata',()=>{
 for(const off of [false,true]){
  const f=fixture({off}),press=f.block(core.OIL_PRESS_ID,0),cake=new Stack(core.OIL_CAKE_ID,2);cake.nameTag='owned cake';cake.lore=['custom'];cake.canPlaceOn=['minecraft:stone'];f.setHand(cake);
  cakeGesture(f,press);f.flush();const expected=cake.clone();expected.amount=1;
  assert.deepEqual(f.held(),expected);assert.equal(f.api.readPress(press).cakes,1);assert.equal(press.permutation.getState(N+'cake_count'),1);
 }
});
test('post-write cake debit and saved-credit failures restore only confirmed owned values',()=>{
 for(const kind of ['hand','save','projection']){
  const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.setHand(new Stack(core.OIL_CAKE_ID,2));let once=true;
  f.setFault(key=>{if(once&&(kind==='hand'&&key==='slot0'||kind==='save'&&key.startsWith(N+'a26_press_minecraft_')||kind==='projection'&&key==='permutation')){once=false;return true}return false});
  // syncPress catches an exception after a successful native projection; its
  // readback is authoritative, so that branch can safely finish the credit.
  if(kind==='projection'){assert.equal(f.api.interactPress(press,f.holder,f.held(),'main'),undefined);assert.equal(f.held().amount,1);assert.equal(f.api.readPress(press).cakes,1)}
  else{assert.throws(()=>f.api.interactPress(press,f.holder,f.held(),'main'),/transaction failed/);assert.equal(f.held().amount,2);assert.equal(f.api.readPress(press).cakes,0);assert.equal(press.permutation.getState(N+'cake_count'),0)}
 }
});
test('failed cake credit cannot refund over a replacement hand or overwrite foreign press state',()=>{
 for(const change of ['hand','press']){
  const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.setHand(new Stack(core.OIL_CAKE_ID,2));let once=true;
  f.setFault(key=>{
   if(!once||!key.startsWith(N+'a26_press_minecraft_'))return false;once=false;
   if(change==='hand'){const foreign=f.held().clone();foreign.nameTag='another owner';f.setHand(foreign)}
   else f.dp.set(key,JSON.stringify(core.normalizePress({cakes:3})));
   return true;
  });
  assert.throws(()=>f.api.interactPress(press,f.holder,f.held(),'main'),/transaction failed/);
  assert.equal(f.held().amount,1);if(change==='hand')assert.equal(f.held().nameTag,'another owner');else assert.equal(f.api.readPress(press).cakes,3);
  assert.ok([...f.dp.keys()].some(key=>key.startsWith(N+'oil_transaction_fault_')));
  assert.throws(()=>f.api.interactPress(press,f.holder,f.held(),'main'),/requires recovery/);
 }
});
test('delayed hammer hit keeps other players progress but cannot strike a new press instance',()=>{
 for(const replace of [false,true]){
  const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.api.writePress(press,{cakes:4,progress:0});f.setHand(new Stack('minecraft:anvil'));
  f.api.interactPress(press,f.holder,f.held(),'main');assert.equal(f.timeouts.length,1);
  const target=replace?f.block(core.OIL_PRESS_ID,0):press;if(replace)f.events.place({block:target});
  f.api.writePress(target,{cakes:4,progress:2});f.timeouts.shift()();assert.equal(f.api.readPress(target).progress,replace?2:6);
 }
});
function breakGesture(f,block,cancel=false){const event={block,player:f.holder,cancel};f.events.break(event);return event}
const recoveryRows=f=>[...f.dp.entries()].filter(([key])=>key.startsWith(N+'oil_transaction_fault_'));
test('deferred machine break refuses cancellations, same-type placements, changed contents and foreign blocks',()=>{
 for(const type of [core.OIL_PRESS_ID,core.BIG_VAT_ID])for(const change of ['already-cancelled','late-uncancel','same-type','foreign','contents','unloaded']){
  const f=fixture(),machine=type===core.OIL_PRESS_ID?f.block(type,0):f.vat;
  if(type===core.OIL_PRESS_ID)f.api.writePress(machine,{cakes:3,progress:4});
  const event=breakGesture(f,machine,change==='already-cancelled');let current=machine;
  if(change==='late-uncancel')event.cancel=false;
  if(change==='same-type'){current=f.block(type,machine.x);f.events.place({block:current})}
  if(change==='foreign')current=f.block('minecraft:stone',machine.x);
  if(change==='contents'){if(type===core.OIL_PRESS_ID)f.api.writePress(machine,{cakes:4,progress:4});else f.api.writeVat(machine,{type:'premium_chili',buckets:6})}
  if(change==='unloaded')f.unload(true);
  const saved=Object.fromEntries(f.dp);f.flush();assert.equal(f.drops.length,0,change);assert.deepEqual(Object.fromEntries(f.dp),saved,change);assert.equal(current.typeId,change==='foreign'?'minecraft:stone':type,change);
 }
});
test('break preserves Java press cakes, packed vat contents and creative no-drop rules',()=>{
 for(const creative of [false,true]){
  const f=fixture({creative}),press=f.block(core.OIL_PRESS_ID,0);f.api.writePress(press,{cakes:3,progress:5});breakGesture(f,press);f.flush();
  assert.equal(press.typeId,'minecraft:air');assert.equal(f.api.readPress(press).cakes,0);
  assert.deepEqual(f.drops.map(e=>[e.stack.typeId,e.stack.amount]),creative?[]:[[core.OIL_PRESS_ID,1],[core.OIL_CAKE_ID,3]]);assert.equal(recoveryRows(f).length,0);
  const v=fixture({creative});v.api.writeVat(v.vat,{type:'premium_chili',buckets:7});breakGesture(v,v.vat);v.flush();
  assert.equal(v.vat.typeId,'minecraft:air');assert.equal(v.api.readVat(v.vat).buckets,0);assert.equal(v.drops.length,creative?0:1);
  if(!creative)assert.deepEqual({...v.api.vatPacked(v.drops[0].stack)},{type:'premium_chili',buckets:7});assert.equal(recoveryRows(v).length,0);
 }
 const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.api.writePress(press,{cakes:4,progress:16,completionDelay:8});breakGesture(f,press);
 f.api.writePress(press,{cakes:4,progress:16,completionDelay:7});f.flush();assert.equal(press.typeId,'minecraft:air','timer-only advance must not prevent removal');assert.equal(f.drops[1].stack.amount,4);
});
test('rejected block removal restores its claim without clearing source data or producing drops',()=>{
 const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.api.writePress(press,{cakes:4,progress:16,completionDelay:8});const before=Object.fromEntries(f.dp);let once=true;
 f.setFault(key=>{if(once&&key==='permutation_before'){once=false;return true}return false});
 assert.throws(()=>f.api.breakPress(press,f.holder),/transaction failed/);assert.equal(press.typeId,core.OIL_PRESS_ID);assert.deepEqual(Object.fromEntries(f.dp),before);assert.equal(f.drops.length,0);assert.equal(f.api.registry.rows().length,1);
});
test('unknown second drop keeps a full recovery receipt and never refunds or retries its source',()=>{
 for(const outcome of ['before','after','unacknowledged']){
  const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.api.writePress(press,{cakes:3,progress:5});
  f.setFault((key,value)=>outcome==='before'?key==='spawn'&&value.typeId===core.OIL_CAKE_ID:key===(outcome==='after'?'spawn_after':'spawn_unacknowledged')&&value.stack.typeId===core.OIL_CAKE_ID);
  assert.throws(()=>f.api.breakPress(press,f.holder),/transaction failed/);assert.equal(press.typeId,'minecraft:air');assert.equal(f.api.readPress(press).cakes,0);
  assert.equal(f.drops.length,outcome==='before'?0:1);const [[faultKey,raw]]=recoveryRows(f),receipt=JSON.parse(raw);
  assert.equal(receipt.phase,'incomplete');assert.equal(JSON.parse(receipt.saved).cakes,3);assert.equal(receipt.outputs[0].recovered,true);assert.equal(receipt.outputs[1].attempted,true);assert.equal(receipt.outputs[1].recovered,false);
  f.setFault(()=>false);const replacement=f.block(core.OIL_PRESS_ID,0);f.events.place({block:replacement});assert.equal(f.dp.get(faultKey),raw,'placement must preserve unresolved escrow');
  assert.throws(()=>f.api.breakPress(replacement,f.holder),/requires recovery/);assert.equal(f.drops.length,outcome==='before'?0:1);
 }
});
function rejectFinalRelease(f,extra=()=>false){let prepared,once=true;f.setFault((key,value)=>{
 if(key.startsWith(N+'oil_transaction_fault_')){
  if(typeof value==='string')prepared=value;
  else if(once){once=false;f.dp.set(key,prepared);return true}
 }
 return extra(key,value);
});}
test('confirmed drop removal, including native post-apply throws, permits exact source and registry rollback',()=>{
 const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.api.writePress(press,{cakes:4,progress:16,completionDelay:8});const before=Object.fromEntries(f.dp);
 rejectFinalRelease(f,key=>key==='drop_remove_after');assert.throws(()=>f.api.breakPress(press,f.holder),/transaction failed/);
 assert.equal(press.typeId,core.OIL_PRESS_ID);assert.deepEqual(Object.fromEntries(f.dp),before);assert.equal(f.drops.length,0);assert.equal(f.api.registry.rows().length,1);
 f.setFault(()=>false);f.api.breakPress(press,f.holder);assert.equal(f.drops.length,2);assert.equal(f.drops[1].stack.amount,4);assert.equal(f.api.registry.rows().length,0);
});
test('rollback never overwrites a replacement block or its saved data',()=>{
 const f=fixture(),press=f.block(core.OIL_PRESS_ID,0);f.api.writePress(press,{cakes:3,progress:5});let foreign,once=true;
 const stateKey=N+'a26_press_minecraft_overworld_p0_p64_p0',foreignRaw=JSON.stringify(core.normalizePress({cakes:1}));
 f.setFault(key=>{if(once&&key==='spawn_after'){once=false;foreign=f.block('minecraft:stone',0);f.dp.set(stateKey,foreignRaw)}return false});
 assert.throws(()=>f.api.breakPress(press,f.holder),/transaction failed/);assert.equal(foreign.typeId,'minecraft:stone');assert.equal(f.dp.get(stateKey),foreignRaw);assert.equal(f.drops.length,0);
 const receipt=JSON.parse(recoveryRows(f)[0][1]);assert.equal(receipt.phase,'incomplete');assert.equal(JSON.parse(receipt.saved).cakes,3);assert.equal(receipt.sourceRecovered,false);
});
test('unconfirmed drop removal retains paid output and never recreates a full vat',()=>{
 const f=fixture();rejectFinalRelease(f,key=>key==='drop_remove_noop');assert.throws(()=>f.api.breakVat(f.vat,f.holder),/transaction failed/);
 assert.equal(f.vat.typeId,'minecraft:air');assert.equal(f.api.readVat(f.vat).buckets,0);assert.equal(f.drops.length,1);assert.equal(f.api.vatPacked(f.drops[0].stack).buckets,4);
 const receipt=JSON.parse(recoveryRows(f)[0][1]);assert.equal(receipt.phase,'incomplete');assert.equal(receipt.outputs[0].confirmed,true);assert.equal(receipt.outputs[0].recovered,false);assert.equal(receipt.sourceRecovered,false);
});
for(const change of ['air','same-type-instance'])test(`deferred vat interaction refuses ${change} without changing its captured bucket`,()=>{
 const f=fixture({count:1}),event={block:f.vat,player:f.holder,itemStack:f.held().clone(),cancel:false,isFirstEvent:true};
 f.events.use(event);assert.equal(event.cancel,true);let current=f.vat;
 if(change==='air')current.setType('minecraft:air');
 else{current=f.block(core.BIG_VAT_ID,f.vat.x);f.events.place({block:current});f.api.writeVat(current,{type:'canola',buckets:4})}
 const before=Object.fromEntries(f.dp);f.flush();assert.deepEqual(Object.fromEntries(f.dp),before);assert.equal(f.drops.length,0);
 assert.equal(f.held().typeId,'minecraft:bucket');assert.equal(f.held().amount,1);assert.equal(f.slots[1],undefined);
 assert.equal(current.typeId,change==='air'?'minecraft:air':core.BIG_VAT_ID);assert.equal(f.api.readVat(current).buckets,4);
});
