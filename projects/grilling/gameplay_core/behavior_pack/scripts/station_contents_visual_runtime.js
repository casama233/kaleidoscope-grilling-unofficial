/** Transient native equipped-item renderers. Helpers never own or deliver station contents. */
import {world,system,ItemStack} from '@minecraft/server';
import {STORAGE_PREFIX,peekStationContainer} from './family_station_storage.js';
import {a25ReadPlateBlock,a25RestoreStack} from './a25_plate_recipe_runtime.js';
import {readGrillState} from './a2740_grill_state_adapter.js';
import {grillVisualStage} from './grill_visual_core.js';
import {resolveSecretSmokedId} from './secret_compat_core.js';
const TYPE='kaleidoscope_grilling:equipment_visual',MAX=512,targets=new Map();
let reader,restore,cursor=0,helpers=0,lastWarning=-1200,indexing=false;
export function configureSecretVisuals(read,build){reader=read;restore=build;}
const key=b=>b.dimension.id+'|'+b.x+'|'+b.y+'|'+b.z;
export function rememberStationVisual(b){if(!b)return;const k=key(b);if(!targets.has(k))targets.set(k,{dimensionId:b.dimension.id,location:{...b.location},parts:new Map()});}
function warn(e){if(system.currentTick-lastWarning>1200){lastWarning=system.currentTick;console.warn('[Grilling contents display] '+e)}}
function discard(row,k){const old=row.parts.get(k);if(!old)return;try{if(old.entity.isValid)old.entity.remove();row.parts.delete(k);helpers--;}catch(e){warn(e)}}
function clear(row){for(const k of [...row.parts.keys()])discard(row,k);}
export function renderItemType(entity,stack){
 // Stable 2.9 exposes native equipment only on players. A renderer can set and
 // verify an item type with native commands; its copy is never a stored item.
 if(!/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(stack?.typeId??''))throw Error('render item identifier');
 entity.runCommand('replaceitem entity @s slot.weapon.mainhand 0 '+stack.typeId+' 1');
 entity.runCommand('testfor @s[hasitem={item='+stack.typeId+',location=slot.weapon.mainhand}]');
 return {typeId:stack.typeId,commandVerified:true};
}
function pose(block,dx,y,dz){const angle={north:0,east:90,south:180,west:270}[block.permutation.getState('minecraft:cardinal_direction')]??0,r=angle*Math.PI/180;return {location:{x:block.x+.5+dx*Math.cos(r)-dz*Math.sin(r),y:block.y+y,z:block.z+.5+dx*Math.sin(r)+dz*Math.cos(r)},angle};}
function render(row,b,k,stack,at,mode){
 let old=row.parts.get(k);if(!stack){discard(row,k);return;}
 if(old&&!old.entity.isValid){discard(row,k);old=undefined;}
 const signature=JSON.stringify({id:stack.typeId,lore:stack.getRawLore(),name:stack.nameTag,at,mode});if(old?.signature===signature)return;
 if(!old){if(helpers>=MAX)return;old={entity:b.dimension.spawnEntity(TYPE,at.location)};row.parts.set(k,old);helpers++;}
 try{old.entity.teleport(at.location,{dimension:b.dimension,rotation:{x:0,y:-at.angle}});old.entity.setProperty('kaleidoscope_grilling:pose',mode);renderItemType(old.entity,stack);old.signature=signature;}catch(e){discard(row,k);throw e;}
}
function composed(row,b,k,stack,at,cooked,seen){
 const ingredients=reader?.(stack)??[];
 for(let i=0;i<3;i++){
  const name=k+'/'+i;seen.add(name);let food;
  if(ingredients[i]){food=restore(ingredients[i]);if(cooked){const id=resolveSecretSmokedId(ingredients[i]);if(id&&id!==food.typeId)food=new ItemStack(id);}}
  const offset=pose(b,at.dx,at.y,at.dz+(i-1)*.15);render(row,b,name,food,offset,2);
 }
}
export function syncStationContentsVisual(block,observers){
 rememberStationVisual(block);const row=targets.get(key(block));
 if(!observers.some(p=>p.dimensionId===row.dimensionId&&Math.hypot(p.x-block.x,p.y-block.y,p.z-block.z)<=48)){clear(row);return;}
 const seen=new Set();
 if(block.typeId==='kaleidoscope_grilling:advanced_rack_block'){
  const c=peekStationContainer(block);
  for(let i=0;i<9;i++){const k='rack/'+i;seen.add(k);const upper=i<5,dx=upper?(i-2)*.14:(i-6.5)*.18;render(row,block,k,c?.getItem(i),pose(block,dx,upper?.61:.35,upper?-.12:-.27),0);}
 }else if(block.typeId==='kaleidoscope_grilling:skewer_plate_block'){
  const rows=a25ReadPlateBlock(block);
  for(let i=0;i<5;i++){const stack=rows[i]?a25RestoreStack(rows[i]):undefined,k='plate/'+i,dx=(i-2)*.14;
   if(stack?.typeId==='kaleidoscope_grilling:secret_skewer')composed(row,block,k,stack,{dx,y:.15,dz:0},false,seen);
   else{seen.add(k);render(row,block,k,stack,pose(block,dx,.15,0),1);}
  }
 }else if(block.typeId==='kaleidoscope_grilling:grill'){
  const c=peekStationContainer(block),state=readGrillState(block);
  for(let i=0;i<3;i++){const stack=c?.getItem(i);if(stack?.typeId==='kaleidoscope_grilling:secret_skewer')composed(row,block,'grill/'+i,stack,{dx:(i-1)*5/16,y:5/16+.025,dz:0},grillVisualStage(state)>=4,seen);}
 }else{clear(row);if(!row.parts.size)targets.delete(key(block));return;}
 for(const k of [...row.parts.keys()])if(!seen.has(k))discard(row,k);
}
function index(){if(indexing)return;indexing=true;system.runJob((function*(){try{for(const name of world.getDynamicPropertyIds()){
 let dimensionId,x,y,z;
 if(name.startsWith(STORAGE_PREFIX)){const p=name.slice(STORAGE_PREFIX.length).split('/');if(p.length===4)[dimensionId,x,y,z]=p;}
 else{const p=/^kaleidoscope_grilling:a25_plate_(minecraft_(?:overworld|nether|the_end))_([pm]\d+)_([pm]\d+)_([pm]\d+)$/.exec(name);if(p){dimensionId=p[1].replace('minecraft_', 'minecraft:');[x,y,z]=p.slice(2).map(n=>Number(n.slice(1))*(n[0]==='m'?-1:1));}}
 if(dimensionId&&[x,y,z].every(n=>Number.isSafeInteger(Number(n)))){const location={x:Number(x),y:Number(y),z:Number(z)},k=dimensionId+'|'+x+'|'+y+'|'+z;if(!targets.has(k))targets.set(k,{dimensionId,location,parts:new Map()});}yield;
 }}catch(e){warn(e)}finally{indexing=false}})());}
function pump(){const viewers=world.getAllPlayers().map(p=>({dimensionId:p.dimension.id,...p.location})),rows=[...targets.values()];
 for(let i=0;i<Math.min(8,rows.length);i++){const row=rows[cursor++%rows.length];try{const b=world.getDimension(row.dimensionId).getBlock(row.location);if(b)syncStationContentsVisual(b,viewers);else clear(row);}catch(e){clear(row);warn(e)}}
}
for(const name of ['playerPlaceBlock','playerInteractWithBlock','playerBreakBlock'])world.afterEvents[name].subscribe(e=>rememberStationVisual(e.block));
system.run(()=>{for(const dim of ['overworld','nether','the_end'])try{for(const e of world.getDimension(dim).getEntities({type:TYPE}))e.remove()}catch{};index();system.runInterval(pump,5);system.runInterval(index,400);});
export const contentsVisualHelperCount=()=>helpers;
