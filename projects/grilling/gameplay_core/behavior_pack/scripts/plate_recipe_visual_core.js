import {RAW_TO_COOKED} from './data.js';
import {canonicalFoodId} from './eating_profile_ids.js';
import {GRILL_MODEL_INDEX} from './grill_visual_data.js';
import {secretVisualState} from './secret_visual_state.js';

export const PLATE_FOOD_VISUAL_TYPE='kaleidoscope_grilling:plate_food_visual';
export const RECIPE_ICON_VISUAL_TYPE='kaleidoscope_grilling:recipe_icon_visual';
const SECRET='kaleidoscope_grilling:secret_skewer';
const COOKED_TO_RAW=Object.freeze(Object.fromEntries(Object.entries(RAW_TO_COOKED).map(([raw,cooked])=>[cooked,raw])));
// Existing Java GUI-16 textures, ordered by the audited grill model index.
export const RECIPE_ICON_MODELS=Object.freeze(Object.fromEntries([
 ...Object.entries(GRILL_MODEL_INDEX).flatMap(([raw,index])=>[[raw,index*2],[RAW_TO_COOKED[raw],index*2+1]]),
 ['kaleidoscope_grilling:ordinary_skewer',38]
]));
export function recipeIconModel(stack){
 const id=canonicalFoodId(stack?.typeId);return Object.hasOwn(RECIPE_ICON_MODELS,id)?RECIPE_ICON_MODELS[id]:undefined;
}
export function recipeAnimationFrame(tick){return Number.isFinite(tick)&&tick>=0?Math.floor(tick/4)%5:0;}
export function plateMeshPlan(stack,readIngredients){
 const id=canonicalFoodId(stack?.typeId);
 if(id===SECRET)return {model:114,secret:secretVisualState(stack,readIngredients)};
 const raw=COOKED_TO_RAW[id]??id,index=GRILL_MODEL_INDEX[raw];
 return index===undefined?undefined:{model:index*6+(raw===id?0:4),secret:[0,0,0]};
}

// Java 1.1.1 SkewerPlateRenderer.LAYOUTS, in authored model units (x,y,z,yaw).
// FIXED rotation is cancelled by the plate renderer; .8 * 1.5 leaves scale 1.2.
export const PLATE_LAYOUTS=Object.freeze([
 [],
 [[8,4,6.3,0]],
 [[5.6,4.15,5.95,0],[10.4,4.2,5.9,0]],
 [[5.6,3.95,6.35,0],[10.4,4,6.3,0],[8,7.375,7.65,-22.5]],
 [[8,3.95,6.35,0],[12.55,4,6.3,0],[3.45,4,6.3,0],[8,7.325,7.7,-45]],
 [[8,3.95,6.35,0],[12.55,4,6.3,0],[3.45,4,6.3,0],[10.4,7.325,7.4,-22.5],[5.7,7.375,7.35,-22.5]]
].map(rows=>Object.freeze(rows.map(row=>Object.freeze(row)))));
const SOURCE_FACING={south:0,west:90,north:180,east:270};
function sourcePose(block,x,y,z,yaw=0){
 const angle=SOURCE_FACING[block.permutation.getState('minecraft:cardinal_direction')];
 if(angle===undefined)return undefined;
 const r=angle*Math.PI/180,dx=x-.5,dz=z-.5;
 return {location:{x:block.x+.5+dx*Math.cos(r)-dz*Math.sin(r),y:block.y+y,z:block.z+.5+dx*Math.sin(r)+dz*Math.cos(r)},angle:angle-yaw};
}
export function plateSlotPose(block,count,index){
 const rows=PLATE_LAYOUTS[Math.max(0,Math.min(5,Number.isFinite(count)?Math.floor(count):0))],slot=rows[index];
 return slot?sourcePose(block,slot[0]/16,slot[1]/16,slot[2]/16,slot[3]):undefined;
}
export function recipeIconPose(block){return sourcePose(block,.5,.625,.3/16);}
// The Java fallback applies the page translation after a .5 scale.
export function recipeMeshPose(block){return sourcePose(block,.5,.625,.15/16);}
