import {PROJECTILE_DODGE_VANILLA_BLOCK_IDS,PROJECTILE_DODGE_FLUID_CARRIER_IDS} from './projectile_dodge_liquid_catalog.js';

// Portable work limit, not a Java restriction. Larger native boxes are explicitly
// unsupported; never truncate their cell enumeration and report them dry.
export const PROJECTILE_DODGE_LIQUID_MAX_CELLS=4096;
const vanillaBlocks=new Set(PROJECTILE_DODGE_VANILLA_BLOCK_IDS);
const fluidCarriers=new Set(PROJECTILE_DODGE_FLUID_CARRIER_IDS);
const axes=['x','y','z'];
const finiteVector=point=>point&&axes.every(axis=>typeof point[axis]==='number'&&Number.isFinite(point[axis]));
const unsupported=reason=>({supported:false,reason});

// Native AABB extents are half sizes. Preserve its actual offset from the actor
// position; do not manufacture a feet/head box or a fixed player body.
export function projectileDodgeLiquidCellPlan(actorPosition,nativeBox,candidate,{maxCells=PROJECTILE_DODGE_LIQUID_MAX_CELLS}={}){
 if(!finiteVector(actorPosition)||!finiteVector(candidate)||!finiteVector(nativeBox?.center)||!finiteVector(nativeBox?.extent)||
    axes.some(axis=>nativeBox.extent[axis]<=0))return unsupported('collision_bounds_invalid');
 if(!Number.isSafeInteger(maxCells)||maxCells<1||maxCells>PROJECTILE_DODGE_LIQUID_MAX_CELLS)return unsupported('work_budget_invalid');
 const min={},max={},size={};let cellCount=1;
 for(const axis of axes){
  const center=nativeBox.center[axis]+(candidate[axis]-actorPosition[axis]);
  const low=center-nativeBox.extent[axis],high=center+nativeBox.extent[axis];
  if(!Number.isFinite(center)||!Number.isFinite(low)||!Number.isFinite(high)||!(high>low))return unsupported('collision_bounds_invalid');
  min[axis]=Math.floor(low);max[axis]=Math.ceil(high);size[axis]=max[axis]-min[axis];
  if(!Number.isSafeInteger(min[axis])||!Number.isSafeInteger(max[axis])||!Number.isSafeInteger(size[axis])||size[axis]<1)return unsupported('collision_bounds_invalid');
  cellCount*=size[axis];
  if(!Number.isSafeInteger(cellCount)||cellCount>maxCells)return unsupported('collision_bounds_work_budget_exceeded');
 }
 return {supported:true,reason:'',min,max,size,cellCount};
}

// A documented positive native presence flag is sufficient to reject the cell.
// False flags are accepted as dry only within the pinned official vanilla
// registry and outside the source-reviewed water/lava carrier mapping.
export function classifyProjectileDodgeLiquidCell({typeId,isLiquid,isWaterlogged}={}){
 if(isLiquid===true)return {supported:true,liquid:true,reason:'native_liquid'};
 if(isWaterlogged===true)return {supported:true,liquid:true,reason:'native_waterlogged'};
 if(typeof typeId!=='string'||!typeId)return unsupported('block_type_unavailable');
 if(fluidCarriers.has(typeId))return {supported:true,liquid:true,reason:'source_fluid_carrier'};
 if(!vanillaBlocks.has(typeId))return unsupported('block_type_unsupported');
 if(isLiquid!==false||isWaterlogged!==false)return unsupported('native_fluid_presence_unavailable');
 return {supported:true,liquid:false,reason:'native_vanilla_dry'};
}
