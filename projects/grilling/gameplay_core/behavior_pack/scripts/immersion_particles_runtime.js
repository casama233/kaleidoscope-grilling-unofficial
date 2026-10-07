import {MolangVariableMap} from '@minecraft/server';
import {interactionParticles,grillParticles} from './immersion_particles_core.js';
import {emitParticleCommands} from './immersion_particle_delivery.js';
import {recordParticleDelivery} from './immersion_feedback_diagnostics.js';
export function emitParticles(dimension,origin,particles){
 const result=emitParticleCommands(dimension,origin,particles,velocity=>{
  const variables=new MolangVariableMap();
  // Java event velocities are blocks/tick; Bedrock particle speeds are blocks/s.
  const nativeVelocity={x:velocity[0]*20,y:velocity[1]*20,z:velocity[2]*20};
  variables.setVector3('variable.kg_velocity',nativeVelocity);
  // Cloud uses direct scalar ?? operands; ordinary feedback retains its vector.
  for(const axis of ['x','y','z'])variables.setFloat('variable.kg_velocity_'+axis,nativeVelocity[axis]);
  return variables;
 });
 recordParticleDelivery(result);return result;
}
export function interactionParticleBurst(dimension,origin,event){emitParticles(dimension,origin,interactionParticles(event))}
export function grillAmbientParticles(block,lit){emitParticles(block.dimension,block.location,grillParticles(lit))}
