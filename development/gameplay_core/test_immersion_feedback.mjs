/** Statistical source-contract checks; no player or renderer simulation. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {interactionParticles,grillParticles,oilImpactPitch,goldenSkewerParticles,invincibleAmbientParticle,createFeedbackCooldown} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_particles_core.js';
import {emitParticleCommands as emitParticles} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_particle_delivery.js';
function seeded(){let n=13579;return ()=>{n=(Math.imul(n,1664525)+1013904223)>>>0;return n/4294967296}}
test('unlit grill emits nothing and consumes no random values',()=>{
 assert.deepEqual(grillParticles(false,()=>{throw Error('unexpected draw')}),[]);
});
test('grill ambient samples use distinct Java firebox heights and horizontal bounds',()=>{
 const random=seeded(),counts={smoke:0,flame:0};
 for(let i=0;i<50000;i++)for(const p of grillParticles(true,random)){
  const smoke=p.id.includes('smoke'),key=smoke?'smoke':'flame';counts[key]++;
  assert.equal(p.offset[1],smoke?.22:.18);
  for(const axis of [0,2])assert.ok(p.offset[axis]>=(smoke?.25:.3)&&p.offset[axis]<(smoke?.75:.7));
 }
 assert.ok(Math.abs(counts.smoke/50000-1/3)<.01);assert.ok(Math.abs(counts.flame/50000-1/8)<.01);
});
test('success bursts preserve Java count, center and Gaussian spatial spread',()=>{
 const random=seeded();
 for(const [event,count,center,spread] of [
  ['seasoningFinished',12,[0,1,0],[.25,.35,.25]],
  ['seasoningAdded',5,[.5,.7,.5],[.12,.12,.12]],
  ['oilPressImpact',14,[.5,.9,.5],[.32,.18,.32]]
 ]){
  const sums=[0,0,0],squares=[0,0,0];let n=0,tail=false;
  for(let i=0;i<3000;i++){
   const burst=interactionParticles(event,random);assert.equal(burst.length,count);
   for(const {offset} of burst){n++;for(let axis=0;axis<3;axis++){const z=(offset[axis]-center[axis])/spread[axis];sums[axis]+=z;squares[axis]+=z*z;if(Math.abs(z)>3)tail=true;}}
  }
  for(let axis=0;axis<3;axis++){assert.ok(Math.abs(sums[axis]/n)<.035);assert.ok(Math.abs(squares[axis]/n-1)<.05)}
  assert.ok(tail,'Gaussian distribution must not collapse to a uniform box');
 }
});
test('particle delivery failures remain cosmetic and do not abort remaining emissions',()=>{
 const calls=[],origin={x:10,y:64,z:-7};
 const result=emitParticles({spawnParticle(id,pos){calls.push({id,pos});if(calls.length===1)throw Error('unloaded')}},origin,[{id:'a',offset:[.5,.7,.5]},{id:'b',offset:[0,1,0]}]);
 assert.deepEqual(calls,[{id:'a',pos:{x:10.5,y:64.7,z:-6.5}},{id:'b',pos:{x:10,y:65,z:-7}}]);
 assert.equal(result.accepted,1);assert.equal(result.failed,1);assert.match(result.lastError,/unloaded/);
});
test('oil press impact varies through the original pitch interval',()=>{
 assert.equal(oilImpactPitch(()=>0),.82);assert.ok(oilImpactPitch(()=>.99999)<.94);assert.ok(oilImpactPitch(()=>.99999)>.9399);
});
test('golden finish draws eighteen spiral points and invincible orbit stays within Java radius/height',()=>{
 const ring=goldenSkewerParticles(()=>0);assert.equal(ring.length,18);
 ring.forEach(({offset},i)=>{assert.ok(Math.abs(Math.hypot(offset[0],offset[2])-.65)<1e-12);assert.equal(offset[1],.25+i*.06)});
 const random=seeded();for(let i=0;i<1000;i++){
  const [{offset,velocity}]=invincibleAmbientParticle(random);assert.ok(Math.abs(Math.hypot(offset[0],offset[2])-.45)<1e-12);assert.ok(offset[1]>=.3&&offset[1]<1.7);assert.deepEqual(velocity,[0,0,0]);
 }
});
test('shield cooldown shares actor identity across wrappers and releases expired bookkeeping',()=>{
 const cooldown=createFeedbackCooldown();assert.equal(cooldown.claim('a',100),true);assert.equal(cooldown.claim('a',100),false);assert.equal(cooldown.claim('b',100),true);
 assert.equal(cooldown.claim('a',105),false);cooldown.sweep(106);assert.equal(cooldown.size,0);assert.equal(cooldown.claim('a',106),true);
});
test('owned particle definitions emit exactly once at zero offset without implicit engine direction',()=>{
 const dir=new URL('../../projects/grilling/gameplay_core/resource_pack/particles/',import.meta.url);
 for(const name of ['basic_crit','electric_spark','villager_happy','endrod','basic_smoke','basic_flame']){
  const {description,components:c}=JSON.parse(fs.readFileSync(new URL('feedback_'+name+'.json',dir),'utf8')).particle_effect;
  assert.equal(description.identifier,'kaleidoscope_grilling:feedback_'+name);
  assert.deepEqual(Object.keys(c).filter(x=>x.includes('emitter_rate')),['minecraft:emitter_rate_instant']);
  assert.equal(c['minecraft:emitter_rate_instant'].num_particles,1);assert.deepEqual(c['minecraft:emitter_shape_point'].offset,[0,0,0]);
  assert.deepEqual(c['minecraft:emitter_shape_point'].direction,['variable.kg_velocity.x','variable.kg_velocity.y','variable.kg_velocity.z']);
  assert.ok(!JSON.stringify(c).includes('variable.direction'));
 }
});
test('native particle adapter supplies all three velocity axes in blocks per second',()=>{
 const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_particles_runtime.js',import.meta.url),'utf8').replace(/^import .*;$/gm,'').replace(/export function/g,'function');
 let received;
 class Variables{constructor(){this.scalars={}}setVector3(key,value){this.key=key;this.value=value}setFloat(key,value){this.scalars[key]=value}}
 const context=vm.createContext({recordParticleDelivery(){},MolangVariableMap:Variables,emitParticleCommands:(dimension,origin,particles,factory)=>{received=factory(particles[0].velocity)}});
 vm.runInContext(source+';this.run=emitParticles;',context);context.run({}, {},[{velocity:[.1,.02,-.05]}]);
 assert.equal(received.key,'variable.kg_velocity');assert.deepEqual({...received.value},{x:2,y:.4,z:-1});
 assert.deepEqual(received.scalars,{'variable.kg_velocity_x':2,'variable.kg_velocity_y':.4,'variable.kg_velocity_z':-1});
});
test('Cloud delivery without event velocity supplies scalar zeros and keeps ordinary vector compatibility',()=>{
 const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_particles_runtime.js',import.meta.url),'utf8').replace(/^import .*;$/gm,'').replace(/export function/g,'function');
 const received=[];
 class Variables{constructor(){this.scalars={}}setVector3(key,value){this.key=key;this.value=value}setFloat(key,value){this.scalars[key]=value}}
 const context=vm.createContext({recordParticleDelivery(){},MolangVariableMap:Variables,emitParticleCommands:emitParticles});
 vm.runInContext(source+';this.run=emitParticles;',context);
 context.run({spawnParticle:(id,position,variables)=>received.push({id,position,variables})},{x:1,y:2,z:3},[{id:'kaleidoscope_grilling:feedback_cloud',offset:[0,0,0]}]);
 assert.equal(received.length,1);assert.deepEqual(received[0].position,{x:1,y:2,z:3});
 assert.equal(received[0].variables.key,'variable.kg_velocity');assert.deepEqual({...received[0].variables.value},{x:0,y:0,z:0});
 assert.deepEqual(received[0].variables.scalars,{'variable.kg_velocity_x':0,'variable.kg_velocity_y':0,'variable.kg_velocity_z':0});
});
test('native effect adapter keeps particles after rejected sounds and coalesces damage feedback',()=>{
 const source=fs.readFileSync(new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_effect_feedback.js',import.meta.url),'utf8').replace(/^import .*;$/gm,'').replace(/export function/g,'function');
 const particles=[],errors=[],queue=[],system={currentTick:100,run:f=>queue.push(f),runInterval(){}};
 const dimension={playSound(){throw Error('sound unavailable')},spawnParticle(id,pos){particles.push({id,pos})}};
 const context=vm.createContext({system,createFeedbackCooldown,goldenSkewerParticles,invincibleAmbientParticle,recordSoundDelivery:e=>errors.push(e),emitParticles,interactionParticleBurst:(dim,origin,event)=>emitParticles(dim,origin,interactionParticles(event,()=>0))});
 vm.runInContext(source+';this.api={goldenSkewerFeedback,ordinaryShieldFeedback,invincibleDamageFeedback};',context);
 // Actor API adapter only. No native entity/player or game simulation is created.
 const actor={id:'actor',dimension,location:{x:0,y:10,z:0},getAABB:()=>({extent:{y:2}})};
 context.api.goldenSkewerFeedback(actor);assert.equal(particles.length,18);
 context.api.ordinaryShieldFeedback(actor);assert.equal(particles.length,46);assert.equal(errors.length,3);
 context.api.invincibleDamageFeedback(actor);context.api.invincibleDamageFeedback({...actor});assert.equal(queue.length,1);assert.equal(particles.length,46);
 queue.shift()();assert.equal(particles.length,58);assert.equal(particles.at(-1).pos.y,12.2);
 system.currentTick=106;context.api.invincibleDamageFeedback({...actor});assert.equal(queue.length,1);
});
