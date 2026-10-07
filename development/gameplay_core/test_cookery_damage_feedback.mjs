/** Actual G damage/feedback subscribers with API-operation adapters, not clients. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {activeEffects,FX_KEY} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/effect_lifecycle_core.js';
import {interactionParticles} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_particles_core.js';
import {emitParticleCommands} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/immersion_particle_delivery.js';

const root=new URL('../../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root),'utf8');
const main=read('projects/grilling/gameplay_core/behavior_pack/scripts/main.js');
const fxGet=main.slice(main.indexOf('function fxGet('),main.indexOf('function fxSet('));
function actor({living=true,effect='hinder',until=2000}={}){
 const applied=[],sound=[],particles=[],impulses=[];
 return {id:'native-actor-'+Math.random(),isSneaking:false,applied,sound,particles,impulses,
  location:{x:2,y:80,z:3},
  dimension:{playSound:(...v)=>sound.push(v),spawnParticle:(...v)=>particles.push(v)},
  getComponent:id=>id==='minecraft:health'&&living?{}:undefined,
  getDynamicProperty:key=>key===FX_KEY?JSON.stringify({[effect]:{until,amp:0}}):undefined,
  addEffect:(...v)=>applied.push(v),applyImpulse:v=>impulses.push(v)};
}
function harness({legacy=false,draw=.5}={}){
 const callbacks={},context=vm.createContext({console,
  Math:Object.assign(Object.create(Math),{random:()=>draw}),SNEAK_LAST:new Map(),
  now:()=>1000,readFx:entity=>activeEffects(JSON.parse(entity.getDynamicProperty(FX_KEY)??'{}'),1000),
  interactionParticleBurst:(dimension,origin,event)=>emitParticleCommands(dimension,origin,interactionParticles(event,()=>.25)),
  world:{afterEvents:Object.fromEntries(['entityHurt','entityHitEntity'].map(k=>[k,{subscribe:callback=>{callbacks[k]=callback}}]))}});
 vm.runInContext(fxGet,context);
 const handler=legacy?"world.afterEvents.entityHitEntity.subscribe(e=>{if(fxGet(e.damagingEntity,'hinder'))try{e.hitEntity.addEffect('slowness',100,{amplifier:1,showParticles:true})}catch{}});":
  main.slice(main.indexOf('world.afterEvents.entityHurt.subscribe(e=>{'),main.indexOf('function canUseSecretSkewer('));
 vm.runInContext(handler,context);
 const line=main.split('\n').find(x=>x.includes('const sneak=!!p.isSneaking'));
 return {callbacks,hurt:event=>callbacks.entityHurt?.(event),tick:entity=>{context.p=entity;vm.runInContext('(()=>{'+line+'})()',context)}};
}
function expectSlow(target){assert.equal(target.applied.length,1);const [name,ticks,options]=target.applied[0];assert.equal(name,'slowness');assert.equal(ticks,100);assert.equal(options.amplifier,1);assert.equal(options.showParticles,true)}
test('a responsible living attacker applies authored Hinder on projectile damage; the old melee-only handler misses it',()=>{
 const attacker=actor(),target=actor();const event={hurtEntity:target,damage:2,damageSource:{cause:'projectile',damagingEntity:attacker,damagingProjectile:actor({living:false})}};
 harness({legacy:true}).hurt(event);assert.equal(target.applied.length,0);
 harness().hurt(event);expectSlow(target);
});
test('melee and attributed non-melee after-hurt callbacks retain the same effect contract',()=>{
 for(const cause of ['entityAttack','magic','thorns']){const target=actor();harness().hurt({hurtEntity:target,damage:2,damageSource:{cause,damagingEntity:actor()}});expectSlow(target)}
});
test('Hinder does not add a positive damage gate absent in both original loader branches',()=>{
 const target=actor();harness().hurt({hurtEntity:target,damage:0,damageSource:{damagingEntity:actor()}});expectSlow(target);
});
test('missing responsible entity uses a native projectile owner, never the projectile effect state',()=>{
 const owner=actor(),target=actor(),projectile={getComponent:id=>id==='minecraft:projectile'?{owner}:undefined};
 harness().hurt({hurtEntity:target,damage:2,damageSource:{damagingProjectile:projectile}});expectSlow(target);
});
test('reported responsible attacker takes precedence over a projectile owner',()=>{
 const target=actor(),attacker=actor({effect:'vigor'}),projectile={getComponent:()=>({owner:actor()})};
 harness().hurt({hurtEntity:target,damage:2,damageSource:{damagingEntity:attacker,damagingProjectile:projectile}});assert.equal(target.applied.length,0);
});
test('missing, expired, nonliving attackers and nonliving victims do not gain Hinder',()=>{
 for(const attacker of [undefined,actor({until:1000}),actor({living:false}),actor({effect:'vigor'})]){
  const target=actor();harness().hurt({hurtEntity:target,damage:2,damageSource:{damagingEntity:attacker}});assert.equal(target.applied.length,0);
 }
 const target=actor({living:false});harness().hurt({hurtEntity:target,damage:2,damageSource:{damagingEntity:actor()}});assert.equal(target.applied.length,0);
});
test('a removed source/projectile or rejected effect remains local to that callback',()=>{
 const h=harness(),target=actor(),broken={getComponent(){throw Error('Removed entity')}};
 assert.doesNotThrow(()=>h.hurt({hurtEntity:target,damageSource:{damagingProjectile:broken}}));assert.equal(target.applied.length,0);
 target.addEffect=()=>{throw Error('Removed target')};assert.doesNotThrow(()=>h.hurt({hurtEntity:target,damageSource:{damagingEntity:actor()}}));
});
test('flatulence press sends ten Cloud commands and the existing original host audio exactly once',()=>{
 const h=harness(),subject=actor({effect:'flatulence'});h.tick(subject);subject.isSneaking=true;h.tick(subject);h.tick(subject);
 assert.equal(subject.impulses.length,1);assert.equal(subject.impulses[0].y,.75);assert.equal(subject.particles.length,10);
 assert.ok(subject.particles.every(x=>x[0]==='kaleidoscope_grilling:feedback_cloud'));assert.equal(subject.sound.length,1);
 const [id,location,options]=subject.sound[0];assert.equal(id,'kaleidoscope_cookery.fart');assert.equal(location,subject.location);assert.equal(options.volume,1);assert.equal(options.pitch,1);
 subject.isSneaking=false;h.tick(subject);subject.isSneaking=true;h.tick(subject);assert.equal(subject.sound.length,2);
});
test('flatulence uses source pitch bounds without firing for inactive effects',()=>{
 for(const draw of [0,.25,.999]){const h=harness({draw}),subject=actor({effect:'flatulence'});subject.isSneaking=true;h.tick(subject);assert.equal(subject.sound[0][2].pitch,.8+draw*.4)}
 for(const subject of [actor({effect:'vigor'}),actor({effect:'flatulence',until:1000})]){subject.isSneaking=true;harness().tick(subject);assert.equal(subject.sound.length,0);assert.equal(subject.particles.length,0)}
});
test('unavailable particles or audio never change the authored impulse or the other feedback channel',()=>{
 const h=harness(),subject=actor({effect:'flatulence'});subject.dimension.spawnParticle=()=>{throw Error('Unloaded particle')};subject.isSneaking=true;assert.doesNotThrow(()=>h.tick(subject));assert.equal(subject.impulses.length,1);assert.equal(subject.sound.length,1);
 const other=actor({effect:'flatulence'});other.dimension.playSound=()=>{throw Error('Unloaded audio')};other.isSneaking=true;assert.doesNotThrow(()=>h.tick(other));assert.equal(other.impulses.length,1);assert.equal(other.particles.length,10);
});
test('Cloud Gaussian event vectors retain source offset, spread and speed',()=>{
 const particles=interactionParticles('flatulence',()=>.25);assert.equal(particles.length,10);
 for(const p of particles){assert.ok(Math.abs(p.offset[0])<1e-14);assert.ok(Math.abs(p.offset[1]-.25)<1e-14);assert.ok(Math.abs(p.offset[2])<1e-14);assert.ok(p.velocity.every(v=>Math.abs(v)<1e-14))}
 const varied=interactionParticles('flatulence',()=>.5),gaussian=-Math.sqrt(2*Math.log(2));
 for(const p of varied){assert.ok(Math.abs(p.offset[0]-gaussian*.25)<1e-14);assert.ok(Math.abs(p.offset[1]-(.25+gaussian*.25))<1e-14);assert.ok(p.velocity.every(v=>Math.abs(v-gaussian*.1)<1e-14))}
});
test('owned Cloud uses the existing G atlas/velocity contract and retains its declared limitation',()=>{
 const cloud=JSON.parse(read('projects/grilling/gameplay_core/resource_pack/particles/feedback_cloud.json')).particle_effect;
 assert.equal(cloud.description.identifier,'kaleidoscope_grilling:feedback_cloud');assert.equal(cloud.description.basic_render_parameters.texture,'textures/particle/kg_java_smoke');
 assert.equal(cloud.components['minecraft:emitter_rate_instant'].num_particles,1);assert.equal(cloud.components['minecraft:particle_appearance_billboard'].uv.texture_width,64);
 const text=JSON.stringify(cloud);assert.ok(text.includes('variable.kg_velocity.x'));assert.ok(!text.includes('variable.kt_'));assert.ok(!text.includes('kaleidoscope_tavern:'));
 const proof=JSON.parse(read('development/gameplay_core/fixtures/java-cookery-effect-feedback-160.json'));assert.equal(proof.client,false);assert.ok(proof.boundaries.some(x=>x.includes('Nearest-player')));
});
