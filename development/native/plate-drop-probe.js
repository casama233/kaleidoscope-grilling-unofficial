/** Actual BDS drops/explosion, no player fixtures and no client acceptance. */
import {world,system,ItemStack} from '@minecraft/server';
import {a25ReadPlateBlock,a25PlateRows,plateStorageStep,plateTransaction,breakPlate} from './a25_plate_recipe_runtime.js';
import {captureSkewerMetadata,metadataSignature} from './skewer_item_snapshot.js';
import {setItemProperty,setItemLore} from './itemData.js';
const N='kaleidoscope_grilling:',phase=N+'qa_drop_phase',saved=N+'qa_drop_saved';
const check=(v,s)=>{if(!v)throw Error(s)},wait=t=>new Promise(r=>system.runTimeout(r,t));
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');try{d.runCommand('tickingarea add circle 128 80 64 2 drop_qa true')}catch{}
 let b;for(let i=0;i<60;i++){await wait(10);try{b=d.getBlock({x:128,y:80,z:64})}catch{}if(b)break;}check(b,'native QA chunk');
 const origin={x:128.5,y:80.5,z:64.5},items=()=>d.getEntities({type:'minecraft:item',location:origin,maxDistance:8});
 const stackOf=e=>e.getComponent('minecraft:item')?.itemStack;
 if(world.getDynamicProperty(phase)===undefined){
  const food=new ItemStack(N+'grilled_beef_skewer');food.nameTag='Packed native keepsake';setItemLore(food,[{rawtext:[{translate:'other:keepsake'},{text:' 原始資料'}]}]);setItemProperty(food,'qa:drop_marker','preserved');
  const row={id:food.typeId,native:captureSkewerMetadata(food),nutrition:4,saturation:.4},rows=Array.from({length:5},()=>row);
  b.below().setType('minecraft:stone');b.setType(N+'skewer_plate_block');check(plateTransaction(b,[plateStorageStep(b,rows)]),'fill native plate');
  check(breakPlate(b),'native break commit');check(b.typeId==='minecraft:air','native removed block');check(a25ReadPlateBlock(b).length===0,'native payload cleared');
  let drops=items().filter(e=>stackOf(e)?.typeId===N+'skewer_plate');check(drops.length===1,'one packed native item');
  check(metadataSignature(a25PlateRows(stackOf(drops[0])))===metadataSignature(rows),'all five native metadata rows packed');check(!breakPlate(b),'repeated break no-op');
  for(const e of items())e.remove();
  b.below().setType('minecraft:obsidian');b.setType(N+'skewer_plate_block');check(plateTransaction(b,[plateStorageStep(b,[row])]),'refill explosion plate');
  check(d.createExplosion(origin,4,{breaksBlocks:true,causesFire:false}),'actual native explosion');await wait(8);
  check(b.typeId==='minecraft:air','explosion routes plate through manual break');drops=items().filter(e=>stackOf(e)?.typeId===N+'skewer_plate');check(drops.length===1,'one packed explosion drop');
  check(metadataSignature(a25PlateRows(stackOf(drops[0])))===metadataSignature([row]),'explosion metadata preserved');check(a25ReadPlateBlock(b).length===0,'explosion clears payload');
  world.setDynamicProperty(saved,metadataSignature(a25PlateRows(stackOf(drops[0]))));world.setDynamicProperty(phase,1);
  console.log('DROP_NATIVE_PASS '+JSON.stringify({phase:'saved',normalBreak:true,fiveRowsPacked:true,repeatNoOp:true,realExplosion:true,oneExplosionDrop:true,metadataPreserved:true,realPlayers:world.getAllPlayers().length,simulatedPlayers:false,client:false}));
 }else{
  const drops=items().filter(e=>stackOf(e)?.typeId===N+'skewer_plate');check(drops.length===1,'one packed item survives restart');check(metadataSignature(a25PlateRows(stackOf(drops[0])))===world.getDynamicProperty(saved),'packed native metadata survives restart');check(b.typeId==='minecraft:air','removed block stays removed');
  console.log('DROP_NATIVE_PASS '+JSON.stringify({phase:'restored',onePackedDropPersisted:true,metadataPersisted:true,blockStaysRemoved:true,realPlayers:world.getAllPlayers().length,simulatedPlayers:false,client:false}));
 }
}catch(e){console.error('DROP_NATIVE_FAIL '+e+' '+e.stack)}},100);
