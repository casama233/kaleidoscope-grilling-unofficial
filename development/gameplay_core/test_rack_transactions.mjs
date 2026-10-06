/** Production function bodies with storage doubles, not Minecraft/simulated players. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as core from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2746_advanced_rack_core.js';
import * as plan from '../../projects/grilling/gameplay_core/behavior_pack/scripts/rack_transfer_plan.js';
import {commitSteps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
import * as layout from '../../projects/grilling/gameplay_core/behavior_pack/scripts/advanced_rack_layout.js';
import {rackSlotAtHit} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_rack_quick_pick.js';
import {captureInteractionIntentFromStacks,interactionIntentMatchesStacks,captureStackIntentSnapshot,stackIntentSnapshotMatches} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2762_interaction_intent_core.js';
const base=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const rackStateDomains=JSON.parse(fs.readFileSync(new URL('../blocks/advanced_rack_block.json',base),'utf8'))['minecraft:block'].description.states;
const source=name=>fs.readFileSync(new URL(name,base),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(async|function|const))/g,'');
class Stack{
 constructor(typeId,amount=1,tags=[]){Object.assign(this,{typeId,amount,maxAmount:64,tags,nameTag:'named',keepOnDeath:false,lockMode:'none',metadata:{lore:['original'],public:{value:7}}});}
 clone(){const c=Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}));return c;}
 getTags(){return [...this.tags];}
 getRawLore(){return [...this.metadata.lore];}
 getCanDestroy(){return this.metadata.canDestroy??[];}
 getCanPlaceOn(){return this.metadata.canPlaceOn??[];}
 getComponent(id){return id==='minecraft:durability'?{damage:this.metadata.damage??0}:undefined;}
 isStackableWith(s){return s?.typeId===this.typeId&&s.nameTag===this.nameTag&&JSON.stringify(s.metadata)===JSON.stringify(this.metadata);}
}
const seasoning=amount=>new Stack('kaleidoscope_grilling:empty_seasoning_bottle',amount);
function fixture(){
 const dp=new Map(),faults=[],blocks=[],queue=[],callbacks={},commands=new Map(),dirty=[],sounds=[],logs=[];let fail=()=>false,startup;
 const write=(key,fn)=>{fn();if(fail(key))throw Error('Injected '+key);};
 const container=(key,size)=>({size,rows:Array(size),getItem(i){return this.rows[i]?.clone();},setItem(i,s){write(key+':'+i,()=>this.rows[i]=s?.clone());}});
 const inv=container('inv',36),dimension={id:'minecraft:overworld',getBlock:p=>blocks.find(b=>b.x===p.x&&b.y===p.y&&b.z===p.z),playSound:(...args)=>sounds.push(args)};
 const permutation=states=>({getState:name=>states[name],withState(name,value){
  const domain=name==='minecraft:cardinal_direction'?['north','east','south','west']:rackStateDomains[name];
  assert.ok(domain?.includes(value),`${name} cannot store ${value}`);return permutation({...states,[name]:value});
 }});
 const block=(x=0)=>{const b={typeId:core.ADVANCED_RACK_BLOCK_ID,x,y:64,z:0,dimension,location:{x,y:64,z:0},permutation:permutation({'minecraft:cardinal_direction':'north','kaleidoscope_grilling:spice_level':0,[layout.RACK_OCCUPANCY_STATE]:0,[layout.RACK_OCCUPANCY_HIGH_STATE]:0}),permutationWrites:0,setPermutation(p){this.permutationWrites++;write('permutation'+x,()=>this.permutation=p);}};b.c=container('rack'+x,9);blocks.push(b);return b;};
 const world={getDynamicProperty:k=>dp.get(k),setDynamicProperty(k,v){write(k,()=>v===undefined?dp.delete(k):dp.set(k,v));},beforeEvents:Object.fromEntries(['playerInteractWithBlock','playerBreakBlock','explosion'].map(name=>[name,{subscribe(fn){callbacks[name]=fn;}}]))};
 const playerInventory=p=>p.inv??inv;
 const context=vm.createContext({...core,...plan,...layout,rackSlotAtHit,commitSteps,captureStackIntentSnapshot,stackIntentSnapshotMatches,world,stationContainer:b=>b.c,console:{warn:(...args)=>logs.push(args.join(' '))},system:{run:fn=>queue.push(fn),beforeEvents:{startup:{subscribe(fn){startup=fn;}}}},CommandPermissionLevel:{Any:0},interactionFeedback(){},markStationContentsDirty:b=>dirty.push(b),playerInventory,getMainHand:p=>playerInventory(p).getItem(p.selectedSlotIndex),captureInteractionIntent:(p,e)=>captureInteractionIntentFromStacks(e,playerInventory(p).getItem(p.selectedSlotIndex),p.offhand,p.selectedSlotIndex),interactionIntentStillCurrent:(p,intent)=>interactionIntentMatchesStacks(intent,playerInventory(p).getItem(p.selectedSlotIndex),p.offhand,p.selectedSlotIndex)});
 vm.runInContext(source('a2746_rack_state_adapter.js'),context);
 vm.runInContext(source('rack_transactions.js'),context);
 // Isolated module scope keeps actual runtime helper names separate from adapter declarations.
 const load=(name,expose)=>vm.runInContext('(()=>{'+source(name)+';return {'+expose+'};})()',context);
 const runtime=load('a2746_advanced_rack_runtime.js','swapWithHotbar,depositSelected,withdrawToInventory,depositMatching,interactRackSlot,clearEmptySlotFilter');
 const automation=load('a2746_rack_automation_api.js','borrowAdvancedRackItem,returnAdvancedRackItem');
 const tx=vm.runInContext('({depositInventorySlot,planRackInsert,commitRackTransfer,rackContainer,rackFiltersKey,readRackFilters,syncRackDisplay})',context);
 const holder={typeId:'minecraft:player',isValid:true,isSneaking:false,selectedSlotIndex:0,dimension,location:{x:0,y:64,z:0},getDynamicProperty:k=>dp.get('holder:'+k),setDynamicProperty:(k,v)=>v===undefined?dp.delete('holder:'+k):dp.set('holder:'+k,v)};
 return {logs,inv,block,world,dp,tx,runtime,automation,holder,dimension,dirty,sounds,callbacks,commands,makeInventory:name=>container(name,36),flush(){while(queue.length)queue.shift()();},start(){startup({customCommandRegistry:{registerCommand(spec,run){commands.set(spec.name,{spec,run});}}});},setFault(fn){fail=fn;},failOnce(target){let once=true;fail=key=>once&&key===target?(once=false,true):false;}};
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

const tool=()=>{const s=new Stack('kaleidoscope_cookery:iron_kitchen_knife');s.maxAmount=1;s.metadata.canDestroy=['minecraft:stone'];s.metadata.canPlaceOn=['minecraft:dirt'];s.metadata.damage=19;return s;};
function click(f,b,slot,options={}){
 const p=options.player??f.holder,direction=b.permutation.getState('minecraft:cardinal_direction'),x=slot<5?layout.RACK_SEASONING_X[slot]:layout.RACK_TOOL_X[slot-5];
 const at=layout.rackDisplayPose(b,x,slot<5?12/16:6/16,.35).location;
 const e={cancel:false,isFirstEvent:true,block:b,player:p,itemStack:(p.inv??f.inv).getItem(p.selectedSlotIndex),faceLocation:{x:at.x-b.x,y:at.y-b.y,z:at.z-b.z},...options};
 f.callbacks.playerInteractWithBlock(e);return e;
}
test('normal event deposits into each empty clicked slot and empty-hand pickup returns exact metadata, all facings',()=>{
 for(const facing of ['north','east','south','west'])for(let slot=0;slot<9;slot++){
  const f=fixture(),b=f.block();b.permutation=b.permutation.withState('minecraft:cardinal_direction',facing);
  for(let i=0;i<9;i++)if(i!==slot)b.c.rows[i]=i<5?seasoning(3):tool();
  const neighbors=JSON.stringify(b.c.rows),held=slot<5?seasoning(9):tool();f.inv.rows[0]=held.clone();
  assert.equal(click(f,b,slot).cancel,true);f.flush();assert.deepEqual(b.c.rows[slot],held);assert.equal(f.inv.rows[0],undefined);
  click(f,b,slot);f.flush();assert.deepEqual(f.inv.rows[0],held);assert.equal(b.c.rows[slot],undefined);assert.equal(JSON.stringify(b.c.rows),neighbors);
  assert.deepEqual(f.sounds.map(row=>row[0]),['item.item_frame.add_item','item.item_frame.remove_item']);
 }
});
test('normal held-item click never withdraws or overwrites an occupied slot; full inventory rejects unsafe sneak swap',()=>{
 const f=fixture(),b=f.block();b.c.rows[0]=seasoning(64);f.inv.rows.fill(new Stack('minecraft:stone',64));const before=snapshot(f),stored=b.c.rows[0].clone();
 assert.equal(f.runtime.interactRackSlot(f.holder,b,0),false);assert.equal(f.runtime.interactRackSlot(f.holder,b,0,true),false);
 assert.equal(snapshot(f),before);assert.deepEqual(b.c.rows[0],stored);assert.equal(f.sounds.length,0);
});
test('sneak swaps retain advanced binding; only empty-hand sneak clears an empty filter transactionally',()=>{
 const f=fixture(),b=f.block();f.inv.rows[0]=seasoning(8);assert.equal(f.runtime.interactRackSlot(f.holder,b,0),'insert');
 assert.equal(f.runtime.interactRackSlot(f.holder,b,0),'pickup');assert.ok(f.tx.readRackFilters(b)[0]);
 f.inv.rows[0]=undefined;assert.equal(f.runtime.interactRackSlot(f.holder,b,0),false);assert.ok(f.tx.readRackFilters(b)[0]);
 const before=snapshot(f);f.failOnce(f.tx.rackFiltersKey(b));assert.equal(f.runtime.interactRackSlot(f.holder,b,0,true),false);assert.equal(snapshot(f),before);
 assert.equal(f.runtime.interactRackSlot(f.holder,b,0,true),'clear_filter');assert.equal(f.tx.readRackFilters(b)[0],null);
 b.c.rows[1]=seasoning(7);f.inv.rows[0]=new Stack('minecraft:cobblestone',8);assert.equal(f.runtime.interactRackSlot(f.holder,b,1,true),'swap');
 assert.equal(f.inv.rows[0].amount,7);assert.equal(f.inv.rows[1].typeId,'minecraft:cobblestone');assert.equal(b.c.rows[1],undefined);
});
test('direct insert failures roll back complete item ownership and filter before any sound',()=>{
 for(const target of ['filter','rack','hand']){
  const f=fixture(),b=f.block();f.inv.rows[0]=seasoning(8);const held=f.inv.rows[0].clone(),before=snapshot(f);
  f.failOnce(target==='filter'?f.tx.rackFiltersKey(b):target==='rack'?'rack0:0':'inv:0');click(f,b,0);f.flush();
  assert.equal(snapshot(f),before);assert.deepEqual(f.inv.rows[0],held);assert.equal(b.c.rows[0],undefined);assert.equal(f.sounds.length,0);
 }
});
test('deferred event rejects repeat, offhand and stale player/hand/facing/rack intent',()=>{
 const mutations=[f=>{f.holder.selectedSlotIndex=1;},f=>{f.inv.rows[0].amount--;},f=>{f.inv.rows[0].metadata.canDestroy=['minecraft:obsidian'];},f=>{f.holder.isSneaking=true;},f=>{f.holder.location.x=100;},f=>{f.holder.dimension={id:'minecraft:nether'};},f=>{f.holder.isValid=false;},(f,b)=>{b.permutation=b.permutation.withState('minecraft:cardinal_direction','east');},(f,b)=>{b.typeId='minecraft:air';}];
 for(const change of mutations){const f=fixture(),b=f.block();f.inv.rows[0]=seasoning(8);click(f,b,0);change(f,b);const hand=f.inv.rows[0]?.clone();f.flush();assert.deepEqual(f.inv.rows[0],hand);assert.equal(b.c.rows[0],undefined);}
 for(const options of [{isFirstEvent:false},{offhand:true}]){
  const f=fixture(),b=f.block();f.inv.rows[0]=seasoning(8);f.holder.offhand=tool();const before=snapshot(f);
  click(f,b,0,options.offhand?{itemStack:f.holder.offhand}:options);f.flush();assert.equal(snapshot(f),before);assert.equal(b.c.rows[0],undefined);
 }
});
test('queued two-player clicks re-read live slot contents and conserve both inventories',()=>{
 const f=fixture(),b=f.block(),p2={...f.holder,inv:f.makeInventory('other'),getDynamicProperty(){},setDynamicProperty(){}};
 f.inv.rows[0]=seasoning(8);p2.inv.rows[0]=seasoning(9);click(f,b,0);click(f,b,0,{player:p2});f.flush();
 assert.equal(b.c.rows[0].amount,17);assert.equal(f.inv.rows[0],undefined);assert.equal(p2.inv.rows[0],undefined);
 click(f,b,0);click(f,b,0,{player:p2});f.flush();assert.equal(f.inv.rows[0].amount,17);assert.equal(p2.inv.rows[0],undefined);assert.equal(b.c.rows[0],undefined);
 f.inv.rows[0]=tool();p2.inv.rows[0]=tool();click(f,b,8);click(f,b,8,{player:p2});f.flush();assert.ok(b.c.rows[8]);assert.equal(f.inv.rows[0],undefined);assert.ok(p2.inv.rows[0]);
});
test('saved rack display occupancy rebuild changes only derived permutation state, keeping all9 native stacks and filters',()=>{
 const f=fixture(),b=f.block();for(const slot of [0,2,4,5,6,7,8])b.c.rows[slot]=slot<5?seasoning(slot+2):tool();
 f.world.setDynamicProperty(f.tx.rackFiltersKey(b),JSON.stringify([core.rackCanonicalFilter(seasoning(1).typeId)]));
 const contents=JSON.stringify(b.c.rows),before=snapshot(f);assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_STATE),0);f.tx.syncRackDisplay(b);
 assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_STATE),5);assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_HIGH_STATE),1);assert.equal(b.permutation.getState('kaleidoscope_grilling:spice_level'),3);
 assert.equal(JSON.stringify(b.c.rows),contents);assert.equal(snapshot(f),before);
});
test('production display sync projects all32 masks to legal low/high states and unchanged repeats are no-ops',()=>{
 for(let mask=0;mask<32;mask++){
  const f=fixture(),b=f.block();for(let slot=0;slot<9;slot++)if(slot>=5||(mask&(1<<slot)))b.c.rows[slot]=slot<5?seasoning(slot+2):tool();
  f.world.setDynamicProperty(f.tx.rackFiltersKey(b),JSON.stringify([core.rackCanonicalFilter(seasoning(1).typeId)]));
  const contents=JSON.stringify(b.c.rows),before=snapshot(f),level=Math.min(4,[0,1,2,3,4].filter(slot=>mask&(1<<slot)).length);
  assert.equal(f.tx.syncRackDisplay(b),level);
  assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_STATE),mask&15,`mask${mask} low`);
  assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_HIGH_STATE),mask>>4,`mask${mask} high`);
  assert.equal(b.permutation.getState('kaleidoscope_grilling:spice_level'),level);
  assert.equal(b.permutation.getState('minecraft:cardinal_direction'),'north');
  const permutation=b.permutation,writes=b.permutationWrites;assert.equal(writes,mask===0?0:1);
  assert.equal(f.tx.syncRackDisplay(b),level);assert.equal(b.permutation,permutation);assert.equal(b.permutationWrites,writes);
  assert.equal(JSON.stringify(b.c.rows),contents);assert.equal(snapshot(f),before);
 }
});
test('known display snapshots synchronize masks16 and31 without reading native storage',()=>{
 const f=fixture(),b=f.block();b.c.getItem=()=>{throw Error('Known snapshot must avoid an inventory reread');};
 for(const mask of [16,31,0]){
  const items=Array.from({length:9},(_,slot)=>slot>=5||(mask&(1<<slot))?slot<5?seasoning(slot+2):tool():undefined),before=JSON.stringify(items);
  f.tx.syncRackDisplay(b,items);
  assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_STATE),mask&15);assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_HIGH_STATE),mask>>4);
  assert.equal(JSON.stringify(items),before);
 }
});
test('display sync detects a changed high bit even when low bits and spice level are unchanged',()=>{
 const f=fixture(),b=f.block();b.c.rows=Array.from({length:9},(_,slot)=>slot<4?seasoning(slot+2):slot>=5?tool():undefined);
 f.tx.syncRackDisplay(b);const writes=b.permutationWrites;b.c.rows[4]=seasoning(6);f.tx.syncRackDisplay(b);
 assert.equal(b.permutationWrites,writes+1);assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_STATE),15);
 assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_HIGH_STATE),1);assert.equal(b.permutation.getState('kaleidoscope_grilling:spice_level'),4);
 b.c.rows[4]=undefined;f.tx.syncRackDisplay(b);assert.equal(b.permutationWrites,writes+2);assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_HIGH_STATE),0);
});
test('failed display writes keep native stacks and filters intact and the derived states can be retried',()=>{
 for(const failure of ['before','after']){
  const f=fixture(),b=f.block();b.c.rows[4]=seasoning(6);for(let slot=5;slot<9;slot++)b.c.rows[slot]=tool();
  f.world.setDynamicProperty(f.tx.rackFiltersKey(b),JSON.stringify([core.rackCanonicalFilter(seasoning(1).typeId)]));
  const contents=JSON.stringify(b.c.rows),before=snapshot(f),setPermutation=b.setPermutation;
  if(failure==='before')b.setPermutation=()=>{throw Error('Injected display rejection');};else f.failOnce('permutation0');
  assert.equal(f.tx.syncRackDisplay(b),1);assert.equal(JSON.stringify(b.c.rows),contents);assert.equal(snapshot(f),before);
  assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_HIGH_STATE),failure==='before'?0:1);
  b.setPermutation=setPermutation;f.tx.syncRackDisplay(b);
  assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_STATE),0);assert.equal(b.permutation.getState(layout.RACK_OCCUPANCY_HIGH_STATE),1);
  assert.equal(JSON.stringify(b.c.rows),contents);assert.equal(snapshot(f),before);
 }
});
test('rack runtime has no form API or opener; shortcut command directly returns matching stacks',()=>{
 const runtimeSource=fs.readFileSync(new URL('a2746_advanced_rack_runtime.js',base),'utf8');assert.doesNotMatch(runtimeSource,/ActionFormData|server-ui|openRackForm|openSlotForm|openRackManagement/);
 const f=fixture(),b=f.block();f.start();f.inv.rows[0]=seasoning(8);f.world.setDynamicProperty(f.tx.rackFiltersKey(b),JSON.stringify([core.rackCanonicalFilter(f.inv.rows[0].typeId)]));
 f.commands.get('kaleidoscope_grilling:rack').run({sourceEntity:f.holder});f.flush();assert.equal(b.c.rows[0].amount,8);assert.equal(f.inv.rows[0],undefined);assert.equal(f.sounds[0][0],'item.item_frame.add_item');
});
test('bulk command accepts identical main/offhand items but still rejects stale mainhand snapshots',()=>{
 const f=fixture(),b=f.block();f.start();f.inv.rows[0]=new Stack('minecraft:totem_of_undying');f.holder.offhand=f.inv.rows[0].clone();f.inv.rows[1]=seasoning(8);
 f.world.setDynamicProperty(f.tx.rackFiltersKey(b),JSON.stringify([core.rackCanonicalFilter(f.inv.rows[1].typeId)]));
 const command=f.commands.get('kaleidoscope_grilling:rack').run;command({sourceEntity:f.holder});f.flush();
 assert.equal(b.c.rows[0].amount,8);assert.equal(f.inv.rows[1],undefined);assert.equal(f.inv.rows[0].typeId,'minecraft:totem_of_undying');
 f.inv.rows[1]=seasoning(9);command({sourceEntity:f.holder});f.inv.rows[0].metadata.canDestroy=['minecraft:obsidian'];f.flush();
 assert.equal(b.c.rows[0].amount,8);assert.equal(f.inv.rows[1].amount,9);
});

test('rack QA is opt-in and records sanitized hit, admission and result without changing transfer',()=>{
 for(const enabled of [false,true]){
  const f=fixture(),b=f.block();f.holder.hasTag=tag=>enabled&&tag==='kg_rack_qa';
  f.holder.name='PRIVATE_PLAYER';f.holder.id='PRIVATE_ID';f.inv.rows[0]=seasoning(1);
  const event={player:f.holder,block:b,isFirstEvent:true,blockFace:'North',faceLocation:{x:.5,y:.72,z:.0625},itemStack:f.inv.getItem(0)};
  f.callbacks.playerInteractWithBlock(event);f.flush();assert.equal(b.c.rows[2]?.amount,1);
  const lines=f.logs.filter(x=>x.startsWith('[Grilling rack QA] '));
  if(!enabled){assert.equal(lines.length,0);continue;}
  const rows=lines.map(x=>JSON.parse(x.slice('[Grilling rack QA] '.length)));
  assert.deepEqual(rows.map(x=>x.stage),['target','resolved','admission','result']);
  assert.equal(rows[1].slot,2);assert.equal(rows[1].row,'seasoning');assert.equal(rows[2].canPlace,true);assert.equal(rows[3].action,'insert');
  assert.ok(!lines.join('').match(/PRIVATE_|original|metadata|location|dimension/));
 }
});
test('rack QA distinguishes invalid hit and stale intent without weakening rejection',()=>{
 for(const kind of ['hit','intent']){
  const f=fixture(),b=f.block();f.holder.hasTag=()=>true;f.inv.rows[0]=seasoning(1);
  const event={player:f.holder,block:b,isFirstEvent:true,blockFace:'North',faceLocation:{x:.5,y:kind==='hit'?.95:.72,z:.0625},itemStack:f.inv.getItem(0)};
  f.callbacks.playerInteractWithBlock(event);if(kind==='intent')f.inv.rows[0].amount=2;f.flush();
  assert.ok(f.logs.some(x=>x.includes(kind==='hit'?'outside_hit_cells':'intent_changed')));assert.equal(b.c.rows.filter(Boolean).length,0);
 }
});
