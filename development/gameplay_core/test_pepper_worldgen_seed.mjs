/** Actual tree placement functions with block/API doubles; native BDS is separate. */
import assert from 'node:assert/strict';
import test from 'node:test';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import * as core from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2748_pepper_tree_core.js';

const bp=new URL('../../projects/grilling/gameplay_core/behavior_pack/',import.meta.url);
const source=readFileSync(new URL('scripts/a2748_pepper_tree_runtime.js',bp),'utf8');
const start=source.indexOf("const STING_UNTIL="),end=source.indexOf('function advanceSapling',start);
assert(start>=0&&end>start);
const functions=source.slice(start,end).replaceAll('export ','');
const key=p=>`${p.x}|${p.y}|${p.z}`;
function fixture({height=2,unloaded,failWrite=0,obstruction,soil='minecraft:dirt'}={}){
 const blocks=new Map(),events=[];let n=0,draw=0,unloadedKey=unloaded;
 const permutation=(id,states={})=>({type:{id},states,getState(k){return this.states[k];}});
 const dimension={heightRange:{min:-64,max:320},getBlock(p){
  if(key(p)===unloadedKey)return undefined;
  if(!blocks.has(key(p)))blocks.set(key(p),{
   location:{...p},dimension,x:p.x,y:p.y,z:p.z,permutation:permutation('minecraft:air'),
   get typeId(){return this.permutation.type.id;},hasTag(){return false;},
   setPermutation(value){events.push(key(p));if(++n===failWrite)throw Error('injected write');this.permutation=value;},
   setType(id){this.setPermutation(permutation(id));}
  });
  return blocks.get(key(p));
 }};
 const origin=dimension.getBlock({x:0,y:0,z:0});origin.permutation=permutation(core.PEPPER_WORLDGEN_SEED_ID);
 dimension.getBlock({x:0,y:-1,z:0}).permutation=permutation(soil);
 if(obstruction)dimension.getBlock(obstruction).permutation=permutation('minecraft:stone');
 const math=Object.create(Math);math.random=()=>draw++===0?(height===2?0:0.75):0.99;
 const context=vm.createContext({...core,Math:math,BlockPermutation:{resolve:permutation}});
 vm.runInContext(functions+';globalThis.api={placePepperTree,growPepperWorldgenSeed};',context);
 const count=id=>[...blocks.values()].filter(b=>b.typeId===id);
 return {api:context.api,origin,blocks,dimension,events,count,loadNeighbor(){unloadedKey=undefined;}};
}
for(const height of [2,3])test(`Worldgen height${height}: full Java ring and crown, no persistent seed`,()=>{
 const f=fixture({height});assert.equal(f.api.growPepperWorldgenSeed(f.origin),'grown');
 assert.equal(f.count(core.PEPPER_LOG_ID).length,height+1);
 assert.equal(f.count(core.PEPPER_LEAVES_ID).length,13);
 assert.equal(f.count(core.PEPPER_WORLDGEN_SEED_ID).length,0);
 for(let x=-1;x<=1;x++)for(let z=-1;z<=1;z++)if(x||z)
  assert.equal(f.dimension.getBlock({x,y:height,z}).typeId,core.PEPPER_LEAVES_ID);
 for(const [x,z] of [[0,0],[-1,0],[1,0],[0,-1],[0,1]])
  assert.equal(f.dimension.getBlock({x,y:height+1,z}).typeId,core.PEPPER_LEAVES_ID);
 for(const b of f.count(core.PEPPER_LEAVES_ID))assert.equal(b.permutation.getState(core.PERSISTENT_STATE),false);
 const writes=f.events.length;assert.equal(f.api.growPepperWorldgenSeed(f.origin),'not_seed');assert.equal(f.events.length,writes);
});
test('Unloaded canopy defers without writing logs; loaded retry completes',()=>{
 const f=fixture({unloaded:'1|2|0'});assert.equal(f.api.growPepperWorldgenSeed(f.origin),'deferred');
 assert.equal(f.events.length,0);assert.equal(f.origin.typeId,core.PEPPER_WORLDGEN_SEED_ID);
 f.loadNeighbor();assert.equal(f.api.growPepperWorldgenSeed(f.origin),'grown');
 assert.equal(f.count(core.PEPPER_LEAVES_ID).length,13);assert.equal(f.count(core.PEPPER_WORLDGEN_SEED_ID).length,0);
});
test('Invalid soil or blocked center clears only the still-matching worldgen seed',()=>{
 for(const options of [{soil:'minecraft:stone'},{obstruction:{x:0,y:1,z:0}}]){
  const f=fixture(options);assert.equal(f.api.growPepperWorldgenSeed(f.origin),'blocked');
  assert.equal(f.count(core.PEPPER_LOG_ID).length,0);assert.equal(f.count(core.PEPPER_LEAVES_ID).length,0);
  assert.equal(f.origin.typeId,'minecraft:air');assert.deepEqual(f.events,['0|0|0']);
  if(options.obstruction)assert.equal(f.dimension.getBlock(options.obstruction).typeId,'minecraft:stone');
 }
});
test('A partial native write failure rolls back every preceding trunk/canopy write',()=>{
 for(const failWrite of [1,2,4,9,16]){
  const f=fixture({failWrite});assert.equal(f.api.placePepperTree(f.origin),false);
  assert.equal(f.count(core.PEPPER_LOG_ID).length,0);assert.equal(f.count(core.PEPPER_LEAVES_ID).length,0);
  assert.equal(f.origin.typeId,core.PEPPER_WORLDGEN_SEED_ID);
 }
});
test('Java bottom cardinals share one probability decision per sign',()=>{
 let state=7;const random=()=>((state=(Math.imul(state,1664525)+1013904223)>>>0)/4294967296);
 for(let trial=0;trial<200;trial++){
  const plan=core.pepperTreePlan(3,Array.from({length:96},random));
  const bottom=new Set(plan.leaves.filter(p=>p.y===1).map(key));
  assert.equal(bottom.has('-1|1|0'),bottom.has('0|1|-1'));
  assert.equal(bottom.has('1|1|0'),bottom.has('0|1|1'));
  assert(plan.leaves.length>=13&&plan.leaves.length<=25);
 }
});
test('Feature and registered hidden seed use the shared source-derived routine',()=>{
 const f=JSON.parse(readFileSync(new URL('features/pepper_tree_worldgen.json',bp),'utf8'));
 assert.equal(f['minecraft:single_block_feature'].places_block,core.PEPPER_WORLDGEN_SEED_ID);
 assert(!('minecraft:tree_feature' in f));
 const block=JSON.parse(readFileSync(new URL('blocks/pepper_worldgen_seed.json',bp),'utf8'))['minecraft:block'];
 assert.equal(block.description.identifier,core.PEPPER_WORLDGEN_SEED_ID);assert(!block.description.menu_category);
 assert.equal(block.components['minecraft:tick'].looping,true);
 assert(core.WORLDGEN_SEED_COMPONENT_ID in block.components);
 const runtime=readFileSync(new URL('scripts/a2860_pepper_worldgen_seed_runtime.js',bp),'utf8');
 assert(runtime.includes('growPepperWorldgenSeed(event.block)'));
 assert(readFileSync(new URL('scripts/main.js',bp),'utf8').includes("import './a2860_pepper_worldgen_seed_runtime.js'"));
});

test('worldgen preserves its seed after transient write failure and retries',()=>{
 for(const failWrite of [1,2,4,9,16]){
  const f=fixture({failWrite});assert.equal(f.api.growPepperWorldgenSeed(f.origin),'deferred');
  assert.equal(f.origin.typeId,core.PEPPER_WORLDGEN_SEED_ID);assert.equal(f.count(core.PEPPER_LOG_ID).length,0);
  assert.equal(f.api.growPepperWorldgenSeed(f.origin),'grown');assert.ok(f.count(core.PEPPER_LEAVES_ID).length>=13);
 }
});
