/** BDS exposes pre-absorption provisional health in the before-hurt callback.
 * Remaining native absorption is not exposed by stable Script API. Its effect
 * maximum is only an upper bound: do not consume rescue on an ambiguous hit.
 * A partially spent shield can therefore still hide a lethal hit; not Java parity.
 */
export function definitelyLethalProvisionalHealth(health,absorption){
 const hp=Number(health);if(!Number.isFinite(hp)||hp>0)return false;
 if(!absorption)return true;
 const amp=Number(absorption.amplifier);
 if(!Number.isInteger(amp)||amp<0||amp>255)return false;
 return hp+4*(amp+1)<=0;
}

/** Java AdvancedSeasoningHandler.onDeath: consume the rescue and add ten
 * minutes of poisoning. The caller supplies a fresh, active effect snapshot;
 * this plan keeps unrelated effects in the same single stored-field update.
 */
export function sameHeavyMetalEffect(actual,expected){
 return !!actual&&!!expected&&Number.isFinite(actual.until)&&Number.isFinite(actual.amp)&&
  actual.until===expected.until&&actual.amp===expected.amp;
}
export function planHeavyMetalTransition(effects,expected,time){
 if(!Number.isFinite(time)||!sameHeavyMetalEffect(effects?.heavy_metal,expected)||
  effects.heavy_metal.until<=time||effects.heavy_metal_poisoning?.until>time)return undefined;
 const next={...effects,heavy_metal_poisoning:{until:time+12000,amp:0}};
 delete next.heavy_metal;return next;
}
