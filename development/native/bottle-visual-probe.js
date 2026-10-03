/** Private actual-player QA only. Copy into a private Grilling BP retaining its
 * header UUID, then import there. Never import this from canonical main.js.
 * /scriptevent kg_qa:bottle_visual seed | inspect
 */
import {ItemStack,EquipmentSlot,system,world} from '@minecraft/server';
import {getItemProperty,setItemProperty,getItemPropertyIds} from './itemData.js';
const NS='kaleidoscope_grilling:',KEY=NS+'seasonings';
const base=[NS+'green_chili_powder',NS+'sichuan_pepper',NS+'onion_powder'];
const full=[...base,'minecraft:redstone','minecraft:gunpowder',NS+'houttuynia_powder',NS+'totem_powder',NS+'dragon_egg_powder'];
function describe(item){
 if(!item)return null;
 return {id:item.typeId,amount:item.amount,name:item.nameTag,lore:item.getLore(),
  properties:Object.fromEntries(getItemPropertyIds(item).map(k=>[k,getItemProperty(item,k)])),
  keepOnDeath:item.keepOnDeath,lockMode:item.lockMode,canDestroy:item.getCanDestroy(),canPlaceOn:item.getCanPlaceOn()};
}
system.afterEvents.scriptEventReceive.subscribe(event=>{
 if(event.id!=='kg_qa:bottle_visual')return;
 const player=event.sourceEntity;
 if(player?.typeId!=='minecraft:player')throw new Error('Bottle visual QA must be invoked by the selected real player');
 if(event.message==='seed'){
  const rows=[['empty_seasoning_bottle',base.slice(0,1),'partial1'],['empty_seasoning_bottle',base.slice(0,2),'partial2'],
   ['pending_seasoning',base,'pending3'],['pending_seasoning',full,'pending8'],['special_seasoning',full,'finished8']];
  const c=player.getComponent('minecraft:inventory').container;
  const free=Array.from({length:c.size},(_,i)=>i).filter(i=>!c.getItem(i));
  if(free.length<rows.length)throw new Error('Bottle QA needs five empty inventory slots; no existing items were changed');
  rows.forEach(([id,ingredients,label],i)=>{
   const item=new ItemStack(NS+id,1);item.nameTag='QA '+label;
   setItemProperty(item,KEY,JSON.stringify(ingredients));setItemProperty(item,NS+'qa_bottle_marker',label);
   if(id==='special_seasoning'){setItemProperty(item,NS+'uses',0);setItemProperty(item,NS+'variant',0);}
   c.setItem(free[i],item);
  });
  console.warn('[Bottle visual QA seeded] '+JSON.stringify(rows.map((_,i)=>({slot:free[i],item:describe(c.getItem(free[i]))}))));
 }else if(event.message==='inspect'){
  const c=player.getComponent('minecraft:inventory').container,e=player.getComponent('minecraft:equippable');
  console.warn('[Bottle visual QA hands] '+JSON.stringify({main:describe(c.getItem(player.selectedSlotIndex)),off:describe(e.getEquipment(EquipmentSlot.Offhand)),
   visual:Object.fromEntries(['main','off'].flatMap(hand=>Array.from({length:8},(_,i)=>[hand+'_'+i,player.getProperty(NS+'bottle_'+hand+'_'+i)])))}));
 }else throw new Error('Bottle visual QA expects seed or inspect');
});
