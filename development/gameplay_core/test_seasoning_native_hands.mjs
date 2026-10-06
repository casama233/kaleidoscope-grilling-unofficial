import {captureSkewerMetadata,restoreSkewerMetadata,metadataSignature} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/skewer_item_snapshot.js';
/**
 * Canonical function-body integration with API doubles, not an engine certificate.
 * Run from repository root: node --test development/gameplay_core/test_seasoning_native_hands.mjs
 * First placement requires one unambiguous bottle hand; API doubles are not GUI acceptance.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=fileURLToPath(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url));
const moduleAt=n=>import(pathToFileURL(path.join(root,n)).href);
const [core,visuals,tx,plans,support,intent]=await Promise.all([
 moduleAt('a2743_seasoning_contract_core.js'),moduleAt('a2766_special_seasoning_visual_core.js'),
 moduleAt('a277_grill_transaction_core.js'),moduleAt('rack_transfer_plan.js'),
 moduleAt('blockSupport.js'),moduleAt('a276_grill_intent_core.js'),
]);
const read=n=>fs.readFileSync(path.join(root,n),'utf8');
const strip=s=>s.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(class|const|function|async))/g,'');
function body(source,name){
 const start=source.indexOf('function '+name+'(');assert.ok(start>=0,'Canonical function missing: '+name);
 let i=source.indexOf('{',start),depth=1,end=i+1;
 for(;depth&&end<source.length;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 assert.equal(depth,0,name+' body is complete');return source.slice(start,end);
}
const N='kaleidoscope_grilling:',EMPTY=N+'empty_seasoning_bottle',PENDING=N+'pending_seasoning';
const stackPhases=new WeakMap();
function restrictionRead(stack,key){const phase=stackPhases.get(stack);if(phase){phase[key]++;if(phase.before)throw new ReferenceError('Restriction getter in before-event');}}
class Stack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.maxAmount=1;this.props={};this.lore=[];this.canDestroy=[];this.canPlaceOn=[];}
 clone(){const copy=Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}));if(stackPhases.has(this))stackPhases.set(copy,stackPhases.get(this));return copy;}
 getRawLore(){return structuredClone(this.lore);}
 getLore(){return this.lore.map(x=>typeof x==='string'?x:x.text??'');}
 setLore(v){this.lore=structuredClone(v);}
 getDynamicPropertyIds(){assert.equal(this.maxAmount,1);return Object.keys(this.props);}
 getDynamicProperty(k){assert.equal(this.maxAmount,1);return structuredClone(this.props[k]);}
 setDynamicProperty(k,v){assert.equal(this.maxAmount,1);if(v===undefined)delete this.props[k];else this.props[k]=structuredClone(v);}
 getCanDestroy(){restrictionRead(this,'destroy');return [...this.canDestroy];}setCanDestroy(v){this.canDestroy=[...v];}
 getCanPlaceOn(){restrictionRead(this,'place');return [...this.canPlaceOn];}setCanPlaceOn(v){this.canPlaceOn=[...v];}
 getComponent(){return undefined;}
}
const json=s=>JSON.stringify(s);
const equal=(a,b,message)=>assert.equal(json(a),json(b),message);

function fixture(){
 const dp=new Map(),entities=new Map(),blocks=new Map(),queue=[];
 const phase={before:false,destroy:0,place:0};
 let serial=0,off,offFault;
 const withPhase=s=>{if(s)stackPhases.set(s,phase);return s;};
 const makeContainer=size=>({size,rows:Array(size),getItem(i){return withPhase(this.rows[i]?.clone());},setItem(i,s){this.rows[i]=withPhase(s?.clone());}});
 const inventory=makeContainer(9);
 const equipment={getEquipment(slot){assert.equal(slot,'offhand');return withPhase(off?.clone());},setEquipment(slot,s){
  assert.equal(slot,'offhand');const fault=offFault;offFault=undefined;
  if(fault?.after)off=withPhase(s?.clone());
  if(fault?.kind==='throw')throw Error('Injected offhand write rejection');
  if(fault?.kind==='false')return false;
  off=withPhase(s?.clone());return true;
 }};
 const permutation=(id,states={})=>({id,getAllStates:()=>({...states}),getState:k=>states[k]});
 function makeBlock(location){let p=permutation('minecraft:air');return {
  ...location,location:{...location},dimension,get typeId(){return p.id;},get permutation(){return p;},
  get isAir(){return p.id==='minecraft:air';},get isLiquid(){return false;},getComponent(){return undefined;},
  below(){return dimension.getBlock({...location,y:location.y-1});},
  above(){return dimension.getBlock({...location,y:location.y+1});},
  setType(id){p=permutation(id);},setPermutation(v){p=v;},
 };}
 const dimension={id:'minecraft:overworld',getBlock(location){
  const k=[location.x,location.y,location.z].join('/');if(!blocks.has(k))blocks.set(k,makeBlock(location));return blocks.get(k);
 },getEntities(q){return [...entities.values()].filter(e=>e.typeId===q.type&&Math.hypot(e.location.x-q.location.x,e.location.y-q.location.y,e.location.z-q.location.z)<=q.maxDistance);},
 spawnEntity(typeId,location){
  const properties=new Map(),c=makeContainer(4),id='helper'+(++serial);
   const e={id,typeId,location:{...location},dimension,c,properties,getDynamicProperty:k=>properties.get(k),
   setDynamicProperty(k,v){if(v===undefined)properties.delete(k);else properties.set(k,v);},
   getComponent:k=>k==='minecraft:inventory'?{container:c}:undefined,remove(){entities.delete(id);}};
  entities.set(id,e);return e;
 }};
 const world={getDynamicProperty:k=>dp.get(k),setDynamicProperty(k,v){if(v===undefined)dp.delete(k);else dp.set(k,v);},getEntity:id=>entities.get(id)};
 const player={id:'test-player',isValid:true,dimension,location:{x:0,y:65,z:0},selectedSlotIndex:0,getGameMode:()=> 'survival',
  getComponent:id=>id==='minecraft:inventory'?{container:inventory}:id==='minecraft:equippable'?equipment:undefined};
 let context,api;
 const load=()=>{
 context=vm.createContext({...core,...visuals,...tx,...plans,...support,...intent,
  hostWorld:world,world,system:{currentTick:10,run:f=>queue.push(f)},ItemStack:Stack,captureSkewerMetadata,restoreSkewerMetadata,metadataSignature,EnchantmentType:class {constructor(id){this.id=id}},
  EquipmentSlot:{Offhand:'offhand'},GameMode:{Survival:'survival',Creative:'creative'},
  BlockPermutation:{resolve:permutation},SEASONING_BLOCK:core.SEASONING_PLACE_BLOCK_ID,
  console:{warn(){},error(){}},markPlacedVisualDirty(){},refreshPlacedBottleAfterPickup(){},blockSound(){},message(){},
  javaInteractionFeedback(){},interactionFailure(){},awardSeasoningMilestones(){},interactionParticleBurst(){},transactionStatus:r=>r.ok,
  EMPTY_SEASONING_ID:EMPTY,PENDING_SEASONING:PENDING,SEASON_USES_KEY:core.SEASONING_USES_KEY,SEASON_VARIANT_KEY:core.SEASONING_VARIANT_KEY,
  seasoningLore:()=>[],
 });
 const run=s=>vm.runInContext(s,context);
 run(body(read('eating_item_runtime.js'),'copyEatingVariant')+'\n'+['bottleFillIngredients','retargetBottleFillStack'].map(n=>body(read('bottle_fill_item_runtime.js'),n)).join('\n'));
 // Load the actual canonical implementations. Only unrelated visual/HUD effects are stubs.
 run(strip(read('itemDataCore.js')));run('configureItemDataWorld(hostWorld)');
 for(const name of ['host_api/food_api_core.js','a2735_player_io.js','a2762_interaction_intent_core.js'])run(strip(read(name)));
 for(const [file,names] of [
  ['a2750_food_state_adapter.js',['readFoodSeasonings','setFoodSeasonings']],
  ['a2766_special_seasoning_visual_runtime.js',['bounded','specialSeasoningVariant']],
  ['a2762_interaction_intent_adapter.js',['captureInteractionIntent','interactionIntentStillCurrent']],
 ])run(names.map(n=>body(read(file),n)).join('\n'));
 run('const heldMain=getMainHand,heldByHand=getHand,creative=isCreative,readSeasonings=readFoodSeasonings,setSeasonings=setFoodSeasonings;');
 for(const name of ['family_station_storage.js','a2743_seasoning_block_adapter.js','seasoning_native_storage.js'])run(strip(read(name)));
 run('const readBottleStack=readPlacedSeasoningStack,writeBottleStack=writePlacedSeasoningStack,isSeasoningBlock=isSeasoningBlockId,stationStorageKey=storageKey;');
 const functions=['copyOne','reducedStack','getUses','setUses','bottleDataFromItem','bottleItem','setBottleVisual','nativeBottles',
  'bottleRollbackStatus','bottleProjectionStep','commitBottleAndHand','pushBottle','handleSeasoningBlock','sameBottleTarget',
  'bottleTargetSnapshot','scheduleNativeBottlePlacement','tryScheduleOffhandBottleInteraction','queueBottlePlacement'];
 const source=read('main.js');
 run(source.slice(source.indexOf('const bottleInteractionSupports='),source.indexOf('function tryScheduleOffhandBottleInteraction(')));
 run(functions.map(n=>body(read('main.js'),n)).join('\n'));
 api=run('({nativeBottles,pushBottle,handleSeasoningBlock,scheduleNativeBottlePlacement,tryScheduleOffhandBottleInteraction,bottleDataFromItem,captureWritableHand,captureInteractionIntent,interactionIntentStillCurrent,getItemProperty,setItemProperty,setItemLore,readFoodSeasonings,setFoodSeasonings,seasoningBlockKey,retargetBottleFillStack})');
 // Exercise the actual subscribed callback; unrelated branches remain observable stubs.
 const subscription='world.beforeEvents.playerInteractWithBlock.subscribe(';
 const start=source.indexOf(subscription),end=source.indexOf('\nworld.afterEvents.playerPlaceBlock',start);
 let listener;
 world.beforeEvents={playerInteractWithBlock:{subscribe:f=>listener=f}};
 Object.assign(context,{tryScheduleBeefBoardOverride:()=>false,skewerAction:()=>null,GRILL_ID:N+'grill',STORAGE_SORT_BLOCKS:new Set(),isInitialBlockPress:x=>x!==false});
 run(source.slice(start,end));api.interact=listener;
 };load();
 const block=dimension.getBlock({x:0,y:64,z:0});block.below().setType('minecraft:stone');
 const get=h=>h==='off'?equipment.getEquipment('offhand'):inventory.getItem(player.selectedSlotIndex);
 const set=(h,s)=>h==='off'?equipment.setEquipment('offhand',s):inventory.setItem(player.selectedSlotIndex,s);
 return {get api(){return api;},block,player,inventory,equipment,dp,entities,get,set,phase,get queued(){return queue.length;},
  interact(overrides={}){const e={block:block.below(),player,blockFace:'Up',itemStack:undefined,isFirstEvent:true,cancel:false,...overrides};api.interact(e);return e;},
  reloadSavedState(){
   assert.equal(queue.length,0,'Only completed transactions are serialized');
   const encode=s=>s&&{...s},decode=s=>s&&withPhase(Object.assign(new Stack(s.typeId,s.amount),s));
   const saved=JSON.parse(JSON.stringify({dp:[...dp],main:inventory.rows.map(encode),off:encode(off),helpers:[...entities].map(([id,e])=>({id,props:[...e.properties],rows:e.c.rows.map(encode)}))}));
   dp.clear();for(const [k,v] of saved.dp)dp.set(k,v);
   inventory.rows=saved.main.map(s=>decode(s??undefined));off=decode(saved.off);
   for(const helper of saved.helpers){const e=entities.get(helper.id);e.properties.clear();for(const [k,v] of helper.props)e.properties.set(k,v);e.c.rows=helper.rows.map(s=>decode(s??undefined));}
   load();
  },
  failOff(kind,after=false){offFault={kind,after};},
  flush(){while(queue.length)queue.shift()();},
  queuePlace(){const e={block,player,face:'Up',permutationToPlace:permutation(N+'seasoning_bottle_1'),cancel:false};api.scheduleNativeBottlePlacement(e);return e;},
  placeMain(){const e={block,player,face:'Up',permutationToPlace:permutation(N+'seasoning_bottle_1'),cancel:false};api.scheduleNativeBottlePlacement(e);while(queue.length)queue.shift()();return e;},
 };
}
function decorated(f,kind,{uses=0,variant=0,partial=1,marker=kind,typeId}={}){
 const s=new Stack(typeId??(kind==='special'?visuals.specialSeasoningVisualId(uses,variant):kind==='pending'?PENDING:EMPTY));
 Object.assign(s,{nameTag:'Original '+marker,keepOnDeath:true,lockMode:'inventory',opaqueNative:{marker}});
 s.setCanDestroy(['minecraft:dirt']);s.setCanPlaceOn(['minecraft:stone']);
 f.api.setItemLore(s,[{text:'Unrelated lore '+marker},{translate:'test.unrelated',with:['retained']}]);
 for(const [k,v] of Object.entries({'other:boolean':true,'other:number':7,'other:string':marker,'other:vector':{x:1,y:2,z:3}}))f.api.setItemProperty(s,k,v);
 f.api.setFoodSeasonings(s,kind==='empty'?core.BASE_SEASONINGS.slice(0,partial):[...core.BASE_SEASONINGS,'minecraft:redstone']);
 if(kind==='special'){f.api.setItemProperty(s,core.SEASONING_USES_KEY,uses);f.api.setItemProperty(s,core.SEASONING_VARIANT_KEY,variant);}
 if(!typeId&&kind!=='special')s.typeId=core.seasoningFillVisualId(s.typeId,f.api.readFoodSeasonings(s));
 return s;
}
function seedForOff(f){
 const seed=decorated(f,'empty',{partial:0,marker:'main seed'});f.set('main',seed);f.placeMain();
 const sentinel=decorated(f,'pending',{marker:'unchanged main',typeId:'minecraft:totem_of_undying'});f.set('main',sentinel);return {seed,sentinel};
}

for(const hand of ['main','off'])for(const kind of ['empty','pending','special']){
 const states=kind==='special'?[{uses:0,variant:0},{uses:1,variant:7},{uses:15,variant:0},{uses:16,variant:7}]:kind==='empty'?[{partial:1},{partial:2}]:[{}];
 for(const state of states)test(`${hand} ${kind} ${json(state)} place/pickup/replace preserves exact stack and opposite hand`,()=>{
  const f=fixture(),original=decorated(f,kind,state);let sentinel,seed;
  if(hand==='off')({seed,sentinel}=seedForOff(f));
  else{sentinel=decorated(f,'pending',{marker:'unchanged off',typeId:'minecraft:totem_of_undying'});f.set('off',sentinel);}
  f.set(hand,original);
  if(hand==='main')f.placeMain();else assert.equal(f.api.pushBottle(f.block,f.player,f.get('off'),'off'),true);
  assert.equal(f.get(hand),undefined);equal(f.get(hand==='main'?'off':'main'),sentinel);
  equal(f.api.nativeBottles(f.block).items.at(-1),original);
  f.api.handleSeasoningBlock(f.block,f.player,hand);equal(f.get(hand),original);equal(f.get(hand==='main'?'off':'main'),sentinel);
  if(kind==='empty'){assert.equal(f.get(hand).typeId,core.seasoningFillVisualId(EMPTY,core.BASE_SEASONINGS.slice(0,state.partial)));equal(f.api.readFoodSeasonings(f.get(hand)),core.BASE_SEASONINGS.slice(0,state.partial));}
  if(hand==='main')f.placeMain();else assert.equal(f.api.pushBottle(f.block,f.player,f.get('off'),'off'),true);
  equal(f.api.nativeBottles(f.block).items.at(-1),original);equal(f.get(hand==='main'?'off':'main'),sentinel);
  if(seed)equal(f.api.nativeBottles(f.block).items[0],seed,'Lower bottle stays unchanged');
 });
}
for(const hand of ['main','off'])test(`${hand} EMPTY ingredient addition uses canonical DP and preserves unrelated metadata`,()=>{
 const f=fixture();if(hand==='off')seedForOff(f);
 const original=decorated(f,'empty',{partial:1});f.set(hand,original);
 if(hand==='main')f.placeMain();else f.api.pushBottle(f.block,f.player,f.get(hand),hand);
 const opposite=hand==='main'?'off':'main',sentinel=decorated(f,'pending',{marker:'other'});f.set(opposite,sentinel);
 f.set(hand,new Stack(core.BASE_SEASONINGS[1]));f.api.handleSeasoningBlock(f.block,f.player,hand);
 const expected=original.clone();f.api.setFoodSeasonings(expected,core.BASE_SEASONINGS.slice(0,2));
 equal(f.api.nativeBottles(f.block).items.at(-1),f.api.retargetBottleFillStack(expected));equal(f.get(opposite),sentinel);assert.equal(f.get(hand),undefined);
});

test('canonical writable main hand pins captured slot for write and rollback',()=>{
 const f=fixture(),original=decorated(f,'pending'),other=decorated(f,'empty',{marker:'new selected slot'});
 f.set('main',original);f.inventory.setItem(1,other);
 const captured=f.api.captureWritableHand(f.player,'main');f.player.selectedSlotIndex=1;
 captured.write(undefined);assert.equal(f.inventory.getItem(0),undefined);equal(f.get('main'),other);
 captured.write(captured.before);equal(f.inventory.getItem(0),original);equal(f.get('main'),other);
});
test('queued first placement rejects selected-slot change even with identical stack',()=>{
 const f=fixture(),s=decorated(f,'empty');f.set('main',s);f.inventory.setItem(1,s);
 f.api.scheduleNativeBottlePlacement({block:f.block,player:f.player,face:'Up',permutationToPlace:{id:N+'seasoning_bottle_1',getAllStates:()=>({}),getState:()=>undefined},cancel:false});
 f.player.selectedSlotIndex=1;f.flush();assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);
 equal(f.inventory.getItem(0),s);equal(f.inventory.getItem(1),s);
});
test('offhand writable slot stays independent; changed main hand invalidates two-hand metadata intent',()=>{
 const f=fixture(),main=decorated(f,'empty'),off=decorated(f,'pending');f.set('main',main);f.set('off',off);
 const intent=f.api.captureInteractionIntent(f.player,off),captured=f.api.captureWritableHand(f.player,'off');
 assert.equal(intent.hand,'off');f.player.selectedSlotIndex=2;assert.equal(f.api.interactionIntentStillCurrent(f.player,intent),false);
 captured.write(undefined);equal(f.inventory.getItem(0),main);assert.equal(f.get('off'),undefined);
 captured.write(captured.before);equal(f.get('off'),off);equal(f.inventory.getItem(0),main);
});
for(const kind of ['false','throw'])for(const after of [false,true])for(const action of ['push','pickup'])test(`offhand ${action} setEquipment ${kind} ${after?'after':'before'} mutation rolls back both parties`,()=>{
 const f=fixture(),{seed,sentinel}=seedForOff(f),original=decorated(f,'special',{uses:15,variant:7});
 f.set('off',original);
 if(action==='pickup'){f.api.pushBottle(f.block,f.player,f.get('off'),'off');assert.equal(f.get('off'),undefined);}
 const before=f.api.nativeBottles(f.block).items.map(s=>s.clone()),raw=[...f.dp.entries()].map(([k,v])=>[k,v]);
 f.failOff(kind,after);
 if(action==='push')assert.equal(f.api.pushBottle(f.block,f.player,f.get('off'),'off'),false);
 else f.api.handleSeasoningBlock(f.block,f.player,'off');
 equal(f.api.nativeBottles(f.block).items,before);equal(f.get('main'),sentinel);equal(f.api.nativeBottles(f.block).items[0],seed);
 equal(f.get('off'),action==='push'?original:undefined);equal([...f.dp.entries()],raw);
 // The one-shot write rejection was recovered; coordinate is still usable.
 if(action==='push')assert.equal(f.api.pushBottle(f.block,f.player,f.get('off'),'off'),true);
 else{f.api.handleSeasoningBlock(f.block,f.player,'off');equal(f.get('off'),original);}
});

for(const kind of ['empty','pending','special'])for(const occupiedMain of [false,true])test(`unique off ${kind} first-place/pickup/replace preserves metadata; main occupied=${occupiedMain}`,()=>{
 const f=fixture(),s=decorated(f,kind,{partial:2,uses:15,variant:7}),other=occupiedMain?decorated(f,'pending',{marker:'main sentinel',typeId:'minecraft:totem_of_undying'}):undefined;
 if(kind==='pending'){f.api.setFoodSeasonings(s,Object.keys(core.SEASONING_KINDS).slice(0,8));s.typeId=PENDING+'_f8';}
 f.set('main',other);f.set('off',s);f.phase.before=true;
 assert.equal(f.queuePlace().cancel,true);assert.equal(f.queued,1);assert.equal(f.phase.destroy+f.phase.place,0);
 f.phase.before=false;f.flush();assert.equal(f.get('off'),undefined);equal(f.get('main'),other);equal(f.api.nativeBottles(f.block).items[0],s);
 // Canonical pickup-by-hand is tested as a double, not a claim about Java's MAIN_HAND pickup/UI.
 f.api.handleSeasoningBlock(f.block,f.player,'off');equal(f.get('off'),s);equal(f.get('main'),other);assert.equal(f.block.typeId,'minecraft:air');
 f.queuePlace();f.flush();equal(f.api.nativeBottles(f.block).items[0],s);equal(f.get('main'),other);
});

for(const difference of ['id','name','dp','restrictions','identical'])test(`two bottle first-placement candidates (${difference}) cancel without guessing or consuming`,()=>{
 const f=fixture(),main=decorated(f,'pending',{marker:'same'}),off=main.clone();
 if(difference==='id')off.typeId=EMPTY;
 if(difference==='name')off.nameTag='Other bottle';
 if(difference==='dp')f.api.setFoodSeasonings(off,core.BASE_SEASONINGS.slice(0,1));
 if(difference==='restrictions')off.setCanDestroy(['minecraft:stone']);
 f.set('main',main);f.set('off',off);f.phase.before=true;
 assert.equal(f.queuePlace().cancel,true);assert.equal(f.queued,0);assert.equal(f.phase.destroy+f.phase.place,0);f.phase.before=false;f.flush();
 assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);assert.equal(f.dp.size,0);equal(f.get('main'),main);equal(f.get('off'),off);
});

for(const hand of ['main','off'])for(const field of ['name','dp','restrictions'])test(`queued off first-placement rejects ${hand} ${field} change without touching either hand`,()=>{
 const f=fixture(),original=decorated(f,'pending'),main=decorated(f,'pending',{marker:'main sentinel',typeId:'minecraft:totem_of_undying'});f.set('main',main);f.set('off',original);
 f.phase.before=true;f.queuePlace();assert.equal(f.phase.destroy+f.phase.place,0);f.phase.before=false;
 const changed=f.get(hand);if(field==='name')changed.nameTag='Changed';if(field==='dp')f.api.setItemProperty(changed,'other:string','changed');if(field==='restrictions')changed.setCanPlaceOn(['minecraft:dirt']);f.set(hand,changed);
 const expectedMain=f.get('main'),expectedOff=f.get('off');f.flush();assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);equal(f.get('main'),expectedMain);equal(f.get('off'),expectedOff);
});

for(const unreadableHand of ['main','off'])test(`first placement cancels when ${unreadableHand} inventory read fails`,()=>{
 const f=fixture(),s=decorated(f,'pending');f.set('off',s);const original=f.player.getComponent;
 f.player.getComponent=id=>{if(id===(unreadableHand==='main'?'minecraft:inventory':'minecraft:equippable'))throw Error('Injected hand read');return original(id);};
 assert.equal(f.queuePlace().cancel,true);assert.equal(f.queued,0);f.player.getComponent=original;equal(f.get('off'),s);assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);
});

for(const kind of ['false','throw'])for(const after of [false,true])test(`off first placement write ${kind} ${after?'after':'before'} mutation rolls back native items and target`,()=>{
 const f=fixture(),s=decorated(f,'special',{uses:15,variant:7}),main=decorated(f,'empty',{typeId:'minecraft:totem_of_undying'});f.set('main',main);f.set('off',s);f.queuePlace();f.failOff(kind,after);f.flush();
 equal(f.get('main'),main);equal(f.get('off'),s);assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);assert.equal(f.dp.size,0);
 f.queuePlace();f.flush();equal(f.api.nativeBottles(f.block).items[0],s);equal(f.get('main'),main);assert.equal(f.get('off'),undefined);
});

// Native 1.26.52.3 evidence: offhand Use emits only beforeInteract with an empty
// event item. These tests run that real subscription, never fabricate placement.
for(const [kind,state] of [['empty',{partial:2}],['pending',{}],['special',{uses:0,variant:0}],['special',{uses:15,variant:7}]])test(`script off ${kind} ${json(state)} interaction/save-reload/main pickup/replace retains exact stack`,()=>{
 const f=fixture(),original=decorated(f,kind,state);
 if(kind==='pending'){f.api.setFoodSeasonings(original,Object.keys(core.SEASONING_KINDS).slice(0,8));original.typeId=PENDING+'_f8';}
 f.set('off',original);f.phase.before=true;
 assert.equal(f.interact().cancel,true);assert.equal(f.queued,1);assert.equal(f.phase.destroy+f.phase.place,0);
 f.phase.before=false;f.flush();assert.equal(f.get('main'),undefined);assert.equal(f.get('off'),undefined);
 equal(f.api.nativeBottles(f.block).items[0],original);f.reloadSavedState();equal(f.api.nativeBottles(f.block).items[0],original);
 // Java-style main-hand pickup remains unchanged. GUI hand transfers are doubles.
 f.api.handleSeasoningBlock(f.block,f.player,'main');equal(f.get('main'),original);assert.equal(f.block.typeId,'minecraft:air');
 f.set('main',undefined);f.set('off',original);assert.equal(f.interact().cancel,true);f.flush();equal(f.api.nativeBottles(f.block).items[0],original);
});

for(const id of ['minecraft:chest','minecraft:barrel','minecraft:furnace','minecraft:anvil','minecraft:crafting_table','minecraft:stonecutter_block','minecraft:enchanting_table',N+'unknown_table','minecraft:oak_planks','minecraft:oak_slab','minecraft:air','minecraft:water'])test(`script supplement preserves interaction with excluded support ${id}`,()=>{
 const f=fixture(),s=decorated(f,'pending');f.set('off',s);f.block.below().setType(id);
 assert.equal(f.interact().cancel,false);assert.equal(f.queued,0);equal(f.get('off'),s);assert.equal(f.entities.size,0);assert.equal(f.dp.size,0);
});
for(const fields of [{isFirstEvent:false},{isFirstEvent:undefined},{cancel:true},{blockFace:'North'},{blockFace:'Down'},{itemStack:new Stack('minecraft:stone')}])test(`script supplement rejects event ${json(fields)} without queue`,()=>{
 const f=fixture(),s=decorated(f,'pending');f.set('off',s);const e=f.interact(fields);
 assert.equal(e.cancel,fields.cancel===true);assert.equal(f.queued,0);equal(f.get('off'),s);assert.equal(f.entities.size,0);
});
for(const target of ['minecraft:stone','minecraft:water','minecraft:tallgrass',N+'seasoning_bottle_1'])test(`script supplement never overwrites target ${target}`,()=>{
 const f=fixture(),s=decorated(f,'pending');f.set('off',s);f.block.setType(target);
 assert.equal(f.interact().cancel,false);assert.equal(f.queued,0);equal(f.get('off'),s);assert.equal(f.block.typeId,target);assert.equal(f.entities.size,0);
});
for(const typeId of ['minecraft:totem_of_undying',EMPTY,PENDING])test(`script supplement leaves occupied main ${typeId} to existing handlers`,()=>{
 const f=fixture(),off=decorated(f,'pending'),main=decorated(f,'empty',{typeId});f.set('off',off);f.set('main',main);
 assert.equal(f.interact().cancel,false);assert.equal(f.queued,0);equal(f.get('main'),main);equal(f.get('off'),off);
 if(typeId!== 'minecraft:totem_of_undying'){assert.equal(f.queuePlace().cancel,true);assert.equal(f.queued,0);}
});
for(const hand of ['main','off'])test(`script supplement fails closed on unreadable ${hand}`,()=>{
 const f=fixture(),s=decorated(f,'pending');f.set('off',s);const original=f.player.getComponent;
 f.player.getComponent=id=>{if(id===(hand==='main'?'minecraft:inventory':'minecraft:equippable'))throw Error('unreadable');return original(id);};
 assert.equal(f.interact().cancel,false);assert.equal(f.queued,0);f.player.getComponent=original;equal(f.get('off'),s);
});
for(const change of ['off ID','off DP','off name','off restrictions','main occupied','selected slot','target','support','dimension','reach','mode','invalid player','unresolved projection'])test(`script queued ${change} change prevents placement and consumption`,()=>{
 const f=fixture(),s=decorated(f,'pending');f.set('off',s);f.phase.before=true;assert.equal(f.interact().cancel,true);assert.equal(f.phase.destroy+f.phase.place,0);f.phase.before=false;
 if(change.startsWith('off')){const changed=f.get('off');if(change==='off ID')changed.typeId=EMPTY;if(change==='off DP')f.api.setItemProperty(changed,'other:string','changed');if(change==='off name')changed.nameTag='changed';if(change==='off restrictions')changed.setCanPlaceOn(['minecraft:dirt']);f.set('off',changed);}
 if(change==='main occupied')f.set('main',new Stack('minecraft:diamond'));
 if(change==='selected slot')f.player.selectedSlotIndex=1;
 if(change==='target')f.block.setType('minecraft:stone');
 if(change==='support')f.block.below().setType('minecraft:cobblestone');
 if(change==='dimension')f.player.dimension={id:'minecraft:nether'};
 if(change==='reach')f.player.location.x=30;
 if(change==='mode')f.player.getGameMode=()=> 'adventure';
 if(change==='invalid player')f.player.isValid=false;
 if(change==='unresolved projection')f.dp.set(f.api.seasoningBlockKey(f.block),'reserved');
 const main=f.get('main'),off=f.get('off');f.flush();equal(f.get('main'),main);equal(f.get('off'),off);assert.equal(f.entities.size,0);
 if(change!=='target')assert.equal(f.block.typeId,'minecraft:air');
 // Claim is always released on rejected deferred actions.
 if(change==='off name'){assert.equal(f.interact().cancel,true);f.flush();equal(f.api.nativeBottles(f.block).items[0],off);}
});
for(const creative of [false,true])for(const order of ['script first','native first'])test(`shared pending claim deduplicates ${order}, creative=${creative}`,()=>{
 const f=fixture(),s=decorated(f,'pending');f.set('off',s);if(creative)f.player.getGameMode=()=> 'creative';
 if(order==='script first'){assert.equal(f.interact().cancel,true);f.queuePlace();}else{f.queuePlace();assert.equal(f.interact().cancel,false);}
 for(let i=0;i<18;i++)f.interact({isFirstEvent:i===0});assert.equal(f.queued,1);f.flush();assert.equal(f.entities.size,1);equal(f.api.nativeBottles(f.block).items[0],s);equal(f.get('off'),creative?s:undefined);
});
for(const kind of ['false','throw'])for(const after of [false,true])test(`script off write ${kind} after=${after} rolls back one deduplicated action and permits a new press`,()=>{
 const f=fixture(),s=decorated(f,'special',{uses:15,variant:7});f.set('off',s);f.interact();f.interact();f.queuePlace();assert.equal(f.queued,1);f.failOff(kind,after);f.flush();
 equal(f.get('off'),s);assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);assert.equal(f.dp.size,0);
 assert.equal(f.interact().cancel,true);f.flush();equal(f.api.nativeBottles(f.block).items[0],s);
});
test('main native first placement remains available after supplement declines the interaction',()=>{
 const f=fixture(),s=decorated(f,'pending');f.set('main',s);assert.equal(f.interact({itemStack:f.get('main')}).cancel,false);assert.equal(f.queued,0);
 f.placeMain();equal(f.api.nativeBottles(f.block).items[0],s);assert.equal(f.get('main'),undefined);
});
test('duplicate event wrappers with the same player ID share a pending claim',()=>{
 const f=fixture(),s=decorated(f,'pending');f.set('off',s);assert.equal(f.interact().cancel,true);
 assert.equal(f.interact({player:{...f.player}}).cancel,false);assert.equal(f.queued,1);f.flush();equal(f.api.nativeBottles(f.block).items[0],s);
});
