import {captureSkewerMetadata,restoreSkewerMetadata,metadataSignature} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/skewer_item_snapshot.js';
import {canonicalFoodId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_profile_ids.js';
/** Actual function bodies and native-storage API doubles; no simulated players. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as core from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2743_seasoning_contract_core.js';
import {seasoningLore} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/localized_lore_core.js';
import {javaInteractionMessage,createFailureFeedbackGate} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/interaction_feedback_core.js';
import * as visuals from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2766_special_seasoning_visual_core.js';
import {commitSteps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
import {slotWrite} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/rack_transfer_plan.js';
import {hasSolidTop} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/blockSupport.js';
import * as placedCore from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2770_placed_visual_core.js';
import {visitUniqueTracked} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a288_visual_budget_core.js';
import {INGREDIENT_COLORS} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2770_placed_visual_data.js';
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const read=n=>fs.readFileSync(new URL(n,root),'utf8');
const strip=s=>s.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(class|const|function|async))/g,'');
function fn(source,name){const start=source.indexOf('function '+name+'(');assert.ok(start>=0,name);let i=source.indexOf('{',start),depth=1,end=i+1;for(;depth&&end<source.length;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}return source.slice(start,end);}
const N='kaleidoscope_grilling:',EMPTY=N+'empty_seasoning_bottle',PENDING=N+'pending_seasoning';
class Stack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.maxAmount=1;this.props={};this.lore=[];this.canDestroy=[];this.canPlaceOn=[];}
 clone(){return Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}));}
 getRawLore(){return structuredClone(this.lore)} getLore(){return this.lore} setLore(v){this.lore=structuredClone(v)}
 getDynamicPropertyIds(){return Object.keys(this.props)} getDynamicProperty(k){return structuredClone(this.props[k])} setDynamicProperty(k,v){if(v===undefined)delete this.props[k];else this.props[k]=structuredClone(v)}
 getCanDestroy(){return [...this.canDestroy]} setCanDestroy(v){this.canDestroy=[...v]} getCanPlaceOn(){return [...this.canPlaceOn]} setCanPlaceOn(v){this.canPlaceOn=[...v]} getComponent(){return undefined}
}
function decorated(kind='special',uses=15){
 const s=new Stack(kind==='special'?visuals.specialSeasoningVisualId(uses,5):kind==='pending'?PENDING:EMPTY);
 Object.assign(s,{nameTag:'Original custom name',lore:[{text:'Unrelated lore'}],keepOnDeath:true,lockMode:'inventory',canDestroy:['minecraft:dirt'],canPlaceOn:['minecraft:stone'],opaqueNative:{marker:'copy all data'}});
 s.props={[core.SEASONING_LIST_KEY]:JSON.stringify(kind==='empty'?[]:core.BASE_SEASONINGS),[core.SEASONING_USES_KEY]:uses,[core.SEASONING_VARIANT_KEY]:5,'other:boolean':true,'other:number':7,'other:string':'kept','other:vector':{x:1,y:2,z:3}};return s;
}
function fixture({withPlacedVisuals=false}={}){
 const dp=new Map(),entities=new Map(),blocks=new Map(),queue=[],drops=[],visualCalls=[],messages=[],feedback=[],customMessages=[];let serial=0,hand,fail=()=>false,mode='survival';
 const mutate=(key,action)=>{action();if(fail(key))throw Error('Injected '+key);};
 const container=(id,size)=>({size,rows:Array(size),getItem(i){return this.rows[i]?.clone()},setItem(i,s){mutate(id+':slot'+i,()=>this.rows[i]=s?.clone())}});
 const dimension={id:'minecraft:overworld',getBlock(p){const k=[p.x,p.y,p.z].join('/');if(!blocks.has(k))blocks.set(k,makeBlock(p));return blocks.get(k);},getEntities(q){return [...entities.values()].filter(e=>e.typeId===q.type&&(!q.location||Math.hypot(e.location.x-q.location.x,e.location.y-q.location.y,e.location.z-q.location.z)<=q.maxDistance))},spawnParticle(){},spawnEntity(typeId,location){
  const id='entity'+(++serial),properties=new Map(),c=container(id,typeId.includes('seasoning')?4:typeId.includes('rack')?9:3);
  const e={id,typeId,location,dimension,c,get isValid(){return entities.has(id)},getDynamicProperty:k=>properties.get(k),setDynamicProperty(k,v){mutate('owner',()=>properties.set(k,v))},getComponent:k=>k==='minecraft:inventory'?{container:c}:undefined,
   getProperty:k=>properties.get(k),setProperty(k,v){visualCalls.push(['property',id,k,v]);mutate('property:'+id,()=>properties.set(k,v))},
   teleport(p){visualCalls.push(['teleport',id]);mutate('teleport:'+id,()=>e.location={...p})},
   remove(){visualCalls.push(['remove',id]);mutate('remove:'+id,()=>entities.delete(id))}};entities.set(id,e);if(fail('spawn-helper'))throw Error('Injected spawn-helper');return e;
 },spawnItem(item,location){const e={id:'drop'+(++serial),item:item.clone(),location,remove(){mutate('drop-remove',()=>drops.splice(drops.indexOf(e),1))}};drops.push(e);if(fail('spawn-drop'))throw Error('Injected spawn-drop');return e;}};
 function permutation(id,states={}){return {id,getAllStates:()=>({...states}),getState:k=>states[k]};}
 function makeBlock(location){let p=permutation('minecraft:air');return {...location,location:{...location},dimension,get typeId(){return p.id},get permutation(){return p},get isAir(){return p.id==='minecraft:air'},get isLiquid(){return false},getComponent(){return undefined},below(){return dimension.getBlock({...location,y:location.y-1})},setType(id){mutate('block:'+location.y,()=>p=permutation(id))},setPermutation(v){mutate('block:'+location.y,()=>p=v)}};}
 const world={getDynamicProperty:k=>dp.get(k),setDynamicProperty(k,v){mutate(k,()=>v===undefined?dp.delete(k):dp.set(k,v))},getEntity:id=>entities.get(id),
  getDynamicPropertyIds:()=>[...dp.keys()],getAllPlayers:()=>[holder],getDimension(id){if(id===dimension.id||id==='overworld')return dimension;throw Error('Unloaded test dimension')},
  afterEvents:Object.fromEntries(['playerPlaceBlock','playerInteractWithBlock','playerBreakBlock'].map(name=>[name,{subscribe(){}}]))};
 // These storage roundtrips explicitly place pending bottles with Java's sneak
 // gesture; standing use is covered by test_seasoning_native_hands.mjs.
 const holder={sendMessage:m=>messages.push(structuredClone(m)),id:'test-player',dimension,location:{x:0,y:65,z:0},isSneaking:true,selectedSlotIndex:0,isValid:true,getGameMode:()=>mode};
 let context,api,placed;
 const load=()=>{
  const system={currentTick:10,run:f=>queue.push(f),runInterval(){},runJob(job){for(const step of job){}}};
  const visualContext=vm.createContext({...placedCore,visitUniqueTracked,INGREDIENT_COLORS,world,system,console:{warn(){}},grillingConfig:()=>({placedHelpers:1024}),HOST_BLOCK_ID:'kaleidoscope_cookery:oil_pot',readPlacedOilPotState(){throw Error('Not a bottle target')}});
  vm.runInContext(strip(read('a2770_placed_visual_queue.js')),visualContext);
  const visualQueue=vm.runInContext('({markPlacedVisualDirty,dirtyPlacedVisuals,visualLocationKey})',visualContext);
  context=vm.createContext({seasoningLore,canonicalFoodId,forgetEatingItem(){},...core,...visuals,interactionParticleBurst(){},world,console:{warn(){}},system:{currentTick:10,run:f=>queue.push(f)},ItemStack:Stack,captureSkewerMetadata,restoreSkewerMetadata,metadataSignature,EnchantmentType:class {constructor(id){this.id=id}},GameMode:{Survival:'survival',Creative:'creative'},commitSteps,slotWrite,hasSolidTop,
   EMPTY_SEASONING_ID:EMPTY,PENDING_SEASONING:PENDING,SEASON_USES_KEY:core.SEASONING_USES_KEY,SEASON_VARIANT_KEY:core.SEASONING_VARIANT_KEY,
   readSeasonings:s=>JSON.parse(s?.props[core.SEASONING_LIST_KEY]??'[]'),setSeasonings(s,v){s.props[core.SEASONING_LIST_KEY]=JSON.stringify(v);},getItemProperty:(s,k)=>s.props[k],setItemProperty:(s,k,v)=>s.props[k]=v,setItemLore:(s,v)=>s.lore=structuredClone(v),getItemRawLore:s=>structuredClone(s.lore),specialSeasoningVariant:s=>s.props[core.SEASONING_VARIANT_KEY]??0,
   markPlacedVisualDirty:visualQueue.markPlacedVisualDirty,refreshPlacedBottleAfterPickup(){},blockSound(){},message(...args){customMessages.push(args)},javaInteractionChat(player,key){player.sendMessage?.({translate:'message.kaleidoscope_grilling.'+key})},javaInteractionFeedback(_p,key){feedback.push(key)},interactionFailure(){},awardSeasoningMilestones(){},transactionStatus:r=>r.ok,
   heldMain:()=>hand?.clone(),heldByHand:()=>hand?.clone(),creative:()=>mode==='creative',
   captureWritableHand(_,which='main'){if(which==='off')return {before:undefined,write(){throw Error('Empty offhand fixture')}};const before=hand?.clone();return {before,write(s){mutate('hand',()=>hand=s?.clone())}}},
   captureInteractionIntent:()=>({hand:'main',signature:JSON.stringify(hand)}),interactionIntentStillCurrent:(_,intent)=>JSON.stringify(hand)===intent.signature});
  vm.runInContext(fn(read('eating_item_runtime.js'),'copyEatingVariant')+'\n'+['bottleFillIngredients','retargetBottleFillStack'].map(n=>fn(read('bottle_fill_item_runtime.js'),n)).join('\n'),context);
  for(const name of ['family_station_storage.js','a2743_seasoning_block_adapter.js','seasoning_native_storage.js'])vm.runInContext(strip(read(name)),context);
  if(withPlacedVisuals){
   visualContext.readPlacedSeasoningStack=vm.runInContext('readPlacedSeasoningStack',context);
   vm.runInContext(strip(read('a2770_placed_visual_runtime.js')),visualContext);
   placed={...visualQueue,...vm.runInContext('({pump,refreshPlacedBottleAfterPickup,tracked,owned})',visualContext)};
   context.refreshPlacedBottleAfterPickup=placed.refreshPlacedBottleAfterPickup;
  }
  vm.runInContext('const readBottleStack=readPlacedSeasoningStack,writeBottleStack=writePlacedSeasoningStack,isSeasoningBlock=isSeasoningBlockId,stationStorageKey=storageKey;',context);
  const names=['copyOne','reducedStack','getUses','setUses','bottleDataFromItem','bottleItem','setBottleVisual','nativeBottles','bottleRollbackStatus','bottleProjectionStep','commitBottleAndHand','pushBottle','refreshBottleIngredientLore','warnMissingSeasoningBase','handleSeasoningBlock','sameBottleTarget','bottleTargetSnapshot','bottleActionSnapshot','bottleActionStillCurrent','scheduleNativeBottlePlacement','scheduleNativeBottleBreak','breakNativeBottles','tickNativeBottleSupport','scheduleNativeBottleExplosion'];
  const main=read('main.js');vm.runInContext('const pendingBottlePlacements=new Set();\n'+fn(main,'queueBottlePlacement')+'\n'+names.map(n=>fn(main,n)).join('\n'),context);
  api=vm.runInContext('({nativeBottles,pushBottle,handleSeasoningBlock,bottleActionSnapshot,bottleActionStillCurrent,scheduleNativeBottlePlacement,scheduleNativeBottleBreak,breakNativeBottles,tickNativeBottleSupport,scheduleNativeBottleExplosion,bottleDataFromItem,bottleItem,seasoningBlockKey,stationContainer,inspectStationStorage,retargetBottleFillStack})',context);
 };
 load();const block=dimension.getBlock({x:0,y:64,z:0});block.below().setType('minecraft:stone');
 return {world,dimension,block,holder,dp,entities,queue,drops,messages,visualCalls,feedback,customMessages,permutation,get api(){return api},get placed(){return placed},get hand(){return hand},set hand(s){hand=s?.clone()},setMode(v){mode=v},reload(){load()},failOnce(target){let once=true;fail=k=>once&&k===target?(once=false,true):false},setFault(fn){fail=fn},place(){const e={block,player:holder,face:'Up',permutationToPlace:permutation(N+'seasoning_bottle_1'),cancel:false};api.scheduleNativeBottlePlacement(e);while(queue.length)queue.shift()();return e;}};
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
 assert.equal(stored.typeId,PENDING+'_f1');assert.equal(stored.nameTag,s.nameTag);equal(stored.lore.filter(l=>l.text),s.lore.filter(l=>l.text));assert.equal(stored.opaqueNative,undefined,'Opaque data cannot be projected across a type change');equal(JSON.parse(stored.props[core.SEASONING_LIST_KEY]),['minecraft:redstone']);
});
test('empty with incomplete ingredients preserves metadata, explicit empty-to-pending promotion recreates it',()=>{
 const f=fixture(),s=decorated('empty');f.hand=s;f.place();
 for(let i=0;i<3;i++){f.hand=new Stack(core.BASE_SEASONINGS[i]);f.api.handleSeasoningBlock(f.block,f.holder);const stored=f.api.nativeBottles(f.block).items[0];assert.equal(stored.typeId,core.seasoningFillVisualId(i<2?EMPTY:PENDING,core.BASE_SEASONINGS.slice(0,i+1)));assert.equal(stored.nameTag,i<2?s.nameTag:undefined);}
});
for(const kind of ['empty','pending'])test('partial '+kind+' add/pickup/replacement roundtrip preserves exact native ingredients and metadata',()=>{
 const f=fixture(),s=decorated(kind);s.props[core.SEASONING_LIST_KEY]='[]';f.hand=s;f.place();
 for(const id of ['minecraft:redstone',core.BASE_SEASONINGS[0]]){
  f.hand=new Stack(id);f.api.handleSeasoningBlock(f.block,f.holder);
 }
 const stored=f.api.nativeBottles(f.block).items[0];
 assert.equal(stored.typeId,N+(kind==='empty'?'partial':'pending')+'_seasoning_f2');equal(JSON.parse(stored.props[core.SEASONING_LIST_KEY]),['minecraft:redstone',core.BASE_SEASONINGS[0]]);
 assert.equal(stored.nameTag,s.nameTag);equal(stored.lore.filter(l=>l.text),s.lore.filter(l=>l.text));assert.equal(stored.opaqueNative,undefined,'Opaque data cannot be projected across a type change');
 f.hand=undefined;f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,stored);assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);
 f.place();equal(f.api.nativeBottles(f.block).items[0],stored);
 f.hand=undefined;f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,stored);
});
test('creative player break returns every native bottle without normalizing it',()=>{
 const f=fixture(),s=decorated('empty');s.props[core.SEASONING_LIST_KEY]=JSON.stringify(core.BASE_SEASONINGS);f.hand=s;f.place();f.setMode('creative');assert.equal(f.api.breakNativeBottles(f.block),true);equal(f.drops[0].item,s);assert.equal(f.entities.size,0);assert.equal(f.block.typeId,'minecraft:air');
});
test('only empty-with-base pickup promotes to fresh pending',()=>{
 const f=fixture(),s=decorated('empty');s.props[core.SEASONING_LIST_KEY]=JSON.stringify(core.BASE_SEASONINGS);f.hand=s;f.place();f.api.handleSeasoningBlock(f.block,f.holder);assert.equal(f.hand.typeId,PENDING+'_f3');assert.equal(f.hand.nameTag,undefined);
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

for(const kind of ['partial','pending'])for(let fill=1;fill<=8;fill++)test(`${kind} fill ${fill} native place/reload/pickup retains the exact proxy stack`,()=>{
 const f=fixture(),s=decorated(kind==='partial'?'empty':'pending');s.typeId=N+kind+'_seasoning_f'+fill;s.props[core.SEASONING_LIST_KEY]=JSON.stringify(Array(fill).fill('minecraft:redstone'));s.lore.push(...seasoningLore(undefined,fill,{pending:kind==='pending',missingBase:kind==='partial'}));
 f.hand=s;f.place();equal(f.api.nativeBottles(f.block).items[0],s);f.reload();equal(f.api.nativeBottles(f.block).items[0],s);
 f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,s);assert.equal(f.block.typeId,'minecraft:air');assert.equal(f.entities.size,0);
});

// Production transaction + placed renderer + dirty queue, using API doubles.
// These assertions prove synchronous script work, not client packet/frame timing.
const placedEntities=f=>[...f.entities.values()].filter(e=>e.typeId===placedCore.SEASON_ENTITY);
const visualRow=(f,block=f.block)=>f.placed.tracked.get(f.placed.visualLocationKey(block.dimension.id,block.location));
function placedFixture(count=1){
 const f=fixture({withPlacedVisuals:true}),originals=[];
 for(let i=0;i<count;i++){
  const s=decorated('special',i+1);s.nameTag='Placed bottle '+i;originals.push(s);f.hand=s;
  if(i)f.api.pushBottle(f.block,f.holder,s);else f.place();
 }
 f.hand=undefined;f.placed.pump();f.visualCalls.length=0;
 return {f,originals};
}
test('successful last pickup removes its owned placed helper before returning, after inventory commit',()=>{
 const {f,originals}=placedFixture(),visual=placedEntities(f)[0],remove=visual.remove;
 visual.remove=()=>{
  equal(f.hand,originals[0]);assert.equal(f.block.typeId,'minecraft:air');
  assert.equal(f.dp.get(f.api.seasoningBlockKey(f.block)),undefined);
  assert.equal([...f.entities.values()].some(e=>e.typeId===N+'inventory_seasoning_v1'),false);
  remove();
 };
 // Neither a world-player query nor a broad nearby-entity lookup is needed.
 f.world.getAllPlayers=()=>{throw Error('Post-commit refresh queried players')};
 f.dimension.getEntities=()=>{throw Error('Post-commit refresh queried entities')};
 f.api.handleSeasoningBlock(f.block,f.holder);
 equal(f.hand,originals[0]);assert.equal(placedEntities(f).length,0);assert.equal(f.placed.tracked.size,0);assert.equal(f.placed.owned.size,0);
 assert.equal(f.placed.dirtyPlacedVisuals.size,1,'Normal reconciliation remains queued');
 const calls=f.visualCalls.length;f.placed.refreshPlacedBottleAfterPickup(f.block);assert.equal(f.visualCalls.length,calls,'Duplicate refresh is inert');
});
for(const count of [2,3,4])test(`${count}-bottle pickup immediately repositions survivors even without a nearby player snapshot`,()=>{
 const {f,originals}=placedFixture(count),row=visualRow(f),ids=[...row.helpers.values()].map(x=>x.id);
 f.holder.location={x:1000,y:65,z:1000};
 f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,originals.at(-1));equal(f.api.nativeBottles(f.block).items,originals.slice(0,-1));
 assert.equal(row.helpers.size,count-1);assert.equal(f.entities.has(ids.at(-1)),false);
 for(let i=0;i<count-1;i++){
  const e=row.helpers.get(i).entity,o=placedCore.positions(count-1)[i];assert.equal(e.id,ids[i]);
  equal(e.location,{x:.5+o[0]/16,y:64,z:.5+o[1]/16});
  assert.equal(e.getProperty(N+'ready'),true);assert.equal(e.getProperty(N+'fill'),Math.ceil((16-(i+1))/2));
 }
 const calls=f.visualCalls.length;f.placed.refreshPlacedBottleAfterPickup(f.block);assert.equal(f.visualCalls.length,calls);
 f.holder.location={x:0,y:65,z:0};f.placed.pump();assert.equal(f.visualCalls.length,calls,'Queued reconciliation is idempotent');
});
for(const target of ['entity1:slot0','block:64','hand','projection'])test(`pickup rollback at ${target} does not touch placed helpers`,()=>{
 const {f,originals}=placedFixture(),row=visualRow(f),entry=row.helpers.get(0),signature=entry.signature;
 f.failOnce(target==='projection'?f.api.seasoningBlockKey(f.block):target);
 f.api.handleSeasoningBlock(f.block,f.holder);
 assert.equal(f.hand,undefined);equal(f.api.nativeBottles(f.block).items,originals);assert.equal(f.block.typeId,N+'seasoning_bottle_1');
 assert.equal(row.helpers.get(0),entry);assert.equal(entry.signature,signature);assert.equal(f.visualCalls.length,0);
 f.placed.pump();assert.equal(f.visualCalls.length,0,'Deferred refresh sees only rolled-back contents');
});
test('failed placed-helper removal preserves the committed pickup and retries through the normal pump',()=>{
 const {f,originals}=placedFixture(),row=visualRow(f),entry=row.helpers.get(0),remove=entry.entity.remove;let attempts=0;
 entry.entity.remove=()=>{if(++attempts===1)throw Error('Visual remove rejected before mutation');remove()};
 assert.doesNotThrow(()=>f.api.handleSeasoningBlock(f.block,f.holder));equal(f.hand,originals[0]);assert.equal(f.block.typeId,'minecraft:air');
 assert.equal(row.helpers.get(0),entry);assert.ok(f.placed.owned.has(entry.id));assert.ok(f.placed.tracked.has(f.placed.visualLocationKey(f.block.dimension.id,f.block.location)));
 assert.equal(f.placed.dirtyPlacedVisuals.size,1);
 f.placed.pump();assert.equal(attempts,2);assert.equal(f.entities.size,0);assert.equal(f.placed.owned.size,0);assert.equal(f.placed.tracked.size,0);equal(f.hand,originals[0]);
});
test('remove-after-mutation visual failure is cleared on retry without repeating the inventory transfer',()=>{
 const {f,originals}=placedFixture(),entry=visualRow(f).helpers.get(0);f.failOnce('remove:'+entry.id);
 f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,originals[0]);assert.equal(f.entities.has(entry.id),false);assert.equal(f.placed.owned.size,1);
 f.placed.pump();assert.equal(f.placed.owned.size,0);assert.equal(f.placed.tracked.size,0);equal(f.hand,originals[0]);
});
test('invalid surviving visual is reconstructed from committed rows during pickup',()=>{
 const {f,originals}=placedFixture(2),row=visualRow(f),old=row.helpers.get(0);f.entities.delete(old.id);
 f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,originals[1]);equal(f.api.nativeBottles(f.block).items,[originals[0]]);
 const replacement=row.helpers.get(0);assert.notEqual(replacement.id,old.id);assert.equal(replacement.entity.getProperty(N+'ready'),true);
 equal(replacement.entity.location,{x:.5,y:64,z:.5});assert.equal(f.placed.owned.has(old.id),false);assert.equal(placedEntities(f).length,1);
});
test('survivor reconstruction failure cannot escape pickup or undo inventory and is retried later',()=>{
 const {f,originals}=placedFixture(2),row=visualRow(f),old=row.helpers.get(0),spawn=f.dimension.spawnEntity;f.entities.delete(old.id);
 f.dimension.spawnEntity=()=>{throw Error('Visual spawn unavailable')};
 assert.doesNotThrow(()=>f.api.handleSeasoningBlock(f.block,f.holder));equal(f.hand,originals[1]);equal(f.api.nativeBottles(f.block).items,[originals[0]]);
 assert.equal(f.placed.dirtyPlacedVisuals.size,1);f.dimension.spawnEntity=spawn;f.placed.pump();
 assert.equal(row.helpers.size,1);equal(row.helpers.get(0).entity.location,{x:.5,y:64,z:.5});assert.equal(row.helpers.get(0).entity.getProperty(N+'ready'),true);
});
test('visual property failure preserves committed survivors and the normal pump rebuilds the display',()=>{
 const {f,originals}=placedFixture(2),row=visualRow(f),old=row.helpers.get(0);f.failOnce('property:'+old.id);
 assert.doesNotThrow(()=>f.api.handleSeasoningBlock(f.block,f.holder));equal(f.hand,originals[1]);equal(f.api.nativeBottles(f.block).items,[originals[0]]);
 assert.equal(row.helpers.size,0);f.placed.pump();assert.equal(row.helpers.size,1);assert.equal(row.helpers.get(0).entity.getProperty(N+'ready'),true);
});
test('immediate pickup refresh is isolated to its tracked coordinate and renderer-owned helpers',()=>{
 const {f,originals}=placedFixture(),other=f.dimension.getBlock({x:4,y:64,z:0});other.below().setType('minecraft:stone');
 const otherBottle=decorated('pending');f.hand=otherBottle;
 f.api.scheduleNativeBottlePlacement({block:other,player:f.holder,face:'Up',permutationToPlace:f.permutation(N+'seasoning_bottle_1'),cancel:false});
 while(f.queue.length)f.queue.shift()();f.hand=undefined;f.placed.pump();
 const otherEntry=visualRow(f,other).helpers.get(0),signature=otherEntry.signature;
 const unowned=f.dimension.spawnEntity(placedCore.SEASON_ENTITY,{x:.5,y:64,z:.5});f.visualCalls.length=0;
 f.api.handleSeasoningBlock(f.block,f.holder);f.placed.refreshPlacedBottleAfterPickup(f.block);
 equal(f.hand,originals[0]);equal(f.api.nativeBottles(other).items,[otherBottle]);assert.equal(visualRow(f,other).helpers.get(0),otherEntry);assert.equal(otherEntry.signature,signature);
 assert.ok(f.entities.has(unowned.id));assert.ok(!f.placed.owned.has(unowned.id));assert.ok(f.entities.has(otherEntry.id));
 assert.equal(f.visualCalls.some(call=>call[1]===unowned.id||call[1]===otherEntry.id),false);
});
test('untracked surviving stack remains queued for normal reconstruction after pickup',()=>{
 const f=fixture({withPlacedVisuals:true}),first=decorated('special',1),second=decorated('special',2);
 f.hand=first;f.place();f.hand=second;f.api.pushBottle(f.block,f.holder,second);f.hand=undefined;
 assert.equal(f.placed.tracked.size,0);f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,second);
 assert.equal(f.placed.tracked.size,0);assert.equal(placedEntities(f).length,0);assert.equal(f.placed.dirtyPlacedVisuals.size,1);
 f.placed.pump();assert.equal(placedEntities(f).length,1);equal(f.api.nativeBottles(f.block).items,[first]);
});

const countKey='tooltip.kaleidoscope_grilling.seasoning.ingredients';
const countOf=s=>s.lore.find(l=>l.translate===countKey)?.with?.[0];
const allEight=['kaleidoscope_grilling:totem_powder',...core.BASE_SEASONINGS,...Object.keys(core.SEASONING_KINDS).filter(id=>id!=='kaleidoscope_grilling:totem_powder'&&!core.BASE_SEASONINGS.includes(id))];
test('totem first then three bases counts 4 through 8 across pickup replacement and runtime reload',()=>{
 const f=fixture();f.hand=new Stack(EMPTY);f.place();
 for(let i=0;i<allEight.length;i++){
  f.hand=new Stack(allEight[i],3);f.api.handleSeasoningBlock(f.block,f.holder);assert.equal(f.hand.amount,2);
  const stored=f.api.nativeBottles(f.block).items[0];assert.equal(countOf(stored),String(i+1));equal(f.api.bottleDataFromItem(stored).ingredients,allEight.slice(0,i+1));
  assert.equal(core.isPendingSeasoningId(stored.typeId),i>=3);
  f.hand=undefined;f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,stored);f.place();f.reload();equal(f.api.nativeBottles(f.block).items[0],stored);
 }
 const before=f.api.nativeBottles(f.block).items[0];f.hand=new Stack('minecraft:redstone',3);f.api.handleSeasoningBlock(f.block,f.holder);assert.equal(f.hand.amount,3);equal(f.api.nativeBottles(f.block).items[0],before);
});
for(const kind of ['empty','pending'])test(kind+' same-kind count preserves independent bottle metadata and custom lore',()=>{
 const f=fixture(),lower=decorated('special'),s=decorated(kind);lower.nameTag='Lower untouched';f.hand=lower;f.place();
 s.props[core.SEASONING_LIST_KEY]='[]';s.lore.push(...seasoningLore(undefined,0,{pending:kind==='pending',missingBase:kind==='empty'}));f.hand=s;f.api.pushBottle(f.block,f.holder,s);
 for(let i=1;i<=8;i++){
  f.hand=new Stack('minecraft:redstone',3);f.api.handleSeasoningBlock(f.block,f.holder);const rows=f.api.nativeBottles(f.block).items,stored=rows[1];equal(rows[0],lower);
  assert.equal(countOf(stored),String(i));equal(stored.lore.filter(l=>l.text),s.lore.filter(l=>l.text));
  for(const key of ['nameTag','amount','keepOnDeath','lockMode','canDestroy','canPlaceOn'])equal(stored[key],s[key]);
  for(const [key,value] of Object.entries(s.props))if(key!==core.SEASONING_LIST_KEY)equal(stored.props[key],value);
  assert.equal(core.isPendingSeasoningId(stored.typeId),kind==='pending');f.reload();equal(f.api.nativeBottles(f.block).items,rows);
 }
});
test('pending promotion count specifically advances from 4 to 8',()=>{
 const f=fixture();f.hand=f.api.bottleItem({kind:'pending',ingredients:allEight.slice(0,4),uses:0,variant:0});f.place();assert.equal(countOf(f.api.nativeBottles(f.block).items[0]),'4');
 for(const id of allEight.slice(4)){f.hand=new Stack(id,3);f.api.handleSeasoningBlock(f.block,f.holder)}
 f.hand=undefined;f.api.handleSeasoningBlock(f.block,f.holder);assert.equal(countOf(f.hand),'8');equal(f.api.bottleDataFromItem(f.hand).ingredients,allEight);
});

const warning={translate:'message.kaleidoscope_grilling.missing_base_seasoning'};
for(const kind of ['empty','pending','special'])for(const ingredients of [[],['minecraft:redstone'],[...core.BASE_SEASONINGS]])test(kind+' pickup exact chat warning '+JSON.stringify(ingredients),()=>{
 const f=fixture(),s=decorated(kind);s.props[core.SEASONING_LIST_KEY]=JSON.stringify(ingredients);f.hand=s;f.place();f.api.handleSeasoningBlock(f.block,f.holder);equal(f.messages,ingredients.length&&!core.hasSeasoningBase(ingredients)?[warning]:[]);
});
test('failed pickup does not warn or mutate original bottle',()=>{
 const f=fixture(),s=decorated('pending');s.props[core.SEASONING_LIST_KEY]='["minecraft:redstone"]';f.hand=s;f.place();f.failOnce('hand');f.api.handleSeasoningBlock(f.block,f.holder);equal(f.messages,[]);equal(f.api.nativeBottles(f.block).items[0],s);
});
for(const fail of [false,true])test('player break four bottles warning follows successful transaction '+!fail,()=>{
 const f=fixture(),original=[];for(const ingredients of [[],['minecraft:redstone'],[...core.BASE_SEASONINGS],['kaleidoscope_grilling:totem_powder']]){const s=decorated('pending');s.props[core.SEASONING_LIST_KEY]=JSON.stringify(ingredients);original.push(s);f.hand=s;if(original.length===1)f.place();else f.api.pushBottle(f.block,f.holder,s)}
 if(fail)f.failOnce('entity1:slot0');f.api.scheduleNativeBottleBreak({block:f.block,player:f.holder,cancel:false});while(f.queue.length)f.queue.shift()();
 equal(f.messages,fail?[]:[warning,warning]);if(fail){equal(f.api.nativeBottles(f.block).items,original);assert.equal(f.drops.length,0)}else{equal(f.drops.map(d=>d.item),original);assert.equal(f.block.typeId,'minecraft:air')}
});
test('nonplayer destruction and support loss never emit missing-base chat',()=>{
 for(const support of [false,true]){const f=fixture(),s=decorated('pending');s.props[core.SEASONING_LIST_KEY]='["minecraft:redstone"]';f.hand=s;f.place();if(support){f.block.below().setType('minecraft:air');f.api.tickNativeBottleSupport(f.block)}else f.api.breakNativeBottles(f.block);equal(f.messages,[])}
});

for(const kind of ['empty','pending'])for(const fail of [false,true])test(kind+' stale full8 pickup repairs only owned lore, transactional failure='+fail,()=>{
 const f=fixture(),s=decorated(kind),ingredients=kind==='pending'?allEight:Array(8).fill('minecraft:redstone');s.props[core.SEASONING_LIST_KEY]=JSON.stringify(ingredients);s.typeId=core.seasoningFillVisualId(s.typeId,ingredients);s.lore.push(...seasoningLore(undefined,4,{pending:kind==='pending',missingBase:kind==='empty'}));f.hand=s;f.place();
 if(fail)f.failOnce('hand');f.api.handleSeasoningBlock(f.block,f.holder);
 if(fail){assert.equal(f.hand,undefined);equal(f.api.nativeBottles(f.block).items[0],s);return}
 const expected=s.clone();expected.lore=[...s.lore.filter(l=>l.text),...seasoningLore(undefined,8,{pending:kind==='pending',missingBase:kind==='empty'})];equal(f.hand,expected);equal(f.hand.props,s.props);
 f.place();f.reload();equal(f.api.nativeBottles(f.block).items[0],expected);f.api.handleSeasoningBlock(f.block,f.holder);equal(f.hand,expected);
});

for(const count of [1,8])for(const input of [core.BASE_SEASONINGS[0],'minecraft:stone'])test('source rejection key for '+input+' on '+count+'/8 finished',()=>{
 const f=fixture(),s=decorated('special');s.props[core.SEASONING_LIST_KEY]=JSON.stringify(Array(count).fill(core.BASE_SEASONINGS[0]));f.hand=s;f.place();const before=f.api.nativeBottles(f.block).items;f.hand=new Stack(input);f.api.handleSeasoningBlock(f.block,f.holder);assert.deepEqual(f.feedback,[count===8?'bottle_full':'invalid_seasoning']);assert.deepEqual(f.customMessages,[]);equal(f.api.nativeBottles(f.block).items,before);assert.equal(f.hand.amount,1);
});
test('fifth bottle remains quiet and unconsumed',()=>{
 const f=fixture();for(let i=0;i<4;i++){f.hand=decorated('empty');if(i)f.api.pushBottle(f.block,f.holder,f.hand);else f.place();}f.hand=decorated('pending');const before=f.hand;assert.equal(f.api.pushBottle(f.block,f.holder,f.hand),false);equal(f.hand,before);assert.deepEqual(f.customMessages,[]);assert.deepEqual(f.feedback,[]);
});

test('the original false-overlay missing-base message goes to translated chat',()=>{
 const chat=[],bar=[],context=vm.createContext({javaInteractionMessage,createFailureFeedbackGate,system:{currentTick:0},world:{afterEvents:{playerLeave:{subscribe(){}}}}});
 vm.runInContext(strip(read('a283_interaction_feedback.js'))+';this.chat=javaInteractionChat;',context);
 const player={sendMessage(v){chat.push(v)},onScreenDisplay:{setActionBar(v){bar.push(v)}}};
 assert.equal(context.chat(player,'missing_base_seasoning'),true);assert.deepEqual(JSON.parse(JSON.stringify(chat)),[javaInteractionMessage('missing_base_seasoning')]);assert.deepEqual(bar,[]);
 assert.equal(context.chat(player,'invented_key'),false);assert.equal(chat.length,1);
});
