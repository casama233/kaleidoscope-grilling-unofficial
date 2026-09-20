import {EquipmentSlot,ItemStack} from '@minecraft/server';
import {SELECTORS,soundFor} from './profile_rules.js';
export const VISUAL_PREFIX='kg_imm:visual_';
const RESTORE='kg_imm:eat_restore';

export function inspectHands(player){
 const eq=player.getComponent('minecraft:equippable');if(!eq)return {};
 return {main:eq.getEquipment(EquipmentSlot.Mainhand),off:eq.getEquipment(EquipmentSlot.Offhand),eq};
}
export function selectHand(player,predicate){
 const h=inspectHands(player);
 if(h.main&&predicate(h.main.typeId))return {name:'main',slot:EquipmentSlot.Mainhand,item:h.main,eq:h.eq,hotbar:player.selectedSlotIndex};
 if(h.off&&predicate(h.off.typeId))return {name:'off',slot:EquipmentSlot.Offhand,item:h.off,eq:h.eq,hotbar:player.selectedSlotIndex};
 return null;
}
export function selector(player){return selectHand(player,id=>Object.hasOwn(SELECTORS,id));}
export function tool(player,id){return selectHand(player,x=>x===id);}
export function stance(player,target){
 const dx=target.location.x-player.location.x,dz=target.location.z-player.location.z,d=Math.hypot(dx,dz);
 if(d<.72||d>1.32||Math.abs(target.location.y-player.location.y)>.75)return false;
 const v=player.getViewDirection();return (v.x*dx+v.z*dz)/d>.90;
}
function getHand(player,performer){
 if(performer.name==='off')return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand);
 return player.getComponent('minecraft:inventory')?.container?.getItem(performer.hotbar);
}
function setHand(player,performer,id){
 if(id===undefined){
  if(performer.name==='off')return performer.eq.setEquipment(EquipmentSlot.Offhand);
  const inv=player.getComponent('minecraft:inventory')?.container;if(!inv)return false;inv.setItem(performer.hotbar);return true;
 }
 const stack=new ItemStack(id,1);
 if(performer.name==='off')return performer.eq.setEquipment(EquipmentSlot.Offhand,stack);
 const inv=player.getComponent('minecraft:inventory')?.container;if(!inv)return false;inv.setItem(performer.hotbar,stack);return true;
}
export function beginEat(player,hand,resolved){
 const selectorId=hand.item.typeId,requested=SELECTORS[selectorId];
 const performer={playerId:player.id,name:hand.name,slot:hand.slot,hotbar:hand.hotbar,eq:hand.eq,selectorId,requested,resolved,helper:false};
 player.setDynamicProperty(RESTORE,JSON.stringify({name:performer.name,hotbar:performer.hotbar,selectorId}));
 if(!setHand(player,performer,VISUAL_PREFIX+'0')){player.setDynamicProperty(RESTORE);throw new Error('Could not install visual skewer');}
 if(resolved==='ONE'||resolved==='THREE'){
  const h=inspectHands(player),opposite=hand.name==='main'?h.off:h.main;
  if(!opposite){
   const helper={name:hand.name==='main'?'off':'main',hotbar:hand.hotbar,eq:h.eq};
   if(setHand(player,helper,'kg_imm:bite_piece')){performer.helper=true;performer.helperHand=helper;}
  }
 }
 player.playAnimation('animation.kg_imm.player.eat_'+resolved.toLowerCase()+'.'+hand.name,{blendOutTime:.12});
 try{player.playSound('kg_imm.'+soundFor(resolved));}catch{}
 return performer;
}
export function bite(player,performer,index){
 if(!performer||player.id!==performer.playerId)return false;
 const current=getHand(player,performer);if(!current?.typeId.startsWith(VISUAL_PREFIX))return false;
 return setHand(player,performer,VISUAL_PREFIX+Math.min(4,index+1));
}
export function finishEat(player,performer){
 if(!performer||player.id!==performer.playerId)return;
 const current=getHand(player,performer);
 if(current?.typeId.startsWith(VISUAL_PREFIX))setHand(player,performer,performer.selectorId);
 if(performer.helper&&performer.helperHand){
  const h=getHand(player,performer.helperHand);if(h?.typeId==='kg_imm:bite_piece')setHand(player,performer.helperHand,undefined);
 }
 try{player.runCommand('stopsound @s kg_imm.'+soundFor(performer.resolved));}catch{}
 player.setDynamicProperty(RESTORE);
}
export function recover(player){
 const raw=player.getDynamicProperty(RESTORE);if(typeof raw!=='string')return false;
 try{
  const saved=JSON.parse(raw),h=inspectHands(player);
  const performer={name:saved.name,hotbar:saved.hotbar,selectorId:saved.selectorId,eq:h.eq};
  const current=getHand(player,performer);
  if(current?.typeId.startsWith(VISUAL_PREFIX))setHand(player,performer,saved.selectorId);
  const opposite={name:saved.name==='main'?'off':'main',hotbar:saved.hotbar,eq:h.eq};
  if(getHand(player,opposite)?.typeId==='kg_imm:bite_piece')setHand(player,opposite,undefined);
 }finally{player.setDynamicProperty(RESTORE);}
 return true;
}
export function playTool(player,kind,hand){player.playAnimation('animation.kg_imm.player.'+kind+'.'+hand.name,{blendOutTime:.12});}
export function playReach(player,hand='main'){player.playAnimation('animation.kg_imm.player.reach.'+hand,{blendOutTime:.12});}
