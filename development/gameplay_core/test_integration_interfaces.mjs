/** Fault injection uses storage adapters. Native cross-pack/restart proof is separate. */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as stackAPI from '../../projects/grilling/gameplay_core/behavior_pack/scripts/integration_stack_core.js';
import * as registry from '../../projects/grilling/gameplay_core/behavior_pack/scripts/integration_registry_core.js';
import * as fortress from '../../projects/grilling/gameplay_core/behavior_pack/scripts/fortress_generation_core.js';
import {stationProjection} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/station_projection_core.js';
import {readPublicFood} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/food_api_core.js';
import {normalizeConfig,configValue} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/server_config_core.js';
class Stack{constructor(id='minecraft:cooked_beef',amount=1){this.typeId=id;this.amount=amount;this.lore=[];this.extra={foreign:'preserve'};}getRawLore(){return structuredClone(this.lore)}setLore(lore){this.lore=structuredClone(lore)}getComponent(k){return k==='minecraft:food'&&this.typeId==='test:data_driven'?{}:undefined}clone(){const n=new Stack(this.typeId,this.amount);Object.assign(n,structuredClone(this));return n;}}
const runtime='projects/grilling/gameplay_core/behavior_pack/scripts/integration_api_runtime.js';
function engine({saved=new Map(),fault}={}){
 registry.resetIntegrationRegistry();const props=new Map(saved),items=[new Stack()],responses=[],events={},blocks=new Map();let config=normalizeConfig(),now=1000;
 const key=p=>[p.x,p.y,p.z].join(','),signals={};const signal=name=>signals[name]??=({subscribe(fn){(events[name]??=[]).push(fn)}});
 const perm=(id,states={})=>({type:{id},getState:k=>states[k]});
 const dim={id:'minecraft:nether',getBlock:p=>blocks.get(key(p))};
 const container={size:items.length,getItem:i=>items[i]?.clone(),setItem(i,s){items[i]=s?.clone();fault?.('slot',i,s)}};
 const world={getAbsoluteTime:()=>now,getDynamicProperty:k=>{fault?.('get',k);return props.get(k)},setDynamicProperty(k,v){fault?.('before_property',k,v);props.set(k,v);fault?.('property',k,v)},getDimension:()=>dim,getEntity:()=>({getComponent:()=>({container})}),getAllPlayers:()=>[],afterEvents:{playerPlaceBlock:signal('place'),playerBreakBlock:signal('break')}};
 const system={run:fn=>fn(),afterEvents:{scriptEventReceive:signal('script')},sendScriptEvent:(id,bytes)=>responses.push({id,...JSON.parse(bytes)})};
 const context={...stackAPI,...registry,...fortress,stationProjection,readPublicFood,world,system,BlockPermutation:{resolve:perm},grillingConfig:()=>config,console};
 const code=fs.readFileSync(runtime,'utf8').replace(/^import .*;\n/gm,'').replace(/\bexport /g,'')+'\nthis.handle=handleIntegrationRequest;';vm.runInNewContext(code,context);
 let n=0;const invoke=(op,extra={})=>context.handle({api:1,requestId:'test/'+(++n),op,...extra});
 const register=()=>invoke('register_producer',{registration:{producerId:'test:producer',items:['minecraft:cooked_beef'],kinds:['cuisine','furnace','smoker','fresh_fortress']}});
 const output=(sequence=1)=>({producerId:'test:producer',sequence,kind:'cuisine',target:{kind:'entity_slot',entityId:'native-container',slot:0},expected:stackAPI.publicStackFingerprint(items[0]),metadata:{hotTicks:600,seasoning:['minecraft:redstone']}});
 function wart(p,age=2){const b={dimension:dim,...p,typeId:'minecraft:nether_wart',permutation:perm('minecraft:nether_wart',{age}),setPermutation(next){this.typeId=next.type.id;this.permutation=next;fault?.('block',key(p),next)}};blocks.set(key(p),b);blocks.set(key({...p,y:p.y-1}),{typeId:'minecraft:soul_sand'});return b;}
 return {props,items,responses,invoke,register,output,wart,events,setNow:v=>now=v,setConfig:v=>config=normalizeConfig(v)};
}
test('producer SDK preserves actual stack and Java-bucketed new deadlines; furnace option defaults off with original 30 seconds',()=>{
 const input=new Stack();input.nameTag='Authored';input.lore=['User lore'];const next=stackAPI.prepareProducedFood(input,{hotTicks:601,seasoning:['minecraft:redstone'],nativeVariant:7},1000);
 assert.equal(readPublicFood(next).state.hotUntil,1600);assert.equal(readPublicFood(next).state.nativeVariant,7);assert.deepEqual(next.extra,input.extra);assert.deepEqual(input.lore,['User lore']);
 assert.equal(readPublicFood(stackAPI.prepareProducedFood(input,{kind:'furnace'},1000)).state.hotUntil,0);
 assert.equal(readPublicFood(stackAPI.prepareProducedFood(input,{kind:'smoker'},1000,{enableSmeltedFoodHeat:true,smeltedFoodSeconds:30})).state.hotUntil,1600);
 assert.equal(configValue('smeltedFoodSeconds',86400),86400);assert.throws(()=>configValue('smeltedFoodSeconds',86401));
 input.lore=Array(20).fill('User lore');assert.throws(()=>stackAPI.prepareProducedFood(input,{},1000),/space/);assert.equal(input.lore.length,20);
});
test('native vanilla foods without a scripting food component use pinned Mojang definitions; nonfoods still reject',()=>{
 for(const id of ['minecraft:suspicious_stew','minecraft:cooked_beef','minecraft:bread']){const input=new Stack(id);assert.equal(input.getComponent('minecraft:food'),undefined);assert.equal(readPublicFood(stackAPI.prepareProducedFood(input,{hotTicks:600},1000)).state.hotUntil,1600);}
 assert.equal(readPublicFood(stackAPI.prepareProducedFood(new Stack('test:data_driven'),{},1000)).valid,true);
 assert.throws(()=>stackAPI.prepareProducedFood(new Stack('minecraft:stone'),{},1000),/not edible/);
});
test('public projection supports two variants of one item and explicit catalog aliases after registry restore',()=>{
 registry.resetIntegrationRegistry();registry.registerProjectionDescriptor({itemId:'minecraft:cooked_beef',provider:'test:model'});
 const first=new Stack(),second=new Stack();stackAPI.writePublicProjection(first,{v:1,provider:'test:model',data:3});stackAPI.writePublicProjection(second,{v:1,provider:'test:model',data:7});
 assert.equal(stationProjection(first).data,3);assert.equal(stationProjection(second).data,7);
 registry.registerHeldVisual({itemId:'test:food',referenceItemId:'minecraft:bread'});const alias=registry.secretVisualIndex('test:food'),saved=registry.integrationRegistrySnapshot();registry.resetIntegrationRegistry();registry.restoreIntegrationRegistry(saved);assert.equal(registry.secretVisualIndex('test:food'),alias);assert.equal(stationProjection(second).data,7);
 assert.throws(()=>registry.registerHeldVisual({itemId:'test:new',referenceItemId:'test:new_texture'}),/resource release/);
 first.lore.push(first.lore[0]);assert.throws(()=>stationProjection(first),/Unreadable/);
});
test('output sequence is bounded, survives restart, rejects stale/conflicting operations and never reheats replay',()=>{
 const e=engine();e.register();const request=e.output();assert.equal(e.invoke('decorate_output',request).replayed,false);assert.equal(readPublicFood(e.items[0]).state.hotUntil,1600);
 e.setNow(2000);assert.equal(e.invoke('decorate_output',request).replayed,true);assert.equal(readPublicFood(e.items[0]).state.hotUntil,1600);
 assert.throws(()=>e.invoke('decorate_output',{...request,metadata:{hotTicks:700}}),/conflict/);
 const restarted=engine({saved:e.props});assert.equal(restarted.invoke('decorate_output',request).replayed,true);
 assert.throws(()=>restarted.invoke('decorate_output',restarted.output(3)),/skipped/);
 restarted.invoke('decorate_output',restarted.output(2));assert.equal([...restarted.props.keys()].filter(k=>k.includes('integration_operation:')).length,1);
 assert.throws(()=>restarted.invoke('decorate_output',request),/stale/);
});
test('CAS comparison ignores JSON key order and refuses a changed target without advancing the sequence',()=>{
 const e=engine();e.register();const request=e.output();request.expected={lore:[],name:'',amount:1,id:'minecraft:cooked_beef'};e.invoke('decorate_output',request);
 const changed=e.output(2);e.items[0].amount=2;assert.throws(()=>e.invoke('decorate_output',changed),/changed/);assert.equal(e.invoke('inspect_producer',{producerId:'test:producer',kind:'cuisine'}).sequence,1);
});
test('post-write slot failures restore the original; failed rollback quarantines the producer',()=>{
 let writes=0;const e=engine({fault(kind){if(kind==='slot'&&++writes===1)throw Error('after write')}});e.register();const request=e.output();assert.throws(()=>e.invoke('decorate_output',request),/after write/);assert.equal(readPublicFood(e.items[0]).present,false);assert.equal(e.invoke('decorate_output',request).decorated,true);
 let count=0;const bad=engine({fault(kind){if(kind==='slot'&&++count<=2)throw Error('slot inaccessible')}});bad.register();assert.throws(()=>bad.invoke('decorate_output',bad.output()));assert.equal(bad.invoke('inspect_producer',{producerId:'test:producer',kind:'cuisine'}).phase,'quarantined');assert.throws(()=>bad.invoke('decorate_output',bad.output(2)),/unresolved/);
});
test('unreadable prepared journal prevents writes; acknowledged output remains credited if commit journal fails',()=>{
 let calls=0;const e=engine({fault(kind,k){if(kind==='property'&&k.includes('integration_operation:')&&++calls===2)throw Error('commit unavailable')}});e.register();const r=e.invoke('decorate_output',e.output());assert.equal(r.decorated,true);assert.equal(r.recoveryPending,true);assert.equal(readPublicFood(e.items[0]).state.hotUntil,1600);
 const restart=engine({saved:e.props});assert.equal(restart.invoke('inspect_producer',{producerId:'test:producer',kind:'cuisine'}).phase,'committed');
 let reads=0;const blocked=engine({fault(kind,k){if(kind==='get'&&k.includes('integration_operation:')&&++reads===2)throw Error('readback')}});blocked.register();assert.throws(()=>blocked.invoke('decorate_output',blocked.output()),/readback/);assert.equal(readPublicFood(blocked.items[0]).present,false);
});
test('a commit rejected before persistence retains the prepared guard after actual credit and blocks subsequent operations',()=>{
 let calls=0;const e=engine({fault(kind,k){if(kind==='before_property'&&k.includes('integration_operation:')&&++calls===2)throw Error('commit unavailable')}});e.register();const r=e.invoke('decorate_output',e.output());assert.equal(r.recoveryPending,true);assert.equal(readPublicFood(e.items[0]).state.hotUntil,1600);
 const restarted=engine({saved:e.props});assert.equal(restarted.invoke('inspect_producer',{producerId:'test:producer',kind:'cuisine'}).phase,'prepared');assert.throws(()=>restarted.invoke('decorate_output',restarted.output(2)),/unresolved/);assert.equal(readPublicFood(restarted.items[0]).present,false);
});
test('registration post-write faults restore both stores and unresolved rollback fails closed',()=>{
 let writes=0;const e=engine({fault(kind,k){if(kind==='property'&&k.includes('integration_registry')&&++writes===1)throw Error('after registry write')}});assert.throws(()=>e.register(),/after registry write/);assert.deepEqual(registry.integrationRegistrySnapshot().producers,[]);assert.deepEqual(JSON.parse(e.props.get('kaleidoscope_grilling:integration_registry_v1')).producers,[]);assert.equal(e.register().replayed,false);
 const bad=engine({fault(kind,k){if(kind==='before_property'&&k.includes('integration_registry'))throw Error('storage unavailable')}});assert.throws(()=>bad.register());assert.throws(()=>bad.invoke('discover'),/unresolved/);
});
test('fresh host batch follows Java signed-long hash/age and rejects player farms, stale or out-of-bounds evidence',()=>{
 const e=engine();e.register();const positions=Array.from({length:16},(_,x)=>({x,y:64,z:0})),blocks=positions.map((p,i)=>e.wart(p,i%4));
 const generation={dimensionId:'minecraft:nether',structureId:'minecraft:fortress',isNewChunk:true,generatedAt:1000,chunk:{x:0,z:0},bounds:{min:{x:0,y:64,z:0},max:{x:15,y:64,z:0}},positions};
 const request={producerId:'test:producer',sequence:1,generation};const result=e.invoke('fresh_fortress',request);assert.equal(result.replaced,positions.filter(fortress.fortressReplacementAt).length);assert(result.replaced>0&&result.replaced<16);
 blocks.forEach((b,i)=>{if(fortress.fortressReplacementAt(positions[i])){assert.equal(b.typeId,'kaleidoscope_grilling:houttuynia_crop');assert.equal(b.permutation.getState('kaleidoscope_grilling:age'),i%4===0?0:i%4===1?3:7);assert.equal(b.permutation.getState('kaleidoscope_grilling:red_variant'),true);}});
 e.setNow(1100);assert.equal(e.invoke('fresh_fortress',request).replayed,true);assert.throws(()=>e.invoke('fresh_fortress',{...request,sequence:2}),/fresh/);
 const farm=engine();farm.register();farm.wart(positions[0]);farm.events.place[0]({block:{dimension:{id:'minecraft:nether'},x:0,z:0}});assert.throws(()=>farm.invoke('fresh_fortress',{...request,generation:{...generation,positions:[positions[0]]}}),/touched/);
 assert.throws(()=>fortress.normalizeFreshFortress({...generation,positions:[{x:16,y:64,z:0}]},1000),/outside/);assert.throws(()=>fortress.normalizeFreshFortress({...generation,isNewChunk:false},1000),/fresh/);
});
test('64-bit hash matches independent fixed Java-long vectors including negative coordinates',()=>{
 // Values derived independently from the pinned Java formula, not the JS function.
 const vectors=[{x:0,y:0,z:0,selected:true},{x:1,y:64,z:0,selected:true},{x:-1,y:64,z:-1,selected:false},{x:2,y:64,z:0,selected:false},{x:15,y:64,z:0,selected:false},{x:30000000,y:127,z:-30000000,selected:false}];
 for(const {selected,...p} of vectors)assert.equal(fortress.fortressReplacementAt(p),selected,JSON.stringify(p));
});
test('portable hash matches all 277 Java-long modulo vectors including the native BDS failure coordinate',()=>{
 const vectors=JSON.parse(fs.readFileSync(new URL('./fixtures/fortress-java-vectors.json',import.meta.url),'utf8'));
 assert.equal(vectors.length,277);
 for(const {mod,...point} of vectors){assert.equal(fortress.fortressHashModulo(point),mod,JSON.stringify(point));assert.equal(fortress.fortressReplacementAt(point),mod<25,JSON.stringify(point));}
});
test('partial native block writes roll back their original ages and leave a retryable receipt',()=>{
 let writes=0;const e=engine({fault(kind){if(kind==='block'&&++writes===1)throw Error('after block write')}});e.register();const position={x:1,y:64,z:0},block=e.wart(position,1),request={producerId:'test:producer',sequence:1,generation:{dimensionId:'minecraft:nether',structureId:'minecraft:fortress',isNewChunk:true,generatedAt:1000,chunk:{x:0,z:0},bounds:{min:position,max:position},positions:[position]}};
 assert.throws(()=>e.invoke('fresh_fortress',request),/after block write/);assert.equal(block.typeId,'minecraft:nether_wart');assert.equal(block.permutation.getState('age'),1);assert.equal(e.invoke('fresh_fortress',request).replaced,1);
});
test('cross-pack event accepts Server only and gives correlated explicit rejection; capabilities keep vanilla callback false',()=>{
 const e=engine();const listener=e.events.script[0],event={id:'kaleidoscope_grilling:integration_request',message:JSON.stringify({api:1,requestId:'foreign/1',op:'discover'})};
 listener({...event,sourceType:'Entity'});assert.equal(e.responses.length,0);listener({...event,sourceType:'Server'});assert.equal(e.responses[0].requestId,'foreign/1');assert.equal(e.responses[0].result.vanillaFortressCallbackInstalled,false);
 listener({...event,sourceType:'Server',message:JSON.stringify({api:1,requestId:'foreign/2',op:'unknown'})});assert.equal(e.responses[1].ok,false);
});
test('client correlates server responses, separates instances, times out and closes pending requests',async()=>{
 const sends=[],timers=new Map(),listeners=new Set();let next=0;
 const system={currentTick:20,sendScriptEvent:(_id,raw)=>sends.push(JSON.parse(raw)),runTimeout:fn=>{timers.set(++next,fn);return next;},clearRun:id=>timers.delete(id),afterEvents:{scriptEventReceive:{subscribe:f=>listeners.add(f),unsubscribe:f=>listeners.delete(f)}}};
 const context={system,utf8Bytes:stackAPI.utf8Bytes,console};vm.runInNewContext(fs.readFileSync('projects/grilling/gameplay_core/behavior_pack/scripts/integration_client.js','utf8').replace(/^import .*;\n/gm,'').replace(/\bexport /g,'')+'\nthis.create=createIntegrationClient;',context);
 const a=context.create('test:client'),b=context.create('test:client'),p=a.request('discover'),q=b.request('discover');assert.notEqual(sends[0].requestId,sends[1].requestId);
 assert.equal(stackAPI.utf8Bytes('煙火🔥'),10);await assert.rejects(a.request('discover',{text:'煙'.repeat(3000)}),/too large/);
 const response=(requestId,sourceType='Server')=>{for(const f of listeners)f({id:'kaleidoscope_grilling:integration_response',sourceType,message:JSON.stringify({api:1,requestId,ok:true,result:{passed:true}})})};
 response(sends[0].requestId,'Entity');assert.equal(timers.size,2);response(sends[1].requestId);assert.equal((await q).passed,true);response(sends[0].requestId);assert.equal((await p).passed,true);
 const timeout=a.request('discover'),rejected=assert.rejects(timeout,/timeout/);const [timer,callback]=[...timers][0];timers.delete(timer);callback();await rejected;
 const waiting=b.request('discover'),closed=assert.rejects(waiting,/closed/);b.close();await closed;a.close();assert.equal(listeners.size,0);assert.equal(timers.size,0);
});
