import {PROJECTILE_DODGE_ATTEMPTS,projectileDodgePositionValid,projectileDodgeBounds,sampleProjectileDodgeAttempt} from './projectile_dodge_movement_core.js';
import {projectileDodgeLiquidPrecheck} from './projectile_dodge_liquid_runtime.js';
import {resolveProjectileDodgeGround} from './projectile_dodge_ground_runtime.js';
const copyPosition=point=>({x:point.x,y:point.y,z:point.z});

function dismountOne(entity){
 try{
  const riding=entity.getComponent('minecraft:riding');if(!riding)return {ok:true};
  const mount=riding.entityRidingOn,rideable=mount?.getComponent('minecraft:rideable');
  if(typeof rideable?.ejectRider!=='function')return {ok:false,reason:'riding_api_unavailable'};
  // Eject only this rider. Never move/eject the mount's other passengers.
  let failed=false;try{rideable.ejectRider(entity)}catch{failed=true}
  // A native mutation can be acknowledged despite a later callback exception.
  if(!entity.getComponent('minecraft:riding'))return {ok:true};
  return {ok:false,reason:failed?'dismount_api_failed':'dismount_not_observed'};
 }catch{return {ok:false,reason:'riding_context_unavailable'}}
}

// Mutable caller owns fee/lifecycle/collision protection; this helper moves only.
// Original downward ground adjustment precedes the adjusted body's liquid gate.
// Exact Java collision shape/temporary movement, navigation and TELEPORT events
// remain separate boundaries; checkForBlocks does not establish their parity.
export function tryProjectileDodgeMovement(entity,{random=Math.random}={}){
 const result={success:false,attempts:0,origin:undefined,destination:undefined,dimensionId:undefined,reason:''};
 let bounds;
 try{
  if(typeof entity.getComponent!=='function'||!entity.getComponent('minecraft:health')){result.reason='living_actor_unavailable';return result}
  const dimension=entity.dimension;result.dimensionId=dimension.id;
  bounds=projectileDodgeBounds(result.dimensionId,dimension.heightRange);
  if(!bounds){result.reason='source_bounds_or_native_coverage_unavailable';return result}
  result.origin=copyPosition(entity.location);
  if(!projectileDodgePositionValid(result.origin)||typeof entity.tryTeleport!=='function'){result.reason='movement_api_unavailable';return result}
 }catch{result.reason='movement_context_unavailable';return result}
 for(let i=0;i<PROJECTILE_DODGE_ATTEMPTS;i++){
  result.attempts++;
  let to;try{to=sampleProjectileDodgeAttempt(result.origin,bounds,random)}catch{result.reason='random_source_unavailable';return result}
  if(!to){result.reason='random_source_unavailable';return result}
  try{if(entity.dimension.id!==result.dimensionId){result.reason='dimension_changed';return result}}catch{result.reason='movement_context_unavailable';return result}
  const dismount=dismountOne(entity);if(!dismount.ok){result.reason=dismount.reason;return result}
  try{if(entity.dimension.id!==result.dimensionId){result.reason='dimension_changed';return result}}catch{result.reason='movement_context_unavailable';return result}
  let afterDismount;
  try{afterDismount=copyPosition(entity.location)}catch{result.reason='movement_context_unavailable';return result}
  const contextCurrent=()=>{try{return entity.dimension.id===result.dimensionId&&['x','y','z'].every(axis=>entity.location[axis]===afterDismount[axis])}catch{return false}};
  const ground=resolveProjectileDodgeGround(entity,to);
  if(!contextCurrent()){result.reason='movement_context_changed';return result}
  if(!ground.supported||!ground.found){result.reason=ground.reason;continue}
  const adjusted=ground.destination,liquid=projectileDodgeLiquidPrecheck(entity,adjusted);
  if(!contextCurrent()){result.reason='movement_context_changed';return result}
  if(!liquid.allow){result.reason=liquid.reason;continue}
  try{if(entity.dimension.id!==result.dimensionId){result.reason='dimension_changed';return result}}catch{result.reason='movement_context_unavailable';return result}
  try{if(entity.getComponent('minecraft:riding')){result.reason='riding_context_changed';return result}}catch{result.reason='riding_context_unavailable';return result}
  if(!contextCurrent()){result.reason='movement_context_changed';return result}
  try{
   if(!entity.tryTeleport(adjusted,{checkForBlocks:true,keepVelocity:true}))continue;
   result.success=true;result.reason='';
   // Preserve observed native success even if the actor vanishes before the
   // destination can be read; a caller must not repeat the already moved use.
   try{const destination=copyPosition(entity.location);if(projectileDodgePositionValid(destination))result.destination=destination;else result.reason='destination_unavailable'}catch{result.reason='destination_unavailable'}
   return result;
  }catch{result.reason='teleport_api_failed';return result}
 }
 result.reason='no_successful_attempt';return result;
}
