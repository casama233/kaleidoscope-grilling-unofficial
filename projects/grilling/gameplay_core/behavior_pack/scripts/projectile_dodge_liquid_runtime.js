import {projectileDodgeLiquidCellPlan,classifyProjectileDodgeLiquidCell} from './projectile_dodge_liquid_core.js';
const axes=['x','y','z'];
const copy=point=>({x:point.x,y:point.y,z:point.z});

// Read-only precheck for a mutable caller after its targeted rider exit. This
// module spends no fee, teleports no actor, emits no feedback and changes no
// attempts. Native collision, ground search and Java engine phases stay separate.
export function projectileDodgeLiquidPrecheck(entity,candidate,options){
 const result={allow:false,supported:false,reason:'',checkedCells:0,plannedCells:0};
 let dimension,dimensionId,position,box,plan;
 try{
  dimension=entity.dimension;dimensionId=dimension.id;position=copy(entity.location);
  if(typeof dimension.getBlock!=='function'||typeof entity.getAABB!=='function'){result.reason='liquid_context_unavailable';return result}
  const nativeBox=entity.getAABB();box={center:copy(nativeBox.center),extent:copy(nativeBox.extent)};
  plan=projectileDodgeLiquidCellPlan(position,box,candidate,options);
 }catch{result.reason='collision_bounds_unavailable';return result}
 if(!plan.supported){result.reason=plan.reason;return result}
 result.plannedCells=plan.cellCount;
 for(let x=plan.min.x;x<plan.max.x;x++)for(let y=plan.min.y;y<plan.max.y;y++)for(let z=plan.min.z;z<plan.max.z;z++){
  const cell={x,y,z};let presence,typeId;
  try{
   const block=dimension.getBlock(cell);if(!block){result.reason='block_context_unavailable';return result}
   typeId=block.typeId;
   presence=classifyProjectileDodgeLiquidCell({typeId,isLiquid:block.isLiquid,isWaterlogged:block.isWaterlogged});
  }catch{result.reason='block_context_unavailable';return result}
  result.checkedCells++;
  if(!presence.supported){result.reason=presence.reason;result.cell={...cell,typeId};return result}
  if(presence.liquid){result.supported=true;result.reason='liquid_cell';result.cell={...cell,typeId,presence:presence.reason};return result}
 }
 try{
  const currentBox=entity.getAABB(),current=entity.location;
  if(entity.dimension.id!==dimensionId||!axes.every(axis=>current[axis]===position[axis]&&currentBox.center[axis]===box.center[axis]&&currentBox.extent[axis]===box.extent[axis])){result.reason='liquid_context_changed';return result}
 }catch{result.reason='liquid_context_unavailable';return result}
 result.allow=true;result.supported=true;result.reason='dry';return result;
}
