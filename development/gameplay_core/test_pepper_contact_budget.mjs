import assert from 'node:assert/strict';
import test from 'node:test';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {PepperContactWork,contactBlockBounds,contactContains} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/pepper_contact_work.js';
import {overlappedBlockPositions} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a285_contact_core.js';
import * as pepper from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2748_pepper_tree_core.js';
const bp=new URL('../../projects/grilling/gameplay_core/behavior_pack/',import.meta.url);
const runtime=readFileSync(new URL('scripts/a2748_pepper_tree_runtime.js',bp),'utf8');
const box=(x=.5,y=1,z=.5,s=.3)=>({center:{x,y,z},extent:{x:s,y:.9,z:s}});
const entity=(id,bounds=box())=>({id,dimensionId:'minecraft:overworld',bounds,valid:true,typeId:'minecraft:pig'});
function fixture(options){
 const work=new PepperContactWork(options),hits=[],reads=[];
 const adapter={valid:e=>e.valid,dimension:e=>e.dimensionId,eligible:e=>e.typeId!=='minecraft:fox'&&e.typeId!=='minecraft:bee',bounds:e=>e.bounds,
  leaf:(d,p)=>{reads.push({d,...p});return 'leaf';},sting:e=>hits.push(e.id)};
 return {work,hits,reads,adapter,tick(t){const result=work.tick(t,adapter);assert(result.entities<=work.entityBudget);assert(result.recovered<=work.entityBudget);assert(result.probes<=work.probeBudget);assert(result.blockReads<=result.probes);return result;}};
}
test('Indexed overlap exactly matches original voxel rule at negative/bucket boundaries',()=>{
 for(const b of [box(.9),box(-8.1),box(8),{center:{x:.5,y:.5,z:.5},extent:{x:.5,y:.5,z:.5}},{center:{x:.25,y:.25,z:.25},extent:{x:0,y:0,z:0}}]){
  const old=new Set(overlappedBlockPositions(b).map(p=>JSON.stringify(p))),bounds=contactBlockBounds(b);
  for(let x=-10;x<=10;x++)for(let y=-2;y<=2;y++)for(let z=-2;z<=2;z++)assert.equal(contactContains(bounds,{x,y,z}),old.has(JSON.stringify({x,y,z})));
 }
});
test('Far/empty dimensions and thousands of cosmetic helpers make zero block probes',()=>{
 const f=fixture();f.work.rememberLeaf('minecraft:overworld',{x:100,y:0,z:100},0);
 for(let i=0;i<2048;i++){const e=entity(String(i),box(.25,.25,.25,0));if(i%2)e.dimensionId='minecraft:the_end';f.work.track(e);}
 for(let t=0;t<150;t++){f.work.rememberLeaf('minecraft:overworld',{x:100,y:0,z:100},t);f.tick(t);}
 assert.equal(f.reads.length,0);assert.equal(f.hits.length,0);
});
test('More than16 entities remain fair when64 probes exhaust before16 slices',()=>{
 const f=fixture({sliceBudget:8});const leaf={x:0,y:0,z:0};
 for(let i=0;i<65;i++)f.work.track(entity(String(i),{center:{x:0,y:0,z:0},extent:{x:16,y:16,z:16}}));
 for(let t=0;t<250&&new Set(f.hits).size<65;t++){f.work.rememberLeaf('minecraft:overworld',leaf,t);f.tick(t);}
 assert.equal(new Set(f.hits).size,65);assert(f.hits.includes('64'));
});
test('A body overlapping from side/below contacts a source far from its center',()=>{
 const f=fixture(),b={center:{x:0,y:0,z:0},extent:{x:16,y:8,z:16}};
 f.work.track(entity('large',b));
 for(let t=0;t<100&&!f.hits.length;t++){f.work.rememberLeaf('minecraft:overworld',{x:15,y:7,z:15},t);f.tick(t);}
 assert.deepEqual(f.hits,['large']);assert.equal(f.reads.length,1);
});
test('Moving entity/removed leaf cannot be stung by a stale continuation',()=>{
 const f=fixture({probeBudget:1,sliceBudget:1}),e=entity('moving',box(.9));f.work.track(e);
 f.work.rememberLeaf(e.dimensionId,{x:1,y:0,z:0},0);f.tick(0);
 e.bounds=box(50);f.tick(1);assert.equal(f.hits.length,0);
 e.bounds=box(.9);f.work.forgetLeaf(f.work.leafKey(e.dimensionId,{x:1,y:0,z:0}));f.tick(2);assert.equal(f.hits.length,0);
});
test('Native missing-leaf validation, unload expiry/reload and dimension changes',()=>{
 const f=fixture(),e=entity('x');f.work.track(e);const p={x:0,y:0,z:0};f.work.rememberLeaf(e.dimensionId,p,0);
 f.adapter.leaf=()=> 'missing';f.tick(0);assert.equal(f.hits.length,0);assert.equal(f.work.leaves.size,0);
 f.work.rememberLeaf(e.dimensionId,p,1);f.adapter.leaf=()=> 'unloaded';f.tick(1);f.tick(25);assert.equal(f.work.leaves.size,0);
 e.dimensionId='minecraft:nether';f.work.rememberLeaf(e.dimensionId,p,26);f.adapter.leaf=()=> 'leaf';
 for(let t=26;t<32&&!f.hits.length;t++)f.tick(t);assert.deepEqual(f.hits,['x']);
 e.valid=false;f.tick(32);assert.equal(f.work.entities.size,0);
});
test('Recovery handle insertion is bounded and fair across source dimensions',()=>{
 const f=fixture({entityBudget:4});f.work.queueRecovery('a',Array.from({length:100},(_,i)=>entity('a'+i)));f.work.queueRecovery('b',[entity('b')]);
 const stats=f.tick(0);assert.equal(stats.recovered,4);assert(f.work.entities.has('b'));assert.equal(f.work.entities.size,4);
});
test('Expired census handles and later health component activation remain safe',()=>{
 const f=fixture(),gone={get id(){throw Error('removed handle');}},e=entity('later');
 f.work.queueRecovery('a',[gone,e]);f.work.rememberLeaf(e.dimensionId,{x:0,y:0,z:0},0);
 let health=false;f.adapter.eligible=()=>health;assert.doesNotThrow(()=>f.tick(0));
 assert.equal(f.work.entities.size,1);assert.equal(f.hits.length,0);health=true;
 for(let t=1;t<=8&&!f.hits.length;t++)f.tick(t);assert.deepEqual(f.hits,['later']);
 e.valid=false;Object.defineProperty(e,'id',{get(){throw Error('invalid id');}});assert.doesNotThrow(()=>f.tick(10));assert.equal(f.work.entities.size,0);
});
test('An entityLoad replacement refreshes a formerly invalid handle with the same ID',()=>{
 const f=fixture(),old=entity('reload');old.valid=false;f.work.track(old);
 const loaded=entity('reload');f.work.track(loaded);f.work.rememberLeaf(loaded.dimensionId,{x:0,y:0,z:0},0);
 f.tick(0);assert.deepEqual(f.hits,['reload']);assert.equal(f.work.entities.get('reload').entity,loaded);
});
test('Actual runtime recovers old saved leaves without recurring all-dimension scan; exemptions/cooldown survive',()=>{
 const listeners={},components={},intervals=[],queries=[],damage=[],effects=[];let now=0;
 const leaves=new Map([['0|0|0',{typeId:pepper.PEPPER_LEAVES_ID}]]),d={id:'minecraft:overworld',getBlock:p=>leaves.get(p.x+'|'+p.y+'|'+p.z),getEntities:()=>{queries.push(d.id);return oldEntities;}};
 const oldEntities=['minecraft:pig','minecraft:fox','minecraft:bee'].map((typeId,i)=>{
  const props=new Map();return {id:String(i),typeId,isValid:true,dimension:d,getComponent:()=>({}),getAABB:()=>box(),getDynamicProperty:k=>props.get(k),setDynamicProperty:(k,v)=>props.set(k,v),addEffect:(...args)=>effects.push({id:String(i),args}),applyDamage:n=>{damage.push({id:String(i),n});return true;}};
 });
 const events=new Proxy({}, {get:(obj,name)=>obj[name]??=( {subscribe(fn){(listeners[name]??=[]).push(fn);}} )});
 const system={get currentTick(){return now;},beforeEvents:{startup:{subscribe(fn){fn({blockComponentRegistry:{registerCustomComponent:(id,value)=>components[id]=value}});}}},runInterval:(fn,n)=>intervals.push({fn,n})};
 const world={afterEvents:events,beforeEvents:events,getAbsoluteTime:()=>now,getAllPlayers:()=>[],getDimension:id=>{assert.equal(id,d.id);return d;}};
 // Execute the real runtime with its imported dependencies supplied as API doubles.
 const body=runtime.replace(/^import[\s\S]*?;\s*/gm,'').replaceAll('export ','');
 const context=vm.createContext({...pepper,PepperContactWork,world,system,console});vm.runInContext(body,context);
 const leaf={typeId:pepper.PEPPER_LEAVES_ID,dimension:d,location:{x:0,y:0,z:0}};
 assert.equal(queries.length,0);assert.equal(intervals.length,1);assert.equal(intervals[0].n,1);
 for(now=0;now<=30;now++){if(now%5===0)components[pepper.LEAVES_COMPONENT_ID].onTick({block:leaf});intervals[0].fn();}
 assert.deepEqual(queries,[d.id]);assert.deepEqual(damage,[{id:'0',n:1},{id:'0',n:1}]);
 assert(effects.every(x=>x.id==='0'));assert.equal(effects[0].args[0],'slowness');assert.equal(effects[0].args[1],10);
 const block=JSON.parse(readFileSync(new URL('blocks/pepper_leaves.json',bp),'utf8'))['minecraft:block'];assert.deepEqual(block.components['minecraft:tick'],{interval_range:[5,5],looping:true});
 assert.equal(typeof components[pepper.LEAVES_COMPONENT_ID].onStepOn,'function');
});
