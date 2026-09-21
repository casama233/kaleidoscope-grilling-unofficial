import {world,system,ItemStack,EquipmentSlot} from '@minecraft/server';
import {itemSpec,effectsFor,kneadResult} from './a27_items_core.js';

const FX_KEY='kaleidoscope_grilling:a21_fx';
const QUALITY_RATIO_KEY='kaleidoscope_grilling:cookery_quality_ratio';

function now(){try{return world.getAbsoluteTime()}catch{return system.currentTick}}
function readFx(entity){try{const raw=entity.getDynamicProperty(FX_KEY);if(typeof raw!=='string')return {};const v=JSON.parse(raw);return v&&typeof v==='object'?v:{}}catch{return {}}}
function writeFx(entity,fx){try{const clean={};for(const [k,v] of Object.entries(fx))if(v&&Number(v.until)>now())clean[k]={until:Number(v.until),amp:Number(v.amp)||0};entity.setDynamicProperty(FX_KEY,Object.keys(clean).length?JSON.stringify(clean):undefined)}catch{}}
function fxSet(entity,name,ticks,amp=0){const fx=readFx(entity);fx[name]={until:now()+Math.max(1,ticks|0),amp:amp|0};writeFx(entity,fx)}
function qualityRatio(stack){
 // Compatibility hook only. A2.7 does not guess Cookery 1.0.6's private quality storage.
 try{const n=Number(stack?.getDynamicProperty(QUALITY_RATIO_KEY));return Number.isFinite(n)&&n>0?n:1}catch{return 1}
}
function applyEffect(player,e){
 if(e.kind==='native'){try{player.addEffect(e.id,e.ticks,{showParticles:true})}catch{};return}
 if(e.kind==='fx')fxSet(player,e.id,e.ticks,e.amp??0);
}
function inventory(player){return player.getComponent('minecraft:inventory')?.container}
function main(player){return inventory(player)?.getItem(player.selectedSlotIndex)}
function off(player){return player.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setMain(player,stack){inventory(player)?.setItem(player.selectedSlotIndex,stack)}
function setOff(player,stack){player.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,stack)}
function handFor(player,id){if(main(player)?.typeId===id)return 'main';if(off(player)?.typeId===id)return 'off';return null}
function setHand(player,hand,stack){return hand==='off'?setOff(player,stack):setMain(player,stack)}

world.afterEvents.itemCompleteUse.subscribe(e=>{
 try{
  const id=e.itemStack?.typeId,spec=itemSpec(id);if(!spec)return;
  const knead=kneadResult(id,e.itemStack?.amount??1);
  if(knead){
   const hand=handFor(e.source,id);if(hand){
    const current=hand==='off'?off(e.source):main(e.source),count=Math.max(1,current?.amount??e.itemStack?.amount??1);
    const out=new ItemStack(knead.id,count);setHand(e.source,hand,out);
    try{e.source.playSound('armor.equip_leather',{volume:.8,pitch:1.1})}catch{}
   }
   return;
  }
  if(!spec.food)return;
  const ratio=qualityRatio(e.itemStack);
  for(const fx of effectsFor(id,ratio))applyEffect(e.source,fx);
 }catch{}
});

export function a27QualityRatio(stack){return qualityRatio(stack)}
