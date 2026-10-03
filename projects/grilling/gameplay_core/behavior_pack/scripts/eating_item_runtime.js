import {ItemStack,EnchantmentType} from '@minecraft/server';
import {captureSkewerMetadata,restoreSkewerMetadata,metadataSignature} from './skewer_item_snapshot.js';
import {canonicalFoodId,eatingItemId,RANDOM_EATING_IDS,isAlternateEatingId} from './eating_profile_ids.js';
import {getHand,setHand} from './a2735_player_io.js';
import {eatingIdentity} from './a285_eating_transaction.js';
const prepared=new Map();
export function forgetEatingItem(playerId){prepared.delete(playerId);}
export function selectedEatingProfile(requested,id){return RANDOM_EATING_IDS.has(canonicalFoodId(id))?(isAlternateEatingId(id)?'THREE_ALT':'THREE'):requested;}
export function copyEatingVariant(stack,id){
 const snapshot=captureSkewerMetadata(stack);snapshot.id=id;
 const out=restoreSkewerMetadata(snapshot,(type,n)=>new ItemStack(type,n),type=>new EnchantmentType(type));out.amount=stack.amount;
 if(out.amount!==stack.amount||metadataSignature(captureSkewerMetadata(out))!==metadataSignature(snapshot))throw Error('Eating variant metadata readback differs');
 return out;
}
// Native duration is chosen BEFORE use begins. No timer debit or selected-slot
// swap can race the engine's food completion. Variants retain all exposed data.
export function prepareEatingItems(player,using){
 if(using)return;
 const prior=prepared.get(player.id)??{};
 for(const hand of ['main','off']){
  const stack=getHand(player,hand),id=stack?.typeId;
  if(!RANDOM_EATING_IDS.has(canonicalFoodId(id))){delete prior[hand];continue;}
  const identity=eatingIdentity(stack);
  if(prior[hand]?.identity===identity&&prior[hand]?.slot===(hand==='off'?-1:player.selectedSlotIndex))continue;
  const target=eatingItemId(id,Math.random()>=.5);
  if(target!==id){const out=copyEatingVariant(stack,target);try{setHand(player,hand,out);if(eatingIdentity(getHand(player,hand))!==eatingIdentity(out))throw Error('Eating variant hand write failed');}catch(error){setHand(player,hand,stack);throw error;}prior[hand]={identity:eatingIdentity(out),slot:hand==='off'?-1:player.selectedSlotIndex};}
  else prior[hand]={identity,slot:hand==='off'?-1:player.selectedSlotIndex};
 }
 prepared.set(player.id,prior);
}
