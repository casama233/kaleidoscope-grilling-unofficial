import test from 'node:test';
import assert from 'node:assert/strict';
import {createGrillAudioController,GRILL_LOOP_TICKS} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_audio_core.js';
// Native sound-operation doubles; no Minecraft or simulated player is constructed.
function fixture(){
 const starts=[],stops=[];
 const audio=createGrillAudioController({play:station=>{
  const id=starts.length;starts.push(station);return {stop(){stops.push(id)}};
 }});
 return {audio,starts,stops};
}
test('cold and lit empty grills remain quiet',()=>{
 const {audio,starts}=fixture();audio.update('a',{},false,0);audio.sweep(20);
 assert.equal(starts.length,0);assert.equal(audio.size,0);
});
test('a loaded occupied grill starts once, and renews without overlapping handles',()=>{
 const {audio,starts,stops}=fixture();
 for(let t=0;t<GRILL_LOOP_TICKS;t++)audio.update('a',{x:1},true,t);
 assert.equal(starts.length,1);assert.deepEqual(stops,[]);
 audio.update('a',{x:1},true,GRILL_LOOP_TICKS);
 assert.equal(starts.length,2);assert.deepEqual(stops,[0]);
});
test('taking the last skewer or extinguishing stops only that grill',()=>{
 const {audio,starts,stops}=fixture();audio.update('a',{},true,0);audio.update('b',{},true,0);
 audio.update('a',{},false,1);assert.deepEqual(stops,[0]);assert.equal(audio.size,1);
 audio.update('b',{},true,2);assert.equal(starts.length,2);
});
test('destruction is immediate and does not stop another grill',()=>{
 const {audio,stops}=fixture();audio.update('a',{},true,0);audio.update('b',{},true,0);
 audio.remove('a');audio.remove('a');assert.deepEqual(stops,[0]);assert.equal(audio.size,1);
});
test('chunk unload expires the stale handle; reload starts a fresh instance',()=>{
 const {audio,starts,stops}=fixture();audio.update('a',{},true,0);audio.sweep(8);
 assert.equal(audio.size,1);audio.sweep(9);assert.deepEqual(stops,[0]);assert.equal(audio.size,0);
 audio.update('a',{},true,10);assert.equal(starts.length,2);
});
test('a failing sound start retries with bounded work and cannot alter station data',()=>{
 let attempts=0;const station=Object.freeze({lit:true,count:3});
 const audio=createGrillAudioController({play:()=>{attempts++;throw Error('sound unavailable')}});
 for(let tick=0;tick<40;tick++)audio.update('a',station,true,tick);
 assert.equal(attempts,2);assert.deepEqual(station,{lit:true,count:3});audio.update('a',station,false,40);
 assert.equal(audio.size,0);
});
