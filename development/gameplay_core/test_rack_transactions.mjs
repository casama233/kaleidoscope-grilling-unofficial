/** Production function bodies with storage doubles, not Minecraft/simulated players. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as core from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2746_advanced_rack_core.js';
import * as plan from '../../projects/grilling/gameplay_core/behavior_pack/scripts/rack_transfer_plan.js';
import {commitSteps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
const base=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const source=name=>fs.readFileSync(new URL(name,base),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(async|function|const))/g,'');
class Stack{
 constructor(typeId,amount=1,tags=[]){Object.assign(this,{typeId,amount,maxAmount:64,tags,nameTag:'named',metadata:{lore:['original'],public:{value:7}}});}
 clone(){const c=Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}));return c;}
 getTags(){return [...this.tags];}
 isStackableWith(s){return s?.typeId===this.typeId&&s.nameTag===this.nameTag&&JSON.stringify(s.metadata)===JSON.stringify(this.metadata);}
}
const seasoning=amount=>new Stack('kaleidoscope_grilling:empty_seasoning_bottle',amount);
function fixture(){
 const dp=new Map(),faults=[],blocks=[];let fail=()=>false;
 const write=(key,fn)=>{fn();if(fail(key))throw Error('Injected '+key);};
 const container=(key,size)=>({size,rows:Array(size),getItem(i){return this.rows[i]?.clone();},setItem(i,s){write(key+':'+i,()=>this.rows[i]=s?.clone());}});
 const inv=container('inv',36),dimension={id:'minecraft:overworld',getBlock:p=>blocks.find(b=>b.x===p.x&&b.y===p.y&&b.z===p.z)};
 const block=(x=0)=>{const b={typeId:core.ADVANCED_RACK_BLOCK_ID,x,y:64,z:0,dimension,location:{x,y:64,z:0},permutation:{getState(){return 0;},withState(){return this;}},setPermutation(){}};b.c=container('rack'+x,9);blocks.push(b);return b;};
 const world={getDynamicProperty:k=>dp.get(k),setDynamicProperty(k,v){write(k,()=>v===undefined?dp.delete(k):dp.set(k,v));},beforeEvents:{playerInteractWithBlock:{subscribe(){}},playerBreakBlock:{subscribe(){}},explosion:{subscribe(){}}}};
 const context=vm.createContext({...core,...plan,commitSteps,world,stationContainer:b=>b.c,console:{warn(){}},system:{beforeEvents:{startup:{subscribe(){}}}},interactionFeedback(){},playerInventory:()=>inv});
 vm.runInContext(source('a2746_rack_state_adapter.js'),context);
 vm.runInContext(source('rack_transactions.js'),context);
 // Isolated module scope keeps actual runtime helper names separate from adapter declarations.
 const load=(name,expose)=>vm.runInContext('(()=>{'+source(name)+';return {'+expose+'};})()',context);
 const runtime=load('a2746_advanced_rack_runtime.js','swapWithHotbar,depositSelected,withdrawToInventory,depositMatching');
 const automation=load('a2746_rack_automation_api.js','borrowAdvancedRackItem,returnAdvancedRackItem');
 const tx=vm.runInContext('({depositInventorySlot,planRackInsert,commitRackTransfer,rackContainer,rackFiltersKey,readRackFilters})',context);
 const holder={selectedSlotIndex:0,dimension,location:{x:0,y:64,z:0},getDynamicProperty:k=>dp.get('holder:'+k),setDynamicProperty:(k,v)=>v===undefined?dp.delete('holder:'+k):dp.set('holder:'+k,v)};
 return {inv,block,world,dp,tx,runtime,automation,holder,dimension,setFault(fn){fail=fn;},failOnce(target){let once=true;fail=key=>once&&key===target?(once=false,true):false;}};
}
const snapshot=f=>JSON.stringify({inv:f.inv.rows,dp:[...f.dp]});
test('Java public rack tags are independent per slot, including dual-tag items',()=>{
 const seasoningTag='kaleidoscope_grilling:advanced_rack_seasonings',toolTag='kaleidoscope_grilling:advanced_rack_tools';
 for(let slot=0;slot<9;slot++){
  assert.equal(core.rackCanPlace(slot,'custom:both',[seasoningTag,toolTag]),true);
  const filter=core.rackCanonicalFilter('custom:both',[seasoningTag,toolTag],slot);
  assert.equal(filter.kind,slot<5?'seasoning':'tool');assert.equal(core.rackCanPlace(slot,'custom:both',[seasoningTag,toolTag],filter),true);
  assert.equal(core.rackCanPlace(slot,'custom:one',[seasoningTag]),slot<5);
  assert.equal(core.rackCanPlace(slot,'custom:one',[toolTag]),slot>=5);
  assert.equal(core.rackCanPlace(slot,'custom:none',[]),false);
 }
});
test('deposit preserves complete native item snapshots and uses pinned source slot',()=>{
 const f=fixture(),b=f.block();f.inv.rows[0]=seasoning(8);const old=f.inv.rows[0].clone();assert.equal(f.runtime.depositSelected(f.holder,b,0),true);
 assert.equal(f.inv.rows[0],undefined);assert.deepEqual(b.c.rows[0],old);assert.ok(f.tx.readRackFilters(b)[0]);
});
for(const target of ['filter','rack','source'])test('deposit '+target+' post-write rejection restores items and exact absent filter property',()=>{
 const f=fixture(),b=f.block();f.inv.rows[0]=seasoning(8);const before=snapshot(f);f.failOnce(target==='filter'?f.tx.rackFiltersKey(b):target==='rack'?'rack0:0':'inv:0');
 assert.equal(f.runtime.depositSelected(f.holder,b,0),false);assert.equal(snapshot(f),before);assert.equal(b.c.rows[0],undefined);
});
test('withdrawal rolls back every earlier inventory merge if later destination write rejects',()=>{
 const f=fixture(),b=f.block();b.c.rows[0]=seasoning(8);f.inv.rows[0]=seasoning(60);const before=snapshot(f);f.failOnce('inv:1');
 assert.equal(f.runtime.withdrawToInventory(f.holder,b,0),false);assert.equal(snapshot(f),before);assert.equal(b.c.rows[0].amount,8);
});
test('withdrawal source rejection rolls back all destination slots',()=>{
 const f=fixture(),b=f.block();b.c.rows[0]=seasoning(8);f.inv.rows[0]=seasoning(60);const before=snapshot(f);f.failOnce('rack0:0');
 assert.equal(f.runtime.withdrawToInventory(f.holder,b,0),false);assert.equal(snapshot(f),before);assert.equal(b.c.rows[0].amount,8);
});
test('full inventory allows only partial withdrawal without loss',()=>{
 const f=fixture(),b=f.block();b.c.rows[0]=seasoning(8);f.inv.rows.fill(new Stack('minecraft:stone',64));f.inv.rows[0]=seasoning(60);
 assert.equal(f.runtime.withdrawToInventory(f.holder,b,0),true);assert.equal(f.inv.rows[0].amount,64);assert.equal(b.c.rows[0].amount,4);
});
for(const target of ['rack0:0','inv:1','inv:2','inv:0'])test('hotbar fallback failure at '+target+' preserves all items and metadata',()=>{
 const f=fixture(),b=f.block();b.c.rows[0]=seasoning(7);f.inv.rows[0]=new Stack('minecraft:cobblestone',8);f.inv.rows[1]=new Stack('minecraft:cobblestone',60);const before=snapshot(f);f.failOnce(target);
 assert.equal(f.runtime.swapWithHotbar(f.holder,b,0),false);assert.equal(snapshot(f),before);assert.equal(b.c.rows[0].amount,7);
});
test('hotbar no-room path leaves source and rack untouched',()=>{
 const f=fixture(),b=f.block();b.c.rows[0]=seasoning(7);f.inv.rows.fill(new Stack('minecraft:stone',64));f.inv.rows[0]=new Stack('minecraft:cobblestone',8);const before=snapshot(f);
 assert.equal(f.runtime.swapWithHotbar(f.holder,b,0),false);assert.equal(snapshot(f),before);assert.equal(b.c.rows[0].amount,7);
});
test('hotbar matching partial merge preserves requested remainder',()=>{
 const f=fixture(),b=f.block();b.c.rows[0]=seasoning(8);f.inv.rows[0]=seasoning(60);assert.equal(f.runtime.swapWithHotbar(f.holder,b,0),true);assert.equal(f.inv.rows[0].amount,64);assert.equal(b.c.rows[0].amount,4);
});
test('depositMatching source failure does not double the deposited stack',()=>{
 const f=fixture(),b=f.block();f.inv.rows[0]=seasoning(8);f.world.setDynamicProperty(f.tx.rackFiltersKey(b),JSON.stringify([core.rackCanonicalFilter(f.inv.rows[0].typeId)]));f.failOnce('inv:0');
 assert.equal(f.runtime.depositMatching(f.holder,b),false);assert.equal(f.inv.rows[0].amount,8);assert.equal(b.c.rows[0],undefined);
});
test('automation filter failure returns the original stack and does not report success',()=>{
 const f=fixture(),b=f.block(),returned=seasoning(8);f.failOnce(f.tx.rackFiltersKey(b));const result=f.automation.returnAdvancedRackItem(f.dimension,{dimension:f.dimension.id,x:0,y:64,z:0,slot:0},returned);
 assert.equal(result.success,false);assert.deepEqual(result.remainder,returned);assert.equal(b.c.rows[0],undefined);assert.equal(f.dp.size,0);
});
test('automation borrow post-write rejection returns no borrowed item and restores source',()=>{
 const f=fixture(),b=f.block();b.c.rows[0]=seasoning(8);f.failOnce('rack0:0');const result=f.automation.borrowAdvancedRackItem(f.dimension,b.location);
 assert.equal(result.success,false);assert.equal(result.stack,undefined);assert.equal(b.c.rows[0].amount,8);
});
test('rollback failure quarantines rack and blocks automatic retry',()=>{
 const f=fixture(),b=f.block();f.inv.rows[0]=seasoning(8);f.setFault(key=>key==='rack0:0');assert.throws(()=>f.runtime.depositSelected(f.holder,b,0),/recovery required/);f.setFault(()=>false);
 assert.ok([...f.dp.keys()].some(k=>k.endsWith('_transaction_fault')));assert.throws(()=>f.tx.rackContainer(b),/quarantined/);
});

test('ambiguous automation return throws recovery-required instead of minting a full remainder',()=>{
 const f=fixture(),b=f.block(),returned=seasoning(8);f.setFault(key=>key==='rack0:0');
 assert.throws(()=>f.automation.returnAdvancedRackItem(f.dimension,{dimension:f.dimension.id,x:0,y:64,z:0,slot:0},returned),/recovery required/);
});
test('malformed filter data fails before any inventory mutation',()=>{
 const f=fixture(),b=f.block();f.inv.rows[0]=seasoning(8);f.world.setDynamicProperty(f.tx.rackFiltersKey(b),'[{"kind":"tool","category":"exact","typeId":"custom:wrong"}]');const before=snapshot(f);
 assert.throws(()=>f.runtime.depositSelected(f.holder,b,0),/Invalid rack filters/);assert.equal(snapshot(f),before);assert.equal(b.c.rows[0],undefined);
});
for(const target of ['rack0:0','rack2:1','inv:0'])test('cross-rack bound return failure '+target+' restores both inventories',()=>{
 const f=fixture(),b=f.block(),other=f.block(2);b.c.rows[0]=seasoning(7);f.inv.rows[0]=new Stack('custom:spice',8,['kaleidoscope_grilling:advanced_rack_seasonings']);
 f.holder.setDynamicProperty('kaleidoscope_grilling:rack_binding_0',JSON.stringify({dimension:f.dimension.id,x:2,y:64,z:0,slot:1}));
 const before=snapshot(f);f.failOnce(target);assert.equal(f.runtime.swapWithHotbar(f.holder,b,0),false);assert.equal(snapshot(f),before);assert.equal(b.c.rows[0].amount,7);assert.equal(other.c.rows[1],undefined);
});
test('cross-rack bound return succeeds before binding switches to requested slot',()=>{
 const f=fixture(),b=f.block(),other=f.block(2);b.c.rows[0]=seasoning(7);f.inv.rows[0]=new Stack('custom:spice',8,['kaleidoscope_grilling:advanced_rack_seasonings']);
 f.holder.setDynamicProperty('kaleidoscope_grilling:rack_binding_0',JSON.stringify({dimension:f.dimension.id,x:2,y:64,z:0,slot:1}));
 assert.equal(f.runtime.swapWithHotbar(f.holder,b,0),true);assert.equal(b.c.rows[0],undefined);assert.equal(other.c.rows[1].amount,8);assert.equal(f.inv.rows[0].amount,7);
 assert.equal(JSON.parse(f.holder.getDynamicProperty('kaleidoscope_grilling:rack_binding_0')).x,0);
});
