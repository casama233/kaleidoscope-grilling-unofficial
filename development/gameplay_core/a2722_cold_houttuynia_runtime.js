import {world,system,ItemStack,EquipmentSlot} from '@minecraft/server';
import {
 COLD_ID,HOUTTUYNIA_ID,CRAFTING_TABLE_ID,COOKERY_EMPTY_ID,COOKERY_FILLED_ID,
 REQUIRED_OIL_TYPE,OIL_TYPE_KEY,OIL_COUNT_KEY,OIL_CAPACITY,FIRE_RESISTANCE_TICKS,
 planColdHouttuynia,nextOilPotId
} from './a2722_cold_houttuynia_core.js';

function inventory(player){return player.getComponent('minecraft:inventory')?.container}
function main(player){return inventory(player)?.getItem(player.selectedSlotIndex)}
function off(player){return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setMain(player,stack){inventory(player)?.setItem(player.selectedSlotIndex,stack)}
function setOff(player,stack){player.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}
function oilType(stack){try{return String(stack?.getDynamicProperty(OIL_TYPE_KEY)??'')}catch{return ''}}
function oilCount(stack){
 if(stack?.typeId!==COOKERY_FILLED_ID)return 0;
 const type=oilType(stack),cap=type?OIL_CAPACITY:256;
 try{
  const raw=stack.getDynamicProperty(OIL_COUNT_KEY);
  return raw===undefined?cap:Math.max(0,Math.min(cap,Number(raw)|0));
 }catch{return cap}
}
function message(player,text){try{player.onScreenDisplay.setActionBar(text)}catch{}}
function give(player,stack){
 const c=inventory(player);
 if(!c){try{player.dimension.spawnItem(stack,player.location)}catch{};return}
 try{const rem=c.addItem(stack);if(rem)player.dimension.spawnItem(rem,player.location)}
 catch{try{player.dimension.spawnItem(stack,player.location)}catch{}}
}
function nextMainStack(stack,count){
 if(count<=0)return undefined;
 const next=stack.clone();next.amount=count;return next;
}
function nextOilStack(stack,count,type){
 if(count<=0)return new ItemStack(COOKERY_EMPTY_ID,1);
 const next=stack.clone();
 try{
  next.setDynamicProperty(OIL_COUNT_KEY,count);
  next.setDynamicProperty(OIL_TYPE_KEY,type);
  next.setLore(['§7Oil: '+count+'/'+OIL_CAPACITY]);
 }catch{}
 return next;
}
function failureText(reason){
 switch(reason){
  case'need_houttuynia':return '§e涼拌折耳根需要主手至少 3 個折耳根';
  case'wrong_oil':return '§c需要高級辣椒油（premium_chili）';
  case'need_oil':return '§c高級辣椒油至少需要 2 點';
  case'need_oil_pot':return '§e副手需要 Cookery 油壺';
  default:return '§7配料不符合涼拌折耳根配方';
 }
}

export function tryCraftColdHouttuynia(player){
 const m=main(player),o=off(player),type=oilType(o),count=oilCount(o);
 const plan=planColdHouttuynia({
  blockId:CRAFTING_TABLE_ID,sneaking:!!player.isSneaking,
  mainId:m?.typeId,mainCount:m?.amount??0,offId:o?.typeId,oilType:type,oilCount:count
 });
 if(!plan.ok){message(player,failureText(plan.reason));return false}
 let output;try{output=new ItemStack(COLD_ID,1)}catch{return false}
 const beforeMain=m.clone(),beforeOff=o.clone();
 const afterMain=nextMainStack(m,plan.nextHouttuyniaCount);
 const afterOff=nextOilStack(o,plan.nextOilCount,type);
 try{
  setMain(player,afterMain);setOff(player,afterOff);
 }catch{
  try{setMain(player,beforeMain);setOff(player,beforeOff)}catch{}
  message(player,'§c合成交易失敗，已嘗試回滾');return false;
 }
 give(player,output);
 try{player.dimension.playSound('random.pop',player.location,{volume:.65,pitch:1.15})}catch{}
 message(player,'§a完成涼拌折耳根（折耳根×3，高級辣椒油 -2）');
 return true;
}

world.beforeEvents.playerInteractWithBlock.subscribe(ev=>{
 if(ev.block?.typeId!==CRAFTING_TABLE_ID||!ev.player?.isSneaking)return;
 if(ev.itemStack?.typeId!==HOUTTUYNIA_ID)return;
 const oil=off(ev.player);
 if(oil?.typeId!==COOKERY_FILLED_ID)return;
 ev.cancel=true;
 if(ev.isFirstEvent===false)return;
 const player=ev.player;
 system.run(()=>{try{tryCraftColdHouttuynia(player)}catch{}});
});

world.afterEvents.itemCompleteUse.subscribe(ev=>{
 if(ev.itemStack?.typeId!==COLD_ID)return;
 try{ev.source.addEffect('fire_resistance',FIRE_RESISTANCE_TICKS,{showParticles:true})}catch{}
});
