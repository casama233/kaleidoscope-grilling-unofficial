import {advancedRackToolVisuals} from './advanced_rack_visual_core.js';
import {rackDisplayPose} from './advanced_rack_layout.js';
import {syncRackDisplay} from './a2746_rack_state_adapter.js';
import {canonicalFoodId} from './eating_profile_ids.js';
import {stationProjection,registerStationProjection} from './station_projection_core.js';
import {readPublicFood} from './host_api/food_api_core.js';
import {captureSkewerMetadata,metadataSignature} from './skewer_item_snapshot.js';
export {registerStationProjection};
import {VisualTargetQueue} from './visual_target_queue.js';
import {grillingConfig} from './server_config_runtime.js';
/** Transient native equipped-item renderers. Helpers never own or deliver station contents. */
import {world,system} from '@minecraft/server';
import {STORAGE_PREFIX,peekStationContainer} from './family_station_storage.js';
import {a25ReadPlateBlock,a25RestoreStack} from './a25_plate_recipe_runtime.js';
const TYPE='kaleidoscope_grilling:equipment_visual',work=new VisualTargetQueue(),targets=work.targets;
let reader,restore,helpers=0,lastWarning=-1200,indexing=false,lastCapacityWarning=-1200,lastAudience=-10;
export function configureSecretVisuals(read,build){reader=read;restore=build;}
const key=b=>b.dimension.id+'|'+b.x+'|'+b.y+'|'+b.z;
export function rememberStationVisual(b){if(!b)return;const k=key(b);if(!targets.has(k))work.add(k,{dimensionId:b.dimension.id,location:{...b.location},parts:new Map()});}
function warn(e){if(system.currentTick-lastWarning>1200){lastWarning=system.currentTick;console.warn('[Grilling contents display] '+e)}}
function discard(row,k){const old=row.parts.get(k);if(!old)return;try{if(old.entity.isValid)old.entity.remove();row.parts.delete(k);helpers--;}catch(e){warn(e)}}
function clear(row){for(const k of [...row.parts.keys()])discard(row,k);}
export function renderItemType(entity,stack){
 // Stable 2.9 exposes native equipment only on players. A renderer can set and
 // verify an item type with native commands; its copy is never a stored item.
 if(!/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(stack?.typeId??''))throw Error('render item identifier');
 const portable=readPublicFood(stack);if(portable.present&&!portable.valid)throw Error('Unreadable public projection metadata');
 const plan=stationProjection(stack,portable.valid?portable.state:undefined);
 entity.runCommand('replaceitem entity @s slot.weapon.mainhand 0 '+stack.typeId+' 1 '+plan.data);
 entity.runCommand('testfor @s[hasitem={item='+stack.typeId+',location=slot.weapon.mainhand,data='+plan.data+'}]');
 return {typeId:stack.typeId,data:plan.data,commandVerified:true};
}
function pose(block,dx,y,dz){const angle={north:0,east:90,south:180,west:270}[block.permutation.getState('minecraft:cardinal_direction')]??0,r=angle*Math.PI/180;return {location:{x:block.x+.5+dx*Math.cos(r)-dz*Math.sin(r),y:block.y+y,z:block.z+.5+dx*Math.sin(r)+dz*Math.cos(r)},angle};}
function render(row,b,k,stack,at,mode){
 let old=row.parts.get(k);if(!stack){discard(row,k);return;}
 if(old&&!old.entity.isValid){discard(row,k);old=undefined;}
 const signature=JSON.stringify({item:metadataSignature(captureSkewerMetadata(stack)),at,mode});if(old?.signature===signature)return;
 if(!old){if(helpers>=grillingConfig().contentsHelpers){if(system.currentTick-lastCapacityWarning>=1200){lastCapacityWarning=system.currentTick;console.warn("[Grilling contents capacity] render budget="+grillingConfig().contentsHelpers+"; storage unaffected; configure contentsHelpers after workload validation")}return;}old={entity:b.dimension.spawnEntity(TYPE,at.location)};row.parts.set(k,old);helpers++;}
 try{old.entity.teleport(at.location,{dimension:b.dimension,rotation:{x:0,y:-at.angle}});old.entity.setProperty('kaleidoscope_grilling:pose',mode);renderItemType(old.entity,stack);old.signature=signature;}catch(e){discard(row,k);throw e;}
}
function composed(row,b,k,stack,at,cooked,seen){
 const ingredients=reader?.(stack,cooked)??[];
 for(let i=0;i<3;i++){
  const name=k+'/'+i;seen.add(name);let food;
  if(ingredients[i])food=restore(ingredients[i]);
  const offset=pose(b,at.dx,at.y,at.dz+(i-1)*.15);render(row,b,name,food,offset,2);
 }
}
export function syncStationContentsVisual(block,observers){
 rememberStationVisual(block);const row=targets.get(key(block));
 if(!observers.some(p=>p.dimensionId===row.dimensionId&&Math.hypot(p.x-block.x,p.y-block.y,p.z-block.z)<=48)){clear(row);return;}
 const seen=new Set();
 if(block.typeId==='kaleidoscope_grilling:advanced_rack_block'){
  const c=peekStationContainer(block);
  // Rebuild only derived display state for old saved racks when discovered.
  // Native contents, filters and ownership remain authoritative and unchanged.
  if(c)syncRackDisplay(block,Array.from({length:9},(_,i)=>c.getItem(i)));
  // Five occupied shelf jars are block bones; all four tools have fixed hooks.
  // Keep native equipped-item Y/Z/pose pending rendered-client calibration.
  for(const {slot,stack,x} of advancedRackToolVisuals(i=>c?.getItem(i))){
   const k='rack/'+slot;seen.add(k);render(row,block,k,stack,rackDisplayPose(block,x,.35,-.27),0);
  }
 }else if(block.typeId==='kaleidoscope_grilling:skewer_plate_block'){
  const rows=a25ReadPlateBlock(block);
  for(let i=0;i<5;i++){const stack=rows[i]?a25RestoreStack(rows[i]):undefined,k='plate/'+i,dx=(i-2)*.14;
   if(canonicalFoodId(stack?.typeId)==='kaleidoscope_grilling:secret_skewer')composed(row,block,k,stack,{dx,y:.15,dz:0},undefined,seen);
   else{seen.add(k);render(row,block,k,stack,pose(block,dx,.15,0),1);}
  }
 }else if(block.typeId==='kaleidoscope_grilling:grill'){
  // Personalized grill meshes belong to grill_visual_runtime; clear old icon parts.
 }else{clear(row);if(!row.parts.size)work.remove(key(block));return;}
 for(const k of [...row.parts.keys()])if(!seen.has(k))discard(row,k);
}
function index(){if(indexing)return;indexing=true;system.runJob((function*(){try{for(const name of world.getDynamicPropertyIds()){
 let dimensionId,x,y,z;
 if(name.startsWith(STORAGE_PREFIX)){const p=name.slice(STORAGE_PREFIX.length).split('/');if(p.length===4)[dimensionId,x,y,z]=p;}
 else{const p=/^kaleidoscope_grilling:a25_plate_(minecraft_(?:overworld|nether|the_end))_([pm]\d+)_([pm]\d+)_([pm]\d+)$/.exec(name);if(p){dimensionId=p[1].replace('minecraft_', 'minecraft:');[x,y,z]=p.slice(2).map(n=>Number(n.slice(1))*(n[0]==='m'?-1:1));}}
 if(dimensionId&&[x,y,z].every(n=>Number.isSafeInteger(Number(n)))){const location={x:Number(x),y:Number(y),z:Number(z)},k=dimensionId+'|'+x+'|'+y+'|'+z;if(!targets.has(k))work.add(k,{dimensionId,location,parts:new Map()});}yield;
 }}catch(e){warn(e)}finally{indexing=false}})());}
export function markStationContentsDirty(block){rememberStationVisual(block);if(block)work.mark(key(block));}
function pump(){
 const viewers=world.getAllPlayers().map(p=>({dimensionId:p.dimension.id,...p.location}));if(system.currentTick-lastAudience>=10){lastAudience=system.currentTick;work.observe(viewers)};
 for(const k of work.take(grillingConfig().contentsTargetsPerTick)){
  const row=targets.get(k);if(!row)continue;
  try{if(!work.visible.has(k)){clear(row);continue;}const b=world.getDimension(row.dimensionId).getBlock(row.location);if(b)syncStationContentsVisual(b,viewers);else clear(row);}catch(e){clear(row);warn(e)}
 }
}
for(const name of ['playerPlaceBlock','playerInteractWithBlock','playerBreakBlock'])world.afterEvents[name].subscribe(e=>markStationContentsDirty(e.block));
// Script transactions cancel native interaction events, so enqueue their post-commit state too.
world.beforeEvents.playerInteractWithBlock.subscribe(e=>{if(['kaleidoscope_grilling:grill','kaleidoscope_grilling:advanced_rack_block','kaleidoscope_grilling:skewer_plate_block'].includes(e.block.typeId)){const d=e.block.dimension,l={...e.block.location};system.run(()=>{try{markStationContentsDirty(d.getBlock(l))}catch{}})}});
system.run(()=>{for(const dim of ['overworld','nether','the_end'])try{for(const e of world.getDimension(dim).getEntities({type:TYPE}))e.remove()}catch{};index();system.runInterval(pump,1);system.runInterval(index,400);});
export const contentsVisualHelperCount=()=>helpers;
