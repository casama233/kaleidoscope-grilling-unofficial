// Cookery 1.6.0 uses blockPosition for sound, separately from its Cloud origin.
export {FLATULENCE_SOUND_ID} from './projectile_dodge_audio_core.js';

export function flatulenceSoundOrigin(entity){
 try{
  const {x,y,z}=entity.location;
  const values=[x,y,z];
  if(!values.every(Number.isFinite))return undefined;
  const block=values.map(Math.floor);
  // Outside the original signed-int BlockPos domain is an unsupported location.
  if(!block.every(n=>n>=-2147483648&&n<=2147483647))return undefined;
  return {x:block[0]+0.5,y:block[1]+0.5,z:block[2]+0.5};
 }catch{return undefined}
}

export function flatulenceSoundPitch(random=Math.random){
 try{
  const draw=random();
  if(!Number.isFinite(draw)||draw<0||draw>=1)return undefined;
  // Original bytecode: Math.random()D, d2f, ldc 0.4f, fmul, fadd with 0.8f.
  return Math.fround(Math.fround(0.8)+Math.fround(Math.fround(draw)*Math.fround(0.4)));
 }catch{return undefined}
}
