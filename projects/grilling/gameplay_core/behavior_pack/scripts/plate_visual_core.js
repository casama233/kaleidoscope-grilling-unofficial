import {canonicalFoodId} from './eating_profile_ids.js';
import {RAW_TO_COOKED} from './data.js';
import {GRILL_MODEL_INDEX} from './grill_visual_data.js';
export const PLATE_FOOD_VISUAL_TYPE='kaleidoscope_grilling:plate_food_visual';
// Original 1.1.1 SkewerPlateRenderer, not evenly spaced native item icons.
export const PLATE_VISUAL_LAYOUTS=Object.freeze([
 [],[[8,4,6.3,0]],[[5.6,4.15,5.95,0],[10.4,4.2,5.9,0]],
 [[5.6,3.95,6.35,0],[10.4,4,6.3,0],[8,7.375,7.65,-22.5]],
 [[8,3.95,6.35,0],[12.55,4,6.3,0],[3.45,4,6.3,0],[8,7.325,7.7,-45]],
 [[8,3.95,6.35,0],[12.55,4,6.3,0],[3.45,4,6.3,0],[10.4,7.325,7.4,-22.5],[5.7,7.375,7.35,-22.5]]
].map(rows=>Object.freeze(rows.map(row=>Object.freeze(row)))));
const COOKED_TO_RAW=Object.freeze(Object.fromEntries(Object.entries(RAW_TO_COOKED).map(([raw,cooked])=>[cooked,raw])));
export function plateVisualPlan(stack){
 const id=canonicalFoodId(stack?.typeId);
 if(id==='kaleidoscope_grilling:ordinary_skewer')return {model:115,secret:false};
 if(id==='kaleidoscope_grilling:secret_skewer')return {model:114,secret:true};
 const raw=COOKED_TO_RAW[id]??id,index=Object.hasOwn(GRILL_MODEL_INDEX,raw??'')?GRILL_MODEL_INDEX[raw]:undefined;
 return index===undefined?undefined:{model:index*6+(COOKED_TO_RAW[id]?4:0),secret:false};
}
export function plateVisualPose(block,slot,count){
 const layout=PLATE_VISUAL_LAYOUTS[Math.max(0,Math.min(5,Math.floor(count)))],cell=layout?.[slot];
 if(!cell)return undefined;
 const angle={south:0,west:90,north:180,east:270}[block.permutation.getState('minecraft:cardinal_direction')]??0,r=angle*Math.PI/180;
 // Actor locations are world coordinates. The existing geometry's model-X
 // basis conversion does not reflect the Java slot's world translation.
 const dx=cell[0]/16-.5,dz=cell[2]/16-.5;
 // The native mesh basis flips Z after source-to-mesh X conversion. Matching
 // Java Ry(slotYaw-facing) needs native yaw180+facing-slotYaw, normalized here.
 const nativeYaw=(angle-cell[3]+360)%360-180;
 return {location:{x:block.x+.5+dx*Math.cos(r)-dz*Math.sin(r),y:block.y+cell[1]/16,z:block.z+.5+dx*Math.sin(r)+dz*Math.cos(r)},angle:nativeYaw?-nativeYaw:0};
}
