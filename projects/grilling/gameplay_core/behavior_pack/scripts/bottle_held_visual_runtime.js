import {world,system} from '@minecraft/server';
import {getMainHand,getOffHand} from './a2735_player_io.js';
import {getItemProperty} from './itemData.js';
import {SEASONING_LIST_KEY,normalizeSeasoningList} from './a2743_seasoning_contract_core.js';
import {bottleHeldVisualPlan,isBottleHeldVisualItem} from './bottle_held_visual_core.js';

const signatures=new Map();

export function readBottleHeldSeasonings(stack){
 if(!isBottleHeldVisualItem(stack?.typeId))return [];
 const raw=getItemProperty(stack,SEASONING_LIST_KEY);
 if(typeof raw!=='string')return [];
 try{return normalizeSeasoningList(JSON.parse(raw))}catch{return []}
}

// Derived client properties only; never replace or write a held ItemStack.
export function syncBottleHeld(player){
 const rows={};
 for(const [hand,stack] of [['main',getMainHand(player)],['off',getOffHand(player)]]){
  const plan=bottleHeldVisualPlan(stack?.typeId,readBottleHeldSeasonings(stack));
  for(let i=0;i<plan.length;i++)rows['kaleidoscope_grilling:bottle_'+hand+'_'+i]=plan[i];
 }
 const signature=JSON.stringify(rows);
 if(signatures.get(player.id)===signature)return;
 // A failed write can leave some properties updated. Invalidate the old cache
 // before writing, so reverting hands also retries a complete projection.
 signatures.delete(player.id);
 for(const [key,value] of Object.entries(rows))player.setProperty(key,value);
 signatures.set(player.id,signature);
}

function syncSafely(player){
 try{syncBottleHeld(player)}catch(error){console.warn('[Grilling held bottle contents] '+error)}
}

world.afterEvents.playerInventoryItemChange.subscribe(e=>system.run(()=>syncSafely(e.player)));
world.afterEvents.playerHotbarSelectedSlotChange.subscribe(e=>system.run(()=>syncSafely(e.player)));
world.afterEvents.playerLeave.subscribe(e=>signatures.delete(e.playerId));
system.runInterval(()=>{for(const player of world.getAllPlayers())syncSafely(player)},5);
