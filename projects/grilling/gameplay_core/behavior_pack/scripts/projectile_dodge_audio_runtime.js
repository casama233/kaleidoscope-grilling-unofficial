import {TELEPORT_ORIGIN_SOUND_ID,FLATULENCE_SOUND_ID,teleportDestinationAudio} from './projectile_dodge_audio_core.js';
import {recordSoundDelivery} from './immersion_feedback_diagnostics.js';

// Sound only: caller owns the successful teleport and immutable original point.
// Stable API has no generic Java isSilent/getSoundSource query. Known vanilla
// actor categories are source-reviewed; other actors use the declared fallback.
export function projectileDodgeTeleportFeedback(entity,origin){
 const result={attempted:0,accepted:0,failed:0,destinationCategoryReviewed:false};
 for(const site of ['origin','destination']){
  result.attempted++;
  try{
   const destination=site==='destination'?teleportDestinationAudio(entity.typeId):undefined;
   if(destination)result.destinationCategoryReviewed=destination.categoryReviewed;
   const location=site==='origin'?{x:origin.x,y:origin.y,z:origin.z}:entity.location;
   entity.dimension.playSound(destination?.soundId??TELEPORT_ORIGIN_SOUND_ID,location,{volume:1,pitch:1});
   result.accepted++;recordSoundDelivery();
  }catch(error){result.failed++;recordSoundDelivery(error)}
 }
 return result;
}
export {FLATULENCE_SOUND_ID};
