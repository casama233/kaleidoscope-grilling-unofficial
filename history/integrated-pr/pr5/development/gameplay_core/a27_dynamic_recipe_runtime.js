import {world,system,ItemStack,EquipmentSlot,GameMode} from '@minecraft/server';

const HOUT='kaleidoscope_grilling:houttuynia';
const COLD='kaleidoscope_grilling:cold_houttuynia';
const POT_EMPTY='kaleidoscope_cookery:oil_pot';
const POT_FILLED='kaleidoscope_cookery:oil_pot_filled';
const OIL_TYPE='kaleidoscope_grilling:oil_type';
const OIL_COUNT='kc_oil_count';

function inv(p){return p.getComponent('minecraft:inventory')?.container}
function main(p){return inv(p)?.getItem(p.selectedSlotIndex)}
function off(p){return p.getComponent('minecraft:equippable')?.getEquipment(EquipmentSlot.Offhand)}
function setOff(p,s){p.getComponent('minecraft:equippable')?.setEquipment(EquipmentSlot.Offhand,s)}
function creative(p){try{return p.getGameMode()===GameMode.Creative}catch{return false}}
function msg(p,t){try{p.onScreenDisplay.setActionBar(t)}catch{}}
function oilType(s){try{return String(s?.getDynamicProperty(OIL_TYPE)??'')}catch{return ''}}
function oilCount(s){try{return Math.max(0,Math.min(64,Number(s?.getDynamicProperty(OIL_COUNT)??0)|0))}catch{return 0}}
function countHout(p){
 const c=inv(p);if(!c)return 0;let n=0;
 for(let i=0;i<c.size;i++){const s=c.getItem(i);if(s?.typeId===HOUT)n+=s.amount}
 return n;
}
function consumeHout(p,count){
 if(creative(p))return true;const c=inv(p);if(!c)return false;
 let left=count;
 for(let i=0;i<c.size&&left>0;i++){
  const s=c.getItem(i);if(s?.typeId!==HOUT)continue;
  const take=Math.min(left,s.amount);left-=take;
  if(take===s.amount)c.setItem(i,undefined);else{s.amount-=take;c.setItem(i,s)}
 }
 return left===0;
}
function consumePremiumOil(p,points){
 const s=off(p);if(s?.typeId!==POT_FILLED||oilType(s)!=='premium_chili'||oilCount(s)<points)return false;
 if(creative(p))return true;
 const remaining=oilCount(s)-points;
 if(remaining<=0){setOff(p,new ItemStack(POT_EMPTY,1));return true}
 const next=new ItemStack(POT_FILLED,1);
 try{
  next.setLore(['§7Oil: '+remaining+'/64']);
  next.setDynamicProperty(OIL_COUNT,remaining);
  next.setDynamicProperty(OIL_TYPE,'premium_chili');
 }catch{}
 setOff(p,next);return true;
}
function give(p,s){
 const c=inv(p);if(!c){p.dimension.spawnItem(s,p.location);return}
 try{const rem=c.addItem(s);if(rem)p.dimension.spawnItem(rem,p.location)}catch{p.dimension.spawnItem(s,p.location)}
}
function canCraft(p){
 const pot=off(p);
 return p.isSneaking&&main(p)?.typeId===HOUT&&pot?.typeId===POT_FILLED&&oilType(pot)==='premium_chili'&&oilCount(pot)>=2&&countHout(p)>=3;
}
function craft(p){
 if(!canCraft(p)){msg(p,'§7涼拌折耳根：需要 3 份折耳根與副手至少 2 點熔岩辣椒油');return false}
 if(!consumeHout(p,3)||!consumePremiumOil(p,2))return false;
 give(p,new ItemStack(COLD,1));
 try{p.playSound('random.pop',{volume:.7,pitch:1.1})}catch{}
 msg(p,'§a完成涼拌折耳根，消耗 2 點熔岩辣椒油');return true;
}

world.beforeEvents.itemUse.subscribe(e=>{
 try{
  if(e.itemStack?.typeId!==HOUT||!e.source.isSneaking)return;
  const pot=off(e.source);if(pot?.typeId!==POT_FILLED||oilType(pot)!=='premium_chili')return;
  e.cancel=true;const p=e.source;system.run(()=>craft(p));
 }catch{}
});

export function a27ColdHouttuyniaCanCraft(player){return canCraft(player)}
