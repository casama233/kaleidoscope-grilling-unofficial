/** Current crop/pepper component and oil-residue event paths with native API doubles.
 * These test transactions and handler reachability, not Minecraft client parity.
 * Run: node --experimental-vm-modules --test development/gameplay_core/test_plant_fertilizer_runtime.mjs
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as oilCore from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a26_oil_machine_core.js';
import {createOilPressRegistry} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/oil_press_registry.js';

const scripts=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const N='kaleidoscope_grilling:',AGE=N+'age',STAGE=N+'stage',FRUIT=N+'has_pepper',PERSISTENT=N+'persistent';
class Stack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.metadata={label:'preserve'};}
 clone(){const out=new Stack(this.typeId,this.amount);out.metadata={...this.metadata};return out;}
 isStackableWith(other){return this.typeId===other.typeId&&JSON.stringify(this.metadata)===JSON.stringify(other.metadata);}
}
class Permutation{
 constructor(id,states={}){this.type={id};this.states={...states};}
 getState(id){return this.states[id];}
 getAllStates(){return {...this.states};}
 withState(id,value){return new Permutation(this.type.id,{...this.states,[id]:value});}
}
const blockKey=p=>p.x+'|'+p.y+'|'+p.z;
async function fixture({creative=false,hand='main',count=3,item=N+'oil_residue'}={}){
 const startup=[],intervals=[],deferred=[],components=new Map(),blocks=new Map(),drops=[],dp=new Map(),randoms=[],events=new Map();
 const hands={main:hand==='main'?new Stack(item,count):new Stack('minecraft:stone',64),off:hand==='off'?new Stack(item,count):undefined};
 let fault=()=>{},unloaded,writeCount=0;
 const signal=name=>({subscribe(fn){if(!events.has(name))events.set(name,[]);events.get(name).push(fn);}});
 const dimension={id:'minecraft:overworld',heightRange:{min:-64,max:320},
  getBlock(p){
   if(blockKey(p)===unloaded)return undefined;
   if(!blocks.has(blockKey(p))){
    const b={dimension,location:{...p},x:p.x,y:p.y,z:p.z,permutation:new Permutation('minecraft:air'),
     get typeId(){return this.permutation.type.id;},hasTag(){return false;},
     setPermutation(value){this.permutation=value;fault('block',{block:b,value,index:++writeCount});},
     setType(id){this.setPermutation(new Permutation(id));}
    };blocks.set(blockKey(p),b);
   }
   return blocks.get(blockKey(p));
  },
  setBlockType(p,id){this.getBlock(p).setType(id);},getLightLevel(){return 15;},playSound(){},spawnParticle(){},
  spawnItem(stack){
   fault('spawn',stack);
   const entity={stack:stack.clone(),isValid:true,getComponent(id){if(id==='minecraft:item')return {itemStack:entity.stack.clone()};},remove(){if(fault('remove',entity)==='reject')return;entity.isValid=false;drops.splice(drops.indexOf(entity),1);}};
   drops.push(entity);const result=fault('spawnAfter',entity);return result==='unreadable'?undefined:entity;
  }
 };
 const world={
  getDynamicProperty:key=>dp.get(key),getDynamicPropertyIds:()=>[...dp.keys()],setDynamicProperty(key,value){if(value===undefined)dp.delete(key);else dp.set(key,value);},
  getDimension:()=>dimension,
  beforeEvents:{playerInteractWithBlock:signal('interact'),playerBreakBlock:signal('break')},
  afterEvents:Object.fromEntries(['entitySpawn','entityLoad','entityRemove','playerSpawn','playerDimensionChange','playerLeave','playerBreakBlock'].map(name=>[name,signal(name)]))
 };
 const slots=Object.fromEntries(['main','off'].map(name=>[name,{
  hasItem:()=>!!hands[name],getItem:()=>hands[name]?.clone(),
  setItem(stack){if(fault('handBefore',{name,stack})==='reject')return;hands[name]=stack?.clone();fault('handAfter',{name,stack});}
 }]));
 const player={id:'player',dimension,selectedSlotIndex:0,getGameMode:()=>creative?'Creative':'Survival',
  getComponent(id){
   if(id==='minecraft:equippable')return {getEquipmentSlot:name=>slots[name],getEquipment:name=>hands[name]?.clone()};
   if(id==='minecraft:inventory')return {container:{size:1,getItem:()=>hands.main?.clone(),setItem:(_,stack)=>slots.main.setItem(stack)}};
  }
 };
 const math=Object.create(Math);math.random=()=>randoms.length?randoms.shift():.99;
 const system={currentTick:0,beforeEvents:{startup:{subscribe(fn){startup.push(fn);}}},runInterval(fn){intervals.push(fn);},run(fn){deferred.push(fn);},runTimeout(fn){deferred.push(fn);}};
 const context=vm.createContext({console:{warn(){}},Math:math});
 const exports={world,system,ItemStack:Stack,BlockPermutation:{resolve:(id,states)=>new Permutation(id,states)},EquipmentSlot:{Mainhand:'main',Offhand:'off',Head:'head'},GameMode:{Creative:'Creative',Survival:'Survival'}};
 const server=new vm.SyntheticModule(Object.keys(exports),function(){for(const [name,value] of Object.entries(exports))this.setExport(name,value);},{context});
 const advancement=new vm.SyntheticModule(['awardMountainFragrance'],function(){this.setExport('awardMountainFragrance',()=>{});},{context});
 const modules=new Map();
 function sourceModule(url){
  if(!modules.has(url.href))modules.set(url.href,new vm.SourceTextModule(fs.readFileSync(url,'utf8'),{context,identifier:url.href}));
  return modules.get(url.href);
 }
 const entry=new vm.SourceTextModule("import './a2731_farmland_crop_host_runtime.js';import './a2714_houttuynia_crop_runtime.js';import './a2748_pepper_tree_runtime.js';export * from './plant_fertilizer.js';",{context,identifier:new URL('test-entry.js',scripts).href});
 await entry.link((specifier,parent)=>{
  if(specifier==='@minecraft/server')return server;
  if(specifier==='./a2753_advancement_runtime.js')return advancement;
  return sourceModule(new URL(specifier,parent.identifier));
 });
 await entry.evaluate();
 for(const fn of startup)fn({blockComponentRegistry:{registerCustomComponent(id,component){assert(!components.has(id));components.set(id,component);}}});
 function plant(id,states={},p={x:0,y:64,z:0}){
  const block=dimension.getBlock(p);block.permutation=new Permutation(id,states);
  const soil=id===N+'pepper_sapling'?'minecraft:dirt':'minecraft:farmland';
  dimension.getBlock({...p,y:p.y-1}).permutation=new Permutation(soil);
  return block;
 }
 function installOilEvent(){
  Object.assign(context,oilCore,exports,entry.namespace,{
   createOilPressRegistry,interactionFeedback(){},javaInteractionFeedback(){},
   held:(_,name)=>hands[name]?.clone(),captureInteractionIntent:()=>({hand,selected:player.selectedSlotIndex,main:hands.main?.clone(),off:hands.off?.clone()}),
   interactionIntentStillCurrent:(_,intent)=>intent.selected===player.selectedSlotIndex&&['main','off'].every(name=>hands[name]?.typeId===intent[name]?.typeId&&hands[name]?.amount===intent[name]?.amount),isInitialBlockPress:first=>first!==false
  });
  const raw=fs.readFileSync(new URL('a26_oil_machine_runtime.js',scripts),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(function|const))/g,'');
  vm.runInContext(raw,context);
 }
 return {api:entry.namespace,player,hands,components,blocks,drops,dp,randoms,events,deferred,plant,dimension,installOilEvent,
  countBlocks:id=>[...blocks.values()].filter(b=>b.typeId===id).length,
  setFault(fn){fault=fn;},unload(p){unloaded=blockKey(p);}
 };
}

for(const name of ['canola','onion','sweet_potato','houttuynia'])test(name+': oil residue invokes the current crop handler twice, preserving item metadata',async()=>{
 const f=await fixture(),crop=f.plant(N+name+'_crop',{[AGE]:0,[N+'red_variant']:true});
 f.randoms.push(0,0);
 f.components.get(N+name+'_crop_logic').onPlayerInteract({block:crop,player:f.player});
 assert.equal(crop.permutation.getState(AGE),4);assert.equal(f.hands.main.amount,2);
 assert.equal(f.hands.main.metadata.label,'preserve');
 if(name==='houttuynia')assert.equal(crop.permutation.getState(N+'red_variant'),true);
 crop.permutation=crop.permutation.withState(AGE,7);
 assert.equal(f.api.usePlantFertilizer(crop,f.player),false);assert.equal(f.hands.main.amount,2);
});
test('ordinary bone meal still makes one application; a residue whose first pass matures the crop costs one',async()=>{
 const f=await fixture({item:'minecraft:bone_meal'}),crop=f.plant(N+'canola_crop',{[AGE]:0});
 f.randoms.push(0);f.components.get(N+'canola_crop_logic').onPlayerInteract({block:crop,player:f.player});
 assert.equal(crop.permutation.getState(AGE),2);assert.equal(f.hands.main.amount,2);
 f.hands.main=new Stack(N+'oil_residue',1);crop.permutation=crop.permutation.withState(AGE,6);f.randoms.push(0);
 assert.equal(f.api.usePlantFertilizer(crop,f.player),true);assert.equal(crop.permutation.getState(AGE),7);assert.equal(f.hands.main,undefined);
});
test('creative and offhand fertilizer uses preserve the correct hand',async()=>{
 for(const options of [{creative:true},{hand:'off'}]){
  const f=await fixture(options),crop=f.plant(N+'onion_crop',{[AGE]:0});f.randoms.push(0,0);
  assert.equal(f.api.usePlantFertilizer(crop,f.player,options.hand),true);
  assert.equal(crop.permutation.getState(AGE),4);
  assert.equal(f.hands[options.hand??'main'].amount,options.creative?3:2);
  if(options.hand==='off')assert.equal(f.hands.main.typeId,'minecraft:stone');
 }
});
test('only supported vanilla crops grow; an arbitrary age property is never fertilizer support',async()=>{
 const f=await fixture(),wheat=f.plant('minecraft:wheat',{growth:0});f.randoms.push(0,0);
 assert.equal(f.api.usePlantFertilizer(wheat,f.player),true);assert.equal(wheat.permutation.getState('growth'),4);
 const unrelated=f.plant('addon:machine',{age:0},{x:1,y:64,z:0});
 assert.equal(f.api.usePlantFertilizer(unrelated,f.player),false);assert.equal(unrelated.permutation.getState('age'),0);assert.equal(f.hands.main.amount,2);
});
for(const kind of ['handBefore','handAfter','block'])test('rejected '+kind+' write restores fertilizer and crop',async()=>{
 const f=await fixture(),crop=f.plant(N+'sweet_potato_crop',{[AGE]:0});f.randoms.push(0,0);
 let once=true;f.setFault(key=>{if(once&&key===kind){once=false;if(kind==='handBefore')return 'reject';throw Error('injected '+kind);}});
 assert.equal(f.api.usePlantFertilizer(crop,f.player),false);
 assert.equal(crop.permutation.getState(AGE),0);assert.equal(f.hands.main.amount,3);
});
test('pepper residue can advance stage then grow the same source-derived tree in one use',async()=>{
 const f=await fixture(),sapling=f.plant(N+'pepper_sapling',{[STAGE]:0});f.randoms.push(0,0,0);
 assert.equal(f.api.usePlantFertilizer(sapling,f.player),true);
 assert.equal(sapling.typeId,N+'pepper_log');assert.equal(f.countBlocks(N+'pepper_log'),3);
 assert.equal(f.countBlocks(N+'pepper_leaves'),13);assert.equal(f.hands.main.amount,2);
});
test('valid sapling attempts consume one residue when both 45% growth rolls miss, as Java BoneMealItem does',async()=>{
 const f=await fixture(),sapling=f.plant(N+'pepper_sapling',{[STAGE]:0});f.randoms.push(.99,.99);
 assert.equal(f.api.usePlantFertilizer(sapling,f.player),true);assert.equal(sapling.permutation.getState(STAGE),0);assert.equal(f.hands.main.amount,2);
});
test('a partial fertilized-tree write failure restores the sapling, canopy and hand together',async()=>{
 const f=await fixture(),sapling=f.plant(N+'pepper_sapling',{[STAGE]:0});f.randoms.push(0,0,0);
 let once=true;f.setFault((kind,value)=>{if(once&&kind==='block'&&value.index===5){once=false;throw Error('injected canopy write');}});
 assert.equal(f.api.usePlantFertilizer(sapling,f.player),false);
 assert.equal(sapling.typeId,N+'pepper_sapling');assert.equal(sapling.permutation.getState(STAGE),0);
 assert.equal(f.countBlocks(N+'pepper_log'),0);assert.equal(f.countBlocks(N+'pepper_leaves'),0);assert.equal(f.hands.main.amount,3);
});
test('the live oil-residue before-event cancels native interaction and defers exactly one plant use',async()=>{
 const f=await fixture(),crop=f.plant(N+'houttuynia_crop',{[AGE]:0});f.installOilEvent();f.randoms.push(0,0);
 const event={block:crop,player:f.player,itemStack:f.hands.main.clone(),isFirstEvent:true,cancel:false};
 for(const fn of f.events.get('interact'))fn(event);
 assert.equal(event.cancel,true);assert.equal(crop.permutation.getState(AGE),0);assert.equal(f.deferred.length,1);
 f.deferred.shift()();assert.equal(crop.permutation.getState(AGE),4);assert.equal(f.hands.main.amount,2);
 event.isFirstEvent=false;for(const fn of f.events.get('interact'))fn(event);
 assert.equal(f.deferred.length,0);assert.equal(f.hands.main.amount,2);
});
test('natural fruiting-leaf decay uses unenchanted drops exactly once',async()=>{
 const f=await fixture(),leaf=f.plant(N+'pepper_leaves',{[FRUIT]:true,[PERSISTENT]:false});f.randoms.push(.099,.019);
 const component=f.components.get(N+'pepper_leaves_logic');component.onRandomTick({block:leaf});
 assert.equal(leaf.typeId,'minecraft:air');
 assert.deepEqual(f.drops.map(e=>[e.stack.typeId,e.stack.amount]),[[N+'pepper_sapling',1],['minecraft:stick',1],[N+'sichuan_pepper',1]]);
 component.onRandomTick({block:leaf});assert.equal(f.drops.length,3);
});
test('a leaf may gain fruit before its natural decay, matching Java randomTick order',async()=>{
 const f=await fixture(),leaf=f.plant(N+'pepper_leaves',{[FRUIT]:false,[PERSISTENT]:false});f.randoms.push(0,.99,.99);
 f.components.get(N+'pepper_leaves_logic').onRandomTick({block:leaf});
 assert.equal(leaf.typeId,'minecraft:air');assert.deepEqual(f.drops.map(e=>e.stack.typeId),[N+'sichuan_pepper']);
});
test('persistent leaves, log-connected leaves and unloaded-neighbor leaves do not decay',async()=>{
 for(const mode of ['persistent','connected','unloaded']){
  const f=await fixture(),leaf=f.plant(N+'pepper_leaves',{[FRUIT]:true,[PERSISTENT]:mode==='persistent'});
  if(mode==='connected')f.dimension.getBlock({x:1,y:64,z:0}).permutation=new Permutation(N+'pepper_log');
  if(mode==='unloaded')f.unload({x:1,y:64,z:0});
  f.components.get(N+'pepper_leaves_logic').onRandomTick({block:leaf});
  assert.equal(leaf.typeId,N+'pepper_leaves');assert.equal(f.drops.length,0);
 }
});
test('an unacknowledged spawn restores the leaf, removes confirmed drops and quarantines the unknown outcome',async()=>{
 const f=await fixture(),leaf=f.plant(N+'pepper_leaves',{[FRUIT]:true,[PERSISTENT]:false});f.randoms.push(0,0);
 let once=true;f.setFault((kind,stack)=>{if(once&&kind==='spawn'&&stack.typeId==='minecraft:stick'){once=false;throw Error('injected second drop');}});
 const component=f.components.get(N+'pepper_leaves_logic');component.onRandomTick({block:leaf});
 assert.equal(leaf.typeId,N+'pepper_leaves');assert.equal(f.drops.length,0);
 assert([...f.dp.keys()].some(key=>key.startsWith(N+'plant_transaction_fault_')));
 f.randoms.push(0,0);component.onRandomTick({block:leaf});assert.equal(leaf.typeId,N+'pepper_leaves');assert.equal(f.drops.length,0);
});
for(const change of ['hand','slot','target_state','target_type'])test('deferred residue rejects changed '+change,async()=>{
 const f=await fixture(),crop=f.plant(N+'canola_crop',{[AGE]:0});f.installOilEvent();
 const event={block:crop,player:f.player,itemStack:f.hands.main.clone(),isFirstEvent:true,cancel:false};
 for(const fn of f.events.get('interact'))fn(event);
 if(change==='hand')f.hands.main=new Stack('minecraft:bone_meal',3);
 if(change==='slot')f.player.selectedSlotIndex=1;
 if(change==='target_state')crop.permutation=crop.permutation.withState(AGE,1);
 if(change==='target_type')crop.permutation=new Permutation(N+'onion_crop',{[AGE]:0});
 f.deferred.shift()();
 assert.equal(crop.permutation.getState(AGE),change==='target_state'?1:0);assert.equal(f.hands.main.amount,3);
});
for(const failure of ['throws_after_spawn','unreadable_handle','wrong_amount','remove_rejected'])test('leaf drop '+failure+' cannot create a retryable duplicate source',async()=>{
 const f=await fixture(),leaf=f.plant(N+'pepper_leaves',{[FRUIT]:true,[PERSISTENT]:false});f.randoms.push(0,0);
 f.setFault((kind,entity)=>{
  if(kind==='spawnAfter'&&entity.stack.typeId===N+'pepper_sapling'){
   if(failure==='throws_after_spawn')throw Error('spawn completed before throw');
   if(failure==='unreadable_handle')return 'unreadable';
   if(failure==='wrong_amount')entity.stack.amount=2;
  }
  if(failure==='remove_rejected'){
   if(kind==='spawn'&&entity.typeId==='minecraft:stick')throw Error('second spawn unknown');
   if(kind==='remove')return 'reject';
  }
 });
 const component=f.components.get(N+'pepper_leaves_logic');component.onRandomTick({block:leaf});
 assert.equal(leaf.typeId,N+'pepper_leaves');assert.equal(f.drops.length,1);
 assert([...f.dp.keys()].some(key=>key.startsWith(N+'plant_transaction_fault_')));
 f.setFault(()=>{});f.randoms.push(0,0);component.onRandomTick({block:leaf});assert.equal(f.drops.length,1);
});
test('failed drop rollback quarantines natural and manual leaf settlement instead of duplicating on retry',async()=>{
 const f=await fixture(),leaf=f.plant(N+'pepper_leaves',{[FRUIT]:true,[PERSISTENT]:false});f.randoms.push(0,0);
 f.setFault((kind,stack)=>{if(kind==='remove'||(kind==='spawn'&&stack.typeId==='minecraft:stick'))throw Error('injected rollback failure');});
 const component=f.components.get(N+'pepper_leaves_logic');component.onRandomTick({block:leaf});
 assert.equal(leaf.typeId,N+'pepper_leaves');assert.equal(f.drops.length,1);
 assert([...f.dp.keys()].some(key=>key.startsWith(N+'plant_transaction_fault_')));
 f.setFault(()=>{});f.randoms.push(0,0);component.onRandomTick({block:leaf});assert.equal(f.drops.length,1);
 f.hands.main=undefined;component.onPlayerInteract({block:leaf,player:f.player});assert.equal(f.drops.length,1);
 const event={block:leaf,player:f.player,cancel:false};for(const fn of f.events.get('break'))fn(event);
 for(const fn of f.deferred)fn();assert.equal(f.drops.length,1);assert.equal(leaf.typeId,N+'pepper_leaves');
});
test('a silently incomplete leaf-permutation rollback is quarantined',async()=>{
 const f=await fixture(),leaf=f.plant(N+'pepper_leaves',{[FRUIT]:true,[PERSISTENT]:false});
 f.setFault((kind,value)=>{
  if(kind!=='block')return;
  if(value.index===1)throw Error('native removal wrote then failed');
  if(value.index===2)value.block.permutation=value.value.withState(FRUIT,false);
 });
 f.components.get(N+'pepper_leaves_logic').onRandomTick({block:leaf});
 assert.equal(leaf.typeId,N+'pepper_leaves');assert.equal(f.drops.length,0);
 assert([...f.dp.keys()].some(key=>key.startsWith(N+'plant_transaction_fault_')));
});
test('manual leaf break cannot deliver fruit captured before another interaction harvested it',async()=>{
 const f=await fixture(),leaf=f.plant(N+'pepper_leaves',{[FRUIT]:true,[PERSISTENT]:false});
 const event={block:leaf,player:f.player,cancel:false};for(const fn of f.events.get('break'))fn(event);
 assert.equal(event.cancel,true);assert.equal(f.deferred.length,1);
 leaf.permutation=leaf.permutation.withState(FRUIT,false);
 f.deferred.shift()();assert.equal(f.drops.length,0);assert.equal(leaf.typeId,N+'pepper_leaves');
});
test('manual leaf break honors an already-cancelled event and a matching source settles once',async()=>{
 const f=await fixture(),leaf=f.plant(N+'pepper_leaves',{[FRUIT]:true,[PERSISTENT]:false});
 const event={block:leaf,player:f.player,cancel:true};for(const fn of f.events.get('break'))fn(event);
 assert.equal(f.deferred.length,0);assert.equal(leaf.typeId,N+'pepper_leaves');
 event.cancel=false;for(const fn of f.events.get('break'))fn(event);
 f.deferred.shift()();assert.equal(leaf.typeId,'minecraft:air');assert.equal(f.drops.length,1);assert.equal(f.drops[0].stack.typeId,N+'sichuan_pepper');
});
