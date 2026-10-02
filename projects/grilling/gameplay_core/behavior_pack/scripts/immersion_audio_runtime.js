import {interactionParticleBurst} from './immersion_particles_runtime.js';
import {system} from '@minecraft/server';
import {createGrillAudioController,stopSoundHandle} from './immersion_audio_core.js';

const stationKey=block=>[block.dimension.id,block.x,block.y,block.z].join('|');
const center=block=>({x:block.x+.5,y:block.y+.35,z:block.z+.5});
const grillAudio=createGrillAudioController({play:({dimension,location})=>
 dimension.playSound('kg_imm.grill_loop',location,{volume:.65,pitch:1})});
export function updateGrillAudio(block,lit,count){
 grillAudio.update(stationKey(block),{dimension:block.dimension,location:center(block)},!!lit&&count>0,system.currentTick);
}
export function removeGrillAudio(block){grillAudio.remove(stationKey(block))}
// Block ticks cease when a chunk unloads. Drop and stop stale native handles.
system.runInterval(()=>grillAudio.sweep(system.currentTick),4);
export function blockSound(block,id,volume=1,pitch=1){
 try{return block.dimension.playSound('kg_imm.'+id,center(block),{volume,pitch})}catch{}
}
export function useSound(player,id,volume=1,pitch=1){
 try{return player.dimension.playSound('kg_imm.'+id,player.location,{volume,pitch})}catch{}
}
export function seasoningFinished(player){
 useSound(player,'action_success',.8);
 interactionParticleBurst(player.dimension,player.location,'seasoningFinished');
}
export {stopSoundHandle};
