import {ADVANCED_RACK_BLOCK_ID} from './a2746_advanced_rack_core.js';

// Reviewed shipped selection box. X/Z origins use the block centre; Y uses its
// bottom. The square X/Z footprint is invariant under all four rack rotations.
export const RACK_SELECTION_BOX=Object.freeze({origin:Object.freeze([-7,5,-7]),size:Object.freeze([14,9,14])});
const MIN=Object.freeze({x:1/16,y:5/16,z:1/16}),MAX=Object.freeze({x:15/16,y:14/16,z:15/16});
const AXES=['x','y','z'];
const vector=v=>!!v&&AXES.every(axis=>Number.isFinite(v[axis]));
const copy=v=>({x:v.x,y:v.y,z:v.z});
function inBox(point){return vector(point)&&AXES.every(axis=>point[axis]>=MIN[axis]&&point[axis]<=MAX[axis]);}

/** Pure slab intersection in block-local coordinates. Never selects another block
 * or substitutes an engine faceLocation when the eye ray is missing or misses. */
export function rackAimHit(origin,direction){
 if(!vector(origin)||!vector(direction))return undefined;
 const length=Math.hypot(direction.x,direction.y,direction.z);
 if(!Number.isFinite(length)||length<=1e-6)return undefined;
 const ray={x:direction.x/length,y:direction.y/length,z:direction.z/length};
 let near=0,far=Infinity;
 for(const axis of AXES){
  const delta=ray[axis],o=origin[axis];
  if(Math.abs(delta)<1e-9){if(o<MIN[axis]||o>MAX[axis])return undefined;continue;}
  const t1=(MIN[axis]-o)/delta,t2=(MAX[axis]-o)/delta;
  near=Math.max(near,Math.min(t1,t2));far=Math.min(far,Math.max(t1,t2));
  if(near>far)return undefined;
 }
 if(far<0)return undefined;
 const point={};
 for(const axis of AXES){
  const value=origin[axis]+ray[axis]*near;
  if(!Number.isFinite(value)||value<MIN[axis]-1e-9||value>MAX[axis]+1e-9)return undefined;
  point[axis]=Math.max(MIN[axis],Math.min(MAX[axis],value));
 }
 return point;
}

/** Direct touch may target off-crosshair. Tavern's measured MCPE-223452 adapter
 * decodes abs(worldCoordinate % 1) by world-axis sign and restores the actual
 * selection-box face. This is not a facing-dependent slot remap. */
export function rackTouchHit(location,face,point){
 if(!vector(location)||!AXES.every(axis=>Number.isInteger(location[axis]))||!vector(point)||AXES.some(axis=>point[axis]<0||point[axis]>1))return undefined;
 const normal={West:['x',false],East:['x',true],Down:['y',false],Up:['y',true],North:['z',false],South:['z',true]}[face];
 if(!normal)return undefined;
 const local={};for(const axis of AXES)local[axis]=location[axis]<0?1-point[axis]:point[axis];
 const [axis,high]=normal;local[axis]=(high?MAX:MIN)[axis];
 return inBox(local)?local:undefined;
}

/** Capture only the actual before-event rack target and current player ray.
 * Public InputInfo distinguishes direct touch from touch crosshair controls.
 * Unknown/unavailable input mode uses the independently validated eye ray.
 * Relative origin and direction can be included in opt-in QA without identity
 * or absolute player/block coordinates. No storage or permissions are changed. */
export function captureRackHit(player,block,face,eventPoint){
 const result={point:undefined,origin:null,direction:null,aimed:null,mode:null,source:'unavailable',reason:null};
 try{
  const location=block?.location;
  if(block?.typeId!==ADVANCED_RACK_BLOCK_ID||!vector(location)||!AXES.every(axis=>Number.isInteger(location[axis])))return {...result,reason:'invalid_rack_target'};
  if(typeof block.dimension?.id!=='string'||player?.dimension?.id!==block.dimension.id)return {...result,reason:'dimension_changed'};
  let directTouch=false;
  try{const input=player.inputInfo;result.mode=input?.lastInputModeUsed??null;directTouch=result.mode==='Touch'&&input?.touchOnlyAffectsHotbar===false;}catch{}
  try{
   const head=player.getHeadLocation(),direction=player.getViewDirection();
   if(vector(head))result.origin={x:head.x-location.x,y:head.y-location.y,z:head.z-location.z};
   if(vector(direction))result.direction=copy(direction);
   result.aimed=rackAimHit(result.origin,result.direction)??null;
  }catch{}
  if(directTouch){
   result.point=rackTouchHit(location,face,eventPoint);result.source='direct_touch';
   if(!result.point)result.reason='invalid_touch_hit';
  }else{
   result.point=result.aimed??undefined;result.source='eye_ray';
   if(!result.point)result.reason='missing_or_missed_ray';
  }
  return result;
 }catch{return {...result,point:undefined,reason:'hit_capture_failed'};}
}
