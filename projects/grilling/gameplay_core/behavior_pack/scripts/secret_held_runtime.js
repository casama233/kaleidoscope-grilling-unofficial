import {canonicalFoodId} from './eating_profile_ids.js';
import {world,system} from '@minecraft/server';
import {getMainHand,getOffHand,isCreative} from './a2735_player_io.js';
import {eatingStillCurrent} from './a285_eating_transaction.js';
import {secretVisualIndex} from './integration_registry_core.js';
import {secretVisualState,partialVisualState} from './secret_visual_state.js';
let reader,rawReader;const signatures=new Map(),completedHands=new Map();
export function configureSecretHeldReader(read,readRaw){reader=read;rawReader=readRaw;}
export function syncSecretHeld(player,{beginHand,completedUse}={}){
 if(!reader)return;
 let completed=completedHands.get(player.id);
 if(beginHand)completed?.delete(beginHand);
 if(completedUse&&!isCreative(player)){
  // A confirmed native single serving can outlive its debit in the held
  // render snapshot. Suppress that exact hand/slot/identity, never a new meal.
  const before=JSON.parse(completedUse.identity),current=completedUse.hand==='off'?getOffHand(player):getMainHand(player);
  if(canonicalFoodId(before.id)==='kaleidoscope_grilling:secret_skewer'&&before.amount===1&&
   eatingStillCurrent(completedUse,current,player.selectedSlotIndex,system.currentTick)){
   if(!completed){completed=new Map();completedHands.set(player.id,completed);}
   completed.set(completedUse.hand,completedUse);
  }
 }
 const rows={};
 for(const [hand,current] of [['main',getMainHand(player)],['off',getOffHand(player)]]){
  const done=completed?.get(hand);
  if(done&&!eatingStillCurrent(done,current,player.selectedSlotIndex,system.currentTick))completed.delete(hand);
  const stack=completed?.has(hand)?undefined:current;
  const id=canonicalFoodId(stack?.typeId);
  const ingredients=id==='kaleidoscope_grilling:secret_skewer'?secretVisualState(stack,reader):id==='kaleidoscope_grilling:unfinished_skewer'?partialVisualState(stack,reader):[];
  for(let i=0;i<3;i++)rows['kaleidoscope_grilling:secret_'+hand+'_'+i]=ingredients[i]??0;
  // Pinned Java helper resolution reads the original last snapshot, not the
  // cooked/effective rows and not a destructively shortened bite-stage list.
  const raw=canonicalFoodId(stack?.typeId)==='kaleidoscope_grilling:secret_skewer'&&rawReader?rawReader(stack):[];
  rows['kaleidoscope_grilling:secret_'+hand+'_piece']=secretVisualIndex(raw[raw.length-1]?.id);
 }
 const signature=JSON.stringify(rows);if(signatures.get(player.id)===signature)return;
 for(const [key,value] of Object.entries(rows))player.setProperty(key,value);
 signatures.set(player.id,signature);
}
world.afterEvents.playerInventoryItemChange.subscribe(e=>system.run(()=>{try{completedHands.delete(e.player.id);syncSecretHeld(e.player)}catch(error){console.warn('[Grilling held ingredients] '+error)}}));
world.afterEvents.playerHotbarSelectedSlotChange.subscribe(e=>system.run(()=>{try{completedHands.get(e.player.id)?.delete('main');syncSecretHeld(e.player)}catch(error){console.warn('[Grilling held ingredients] '+error)}}));
world.afterEvents.playerLeave.subscribe(e=>{signatures.delete(e.playerId);completedHands.delete(e.playerId)});
system.runInterval(()=>{for(const player of world.getAllPlayers())try{syncSecretHeld(player)}catch(error){console.warn('[Grilling held ingredients] '+error)}},20);
