/** Production visual functions/adapters with API doubles; not native client evidence. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as visuals from '../../projects/grilling/gameplay_core/behavior_pack/scripts/bottle_held_visual_core.js';
import * as seasoning from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2743_seasoning_contract_core.js';

const N='kaleidoscope_grilling:',EMPTY=N+'empty_seasoning_bottle',PENDING=N+'pending_seasoning';
const ids=[N+'dragon_egg_powder',N+'green_chili_powder',N+'houttuynia_powder',N+'onion_powder',N+'sichuan_pepper',N+'totem_powder','minecraft:gunpowder','minecraft:redstone'];
const zeros=()=>Array(8).fill(0);
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const read=name=>fs.readFileSync(new URL(name,root),'utf8');
const strip=source=>source.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport (?=(class|const|function|async))/g,'');
const plain=value=>JSON.parse(JSON.stringify(value));

test('palette indices have one stable sorted contract shared with assets',()=>{
 assert.deepEqual(visuals.BOTTLE_HELD_INGREDIENT_IDS,ids);
 assert.deepEqual(ids.map(id=>visuals.BOTTLE_HELD_INGREDIENT_INDEX[id]),[1,2,3,4,5,6,7,8]);
 assert.equal(visuals.BOTTLE_HELD_FALLBACK_INDEX,9);
 assert.ok(Object.isFrozen(visuals.BOTTLE_HELD_INGREDIENT_IDS));
 assert.ok(Object.isFrozen(visuals.BOTTLE_HELD_INGREDIENT_INDEX));
});
test('empty and non-bottle items clear every layer, including finished bottles',()=>{
 for(const id of [undefined,EMPTY,PENDING,'minecraft:stone',N+'special_seasoning_r8_v0']){
  assert.deepEqual(visuals.bottleHeldVisualPlan(id),zeros());
 }
 assert.deepEqual(visuals.bottleHeldVisualPlan('minecraft:stone',ids),zeros());
 assert.deepEqual(visuals.bottleHeldVisualPlan(N+'special_seasoning_r8_v0',ids),zeros());
});
test('partial EMPTY and PENDING retain ingredient order, repeats and palette colors',()=>{
 for(const id of [EMPTY,PENDING]){
  assert.deepEqual(visuals.bottleHeldVisualPlan(id,[ids[7],ids[1],ids[7]]),[8,2,8,0,0,0,0,0]);
  assert.deepEqual(visuals.bottleHeldVisualPlan(id,ids),[1,2,3,4,5,6,7,8]);
 }
});
test('capacity and normalization match the seasoning mechanic contract',()=>{
 assert.deepEqual(visuals.bottleHeldVisualPlan(EMPTY,[null,ids[0],7,...ids]),[1,1,2,3,4,5,6,7]);
 assert.deepEqual(visuals.bottleHeldVisualPlan(PENDING,{ingredient:ids[0]}),zeros());
 assert.deepEqual(visuals.bottleHeldVisualPlan(PENDING,[...ids,'external:extra']),[1,2,3,4,5,6,7,8]);
});
test('preserved unknown ingredient IDs use fallback without mutating their array',()=>{
 const values=Object.freeze(['other_addon:seasoning','toString',ids[4]]);
 assert.deepEqual(visuals.bottleHeldVisualPlan(EMPTY,values),[9,9,5,0,0,0,0,0]);
 assert.deepEqual(values,['other_addon:seasoning','toString',ids[4]]);
});

function fixture(){
 const callbacks={},queue=[],intervals=[],writes=[],warnings=[],properties=new Map();
 let main,off,failure,readFailure;
 const component={size:9,getItem(slot){assert.equal(slot,player.selectedSlotIndex);return main},setItem(){throw Error('Visual runtime must not write inventory')}};
 const equipment={getEquipment(slot){assert.equal(slot,'offhand');return off},setEquipment(){throw Error('Visual runtime must not write equipment')}};
 const player={id:'holder',selectedSlotIndex:2,getComponent(id){return id==='minecraft:inventory'?{container:component}:id==='minecraft:equippable'?equipment:undefined},setProperty(key,value){writes.push([key,value]);properties.set(key,value);if(failure?.(key))throw Error('Injected property write failure')}};
 const world={afterEvents:Object.fromEntries(['playerInventoryItemChange','playerHotbarSelectedSlotChange','playerLeave'].map(name=>[name,{subscribe(callback){callbacks[name]=callback}}])),getAllPlayers:()=>[player],getDynamicProperty(){throw Error('Unstackable bottles must read native item properties')},setDynamicProperty(){throw Error('Visual runtime must not write world metadata')}};
 const system={run:callback=>queue.push(callback),runInterval(callback,ticks){intervals.push({callback,ticks})}};
 const context=vm.createContext({...visuals,...seasoning,world,system,EquipmentSlot:{Offhand:'offhand'},GameMode:{Creative:'creative'},console:{warn:value=>warnings.push(value)}});
 vm.runInContext(strip(read('a2735_player_io.js')),context);
 // itemDataCore has module-private world state. Keep it in its own scope,
 // as the real ESM import does, instead of shadowing the Minecraft world.
 vm.runInContext('Object.assign(globalThis,(function(){'+strip(read('itemDataCore.js'))+';return {configureItemDataWorld,getItemProperty};})())',context);
 vm.runInContext('configureItemDataWorld(world)',context);
 vm.runInContext(strip(read('bottle_held_visual_runtime.js')),context);
 const api=vm.runInContext('({syncBottleHeld,readBottleHeldSeasonings})',context);
 const stack=(typeId,ingredients,...explicitRaw)=>Object.freeze({typeId,amount:1,maxAmount:1,nameTag:'Preserve me',getDynamicProperty(key){assert.equal(key,seasoning.SEASONING_LIST_KEY);if(readFailure)throw Error('Injected item read failure');return explicitRaw.length?explicitRaw[0]:JSON.stringify(ingredients)},setDynamicProperty(){throw Error('Visual runtime must not write item metadata')},setLore(){throw Error('Visual runtime must not write lore')}});
 return {player,api,callbacks,writes,warnings,properties,intervals,stack,get main(){return main},set main(value){main=value},get off(){return off},set off(value){off=value},setFailure(value){failure=value},setReadFailure(value){readFailure=value},flush(){while(queue.length)queue.shift()()},layers(hand){return Array.from({length:8},(_,i)=>properties.get(N+'bottle_'+hand+'_'+i))}};
}

test('real reader and hand adapters publish independent hands without changing native stacks',()=>{
 const f=fixture();f.main=f.stack(EMPTY,[ids[1],ids[4]]);f.off=f.stack(PENDING,[ids[7],'external:spice']);
 const main=f.main,off=f.off;f.api.syncBottleHeld(f.player);
 assert.deepEqual(f.layers('main'),[2,5,0,0,0,0,0,0]);assert.deepEqual(f.layers('off'),[8,9,0,0,0,0,0,0]);
 assert.strictEqual(f.main,main);assert.strictEqual(f.off,off);assert.equal(f.main.nameTag,'Preserve me');assert.equal(f.writes.length,16);
 f.api.syncBottleHeld(f.player);assert.equal(f.writes.length,16);
});
test('malformed or missing data clears contents without trying to rewrite it',()=>{
 const f=fixture();for(const raw of [undefined,'broken','{}','null','[4,null]']){
  const stack=f.stack(PENDING,[],raw);assert.deepEqual(plain(f.api.readBottleHeldSeasonings(stack)),[]);
 }
 const nonBottle=f.stack('minecraft:stone',[],JSON.stringify(ids));assert.deepEqual(plain(f.api.readBottleHeldSeasonings(nonBottle)),[]);
});
test('inventory and hotbar callbacks defer reads and publish the latest actual slots',()=>{
 const f=fixture();f.main=f.stack(EMPTY,[ids[0]]);f.callbacks.playerInventoryItemChange({player:f.player});
 assert.equal(f.writes.length,0);f.main=f.stack(PENDING,[ids[5]]);f.flush();assert.deepEqual(f.layers('main'),[6,0,0,0,0,0,0,0]);
 f.main=undefined;f.callbacks.playerHotbarSelectedSlotChange({player:f.player});f.flush();assert.deepEqual(f.layers('main'),zeros());
});
test('five-tick interval picks up offhand-only changes and clears unequipped bottles',()=>{
 const f=fixture();assert.equal(f.intervals.length,1);assert.equal(f.intervals[0].ticks,5);
 f.off=f.stack(EMPTY,[ids[6]]);f.intervals[0].callback();assert.deepEqual(f.layers('off'),[7,0,0,0,0,0,0,0]);
 f.off=f.stack('minecraft:stone',ids);f.intervals[0].callback();assert.deepEqual(f.layers('off'),zeros());
});
test('failed property writes retry the complete projection and cache only successful state',()=>{
 const f=fixture();f.main=f.stack(EMPTY,[ids[0]]);let fail=true;f.setFailure(key=>key===N+'bottle_main_1'&&fail?(fail=false,true):false);
 f.intervals[0].callback();assert.equal(f.warnings.length,1);assert.equal(f.writes.length,2);
 f.intervals[0].callback();assert.equal(f.writes.length,18);assert.deepEqual(f.layers('main'),[1,0,0,0,0,0,0,0]);
 f.intervals[0].callback();assert.equal(f.writes.length,18);
});
test('reverting hands after a partial write failure restores the previous projection',()=>{
 const f=fixture();f.main=f.stack(EMPTY,[ids[0]]);f.api.syncBottleHeld(f.player);
 f.main=f.stack(EMPTY,[ids[7],ids[6]]);let fail=true;f.setFailure(key=>key===N+'bottle_main_1'&&fail?(fail=false,true):false);
 f.intervals[0].callback();assert.equal(f.properties.get(N+'bottle_main_0'),8);
 f.main=f.stack(EMPTY,[ids[0]]);f.intervals[0].callback();assert.deepEqual(f.layers('main'),[1,0,0,0,0,0,0,0]);
});
test('item property read errors retry when the native item becomes readable',()=>{
 const f=fixture();f.main=f.stack(EMPTY,[ids[2]]);f.setReadFailure(true);f.intervals[0].callback();assert.equal(f.writes.length,0);assert.equal(f.warnings.length,1);
 f.setReadFailure(false);f.intervals[0].callback();assert.deepEqual(f.layers('main'),[3,0,0,0,0,0,0,0]);
});
test('player leave clears successful cache for the same player ID',()=>{
 const f=fixture();f.main=f.stack(PENDING,[ids[3]]);f.api.syncBottleHeld(f.player);assert.equal(f.writes.length,16);
 f.callbacks.playerLeave({playerId:f.player.id});f.api.syncBottleHeld(f.player);assert.equal(f.writes.length,32);
});
