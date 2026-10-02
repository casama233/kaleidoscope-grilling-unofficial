import {system} from '@minecraft/server';
// Bounded counters only; accepted API calls are not client rendering evidence.
const totals={particleAccepted:0,particleFailed:0,soundAccepted:0,soundFailed:0,lastParticleError:'',lastSoundError:''};
let lastWarning=-1200;
function warn(kind,error){
 if(system.currentTick-lastWarning<1200)return;lastWarning=system.currentTick;
 console.warn('[Grilling feedback] '+kind+' delivery failed: '+String(error)+'; particle failures='+totals.particleFailed+', sound failures='+totals.soundFailed);
}
export function recordParticleDelivery(result){
 totals.particleAccepted+=result.accepted;totals.particleFailed+=result.failed;
 if(result.failed){totals.lastParticleError=result.lastError;warn('particle',result.lastError)}
}
export function recordSoundDelivery(error){
 if(error===undefined){totals.soundAccepted++;return}
 totals.soundFailed++;totals.lastSoundError=String(error);warn('sound',error);
}
export function feedbackDiagnostics(){return {...totals}}
