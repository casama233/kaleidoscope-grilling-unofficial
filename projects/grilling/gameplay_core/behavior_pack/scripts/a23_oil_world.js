import {world,system,ItemStack,EquipmentSlot,GameMode,BlockPermutation} from '@minecraft/server';
import {OIL_BUCKET_POINTS} from './a24_skewering_core.js';
import {COOKERY_EMPTY_ID as COOKERY_EMPTY,COOKERY_FILLED_ID as COOKERY_FILLED,planCookeryTypedOilAddition} from './a2734_cookery_oil_pot_adapter.js';

const REG='kaleidoscope_grilling:a23_oil_sources';
export const OIL_TYPES=Object.freeze({
 canola:{block:'kaleidoscope_grilling:canola_oil',bucket:'kaleidoscope_grilling:canola_oil_bucket',interval:6},
 secret_chili:{block:'kaleidoscope_grilling:secret_chili_oil',bucket:'kaleidoscope_grilling:secret_chili_oil_bucket',interval:8},
 premium_chili:{block:'kaleidoscope_grilling:premium_chili_oil',bucket:'kaleidoscope_grilling:premium_chili_oil_bucket',interval:10}
});
const BLOCK_TO_TYPE=Object.freeze(Object.fromEntries(Object.entries(OIL_TYPES).map(([k,v])=>[v.block,k])));
const BUCKET_TO_TYPE=Object.freeze(Object.fromEntries(Object.entries(OIL_TYPES).map(([k,v])=>[v.bucket,k])));
const OFFSETS={Up:[0,1,0],Down:[0,-1,0],East:[1,0,0],West:[-1,0,0],North:[0,0,1],South:[0,0,-1]};
const HORIZ=[[1,0,0],[-1,0,0],[0,0,1],[0,0,-1]];
const MAX_SOURCES=64,MAX_CELLS=160,MAX_DROP=16;

function enc(n){return n<0?'m'+Math.abs(n):'p'+n}
function posKey(d,x,y,z){return d+'|'+x+'|'+y+'|'+z}
function readReg(){try{const raw=world.getDynamicProperty(REG);return typeof raw==='string'?JSON.parse(raw):[]}catch{return []}}
function saveReg(rows){world.setDynamicProperty(REG,JSON.stringify(rows.slice(0,MAX_SOURCES)))}
function isOil(id){return Object.hasOwn(BLOCK_TO_TYPE,id)}
function level(block){try{return Number(block.permutation.getState('kaleidoscope_grilling:level')??0)}catch{return 0}}
function setOil(block,type,lvl){
 const def=OIL_TYPES[type];if(!def)return false;
 try{block.setPermutation(BlockPermutation.resolve(def.block,{'kaleidoscope_grilling:level':Math.max(0,Math.min(7,lvl|0))}));return true}catch{return false}
}
function canFlowInto(block,type,source=false){
 if(!block)return false;if(block.typeId==='minecraft:air')return true;
 if(block.typeId===OIL_TYPES[type].block)return !source||level(block)>0;
 return false;
}
function playerContainer(p){return p.getComponent('minecraft:inventory')?.container}
function main(p){return playerContainer(p)?.getItem(p.selectedSlotIndex)}
function off(p){return p.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function findHand(p,id){const m=main(p);if(m?.typeId===id)return 'main';const o=off(p);if(o?.typeId===id)return 'off';return null}
function setHand(p,hand,stack){if(hand==='off')return p.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack);return playerContainer(p)?.setItem(p.selectedSlotIndex,stack)}
function creative(p){try{return p.getGameMode()===GameMode.Creative}catch{return false}}
function addItem(p,stack){const c=playerContainer(p);if(!c)return;const rem=c.addItem(stack);if(rem)p.dimension.spawnItem(rem,p.location)}
function sourceRow(dim,loc,type){return {k:posKey(dim.id,loc.x,loc.y,loc.z),d:dim.id,x:loc.x,y:loc.y,z:loc.z,type,cells:[]}}
function registerSource(dim,loc,type){
 const rows=readReg(),k=posKey(dim.id,loc.x,loc.y,loc.z),found=rows.find(r=>r.k===k);
 if(found){found.type=type;saveReg(rows);return}
 if(rows.length>=MAX_SOURCES)return;rows.push(sourceRow(dim,loc,type));saveReg(rows)
}
function sourceKeys(rows){return new Set(rows.map(r=>r.k))}
function claimedByOther(rows,row,cell){return rows.some(r=>r!==row&&Array.isArray(r.cells)&&r.cells.includes(cell))}
function clearCells(row,rows){
 let dim;try{dim=world.getDimension(row.d)}catch{return}
 const sources=sourceKeys(rows);
 for(const cell of row.cells??[]){
  if(sources.has(cell)||claimedByOther(rows,row,cell))continue;
  const [,xs,ys,zs]=cell.split('|');const b=dim.getBlock({x:Number(xs),y:Number(ys),z:Number(zs)});
  if(b&&b.typeId===OIL_TYPES[row.type]?.block)try{b.setType('minecraft:air')}catch{}
 }
}
function compute(row,rows){
 const def=OIL_TYPES[row.type];if(!def)return false;
 let dim;try{dim=world.getDimension(row.d)}catch{return false}
 const source=dim.getBlock({x:row.x,y:row.y,z:row.z});
 if(!source||source.typeId!==def.block||level(source)!==0){clearCells(row,rows);return false}
 const queue=[{x:row.x,y:row.y,z:row.z,l:0,drop:0}],seen=new Map(),desired=new Map();
 while(queue.length&&desired.size<MAX_CELLS){
  const n=queue.shift(),k=posKey(row.d,n.x,n.y,n.z);
  const old=seen.get(k);if(old!==undefined&&old<=n.l)continue;seen.set(k,n.l);
  const b=dim.getBlock({x:n.x,y:n.y,z:n.z});if(!b||(!canFlowInto(b,row.type)&&k!==row.k))continue;
  desired.set(k,{...n});
  const below=dim.getBlock({x:n.x,y:n.y-1,z:n.z});
  if(n.drop<MAX_DROP&&canFlowInto(below,row.type)){
   queue.push({x:n.x,y:n.y-1,z:n.z,l:n.l,drop:n.drop+1});continue;
  }
  if(n.l>=7)continue;
  for(const [dx,dy,dz] of HORIZ)queue.push({x:n.x+dx,y:n.y,z:n.z+dz,l:n.l+1,drop:n.drop});
 }
 const desiredKeys=new Set(desired.keys()),sourceSet=sourceKeys(rows);
 for(const [k,n] of desired){
  if(k===row.k)continue;const b=dim.getBlock({x:n.x,y:n.y,z:n.z});if(b&&(b.typeId==='minecraft:air'||b.typeId===def.block))setOil(b,row.type,n.l);
 }
 for(const cell of row.cells??[]){
  if(desiredKeys.has(cell)||sourceSet.has(cell)||claimedByOther(rows,row,cell))continue;
  const [,xs,ys,zs]=cell.split('|');const b=dim.getBlock({x:Number(xs),y:Number(ys),z:Number(zs)});
  if(b&&b.typeId===def.block&&level(b)>0)try{b.setType('minecraft:air')}catch{}
 }
 row.cells=[...desiredKeys].filter(k=>k!==row.k);return true;
}
function faceTarget(e){const o=OFFSETS[e.blockFace]??[0,1,0],p=e.block.location;return {x:p.x+o[0],y:p.y+o[1],z:p.z+o[2]}}
function placeFromBucket(player,dim,loc,type,hand){
 const b=dim.getBlock(loc);if(!b||!(b.typeId==='minecraft:air'||isOil(b.typeId)))return false;
 if(!setOil(b,type,0))return false;registerSource(dim,loc,type);
 if(!creative(player))setHand(player,hand,new ItemStack('minecraft:bucket',1));return true;
}
function takeSource(player,block,type,hand,toCookery=false){
 if(level(block)!==0)return false;
 const held=hand==='off'?off(player):main(player);
 let nextPot;
 if(toCookery){
  const plan=planCookeryTypedOilAddition(held,type,OIL_BUCKET_POINTS);
  if(!plan.ok)return false;
  nextPot=plan.next;
 }
 const rows=readReg(),k=posKey(block.dimension.id,block.x,block.y,block.z),row=rows.find(r=>r.k===k);
 try{block.setType('minecraft:air')}catch{return false}
 if(row){clearCells(row,rows);saveReg(rows.filter(r=>r!==row))}
 if(toCookery)setHand(player,hand,nextPot);else setHand(player,hand,new ItemStack(OIL_TYPES[type].bucket,1));
 return true;
}
world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 if(e.block.typeId==='kaleidoscope_grilling:big_vat')return;
 const item=e.itemStack,typeFromBlock=BLOCK_TO_TYPE[e.block.typeId],bucketType=item?BUCKET_TO_TYPE[item.typeId]:undefined;
 if(typeFromBlock&&(item?.typeId==='minecraft:bucket'||item?.typeId===COOKERY_EMPTY||item?.typeId===COOKERY_FILLED)){
  e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension,hand=findHand(p,item.typeId);
  system.run(()=>{const b=dim.getBlock(loc);if(b&&hand)takeSource(p,b,typeFromBlock,hand,item.typeId!== 'minecraft:bucket')});return;
 }
 if(bucketType){
  e.cancel=true;const p=e.player,loc=faceTarget(e),dim=e.block.dimension,hand=findHand(p,item.typeId);
  system.run(()=>{if(hand)placeFromBucket(p,dim,loc,bucketType,hand)});return;
 }
});
world.beforeEvents.playerBreakBlock.subscribe(e=>{
 if(!isOil(e.block.typeId))return;e.cancel=true;const dim=e.block.dimension,loc={...e.block.location};
 system.run(()=>{const b=dim.getBlock(loc);if(b&&isOil(b.typeId))try{b.setType('minecraft:air')}catch{}});
});
system.runInterval(()=>{
 const rows=readReg(),keep=[];
 for(const row of rows){
  const def=OIL_TYPES[row.type];if(!def)continue;
  if(system.currentTick%def.interval!==0){keep.push(row);continue}
  if(compute(row,rows))keep.push(row);
 }
 if(JSON.stringify(keep)!==JSON.stringify(rows))saveReg(keep);else saveReg(rows);
},1);
