import {world,system,ItemStack} from '@minecraft/server';
import {OIL_TYPES} from './a23_oil_world.js';
import {readCookeryOilPot,planCookeryTypedOilAddition} from './a2734_cookery_oil_pot_adapter.js';
import {
 getMainHand,getOffHand,setMainHand,setOffHand,isCreative as creative
} from './a2735_player_io.js';
import {oilTypeForBucketId,planOffhandOilFill,ITEM_FILL_POINTS} from './a2737_offhand_oil_fill_core.js';

function message(player,text){try{player.onScreenDisplay.setActionBar(text)}catch{}}

function verifyPot(stack,type,count){
 const state=readCookeryOilPot(stack);
 return state.filled&&state.type===type&&state.count===count;
}

function fillOffhandPot(player,expectedBucketId){
 const main=getMainHand(player),off=getOffHand(player);
 if(main?.typeId!==expectedBucketId)return false;
 const type=oilTypeForBucketId(main.typeId,OIL_TYPES);if(!type)return false;

 const preview=planOffhandOilFill(readCookeryOilPot(off),type);
 if(!preview.handled)return false;
 if(!preview.ok){message(player,'§c油壺內已有不同內容或容量不足');return true}

 const plan=planCookeryTypedOilAddition(off,type,ITEM_FILL_POINTS);
 if(!plan.ok){message(player,'§c油壺內已有不同內容或容量不足');return true}

 let beforeMain,beforeOff;
 try{beforeMain=main.clone();beforeOff=off.clone()}catch{message(player,'§c油壺更新失敗');return true}

 const keepBucket=creative(player);
 try{
  setOffHand(player,plan.next);
  if(!keepBucket)setMainHand(player,new ItemStack('minecraft:bucket',1));
 }catch{
  try{setMainHand(player,beforeMain);setOffHand(player,beforeOff)}catch{}
  message(player,'§c油壺更新失敗，已嘗試回滾');return true;
 }

 const afterOff=getOffHand(player),afterMain=getMainHand(player);
 const potOk=verifyPot(afterOff,plan.type,plan.nextCount);
 const bucketOk=keepBucket?afterMain?.typeId===expectedBucketId:afterMain?.typeId==='minecraft:bucket';
 if(!potOk||!bucketOk){
  try{setMainHand(player,beforeMain);setOffHand(player,beforeOff)}catch{}
  message(player,'§c油壺更新驗證失敗，已嘗試回滾');return true;
 }

 try{player.playSound(type==='premium_chili'?'bucket.empty_lava':'bucket.empty_water',{volume:.9,pitch:.8+.5*plan.nextCount/plan.capacity})}catch{}
 message(player,'§a已向油壺加入 '+ITEM_FILL_POINTS+' 點油（'+plan.nextCount+'/'+plan.capacity+'）');
 return true;
}

world.beforeEvents.itemUse.subscribe(ev=>{
 const player=ev.source,eventItem=ev.itemStack,main=getMainHand(player),off=getOffHand(player);
 if(!eventItem||main?.typeId!==eventItem.typeId)return;
 const type=oilTypeForBucketId(main.typeId,OIL_TYPES);if(!type)return;
 const preview=planOffhandOilFill(readCookeryOilPot(off),type);
 if(!preview.handled)return;
 ev.cancel=true;
 const bucketId=main.typeId;
 system.run(()=>{try{fillOffhandPot(player,bucketId)}catch{}});
});
