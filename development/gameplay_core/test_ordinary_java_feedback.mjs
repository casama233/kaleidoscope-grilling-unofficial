/** Author CursedSkewerItem contract; API-operation adapters, no simulated players. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {interactionParticles} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_particles_core.js';
import {emitParticleCommands} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_particle_delivery.js';
import {createFeedbackCooldown,goldenSkewerParticles,invincibleAmbientParticle} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_particles_core.js';
import {ordinaryChallengeOutcome} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2758_advancement_challenge_core.js';
const root=new URL('../../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root),'utf8');
function fixture({challenged=false,draw=.75,brokenSound=false}={}){
 const sound=[],particles=[],awards=[],damage=[],queue=[];let shield=challenged;
 const actor={id:'ordinary-probe',location:{x:4,y:80,z:4},dimension:{playSound:(id,location,options)=>{sound.push({id,location,options});if(brokenSound)throw Error('unloaded sound')},spawnParticle:(id,pos)=>particles.push({id,pos})},applyDamage:(value,options)=>damage.push({value,options}),kill:()=>{throw Error('Generic kill must not bypass the damage pipeline')}};
 const source=read('projects/grilling/gameplay_core/behavior_pack/scripts/immersion_effect_feedback.js').replace(/^import .*;$/gm,'').replace(/export function/g,'function');
 const context=vm.createContext({console,Math:Object.assign(Object.create(Math),{random:()=>draw}),system:{currentTick:100,run:f=>queue.push(f),runInterval(){}},createFeedbackCooldown,goldenSkewerParticles,invincibleAmbientParticle,recordSoundDelivery(){},emitParticles:emitParticleCommands,interactionParticleBurst:(dim,origin,event)=>emitParticleCommands(dim,origin,interactionParticles(event,()=>.4)),fxGet:()=>shield,fxClear:()=>{shield=false},ordinaryChallengeOutcome,awardOrdinaryChallenge:(_a,result)=>awards.push(result)});
 vm.runInContext(source,context);
 const main=read('projects/grilling/gameplay_core/behavior_pack/scripts/main.js');vm.runInContext(main.slice(main.indexOf('function applyOrdinary('),main.indexOf('function afterCommitted(')),context);
 return {actor,sound,particles,awards,damage,apply:()=>context.applyOrdinary(actor),flush:()=>{while(queue.length)queue.shift()()}};
}
test('ordinary fatal branch sends original feedback before damage, including the unchallenged case',()=>{
 for(const challenged of [false,true]){
  const f=fixture({challenged});f.apply();assert.equal(f.damage.length,0);
  assert.deepEqual(f.sound.map(x=>[x.id,x.options.volume,x.options.pitch]),[['kg_java21.ordinary_break',1,.65],['kg_java21.ordinary_impact',.7,.55]]);
  assert.equal(f.particles.filter(x=>x.id.endsWith('damage_indicator')).length,24);assert.equal(f.particles.filter(x=>x.id.endsWith('large_smoke')).length,18);
  f.flush();assert.equal(f.damage.length,1);assert.equal(f.damage[0].options.cause,'override');assert.equal(f.damage[0].value,3.4028234663852886e38);
  assert.deepEqual(f.awards,challenged?['spear']:[]);
 }
});
test('shield success retains original shield/chime burst and never applies fatal damage',()=>{
 const f=fixture({challenged:true,draw:.25});f.apply();f.flush();assert.equal(f.damage.length,0);assert.deepEqual(f.awards,['shield']);assert.equal(f.particles.length,28);
 assert.deepEqual(f.sound.map(x=>[x.id,x.options.volume,x.options.pitch]),[['kg_java21.shield',1,.8],['kg_java21.chime',.8,1.35]]);
});
test('a rejected feedback sound never prevents the remaining particles or fatal damage',()=>{
 const f=fixture({brokenSound:true});f.apply();f.flush();assert.equal(f.sound.length,2);assert.equal(f.particles.length,42);assert.equal(f.damage.length,1);
});
test('Java event gain survives import, including quiet amethyst shimmer rather than the Bedrock gain',()=>{
 const rp=JSON.parse(read('projects/grilling/gameplay_core/resource_pack/sounds/sound_definitions.json')).sound_definitions;
 const proof=JSON.parse(read('development/gameplay_core/fixtures/java-feedback-audio-1.21.1.json'));
 for(const [alias,ref] of Object.entries(proof.events)){
  const original=ref.original.sounds.map(x=>typeof x==='string'?{name:x}:x),actual=rp['kg_java21.'+alias].sounds;
  assert.equal(actual.length,original.length);
  actual.forEach((x,i)=>{assert.equal(x.volume??1,original[i].volume??1);assert.equal(x.pitch??1,original[i].pitch??1);assert.ok(x.name.endsWith(original[i].name))});
 }
 assert.equal(rp['kg_java21.chime'].sounds[0].volume,.2);
});
