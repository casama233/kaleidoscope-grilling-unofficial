/** Actual deferred destruction functions with API doubles; not native BDS evidence. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {initialState} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/core_logic.js';
import {captureSkewerMetadata,metadataSignature} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/skewer_item_snapshot.js';

const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
const start=source.indexOf('function grillBreakSnapshot('),end=source.indexOf('function heatForOil(',start);
assert.ok(start>=0&&end>start,'Current destruction functions must remain exercised');
assert.ok(source.includes('world.beforeEvents.explosion.subscribe(scheduleGrillExplosion);'),'Production explosion entry must use the tested function');
assert.ok(source.includes('if(e.block.typeId===GRILL_ID){scheduleGrillPlayerBreak(e);return}'),'Production player break must use the tested function');

function fixture(){
 let restricted=true;
 const GRILL_ID='kaleidoscope_grilling:grill',queue=[],calls=[],logs=[],dp=new Map([['owner','first-owner']]);
 const state={...initialState(),lit:true,phase:1,phaseTicks:90,flipCooldown:8},states={'minecraft:cardinal_direction':'north','kaleidoscope_grilling:lit':true,'kaleidoscope_grilling:legged':true};
 const item={typeId:'kaleidoscope_grilling:raw_beef_skewer',amount:1,nameTag:'Original',props:{'test:owner':'kept'},clone(){return {...this,props:structuredClone(this.props)}},getDynamicPropertyIds(){return Object.keys(this.props)},getDynamicProperty(k){return this.props[k]},getRawLore(){return [{text:'Original lore'}]},getCanDestroy(){if(restricted)throw Error('getCanDestroy forbidden in before event');return []},getCanPlaceOn(){if(restricted)throw Error('getCanPlaceOn forbidden in before event');return []},getComponent(){}};
 const container={size:3,rows:[item],getItem(i){return this.rows[i]}};
 const dimension={id:'minecraft:overworld',getBlock(){return block}},block={isValid:true,typeId:GRILL_ID,dimension,location:{x:0,y:64,z:0},permutation:{getAllStates(){return {...states}}}};
 const context=vm.createContext({GRILL_ID,metadataSignature,captureSkewerMetadata,readState(){return {...state}},peekStationContainer(){return container},stationStorageKey(){return 'owner'},world:{getDynamicProperty:k=>dp.get(k)},system:{run:fn=>queue.push(fn)},console:{warn:v=>logs.push(v)},customBreak:(...args)=>calls.push(args)});
 const api=vm.runInContext('(()=>{'+source.slice(start,end)+';return {scheduleGrillExplosion,scheduleGrillPlayerBreak};})()',context);
 return {api,block,item,container,state,states,dp,calls,logs,queue,flush(){restricted=false;while(queue.length)queue.shift()()}};
}

test('explosion respects early, later and unreadable cancellation without touching items',()=>{
 for(const mode of ['allowed','early','late','unreadable_early','unreadable_late']){
  const f=fixture(),other={typeId:'minecraft:stone'};let deferred=false,kept,edits=0;
  const event={get cancel(){if(mode==='unreadable_early'||(mode==='unreadable_late'&&deferred))throw Error('unreadable event');return mode==='early'||(mode==='late'&&deferred)},getImpactedBlocks:()=>[f.block,other],setImpactedBlocks(rows){kept=[...rows];edits++}};
  f.api.scheduleGrillExplosion(event);deferred=true;f.flush();
  assert.equal(f.calls.length,mode==='allowed'?1:0,mode);
  assert.equal(edits,['early','unreadable_early'].includes(mode)?0:1,mode);
  if(edits)assert.deepEqual(kept,[other],'Unrelated blocks remain in the original explosion');
  assert.equal(f.item.amount,1);assert.equal(f.dp.get('owner'),'first-owner');
 }
});

test('explosion rejects a replaced target, changed owner, phase, facing or item payload',()=>{
 const mutations={
  block:f=>{f.block.typeId='minecraft:stone'},unloaded:f=>{f.block.isValid=false},
  owner:f=>f.dp.set('owner','replacement-owner'),phase:f=>{f.state.phase=2},
  facing:f=>{f.states['minecraft:cardinal_direction']='east'},
  metadata:f=>{f.item.props['test:owner']='replacement'},count:f=>{f.item.amount=2}
 };
 for(const [name,mutate] of Object.entries(mutations)){
  const f=fixture();f.api.scheduleGrillExplosion({cancel:false,getImpactedBlocks:()=>[f.block],setImpactedBlocks(){}});mutate(f);f.flush();
  assert.equal(f.calls.length,0,name);
 }
});

test('ordinary cooking clock advancement still permits the captured explosion',()=>{
 const f=fixture();f.api.scheduleGrillExplosion({cancel:false,getImpactedBlocks:()=>[f.block],setImpactedBlocks(){}});
 f.state.phaseTicks+=1;f.state.flipCooldown-=1;f.flush();
 assert.equal(f.calls.length,1);assert.equal(f.calls[0][0],f.block);assert.equal(f.calls[0][1],undefined);
});

test('unreadable captured storage stays protected from native explosion destruction',()=>{
 const f=fixture();let kept;f.container.getItem=()=>{throw Error('native inventory unavailable')};
 f.api.scheduleGrillExplosion({cancel:false,getImpactedBlocks:()=>[f.block],setImpactedBlocks(rows){kept=[...rows]}});f.flush();
 assert.deepEqual(kept,[]);assert.equal(f.calls.length,0);assert.equal(f.queue.length,0);
});

test('player break uses the same owner protection and ignores already cancelled gestures',()=>{
 for(const mode of ['valid','already_cancelled','replacement']){
  const f=fixture(),player={id:'player'},event={cancel:mode==='already_cancelled',block:f.block,player};
  f.api.scheduleGrillPlayerBreak(event);if(mode==='replacement')f.dp.set('owner','replacement-owner');f.flush();
  assert.equal(f.calls.length,mode==='valid'?1:0,mode);
  if(f.calls.length)assert.equal(f.calls[0][1],player);
 }
});
