import test from 'node:test';import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
import {finishedFoodMeta} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/food_finish_core.js';
import {eatingProfile} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/player_presentation_core.js';
test('hot dishes crossing the completion boundary lose hot seasoning/saturation eligibility',()=>{
 const started={hot:true,hotUntil:100,seasonings:['salt'],origin:'wok'};
 assert.equal(finishedFoodMeta(started,99).hot,true);
 for(const finish of [100,101,190])assert.equal(finishedFoodMeta(started,finish).hot,false);
 assert.deepEqual(started,{hot:true,hotUntil:100,seasonings:['salt'],origin:'wok'});
 assert.deepEqual(finishedFoodMeta(started,101).seasonings,['salt']);
});
test('cold food never reacquires heat from a stale stored timestamp',()=>assert.equal(finishedFoodMeta({hot:false,hotUntil:300},50).hot,false));
test('both random branches select one shared curve, checkpoint duration and code',()=>{
 assert.deepEqual(eatingProfile('THREE_RANDOM',0),{profile:'THREE',code:3,duration:100});
 assert.deepEqual(eatingProfile('THREE_RANDOM',.4999),{profile:'THREE',code:3,duration:100});
 assert.deepEqual(eatingProfile('THREE_RANDOM',.5),{profile:'THREE_ALT',code:4,duration:90});
 assert.deepEqual(eatingProfile('THREE_RANDOM',.999),{profile:'THREE_ALT',code:4,duration:90});
 assert.throws(()=>eatingProfile('BAD'));
});

// Execute the production snapshot/finish routines. The time adapter models
// elapsed duration only; this is not a Minecraft effect-persistence recording.
const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/main.js',import.meta.url),'utf8');
const effectSource=source.slice(source.indexOf('function fxSnapshot('),source.indexOf('function applyFixedEffect('));
function hotEffects(){
 let tick=1000;const custom={},native=new Map();
 const player={getEffects:()=>[...native.values()],removeEffect:id=>native.delete(id),addEffect:(typeId,duration,{amplifier})=>native.set(typeId,{typeId,duration,amplifier})};
 const ctx=vm.createContext({now:()=>tick,readFx:()=>custom,writeFx(){}});
 vm.runInContext(effectSource,ctx);
 return {ctx,custom,native,player,at(value){tick=value}};
}
test('existing custom hot effect uses the same start duration as the native hot-effect path',()=>{
 const f=hotEffects();
 Object.assign(f.custom,{warmth:{until:1800,amp:2},unchanged:{until:2000,amp:0},invincible:{until:1200,amp:1}});
 f.native.set('strength',{typeId:'strength',duration:800,amplifier:2});
 const before=f.ctx.fxSnapshot(f.player),nativeBefore=f.ctx.nativeSnapshot(f.player);
 f.at(1090);f.custom.warmth.until=1990;f.custom.invincible.until=1290;f.custom.vigor={until:1690,amp:0};
 f.native.get('strength').duration=900;
 f.ctx.doubleNewNative(f.player,nativeBefore);f.ctx.doubleNewFx(f.player,before);
 assert.equal(f.native.get('strength').duration,1000);
 assert.equal(f.custom.warmth.until-1090,1000);assert.equal(f.custom.warmth.amp,2);
 assert.equal(f.custom.unchanged.until,2000);assert.equal(f.custom.invincible.until,1290);
 assert.equal(f.custom.vigor.until-1090,1200);
});
test('a custom effect that expires during eating still retains its start-duration comparison',()=>{
 const f=hotEffects();f.custom.warmth={until:1040,amp:0};
 const before=f.ctx.fxSnapshot(f.player);f.at(1090);f.custom.warmth={until:1990,amp:0};
 f.ctx.doubleNewFx(f.player,before);
 assert.equal(f.custom.warmth.until-1090,1760);
});
