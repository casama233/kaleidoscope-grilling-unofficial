import {world,system,ItemStack,EquipmentSlot} from '@minecraft/server';
import {
 BOARD_ID,CHICKEN_ID,CHICKEN_SKIN_ID,CHICKEN_WING_ID,
 KITCHEN_KNIVES,isKitchenKnife,stationKey,chickenSkinCompletionCandidate,
 chickenBoardCompletionCommitted,chickenSkinDropCount,chickenWingDropCount
} from './a2710_chicken_acquisition_core.js';

const PENDING_SKIN=new Map();

function pos(block){
 const p=block?.location??block;
 return {x:Number(p?.x??0),y:Number(p?.y??0),z:Number(p?.z??0)};
}
function boardKey(block){
 const p=pos(block);return stationKey(block.dimension.id,p.x,p.y,p.z);
}
function parseState(raw){
 if(raw===undefined||raw===null||raw==='')return {};
 try{return JSON.parse(String(raw))}catch{return {}}
}
function readBoardState(block){
 try{return parseState(world.getDynamicProperty(boardKey(block)))}catch{return {}}
}
function mainHand(player){
 try{
  const slot=player.getComponent('minecraft:equippable')?.getEquipmentSlot(EquipmentSlot.Mainhand);
  return slot?.hasItem()?slot.getItem():undefined;
 }catch{return undefined}
}
function lootingLevel(stack){
 try{
  const c=stack?.getComponent('minecraft:enchantable');
  return Math.max(0,Number(c?.getEnchantment('looting')?.level??c?.getEnchantment('minecraft:looting')?.level??0)||0);
 }catch{return 0}
}
function dropAt(dimension,location,id,count){
 if(count<=0)return;
 dimension.spawnItem(new ItemStack(id,count),{x:location.x+.5,y:location.y+.45,z:location.z+.5});
}
function watchChickenSkin(event){
 const block=event?.block,player=event?.player;
 if(!block||!player||block.typeId!==BOARD_ID)return;
 const held=mainHand(player),state=readBoardState(block);
 if(!chickenSkinCompletionCandidate(state,held?.typeId,event.isFirstEvent))return;
 const key=boardKey(block);if(PENDING_SKIN.has(key))return;
 const dimension=block.dimension,location=pos(block),before=JSON.parse(JSON.stringify(state)),token=system.currentTick;
 PENDING_SKIN.set(key,token);
 system.run(()=>{
  try{
   const current=PENDING_SKIN.get(key);if(current!==token)return;
   const live=dimension.getBlock(location);
   const after=live?.typeId===BOARD_ID?readBoardState(live):{};
   if(!chickenBoardCompletionCommitted(before,after))return;
   dropAt(dimension,location,CHICKEN_SKIN_ID,chickenSkinDropCount(Math.random()));
  }catch{}finally{
   if(PENDING_SKIN.get(key)===token)PENDING_SKIN.delete(key);
  }
 });
}

world.beforeEvents.playerInteractWithBlock.subscribe(watchChickenSkin);

world.afterEvents.entityDie.subscribe(event=>{
 try{
  const dead=event.deadEntity;if(dead?.typeId!==CHICKEN_ID)return;
  const killer=event.damageSource?.damagingEntity;if(killer?.typeId!=='minecraft:player')return;
  const weapon=mainHand(killer);if(!isKitchenKnife(weapon?.typeId))return;
  const count=chickenWingDropCount(Math.random(),Math.random(),lootingLevel(weapon));
  const p=dead.location;
  dead.dimension.spawnItem(new ItemStack(CHICKEN_WING_ID,count),{x:p.x,y:p.y,z:p.z});
 }catch{}
});

export const a2710KnifeIds=KITCHEN_KNIVES;
