import {system,world} from '@minecraft/server';
import {currentPlacedOilPotCandidates,readPlacedOilPotState} from './a2739_cookery_oil_pot_block_adapter.js';
import {HOST_BLOCK_ID} from './a2736_typed_oil_pot_block_core.js';
import {premiumOilPotInRange,premiumOilPotParticles} from './oil_ambient_core.js';
import {emitParticles} from './immersion_particles_runtime.js';

// Java samples this independently on each nearby client every eight ticks.
// Use Player.spawnParticle through the existing Molang velocity adapter, so
// overlapping observers neither multiply each other's bursts nor share a draw.
// Discovery comes from the placed renderer/public Oil API, never private data.
system.runInterval(()=>{
 const players=world.getAllPlayers();
 for(const station of currentPlacedOilPotCandidates())try{
  const nearby=players.filter(player=>premiumOilPotInRange(station,player));
  if(!nearby.length)continue;
  const block=world.getDimension(station.dimensionId).getBlock(station);
  if(block?.typeId!==HOST_BLOCK_ID)continue;
  const state=readPlacedOilPotState(block);
  if(state?.type!=='premium_chili'||!(state.count>0))continue;
  for(const player of nearby)emitParticles(player,station,premiumOilPotParticles());
 }catch{} // An unloaded target is not authority to modify a block or its oil.
},8);
