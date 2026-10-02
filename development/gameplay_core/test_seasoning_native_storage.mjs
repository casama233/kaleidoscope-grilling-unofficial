/** Actual function bodies and native-storage API doubles; no simulated players. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as core from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2743_seasoning_contract_core.js';
import * as visuals from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2766_special_seasoning_visual_core.js';
import {commitSteps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
import {slotWrite} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/rack_transfer_plan.js';
import {hasSolidTop} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/blockSupport.js';
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const read=n=>fs.readFileSync(new URL(n,root),'utf8');
const strip=s=>s.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(class|const|function|async))/g,'');
function fn(source,name){const start=source.indexOf('function '+name+'(');assert.ok(start>=0,name);let i=source.indexOf('{',start),depth=1,end=i+1;for(;depth&&end<source.length;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}return source.slice(start,end);}
const N='kaleidoscope_grilling:',EMPTY=N+'empty_seasoning_bottle',PENDING=N+'pending_seasoning';
class Stack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.maxAmount=16;this.props={};this.lore=[];}
 clone(){return Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}));}
}
function decorated(kind='special',uses=15){
 const s=new Stack(kind==='special'?visuals.specialSeasoningVisualId(uses,5):kind==='pending'?PENDING:EMPTY);
 Object.assign(s,{nameTag:'Original custom name',lore:[{text:'Unrelated lore'}],keepOnDeath:true,lockMode:'inventory',canDestroy:['minecraft:dirt'],canPlaceOn:['minecraft:stone'],opaqueNative:{marker:'copy all data'}});
 s.props={[core.SEASONING_LIST_KEY]:JSON.stringify(kind==='empty'?[]:core.BASE_SEASONINGS),[core.SEASONING_USES_KEY]:uses,[core.SEASONING_VARIANT_KEY]:5,'other:boolean':true,'other:number':7,'other:string':'kept','other:vector':{x:1,y:2,z:3}};return s;
}
function fixture(){
 const dp=new Map(),entities=new Map(),blocks=new Map(),queue=[],drops=[];let serial=0,hand,fail=()=>false,mode='survival';
 const mutate=(key,action)=>{action();if(fail(key))throw Error('Injected '+key);};
 const container=(id,size)=>({size,rows:Array(size),getItem(i){return this.rows[i]?.clone()},setItem(i,s){mutate(id+':slot'+i,()=>this.rows[i]=s?.clone())}});
 const dimension={id:'minecraft:overworld',getBlock(p){const k=[p.x,p.y,p.z].join('/');if(!blocks.has(k))blocks.set(k,makeBlock(p));return blocks.get(k);},getEntities(q){return [...entities.values()].filter(e=>e.typeId===q.type&&Math.hypot(e.location.x-q.location.x,e.location.y-q.location.y,e.location.z-q.location.z)<=q.maxDistance)},spawnParticle(){},spawnEntity(typeId,location){
  const id='entity'+(++serial),properties=new Map(),c=container(id,typeId.includes('seasoning')?4:typeId.includes('rack')?9:3);
  const e={id,typeId,location,dimension,c,getDynamicProperty:k=>properties.get(k),setDynamicProperty(k,v){mutate('owner',()=>properties.set(k,v))},getComponent:k=>k==='minecraft:inventory'?{container:c}:undefined,remove(){mutate('remove:'+id,()=>entities.delete(id))}};entities.set(id,e);if(fail('spawn-helper'))throw Error('Injected spawn-helper');return e;
 },spawnItem(item,location){const e={id:'drop'+(++serial),item:item.clone(),location,remove(){mutate('drop-remove',()=>drops.splice(drops.indexOf(e),1))}};drops.push(e);if(fail('spawn-drop'))throw Error('Injected spawn-drop');return e;}};
 function permutation(id,states={}){return {id,getAllStates:()=>({...states}),getState:k=>states[k]};}
 function makeBlock(location){let p=permutation('minecraft:air');return {...location,location:{...location},dimension,get typeId(){return p.id},get permutation(){return p},get isAir(){return p.id==='minecraft:air'},get isLiquid(){return false},getComponent(){return undefined},below(){return dimension.getBlock({...location,y:location.y-1})},setType(id){mutate('block:'+location.y,()=>p=permutation(id))},setPermutation(v){mutate('block:'+location.y,()=>p=v)}};}
 const world={getDynamicProperty:k=>dp.get(k),setDynamicProperty(k,v){mutate(k,()=>v===undefined?dp.delete(k):dp.set(k,v))},getEntity:id=>entities.get(id)};
 const holder={dimension,location:{x:0,y:65,z:0},selectedSlotIndex:0,isValid:true,getGameMode:()=>mode};
 let context,api;
 const load=()=>{
  context=vm.createContext({...core,...visuals,world,console:{warn(){}},system:{currentTick:10,run:f=>queue.push(f)},ItemStack:Stack,GameMode:{Survival:'survival',Creative:'creative'},commitSteps,slotWrite,hasSolidTop,
   EMPTY_SEASONING_ID:EMPTY,PENDING_SEASONING:PENDING,SEASON_USES_KEY:core.SEASONING_USES_KEY,SEASON_VARIANT_KEY:core.SEASONING_VARIANT_KEY,
   readSeasonings:s=>JSON.parse(s?.props[core.SEASONING_LIST_KEY]??'[]'),setSeasonings(s,v){s.props[core.SEASONING_LIST_KEY]=JSON.stringify(v);},getItemProperty:(s,k)=>s.props[k],setItemProperty:(s,k,v)=>s.props[k]=v,setItemLore:(s,v)=>s.lore=structuredClone(v),specialSeasoningVariant:s=>s.props[core.SEASONING_VARIANT_KEY]??0,
   markPlacedVisualDirty(){},blockSound(){},message(){},javaInteractionFeedback(){},interactionFailure(){},awardSeasoningMilestones(){},transactionStatus:r=>r.ok,
   heldMain:()=>hand?.clone(),heldByHand:()=>hand?.clone(),creative:()=>mode==='creative',
   captureWritableHand(){const before=hand?.clone();return {before,write(s){mutate('hand',()=>hand=s?.clone())}}},
   captureInteractionIntent:()=>({hand:'main',signature:JSON.stringify(hand)}),interactionIntentStillCurrent:(_,intent)=>JSON.stringify(hand)===intent.signature});
  for(const name of ['family_station_storage.js','a2743_seasoning_block_adapter.js','seasoning_native_storage.js'])vm.runInContext(strip(read(name)),context);
  vm.runInContext('const readBottleStack=readPlacedSeasoningStack,writeBottleStack=writePlacedSeasoningStack,isSeasoningBlock=isSeasoningBlockId,stationStorageKey=storageKey;',context);
  const names=['copyOne','reducedStack','getUses','setUses','bottleDataFromItem','bottleItem','setBottleVisual','nativeBottles','bottleRollbackStatus','bottleProjectionStep','commitBottleAndHand','pushBottle','handleSeasoningBlock','sameBottleTarget','bottleTargetSnapshot','bottleActionSnapshot','bottleActionStillCurrent','scheduleNativeBottlePlacement','scheduleNativeBottleBreak','breakNativeBottles','tickNativeBottleSupport','scheduleNativeBottleExplosion'];
  const main=read('main.js');vm.runInContext(names.map(n=>fn(main,n)).join('\n'),context);
  api=vm.runInContext('({nativeBottles,pushBottle,handleSeasoningBlock,bottleActionSnapshot,bottleActionStillCurrent,scheduleNativeBottlePlacement,scheduleNativeBottleBreak,breakNativeBottles,tickNativeBottleSupport,scheduleNativeBottleExplosion,bottleDataFromItem,bottleItem,seasoningBlockKey,stationContainer,inspectStationStorage})',context);
 };
 load();const block=dimension.getBlock({x:0,y:64,z:0});block.below().setType('minecraft:stone');
 return {world,dimension,block,holder,dp,entities,queue,drops,permutation,get api(){return api},get hand(){return hand},set hand(s){hand=s?.clone()},setMode(v){mode=v},reload(){load()},failOnce(target){let once=true;fail=k=>once&&k===target?(once=false,true):false},setFault(fn){fail=fn},place(){const e={block,player:holder,face:'Up',permutationToPlace:permutation(N+'seasoning_bottle_1'),cancel:false};api.scheduleNativeBottlePlacement(e);while(queue.length)queue.shift()();return e;}};
}
const equal=(a,b)=>assert.equal(JSON.stringify(a),JSON.stringify(b));
for(const uses of [1,15])test('first placement and pickup preserve exact finished native stack uses '+uses,()=>{
 const f=fixture(),original=decorated('special',uses);f.hand=original;assert.equal(f.place().cancel,true);assert.equal(f.hand,undefined);equal(f.api.nativeBottles(f.block).items[0],original);
 f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,original);assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);
});
test('four differently named stacks survive independent runtime reload and variant owner changes',()=>{
 const f=fixture(),all=[];for(let i=0;i<4;i++){const s=decorated('special',i+1);s.nameTag='Bottle '+i;all.push(s);f.hand=s;if(!i)f.place();else f.api.pushBottle(f.block,f.holder,s);}
 assert.equal(f.block.typeId,N+'seasoning_bottle_4');f.reload();equal(f.api.nativeBottles(f.block).items,all);
 for(let i=3;i>=0;i--){f.hand=undefined;f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,all[i]);}
 assert.equal(f.entities.size,0);
});
test('pending remains pending and retains unrelated metadata when incomplete ingredients are added',()=>{
 const f=fixture(),s=decorated('pending');s.props[core.SEASONING_LIST_KEY]='[]';f.hand=s;f.place();f.hand=new Stack('minecraft:redstone');f.api.handleSeasoningBlock(f.block,f.holder);const stored=f.api.nativeBottles(f.block).items[0];
 assert.equal(stored.typeId,PENDING);assert.equal(stored.nameTag,s.nameTag);equal(stored.lore,s.lore);equal(stored.opaqueNative,s.opaqueNative);equal(JSON.parse(stored.props[core.SEASONING_LIST_KEY]),['minecraft:redstone']);
});
test('empty with incomplete ingredients preserves metadata, explicit empty-to-pending promotion recreates it',()=>{
 const f=fixture(),s=decorated('empty');f.hand=s;f.place();
 for(let i=0;i<3;i++){f.hand=new Stack(core.BASE_SEASONINGS[i]);f.api.handleSeasoningBlock(f.block,f.holder);const stored=f.api.nativeBottles(f.block).items[0];assert.equal(stored.typeId,i<2?EMPTY:PENDING);assert.equal(stored.nameTag,i<2?s.nameTag:undefined);}
});
test('creative player break returns every native bottle without normalizing it',()=>{
 const f=fixture(),s=decorated('empty');s.props[core.SEASONING_LIST_KEY]=JSON.stringify(core.BASE_SEASONINGS);f.hand=s;f.place();f.setMode('creative');assert.equal(f.api.breakNativeBottles(f.block),true);equal(f.drops[0].item,s);assert.equal(f.entities.size,0);assert.equal(f.block.typeId,'minecraft:air');
});
test('only empty-with-base pickup promotes to fresh pending',()=>{
 const f=fixture(),s=decorated('empty');s.props[core.SEASONING_LIST_KEY]=JSON.stringify(core.BASE_SEASONINGS);f.hand=s;f.place();f.api.handleSeasoningBlock(f.block,f.holder);assert.equal(f.hand.typeId,PENDING);assert.equal(f.hand.nameTag,undefined);
});
for(const target of ['block:64','entity1:slot0','hand'])test('first placement failure '+target+' retains original input and restores target',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.failOnce(target);f.place();equal(f.hand,s);assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);assert.equal(f.dp.size,0);
});
test('first placement projection rejection retains input and clears native duplicate',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.failOnce(f.api.seasoningBlockKey(f.block));f.place();equal(f.hand,s);assert.equal(f.block.typeId,'minecraft:air');for(const e of f.entities.values())assert.ok(e.c.rows.every(x=>!x));
});
test('changed target and changed hand cancel deferred placement before any debit',()=>{
 for(const what of ['hand','target']){const f=fixture(),s=decorated();f.hand=s;f.api.scheduleNativeBottlePlacement({block:f.block,player:f.holder,face:'Up',permutationToPlace:f.permutation(N+'seasoning_bottle_1')});if(what==='hand')f.hand=new Stack('minecraft:stone');else f.block.setType('minecraft:stone');while(f.queue.length)f.queue.shift()();assert.equal(f.entities.size,0);assert.equal(f.hand.typeId,what==='hand'?'minecraft:stone':s.typeId);}
});
for(const target of ['entity1:slot0','block:64','hand'])test('pickup rejection '+target+' retains original native item and projection',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.place();const raw=f.dp.get(f.api.seasoningBlockKey(f.block));f.failOnce(target);assert.equal(f.api.handleSeasoningBlock(f.block,f.holder),undefined);assert.equal(f.hand,undefined);equal(f.api.nativeBottles(f.block).items[0],s);assert.equal(f.dp.get(f.api.seasoningBlockKey(f.block)),raw);
});
test('legacy rows bootstrap only when no owner exists and cannot invent lost metadata',()=>{
 const f=fixture();f.block.setType(N+'seasoning_bottle_1');const row={kind:'special',ingredients:[...core.BASE_SEASONINGS],uses:15,variant:5};f.world.setDynamicProperty(f.api.seasoningBlockKey(f.block),JSON.stringify([row]));const native=f.api.nativeBottles(f.block);equal(f.api.bottleDataFromItem(native.items[0]),row);assert.equal(native.items[0].nameTag,undefined);f.reload();equal(f.api.nativeBottles(f.block).items,native.items);
});
test('missing linked helper never falls back to reconstructing legacy rows',()=>{
 const f=fixture();f.hand=decorated();f.place();f.entities.clear();assert.throws(()=>f.api.nativeBottles(f.block),/unavailable/);assert.equal(f.entities.size,0);
});
test('existing block without state does not synthesize an empty bottle',()=>{
 const f=fixture();f.block.setType(N+'seasoning_bottle_1');assert.throws(()=>f.api.nativeBottles(f.block),/no readable/);assert.equal(f.entities.size,0);
});
test('native/projection mismatch fails closed instead of replacing the native item',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.place();const c=f.api.stationContainer(f.block);c.setItem(0,new Stack('minecraft:stone'));assert.throws(()=>f.api.nativeBottles(f.block),/mismatch/);assert.equal(c.getItem(0).typeId,'minecraft:stone');
});

test('unknown native item cannot masquerade as empty bottle and be promoted',()=>{
 const f=fixture();f.hand=decorated('empty');f.place();const c=f.api.stationContainer(f.block),valuable=new Stack('minecraft:diamond');valuable.nameTag='Do not replace';c.setItem(0,valuable);
 assert.throws(()=>f.api.nativeBottles(f.block),/mismatch/);assert.equal(c.getItem(0).typeId,'minecraft:diamond');
});
test('pre-cancelled protected break is ignored',()=>{
 const f=fixture();f.hand=decorated();f.place();f.api.scheduleNativeBottleBreak({block:f.block,cancel:true});assert.equal(f.queue.length,0);assert.equal(f.drops.length,0);
});
test('deferred break rejects a replaced owner or changed target',()=>{
 for(const changed of ['owner','target']){const f=fixture();f.hand=decorated();f.place();f.api.scheduleNativeBottleBreak({block:f.block,cancel:false});
  if(changed==='target')f.block.setType(N+'seasoning_bottle_2');else{const key=[...f.dp.keys()].find(k=>k.includes('storage_v1/'));const value=JSON.parse(f.dp.get(key));value.token+='replacement';f.world.setDynamicProperty(key,JSON.stringify(value));}
  while(f.queue.length)f.queue.shift()();assert.equal(f.drops.length,0);assert.notEqual(f.block.typeId,'minecraft:air');
 }
});

test('new ledger write-after-mutation failure retires demonstrably new empty helper',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.failOnce('kaleidoscope_grilling:storage_v1/minecraft:overworld/0/64/0');f.place();equal(f.hand,s);assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);assert.equal(f.dp.size,0);
});
test('queued bottle interaction identity rejects replacement owner and projection',()=>{
 const f=fixture();f.hand=decorated();f.place();const capture=f.api.bottleActionSnapshot(f.block);assert.equal(f.api.bottleActionStillCurrent(f.block,capture),true);
 const k=f.api.seasoningBlockKey(f.block);f.world.setDynamicProperty(k,'[]');assert.equal(f.api.bottleActionStillCurrent(f.block,capture),false);
});

test('support loss destroys Java bottle contents and retires helper without player payout',()=>{
 const f=fixture();f.hand=decorated();f.place();f.block.below().setType('minecraft:air');f.api.tickNativeBottleSupport(f.block);
 assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);assert.equal(f.dp.size,0);assert.equal(f.drops.length,0);
});
test('explosion keeps unrelated impacted blocks and clears matched bottle ownership without drops',()=>{
 const f=fixture();f.hand=decorated();f.place();const other=f.block.below();let impacted=[f.block,other];
 f.api.scheduleNativeBottleExplosion({cancel:false,getImpactedBlocks:()=>impacted,setImpactedBlocks:v=>impacted=v});equal(impacted,[other]);
 while(f.queue.length)f.queue.shift()();assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);assert.equal(f.dp.size,0);assert.equal(f.drops.length,0);
});
test('cancelled explosion and replaced bottle cannot destroy an unrelated new owner',()=>{
 for(const cancelled of [true,false]){const f=fixture();f.hand=decorated();f.place();let impacted=[f.block];
 f.api.scheduleNativeBottleExplosion({cancel:cancelled,getImpactedBlocks:()=>impacted,setImpactedBlocks:v=>impacted=v});
 if(!cancelled)f.block.setType('minecraft:stone');while(f.queue.length)f.queue.shift()();assert.equal(f.entities.size,1);assert.equal(f.drops.length,0);
 }
});
test('support removal failure restores original native contents instead of losing them',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.place();f.block.below().setType('minecraft:air');f.failOnce('block:64');f.api.tickNativeBottleSupport(f.block);
 assert.equal(f.block.typeId,N+'seasoning_bottle_1');equal(f.api.nativeBottles(f.block).items[0],s);assert.equal(f.drops.length,0);
});

test('empty retirement ledger-clear failure is safely retryable at the same coordinate',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.place();
 const key=[...f.dp.keys()].find(k=>k.includes('storage_v1/'));
 // Persist the retirement intent then reject its final deletion before mutation.
 const original=f.world.setDynamicProperty;let rejected=false;
 f.world.setDynamicProperty=(k,v)=>{if(k===key&&v===undefined&&!rejected){rejected=true;throw Error('ledger unavailable')}return original(k,v)};
 f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,s);assert.equal(f.entities.size,0);assert.equal(JSON.parse(f.dp.get(key)).retiredEmpty,true);
 f.place();assert.equal(f.hand,undefined);equal(f.api.nativeBottles(f.block).items[0],s);
});
test('remove-after-mutation retirement failure reuses the coordinate without cloning items',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.place();const c=f.api.stationContainer(f.block);
 f.setFault(k=>k.startsWith('remove:'));f.api.handleSeasoningBlock(f.block,f.holder);
 // remove-after-throw leaves a proven empty tombstone; a retry can clear it.
 const key=[...f.dp.keys()].find(k=>k.includes('storage_v1/'));assert.equal(JSON.parse(f.dp.get(key)).retiredEmpty,true);
 f.setFault(()=>false);f.place();assert.equal(f.hand,undefined);equal(f.api.nativeBottles(f.block).items[0],s);
});

test('unacknowledged drop creation quarantines the original inventory instead of claiming rollback',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.place();f.failOnce('spawn-drop');
 assert.throws(()=>f.api.breakNativeBottles(f.block),/recovery required/);assert.equal(f.drops.length,1);
 assert.throws(()=>f.api.nativeBottles(f.block),/quarantined/);
 const raw=[...f.dp.entries()].find(([k])=>k.includes('storage_v1/'))[1];assert.ok(JSON.parse(raw).quarantine);
});
test('retirement with unexpected nonempty inventory fails closed and preserves its items',()=>{
 const f=fixture(),s=decorated();f.hand=s;f.place();const c=f.api.stationContainer(f.block),entity=[...f.entities.values()][0];
 entity.remove=()=>{throw Error('remove rejected')};f.api.handleSeasoningBlock(f.block,f.holder);
 c.setItem(0,new Stack('minecraft:diamond'));f.hand=s;f.place();assert.equal(f.hand.typeId,s.typeId);assert.equal(c.getItem(0).typeId,'minecraft:diamond');assert.equal(f.block.typeId,'minecraft:air');
});
