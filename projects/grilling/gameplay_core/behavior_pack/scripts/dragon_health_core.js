/** Java 1.1.1 maximum-health bonus. Native groups own damage and healing. */
export function dragonHealthBonus(amplifier){return amplifier===undefined?0:amplifier>0?10:6;}
export function dragonHealthGain(previousAmplifier,nextAmplifier){return Math.max(0,dragonHealthBonus(nextAmplifier)-dragonHealthBonus(previousAmplifier));}
