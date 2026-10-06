import {isPendingSeasoningId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2743_seasoning_contract_core.js';
/** Real motion-only runtime with API doubles; no native client claim. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {isSpecialSeasoningId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2766_special_seasoning_visual_core.js';
const N='kaleidoscope_grilling:',PENDING=N+'pending_seasoning';
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const source=fs.readFileSync(new URL('seasoning_motion_runtime.js',root),'utf8').replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=function)/g,'');
function fixture(){
 const properties=new Map(),events={},animations=[],system={currentTick:100};let main,off,reject;
 const identity=stack=>stack?JSON.stringify(stack):null;
 const world={afterEvents:Object.fromEntries(['playerLeave','playerSpawn'].map(k=>[k,{subscribe(cb){events[k]=cb}}]))};
 const player={id:'holder',selectedSlotIndex:2,playAnimation(name,options){animations.push({name,options})},setProperty(k,v){if(reject?.(k))throw Error('Injected property failure');properties.set(k,v)}};
 const context=vm.createContext({world,system,isSpecialSeasoningId,isPendingSeasoningId,getMainHand:()=>main,getOffHand:()=>off,eatingIdentity:identity});
 vm.runInContext(source,context);const api=vm.runInContext('({beginSeasoningMotion,syncSeasoningMotion})',context);
 return {api,player,system,events,animations,properties,identity,get main(){return main},set main(x){main=x},get off(){return off},set off(x){off=x},setFailure(cb){reject=cb},read:k=>properties.get(N+k),pending(hand){return {hand,use:{identity:identity(hand==='off'?off:main),slot:player.selectedSlotIndex}}}};
}
test('native session chooses one hand with two pending bottles',()=>{
 const f=fixture();f.main={typeId:PENDING,amount:1,ingredients:['redstone']};f.off={typeId:PENDING,amount:1,ingredients:['gunpowder']};
 f.api.syncSeasoningMotion(f.player,f.pending('main'));assert.equal(f.read('pending_hand'),1);
 f.api.syncSeasoningMotion(f.player,f.pending('off'));assert.equal(f.read('pending_hand'),2);
 f.api.syncSeasoningMotion(f.player,undefined);assert.equal(f.read('pending_hand'),0);
});
for(const hand of ['main','off'])test(`${hand} stale metadata or hand cancels pending`,()=>{
 const f=fixture();f[hand]={typeId:PENDING,amount:1,ingredients:['redstone']};const pending=f.pending(hand);
 f.api.syncSeasoningMotion(f.player,pending);assert.equal(f.read('pending_hand'),hand==='main'?1:2);
 f[hand]={...f[hand],ingredients:['gunpowder']};f.api.syncSeasoningMotion(f.player,pending);assert.equal(f.read('pending_hand'),0);
 f[hand]=undefined;f.api.syncSeasoningMotion(f.player,pending);assert.equal(f.read('pending_hand'),0);
});
test('main selected slot change cancels while offhand remains independent',()=>{
 const f=fixture();f.main={typeId:PENDING,amount:1};const pending=f.pending('main');f.player.selectedSlotIndex++;f.api.syncSeasoningMotion(f.player,pending);assert.equal(f.read('pending_hand'),0);
 f.off={typeId:PENDING,amount:1};const off=f.pending('off');f.player.selectedSlotIndex++;f.api.syncSeasoningMotion(f.player,off);assert.equal(f.read('pending_hand'),2);
});
for(const hand of ['main','off'])test(`${hand} sprinkle is ten ticks, current identity checked, no inventory mutation`,()=>{
 const f=fixture(),stack=Object.freeze({typeId:N+'special_seasoning_r8_v3',amount:1,uses:1});f[hand]=stack;
 f.api.beginSeasoningMotion(f.player,hand);assert.equal(f.read('season_hand'),hand==='main'?1:2);assert.equal(f.read('season_phase'),1);
 for(let i=0;i<10;i++){f.system.currentTick=100+i;f.api.syncSeasoningMotion(f.player);assert.equal(f.read('season_phase'),i+1);assert.strictEqual(f[hand],stack)}
 f.system.currentTick=110;f.api.syncSeasoningMotion(f.player);assert.equal(f.read('season_phase'),0);assert.equal(f.read('season_hand'),0);
});
test('switching item or slot cancels sprinkle, restarting extends only newest session',()=>{
 const f=fixture();f.main={typeId:N+'special_seasoning_r8_v0',amount:1};f.api.beginSeasoningMotion(f.player,'main');
 f.system.currentTick=105;f.api.beginSeasoningMotion(f.player,'main');f.system.currentTick=110;f.api.syncSeasoningMotion(f.player);assert.equal(f.read('season_phase'),6);
 f.player.selectedSlotIndex++;f.api.syncSeasoningMotion(f.player);assert.equal(f.read('season_phase'),0);
 f.api.beginSeasoningMotion(f.player,'main');f.main={typeId:N+'empty_seasoning_bottle',amount:1};f.api.syncSeasoningMotion(f.player);assert.equal(f.read('season_phase'),0);
});
test('property failure retries without caching a failed pending-hand update',()=>{
 const f=fixture();f.main={typeId:PENDING,amount:1};const pending=f.pending('main');let fail=true;
 f.setFailure(k=>k===N+'pending_hand'&&fail?(fail=false,true):false);assert.throws(()=>f.api.syncSeasoningMotion(f.player,pending));
 f.api.syncSeasoningMotion(f.player,pending);assert.equal(f.read('pending_hand'),1);
});
test('spawn and leave forget old sessions and clear client motion properties',()=>{
 const f=fixture();f.main={typeId:N+'special_seasoning_r8_v0',amount:1};f.api.beginSeasoningMotion(f.player,'main');
 f.events.playerLeave({playerId:f.player.id});f.events.playerSpawn({player:f.player});
 for(const k of ['season_hand','season_phase','pending_hand'])assert.equal(f.read(k),0);
 f.system.currentTick+=2;f.api.syncSeasoningMotion(f.player);assert.equal(f.read('season_phase'),0);
});

test('only main-hand completed seasoning starts the finite anchor and pins no other action',()=>{
 for(const hand of ['main','off'])for(const typeId of [PENDING,N+'empty_seasoning_bottle',N+'special_seasoning_r8_v3',N+'special_seasoning_fake']){
  const f=fixture();f[hand]={typeId,amount:1};f.api.beginSeasoningMotion(f.player,hand);
  assert.equal(f.animations.length,hand==='main'&&isSpecialSeasoningId(typeId)?1:0);
  if(f.animations.length){const a=f.animations[0];assert.equal(a.name,'animation.kg_seasoning.player.sprinkle_anchor.right');assert.equal(a.options.blendOutTime,0);assert.equal(a.options.controller,'kg_seasoning_sprinkle_anchor');assert.ok(a.options.stopExpression.includes(typeId));assert.ok(a.options.stopExpression.includes("q.property('kaleidoscope_grilling:season_hand') == 2"));assert.ok(!a.options.stopExpression.includes('season_phase'));}
 }
});

for(const fill of [1,8])test('pending fill '+fill+' participates in native motion',()=>{const f=fixture();f.off={typeId:PENDING+'_f'+fill,amount:1};f.api.syncSeasoningMotion(f.player,f.pending('off'));assert.equal(f.read('pending_hand'),2);});
