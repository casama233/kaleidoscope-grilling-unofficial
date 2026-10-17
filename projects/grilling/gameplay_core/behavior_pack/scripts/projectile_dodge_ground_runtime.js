import {projectileDodgeBounds} from './projectile_dodge_movement_core.js';
import {projectileDodgeGroundSampleValid,projectileDodgeGroundPlan,classifyProjectileDodgeGroundCell} from './projectile_dodge_ground_core.js';
const axes=['x','y','z'];
const copy=point=>({x:point.x,y:point.y,z:point.z});
const same=(a,b)=>axes.every(axis=>a[axis]===b[axis]);

// Read-only source-column resolver. Caller owns dismount, fee/lifecycle,
// collision/liquid checks, actual teleport, navigation and feedback.
export function resolveProjectileDodgeGround(entity,sample){
 const result={supported:false,found:false,reason:'',readCells:0,descent:0,maxReads:0,destination:undefined,supportCell:undefined};
 let candidate,dimension,dimensionId,position,plan;
 try{candidate=copy(sample)}catch{result.reason='ground_sample_invalid';return result}
 if(!projectileDodgeGroundSampleValid(candidate)){result.reason='ground_sample_invalid';return result}
 try{
  dimension=entity.dimension;dimensionId=dimension.id;position=copy(entity.location);
  const bounds=projectileDodgeBounds(dimensionId,dimension.heightRange);
  if(!bounds){result.reason='ground_source_bounds_unavailable';return result}
  // The author caller clamps its samples to these original logical bounds.
  // This keeps the full source column finite, without a shorter work cutoff.
  if(candidate.y<bounds.min||candidate.y>bounds.max){result.reason='ground_source_sample_out_of_bounds';return result}
  if(!projectileDodgeGroundSampleValid(position)||typeof dimension.getBlock!=='function'||typeof dimension.isChunkLoaded!=='function'){result.reason='ground_context_unavailable';return result}
  plan=projectileDodgeGroundPlan(candidate,bounds.min);
  if(!plan.supported){result.reason=plan.reason;return result}
  result.dimensionId=dimensionId;result.sourceMinimum=bounds.min;result.maxReads=plan.maxReads;
 }catch{result.reason='ground_context_unavailable';return result}
 const current=()=>{try{return entity.dimension.id===dimensionId&&same(entity.location,position)}catch{return false}};
 try{
  // hasChunkAt's integer starting x/z is checked before any below-cell read.
  if(dimension.isChunkLoaded({...plan.cursor})!==true){result.reason='ground_chunk_unavailable';return result}
 }catch{result.reason='ground_chunk_unavailable';return result}
 if(!current()){result.reason='ground_context_changed';return result}
 let cursor={...plan.cursor},workingY=plan.workingY;
 while(cursor.y>plan.minimum){
  const below={x:cursor.x,y:cursor.y-1,z:cursor.z};let motion,typeId;
  result.readCells++;
  try{
   const block=dimension.getBlock(below);if(!block){result.reason='ground_block_unavailable';return result}
   // Bind identity and all states to one immutable native permutation snapshot,
   // rather than mix a current Block label with a later permutation's states.
   const permutation=block.permutation;
   if(typeof permutation?.getAllStates!=='function'){result.reason='ground_block_states_unavailable';return result}
   typeId=permutation.type.id;
   motion=classifyProjectileDodgeGroundCell({typeId,states:permutation.getAllStates()});
  }catch{result.reason='ground_block_states_unavailable';return result}
  if(!current()){result.reason='ground_context_changed';return result}
  if(!motion.supported){result.reason=motion.reason;result.cell={...below,typeId};return result}
  if(motion.blocksMotion){
   result.supported=true;result.found=true;result.reason='ground_support';
   result.destination={x:candidate.x,y:workingY,z:candidate.z};result.supportCell={...below,typeId};return result;
  }
  // Keep DOUBLE workingY and integer cursor separate. A true support read
  // above does not decrement either value or snap to a block surface.
  workingY-=1;cursor=below;result.descent++;
 }
 if(!current()){result.reason='ground_context_changed';return result}
 result.supported=true;result.reason='no_ground_support';return result;
}
