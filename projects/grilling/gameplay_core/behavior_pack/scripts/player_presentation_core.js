export const EAT_NATIVE_TICKS_PROPERTY='kaleidoscope_grilling:eat_native_ticks';
export function eatingNativeTicks(value){const n=Number(value);return Number.isInteger(n)&&n>0&&n<=72000?n:0;}
export const EAT_PROJECTION_PROPERTY='kaleidoscope_grilling:eat_projection';
export const EAT_PROFILE_PROPERTY='kaleidoscope_grilling:eat_profile';
export const EAT_HAND_PROPERTY='kaleidoscope_grilling:eat_hand';
export const PROFILE_CODES=Object.freeze({ONE:1,TWO:2,THREE:3,THREE_ALT:4,FOUR:5});
export function eatingProfile(requested,random01=Math.random()){
 const profile=requested==='THREE_RANDOM'?(random01<.5?'THREE':'THREE_ALT'):requested;
 if(!Object.hasOwn(PROFILE_CODES,profile))throw Error('Unknown eating profile');
 return {profile,code:PROFILE_CODES[profile],duration:profile==='THREE'?100:90};
}
