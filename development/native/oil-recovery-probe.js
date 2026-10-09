/** Real ContainerSlots and world persistence; injected storage failures, no players. */
import {world,system,ItemStack} from '@minecraft/server';
import {consumeSharedOilSlot,commitSharedStationOil} from './api/oil_api_host.js';
import {createPublicOilPot,readPublicOil} from './api/oil_api_core.js';
const PHASE='qa:oil_recovery38_phase',OWNER='qa-oil38-unresolved',key=id=>'senluo:oil_hand_fault:'+id;
const check=(v,s)=>{if(!v)throw Error(s)},wait=t=>new Promise(r=>system.runTimeout(r,t));
const count=s=>readPublicOil(s.getItem()).state.count;
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');try{d.runCommand('tickingarea add circle 160 80 64 2 oil_recovery_qa true')}catch{}
 let b;for(let i=0;i<60;i++){await wait(10);try{b=d.getBlock({x:160,y:80,z:64})}catch{}if(b)break}check(b,'QA chunk');
 if(world.getDynamicProperty(PHASE)===undefined){
  b.setType('minecraft:chest');const inventory=b.getComponent('minecraft:inventory').container;
  const make=(type,n)=>{const s=createPublicOilPot(ItemStack,type,n);s.setDynamicProperty('qa:keepsake','preserved');return s};
  const normal=inventory.getSlot(0);normal.setItem(make('premium_chili',8));
  check(consumeSharedOilSlot(normal,1,false,{ownerId:'qa-oil38-normal'}).ok,'normal debit');check(count(normal)===7,'normal quantity');check(normal.getItem().getDynamicProperty('qa:keepsake')==='preserved','foreign property');
  check(JSON.parse(world.getDynamicProperty(key('qa-oil38-normal'))).phase==='committed','terminal receipt');
  const uncertain=inventory.getSlot(1);uncertain.setItem(make('secret_chili',8));let writes=0;
  const fault={hasItem:()=>uncertain.hasItem(),getItem:()=>uncertain.getItem(),setItem(s){writes++;if(writes===1){uncertain.setItem(s);throw Error('injected applied debit')}if(writes===2)throw Error('injected rollback rejection');uncertain.setItem(s)}};
  const savedKey='qa:oil_recovery38_station',host={save(_b,state){world.setDynamicProperty(savedKey,JSON.stringify(state))},load(){return JSON.parse(world.getDynamicProperty(savedKey)??'{}')},raw(){return world.getDynamicProperty(savedKey)},sync(){}};
  const failed=commitSharedStationOil(b,fault,{},host,{ownerId:OWNER});check(!failed.ok&&failed.recoveryRequired,'unresolved debit');check(count(uncertain)===7,'one uncertain debit only');check(world.getDynamicProperty(savedKey)===undefined,'station not credited');
  const receipt=JSON.parse(world.getDynamicProperty(key(OWNER)));check(receipt.phase==='prepared','durable prepared');check(receipt.before.properties['qa:keepsake']==='preserved','original metadata retained');
  const replacement=inventory.getSlot(2);replacement.setItem(make('canola',20));check(!consumeSharedOilSlot(replacement,1,false,{ownerId:OWNER}).ok,'other slot blocked');check(count(replacement)===20,'replacement unchanged');
  const clean=inventory.getSlot(3);clean.setItem(make('canola',8));let once=true;
  const recoverable={hasItem:()=>clean.hasItem(),getItem:()=>clean.getItem(),setItem(s){clean.setItem(s);if(once){once=false;throw Error('injected acknowledged restore case')}}};
  check(!consumeSharedOilSlot(recoverable,1,false,{ownerId:'qa-oil38-restored'}).ok,'recoverable attempt rejected');check(count(clean)===8,'exact rollback');check(JSON.parse(world.getDynamicProperty(key('qa-oil38-restored'))).phase==='rolled_back','rollback receipt');
  check(consumeSharedOilSlot(clean,1,false,{ownerId:'qa-oil38-restored'}).ok&&count(clean)===7,'safe retry');
  world.setDynamicProperty(PHASE,1);console.log('OIL_RECOVERY_NATIVE_PASS '+JSON.stringify({phase:'saved',nativeContainerSlots:true,realWorldReceipts:true,normalTypedDebit:true,foreignMetadata:true,partialWriteInjected:true,rollbackFailureInjected:true,preparedGuard:true,replacementSlotBlocked:true,exactRollbackRetry:true,players:world.getAllPlayers().length,simulatedPlayers:false,client:false}));
 }else{
  const inventory=b.getComponent('minecraft:inventory').container,uncertain=inventory.getSlot(1),replacement=inventory.getSlot(2);
  check(count(uncertain)===7&&count(replacement)===20,'native item persistence');check(JSON.parse(world.getDynamicProperty(key(OWNER))).phase==='prepared','prepared receipt persisted');
  check(!consumeSharedOilSlot(replacement,1,false,{ownerId:OWNER}).ok&&count(replacement)===20,'restart retry remains blocked');
  check(JSON.parse(world.getDynamicProperty(key('qa-oil38-normal'))).phase==='committed','settled receipt persisted');
  console.log('OIL_RECOVERY_NATIVE_PASS '+JSON.stringify({phase:'restored',nativeItemsPersisted:true,ownerReceiptPersisted:true,retryBlocked:true,terminalReceiptPersisted:true,players:world.getAllPlayers().length,simulatedPlayers:false,client:false}));
 }
}catch(e){console.error('OIL_RECOVERY_NATIVE_FAIL '+e+' '+e.stack)}},100);
