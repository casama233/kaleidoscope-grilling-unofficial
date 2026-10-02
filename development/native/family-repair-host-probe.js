/** Test-only Cookery import. Native containers/helpers, zero actors; never ships. */
import {world,system,ItemStack} from '@minecraft/server';
import {createPublicOilPot,readPublicOil} from './api/oil_api_core.js';
import {consumeSharedOilSlot,writeSharedPlacedOil,readSharedPlacedOil,fillSharedPlacedOil,commitSharedStationOil,publishLegacyHostOil} from './api/oil_api_host.js';
import {deliverCuisineOutput,createNativeSuspiciousStew} from './api/cuisine_api_host.js';
import {readPublicFood} from './api/food_api_core.js';
import {publishAuthorIngredientBehaviors} from './api/ingredient_api_host.js';
import {publicMethodLabel,publicExtensionName} from './api/guide_labels_core.js';
import {KC_EXTENSION_CAPABILITIES} from './api/extensionRegistry.js';
const wait=t=>new Promise(r=>system.runTimeout(r,t));const check=(v,label)=>{if(!v)throw Error(label)};
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');d.runCommand('tickingarea add circle 48 80 64 2 repair_api true');let chest;
 for(let i=0;i<60;i++){await wait(10);try{chest=d.getBlock({x:48,y:80,z:64})}catch{}if(chest)break}check(chest,'chunk');
 const previous=world.getDynamicProperty('qa:family-repair-api');if(!previous)chest.setType('minecraft:chest');
 const bag=chest.getComponent('minecraft:inventory').container,pot=d.getBlock({x:49,y:80,z:64}),kitchen=d.getBlock({x:50,y:80,z:64});
 for(const b of [pot,kitchen])b.below().setType('minecraft:stone');if(!previous){pot.setType('kaleidoscope_cookery:oil_pot');kitchen.setType('kaleidoscope_cookery:pot');}
 const legacyFull=publishLegacyHostOil(new ItemStack('kaleidoscope_cookery:oil_pot_filled'));check(readPublicOil(legacyFull).state.count===256,'author full legacy snapshot');
 const types=['','canola','secret_chili','premium_chili'];
 if(!previous)for(let i=0;i<4;i++){bag.setItem(16+i,createPublicOilPot(ItemStack,types[i],3));check(consumeSharedOilSlot(bag.getSlot(16+i),3).ok,'native depletion');}
 for(let i=0;i<4;i++)check(bag.getItem(16+i).typeId==='kaleidoscope_cookery:oil_pot'&&readPublicOil(bag.getItem(16+i)).state.count===0,'restored empty pot');
 if(!previous){writeSharedPlacedOil(pot,{v:1,type:'premium_chili',count:8,revision:1});bag.setItem(20,new ItemStack('kaleidoscope_grilling:premium_chili_oil_bucket'));check(fillSharedPlacedOil(pot,bag.getSlot(20),'premium_chili').ok,'native placed fill');}
 const placed=readSharedPlacedOil(pot);check(placed.type==='premium_chili'&&placed.count===16,'placed persisted');
 bag.setItem(21,new ItemStack('kaleidoscope_grilling:canola_oil_bucket'));check(!fillSharedPlacedOil(pot,bag.getSlot(21),'canola').ok,'placed mixed oil rejected');
 if(!previous){bag.setItem(22,createPublicOilPot(ItemStack,'secret_chili',8));const state={},key='qa:station-oil';check(commitSharedStationOil(kitchen,bag.getSlot(22),state,{save(_b,s){world.setDynamicProperty(key,JSON.stringify(s))},load:()=>JSON.parse(world.getDynamicProperty(key)),sync(){}}).ok,'native station commit');}
 check(readPublicOil(bag.getItem(22)).state.count===7,'station debit persisted');
 const receipt=deliverCuisineOutput(kitchen,{grillingOilType:'premium_chili'},'minecraft:suspicious_stew',1,'pot',{container:bag,targetBlock:chest,operationId:'qa:stew-4',nativeStack:createNativeSuspiciousStew(kitchen,4)});
 const actual=bag.getItem(receipt.target.slot);check(readPublicFood(actual).state.hotUntil===receipt.metadata.hotUntil,'output metadata');check(previous?receipt.replayed:!receipt.replayed,'output replay');
 const published=publishAuthorIngredientBehaviors();check(published>0,'food behaviors published');
 for(const cap of ['cuisine_output_receipt_v2','guidebook_localized_labels_v1','secret_ingredient_behaviors_v1'])check(KC_EXTENSION_CAPABILITIES.includes(cap),'capability '+cap);
 check(publicMethodLabel('Oil Press','zh_TW')==='榨油器','localized method');check(publicExtensionName({names:{zh_TW:{'qa:item':'材料'}}},'zh_TW','qa:item')==='材料','localized item');
 world.setDynamicProperty('qa:family-repair-api',true);
 console.log('OILAPI_NATIVE_PASS '+JSON.stringify({phase:previous?'restart':'first',placed,legacyFilledDefault:256,emptyPots:4,stationRemaining:7,suspiciousStewSlot:receipt.target.slot,outputReplayed:!!receipt.replayed,registeredFoodBehaviors:published,actualNativeContainers:true,players:world.getAllPlayers().length,client:false}));
}catch(e){console.error('OILAPI_NATIVE_FAIL '+e+' '+e.stack)}},260);
