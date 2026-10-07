/** Actual owned audio helper, with API-operation adapters; no client certification. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {TELEPORT_ORIGIN_SOUND_ID,FLATULENCE_SOUND_ID,teleportDestinationAudio} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/projectile_dodge_audio_core.js';
const root=new URL('../../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root),'utf8');
const fixture=JSON.parse(read('development/gameplay_core/fixtures/java-projectile-dodge-audio-160.json'));
const definitions=JSON.parse(read('projects/grilling/gameplay_core/resource_pack/sounds/sound_definitions.json')).sound_definitions;
function harness(typeId,{failAt=[],invalidLocation=false}={}){
 const calls=[],delivery=[],origin={x:1,y:80,z:2},destination={x:3,y:81,z:4};
 const entity={typeId,dimension:{playSound:(...args)=>{calls.push(args);if(failAt.includes(calls.length))throw Error('Unavailable sound instance')}},
  get location(){if(invalidLocation)throw Error('Removed destination');return destination},
  get isSilent(){throw Error('Invented silence property must not be queried')},
  getSoundSource(){throw Error('Java-only method must not be invoked')},
  setDynamicProperty(){throw Error('Audio cannot mutate effects')},tryTeleport(){throw Error('Audio cannot retry teleport')}};
 const code=read('projects/grilling/gameplay_core/behavior_pack/scripts/projectile_dodge_audio_runtime.js')
  .replace(/^import .*;$/gm,'').replace(/export function/g,'function').replace(/^export \{.*\};$/gm,'');
 const context=vm.createContext({TELEPORT_ORIGIN_SOUND_ID,FLATULENCE_SOUND_ID,teleportDestinationAudio,recordSoundDelivery:error=>delivery.push(error)});vm.runInContext(code,context);
 return {entity,origin,destination,calls,delivery,run:()=>context.projectileDodgeTeleportFeedback(entity,origin)};
}
test('both independently reviewed loader indices identify the original two selected teleport samples',()=>{
 const forge=fixture.loader_sources['forge1.20.1'],neo=fixture.loader_sources['neoforge1.21.1'];
 assert.equal(forge.minecraft,'1.20.1');assert.equal(neo.minecraft,'1.21.1');assert.notEqual(forge.asset_index.url,neo.asset_index.url);
 assert.deepEqual(forge.original_event,neo.original_event);assert.deepEqual(forge.samples,neo.samples);
 assert.deepEqual(forge.original_event.sounds,['mob/endermen/portal','mob/endermen/portal2']);
 assert.deepEqual(forge.samples.map(x=>[x.publisher_sha1,x.size]),[['7b4b5323ef066caa1ae43cbe66fffd9dfce4ed32',10010],['35461b6a4253db40973549e82d91f267c686be85',7442]]);
});
test('selected category aliases retain original event weights/gain and point at the same two owned samples',()=>{
 for(const [category,id] of Object.entries(fixture.destination_sound_ids)){
  const definition=definitions[id];assert.equal(definition.category,category);assert.equal(definition.max_distance,16);
  assert.deepEqual(definition.sounds.map(x=>[x.name,x.volume??1,x.pitch??1,x.weight??1]),[
   ['sounds/kg_java21/mob/endermen/portal',1,1,1],['sounds/kg_java21/mob/endermen/portal2',1,1,1]]);
 }
});
test('actual helper uses immutable origin PLAYERS and the reviewed actor category at the successful destination',()=>{
 for(const [typeId,expectedCategory] of [['minecraft:player','player'],['minecraft:cow','neutral'],['minecraft:zombie','hostile'],['minecraft:bat','neutral']]){
  const h=harness(typeId),result=h.run();assert.equal(result.attempted,2);assert.equal(result.accepted,2);assert.equal(result.failed,0);assert.equal(result.destinationCategoryReviewed,true);
  assert.deepEqual(h.calls.map(x=>x[0]),[TELEPORT_ORIGIN_SOUND_ID,fixture.destination_sound_ids[expectedCategory]]);
  assert.equal(h.calls[0][1].x,h.origin.x);assert.equal(h.calls[0][1].y,h.origin.y);assert.equal(h.calls[0][1].z,h.origin.z);assert.notEqual(h.calls[0][1],h.origin);
  assert.equal(h.calls[1][1],h.destination);for(const call of h.calls){assert.equal(call[2].volume,1);assert.equal(call[2].pitch,1)}
 }
});
test('a failed origin sound still attempts destination and never changes gameplay',()=>{
 const h=harness('minecraft:cow',{failAt:[1]}),result=h.run();assert.equal(h.calls.length,2);assert.equal(result.accepted,1);assert.equal(result.failed,1);assert.ok(h.delivery[0] instanceof Error);assert.equal(h.delivery[1],undefined);
});
test('a failed destination sound retains origin and both failures remain bounded',()=>{
 for(const failAt of [[2],[1,2]]){const h=harness('minecraft:zombie',{failAt}),result=h.run();assert.equal(result.attempted,2);assert.equal(result.failed,failAt.length);assert.equal(result.accepted,2-failAt.length);assert.equal(h.calls.length,2)}
 const h=harness('minecraft:cow',{invalidLocation:true}),result=h.run();assert.equal(result.accepted,1);assert.equal(result.failed,1);assert.equal(h.calls[0][0],TELEPORT_ORIGIN_SOUND_ID);
});
test('unknown actor category is an explicit neutral adaptation with no invented silence query',()=>{
 const h=harness('some_addon:custom_actor'),result=h.run();assert.equal(result.accepted,2);assert.equal(result.destinationCategoryReviewed,false);assert.equal(h.calls[1][0],fixture.destination_sound_ids.neutral);
 assert.equal(fixture.client,false);assert.ok(fixture.boundaries.some(x=>x.includes('isSilent')));
});
test('flatulence category correction references current original host samples without duplicating them',()=>{
 assert.equal(FLATULENCE_SOUND_ID,'kg_cookery.flatulence');assert.equal(fixture.flatulence.original_java_category,'PLAYERS');assert.equal(fixture.flatulence.host_definition.category,'neutral');
 assert.equal(definitions[FLATULENCE_SOUND_ID].category,'player');assert.equal(fixture.flatulence.original_java_fixed_range,16);assert.equal(definitions[FLATULENCE_SOUND_ID].max_distance,16);assert.deepEqual(definitions[FLATULENCE_SOUND_ID].sounds,fixture.flatulence.host_definition.sounds);
 assert.deepEqual(definitions[FLATULENCE_SOUND_ID].sounds.map(x=>x.name),['sounds/kc_entity_fart_fart_0','sounds/kc_entity_fart_fart_1','sounds/kc_entity_fart_fart_2']);
 for(const sample of definitions[FLATULENCE_SOUND_ID].sounds)assert.equal(fs.existsSync(new URL('projects/grilling/gameplay_core/resource_pack/'+sample.name+'.ogg',root)),false);
});
