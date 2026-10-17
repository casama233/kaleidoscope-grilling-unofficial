// Copy into an isolated candidate's scripts and import only for native API checks.
// Never export the probe as part of the release, and never run in the live world.
import {world,system} from '@minecraft/server';
import {interactionParticles,grillParticles} from './immersion_particles_core.js';
import {emitParticles} from './immersion_particles_runtime.js';
import {goldenSkewerFeedback,ordinaryShieldFeedback,invincibleAmbientFeedback,invincibleDamageFeedback} from './immersion_effect_feedback.js';
import {feedbackDiagnostics} from './immersion_feedback_diagnostics.js';
const need=(value,message)=>{if(!value)throw Error(message)};
system.runTimeout(()=>{
 let entity;
 try{
  need(world.getAllPlayers().length===0,'unexpected real player');
  const dimension=world.getDimension('overworld'),location={x:0,y:81,z:64},before=feedbackDiagnostics();
  entity=dimension.spawnEntity('minecraft:pig',location);
  need(entity.getAABB().extent.y>0,'native collision height unavailable');
  for(const event of ['oilPressImpact','seasoningAdded','seasoningFinished'])emitParticles(dimension,location,interactionParticles(event));
  emitParticles(dimension,location,grillParticles(true,()=>0));
  goldenSkewerFeedback(entity);ordinaryShieldFeedback(entity);invincibleAmbientFeedback(entity);
  invincibleDamageFeedback(entity);invincibleDamageFeedback(entity);
  system.runTimeout(()=>{try{
   const after=feedbackDiagnostics(),particles=after.particleAccepted-before.particleAccepted,sounds=after.soundAccepted-before.soundAccepted;
   need(after.particleFailed===before.particleFailed,'native particle API failure: '+after.lastParticleError);
   need(after.soundFailed===before.soundFailed,'native sound API failure: '+after.lastSoundError);
   need(particles>=92,'missing native particle calls: '+particles);need(sounds>=4,'missing native sound calls: '+sounds);
   console.warn('FEEDBACK_NATIVE_PASS '+JSON.stringify({players:0,simulated_players:false,native_aabb:true,particle_api_accepted:particles,sound_api_accepted:sounds,expected_probe_particles:92,client:false,rendered_particle_count_verified:false,player_damage_event_verified:false}));
  }catch(error){console.warn('FEEDBACK_NATIVE_FAIL '+error)}finally{try{entity.remove()}catch{}}},3);
 }catch(error){try{entity?.remove()}catch{};console.warn('FEEDBACK_NATIVE_FAIL '+error)}
},100);
