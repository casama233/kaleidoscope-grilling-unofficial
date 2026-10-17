import {EquipmentSlot,GameMode} from '@minecraft/server';

export function playerInventory(player){
 try{return player?.getComponent('minecraft:inventory')?.container}catch{return undefined}
}

export function getMainHand(player){
 try{return playerInventory(player)?.getItem(player.selectedSlotIndex)}catch{return undefined}
}

export function setMainHand(player,stack){
 const container=playerInventory(player);
 if(!container)return undefined;
 return container.setItem(player.selectedSlotIndex,stack);
}

export function getOffHand(player){
 try{return player?.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}catch{return undefined}
}

export function setOffHand(player,stack){
 try{return player?.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}catch{return undefined}
}

export function getHand(player,hand){
 return hand==='off'?getOffHand(player):getMainHand(player);
}

export function setHand(player,hand,stack){
 return hand==='off'?setOffHand(player,stack):setMainHand(player,stack);
}

export function findHand(player,itemId){
 const main=getMainHand(player);
 if(main?.typeId===itemId)return 'main';
 const off=getOffHand(player);
 if(off?.typeId===itemId)return 'off';
 return null;
}

export function findHandEntry(player,itemId){
 const name=findHand(player,itemId);
 return name?{name,stack:getHand(player,name)}:null;
}

export function isCreative(player){
 try{return player?.getGameMode?.()===GameMode.Creative}catch{return false}
}
