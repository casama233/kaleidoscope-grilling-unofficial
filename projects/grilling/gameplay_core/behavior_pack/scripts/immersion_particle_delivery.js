/** Particle command delivery only; the production adapter supplies native Molang maps. */
export function emitParticleCommands(dimension,origin,particles,variablesFor=()=>undefined){
 const result={accepted:0,failed:0,lastError:''};
 for(const {id,offset,velocity=[0,0,0]} of particles)try{
  dimension.spawnParticle(id,{x:origin.x+offset[0],y:origin.y+offset[1],z:origin.z+offset[2]},variablesFor(velocity));
  result.accepted++;
 }catch(error){result.failed++;result.lastError=String(error)}
 return result;
}
