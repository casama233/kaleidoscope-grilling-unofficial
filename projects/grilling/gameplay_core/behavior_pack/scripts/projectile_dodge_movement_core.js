// Cookery1.6 + independently reviewed vanilla dimension data for MC1.20.1/1.21.1.
export const PROJECTILE_DODGE_ATTEMPTS=16,PROJECTILE_DODGE_RANGE=3;
const VANILLA_LOGICAL_BOUNDS=Object.freeze({
 'minecraft:overworld':Object.freeze({min:-64,max:319}),
 'minecraft:nether':Object.freeze({min:0,max:127}),
 'minecraft:the_end':Object.freeze({min:0,max:255})
});
export function projectileDodgePositionValid(value){return !!value&&['x','y','z'].every(axis=>Number.isFinite(value[axis]))}
export function projectileDodgeBounds(dimensionId,nativeRange){
 const bounds=VANILLA_LOGICAL_BOUNDS[dimensionId];
 if(!bounds||!nativeRange||!Number.isFinite(nativeRange.min)||!Number.isFinite(nativeRange.max)||nativeRange.min>bounds.min||nativeRange.max<bounds.max)return undefined;
 // Native max is only a coverage guard. Never infer logical height or max-1.
 return {...bounds};
}
export function sampleProjectileDodgeAttempt(origin,bounds,random=Math.random){
 if(!projectileDodgePositionValid(origin)||!bounds)return undefined;
 const draws=[random(),random(),random()];
 if(draws.some(value=>!Number.isFinite(value)||value<0||value>=1))return undefined;
 return {x:origin.x+(draws[0]-.5)*PROJECTILE_DODGE_RANGE,
  y:Math.max(bounds.min,Math.min(bounds.max,origin.y+(draws[1]-.5)*PROJECTILE_DODGE_RANGE)),
  z:origin.z+(draws[2]-.5)*PROJECTILE_DODGE_RANGE};
}
