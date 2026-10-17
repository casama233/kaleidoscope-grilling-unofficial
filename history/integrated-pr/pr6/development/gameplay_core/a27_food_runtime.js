import {world,system,ItemStack,EquipmentSlot} from '@minecraft/server';
import {A27_EFFECTS} from './a27_content_core.js';

const FX_KEY='kaleidoscope_grilling:a21_fx';
const POWDER='kaleidoscope_grilling:sweet_potato_powder';
const SHEET='kaleidoscope_grilling:raw_sweet_potato_sheet';

function now(){try{return world.getAbsoluteTime()}catch{return system.currentTick}}
function readFx(entity){
 try{const raw=entity.getDynamicProperty(FX_KEY);if(typeof raw!=='string')return {};const v=JSON.parse(raw);return v&&typeof v==='object'?v:{}}catch{return {}}
}
function writeFx(entity,fx){
 try{
  const t=now(),clean={};
  for(const [k,v] of Object.entries(fx))if(v&&Number(v.until)>t)clean[k]={until:Number(v.until),amp:Number(v.amp)||0};
  entity.setDynamicProperty(FX_KEY,Object.keys(clean).length?JSON.stringify(clean):undefined);
 }catch{}
}
function fxSet(entity,name,ticks,amp=0){
 const fx=readFx(entity),t=now(),old=fx[name];
 const until=t+Math.max(1,ticks|0);
 fx[name]={until:Math.max(Number(old?.until)||0,until),amp:Math.max(Number(old?.amp)||0,amp|0)};
 writeFx(entity,fx);
}
export function applyA27Effects(player,id){
 for(const e of A27_EFFECTS[id]??[]){
  if(e.kind==='native'){try{player.addEffect(e.name,e.ticks,{amplifier:e.amp??0,showParticles:true})}catch{}}
  else fxSet(player,e.name,e.ticks,e.amp??0);
 }
}
function replacePowderStack(player){
 try{
  const c=player.getComponent('minecraft:inventory')?.container,slot=player.selectedSlotIndex,main=c?.getItem(slot);
  if(main?.typeId===POWDER){c.setItem(slot,new ItemStack(SHEET,main.amount));return true}
  const eq=player.getComponent('minecraft:equippable'),off=eq?.getEquipment(EquipmentSlot.Offhand);
  if(off?.typeId===POWDER){eq.setEquipment(EquipmentSlot.Offhand,new ItemStack(SHEET,off.amount));return true}
 }catch{}
 return false;
}
world.afterEvents.itemCompleteUse.subscribe(e=>{
 const id=e.itemStack?.typeId;
 if(id===POWDER){system.run(()=>{if(replacePowderStack(e.source))try{e.source.playSound('armor.equip_leather',{volume:.8,pitch:1.1})}catch{}});return}
 if(A27_EFFECTS[id])applyA27Effects(e.source,id);
});
