/** Independent BDS only. Real native storage; zero players, no client claim. */
import {world,system,ItemStack} from '@minecraft/server';
import {stationContainer,peekStationContainer} from './family_station_storage.js';
import {captureSkewerMetadata,metadataSignature} from './skewer_item_snapshot.js';
import {setItemProperty,setItemLore} from './itemData.js';
import {a25ReadPlateBlock,plateStorageStep,plateHandStep,plateTransaction,posKey} from './a25_plate_recipe_runtime.js';
const N='kaleidoscope_grilling:',phase=N+'qa_plate_phase',saved=N+'qa_plate_saved';
const wait=t=>new Promise(r=>system.runTimeout(r,t));
const check=(v,s)=>{if(!v)throw Error(s)};
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');try{d.runCommand('tickingarea add circle 112 80 64 2 plate_qa true')}catch{}
 let b;for(let i=0;i<60;i++){await wait(10);try{b=d.getBlock({x:112,y:80,z:64})}catch{}if(b)break;}check(b,'QA chunk unavailable');
 const carrier=d.getBlock({x:115,y:80,z:64});check(carrier,'native storage block');
 if(world.getDynamicProperty(phase)===undefined){
  b.below().setType('minecraft:stone');b.setType(N+'skewer_plate_block');carrier.below().setType('minecraft:stone');carrier.setType(N+'advanced_rack_block');
  const c=stationContainer(carrier),s=new ItemStack(N+'grilled_beef_skewer',3);s.nameTag='Native preserved food';
  setItemLore(s,[{rawtext:[{translate:'other:keepsake'},{text:' 保留'}]}]);setItemProperty(s,'qa:plate_marker','native metadata');c.setItem(0,s);
  const original=metadataSignature({amount:s.amount,...captureSkewerMetadata(s)}),row={id:s.typeId,native:captureSkewerMetadata(s),nutrition:4,saturation:.4};
  const key=posKey(N+'a25_plate_',b),before=c.getItem(0)?.clone(),after=before.clone();after.amount--;
  let once=true;const captured={before,read:()=>c.getItem(0),write(value){c.setItem(0,value);if(once){once=false;throw Error('QA native post-write rejection')}}};
  check(!plateTransaction(b,[plateStorageStep(b,[row]),plateHandStep(captured,after)]),'native post-write failure rolls back');
  check(world.getDynamicProperty(key)===undefined,'exact absence restored');check(b.permutation.getState(N+'plate_count')===0,'count restored');
  check(metadataSignature({amount:c.getItem(0).amount,...captureSkewerMetadata(c.getItem(0))})===original,'native source metadata restored');
  const success={before:c.getItem(0).clone(),read:()=>c.getItem(0),write:value=>c.setItem(0,value)};
  check(plateTransaction(b,[plateStorageStep(b,[row]),plateHandStep(success,after)]),'native transfer commit');check(c.getItem(0).amount===2,'source count debited once');
  const directions=[];for(const direction of ['south','west','north','east']){b.setPermutation(b.permutation.withState('minecraft:cardinal_direction',direction));check(b.permutation.getState('minecraft:cardinal_direction')===direction,'native direction '+direction);directions.push(direction)}
  b.setPermutation(b.permutation.withState('minecraft:cardinal_direction','west'));
  const valid=world.getDynamicProperty(key);world.setDynamicProperty(key,'broken JSON');let rejected=false;try{a25ReadPlateBlock(b)}catch{rejected=true}check(rejected,'damaged native data rejected');check(world.getDynamicProperty(key)==='broken JSON','damaged payload untouched');world.setDynamicProperty(key,valid);
  world.setDynamicProperty(saved,JSON.stringify({rows:a25ReadPlateBlock(b),source:{amount:c.getItem(0).amount,...captureSkewerMetadata(c.getItem(0))}}));world.setDynamicProperty(phase,1);
  console.log('PLATE_NATIVE_PASS '+JSON.stringify({phase:'saved',directions,rollback:true,rawAbsenceRestored:true,metadataPreserved:true,invalidDataRejected:true,nativeSourceCount:2,client:false,realPlayers:world.getAllPlayers().length,simulatedPlayers:false}));
 }else{
  const c=peekStationContainer(carrier);check(c,'restored native carrier');
  const actual={rows:a25ReadPlateBlock(b),source:{amount:c.getItem(0).amount,...captureSkewerMetadata(c.getItem(0))}};
  check(metadataSignature(actual)===metadataSignature(JSON.parse(world.getDynamicProperty(saved))),'actual contents survived restart');check(b.permutation.getState('minecraft:cardinal_direction')==='west','saved direction preserved');check(b.permutation.getState(N+'plate_count')===1,'saved count preserved');
  console.log('PLATE_NATIVE_PASS '+JSON.stringify({phase:'restored',nativeMetadataPersisted:true,directionPreserved:true,countPreserved:true,client:false,realPlayers:world.getAllPlayers().length,simulatedPlayers:false}));
 }
}catch(e){console.error('PLATE_NATIVE_FAIL '+e+' '+e.stack)}},100);
