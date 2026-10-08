/** Fault tests of actual production functions with storage doubles, not Minecraft players. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as core from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a26_oil_machine_core.js';
import {commitSteps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
import {createOilPressRegistry} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/oil_press_registry.js';
const raw=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/a26_oil_machine_runtime.js',import.meta.url),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(function|const))/g,'');
const N='kaleidoscope_grilling:';
class Stack{
 constructor(id,amount=1){this.typeId=id;this.amount=amount;this.maxAmount=id==='minecraft:bucket'?16:id.includes('bucket')?1:64;this.props={};this.lore=[];}
 clone(){const s=Object.assign(new Stack(this.typeId,this.amount),this);s.props={...this.props};s.lore=[...this.lore];return s;}
 isStackableWith(other){return this.typeId===other.typeId;}
}
function fixture({count=16,creative=false,full=false,off=false,potReject=false}={}){
 const dp=new Map(),blocks=new Map(),intervals=[],drops=[],slots=[new Stack('minecraft:bucket',count),full?new Stack('minecraft:stone',64):undefined];
 let offhand=new Stack('minecraft:bucket',count),fault=()=>false,unloaded=false;
 function mayFail(kind,value){if(fault(kind,value))throw Error('injected '+kind);}
 const container={size:2,getItem:i=>slots[i]?.clone(),setItem(i,s){slots[i]=s?.clone();mayFail('slot'+i,s);}};
 const dimension={id:'minecraft:overworld',getBlock(at){if(unloaded)throw Error('unloaded');return blocks.get(at.x+'|'+at.y+'|'+at.z);},playSound(){},spawnItem(stack,location){mayFail('spawn',stack);const e={stack:stack.clone(),remove(){drops.splice(drops.indexOf(e),1);}};drops.push(e);return e;}};
 const world={getDynamicProperty:k=>dp.get(k),getDynamicPropertyIds:()=>[...dp.keys()],setDynamicProperty(k,v){if(v===undefined)dp.delete(k);else dp.set(k,v);mayFail(k,v);},getDimension:()=>dimension,beforeEvents:{playerInteractWithBlock:{subscribe(){}},playerBreakBlock:{subscribe(){}}}};
 const holder={selectedSlotIndex:0,dimension,location:{x:0,y:64,z:0}};
 const context=vm.createContext({...core,commitSteps,createOilPressRegistry,world,console:{warn(){}},ItemStack:Stack,system:{currentTick:0,runInterval(fn){intervals.push(fn)},run(){},runTimeout(){}},creative:()=>creative,playerContainer:()=>container,ensureOilHandPublished:()=>true,held:(_,hand)=>hand==='off'?offhand.clone():slots[0]?.clone(),
  captureWritableHand(_,hand){const before=hand==='off'?offhand.clone():slots[0]?.clone();return {before,write(s){if(hand==='off'){offhand=s?.clone();mayFail('offhand',s);}else container.setItem(0,s);}};},
  COOKERY_EMPTY:'kaleidoscope_cookery:oil_pot',COOKERY_FILLED:'kaleidoscope_cookery:oil_pot_filled',
  readCookeryOilPot:s=>({type:s.props.type,count:s.props.count}),buildCookeryOilPot(type,count,s){if(potReject)return undefined;const out=s.clone();out.typeId='kaleidoscope_cookery:oil_pot_filled';out.props={type,count};return out;},interactionFeedback(){},javaInteractionFeedback(){}});
 vm.runInContext(raw,context);const api=vm.runInContext('({takeVatBucket,fillVatFromBucket,fillPotFromVat,finishPress,interactPress,readVat,writeVat,readPress,writePress,registerPress,registry:pressRegistry})',context);
 function block(id,x){const b={typeId:id,x,y:64,z:0,dimension,location:{x,y:64,z:0},permutation:{withState(){return this},getState(){return 'north'}},setPermutation(){}};blocks.set(x+'|64|0',b);return b;}
 const vat=block(core.BIG_VAT_ID,1);api.writeVat(vat,{type:'canola',buckets:4});
 return {api,vat,block,slots,drops,dp,world,holder,intervals,hand:off?'off':'main',held:()=>off?offhand:slots[0],setFault(fn){fault=fn;},unload(v){unloaded=v;},setPot(){const p=new Stack('kaleidoscope_cookery:oil_pot_filled');p.props={type:'canola',count:8};p.lore=Array.from({length:20},(_,i)=>'custom '+i);slots[0]=p;return p;}};
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
