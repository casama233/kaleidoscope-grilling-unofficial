import {world,system} from '@minecraft/server';
import {getMainHand,getOffHand} from './a2735_player_io.js';
import {getItemProperty} from './itemData.js';
import {SEASONING_LIST_KEY,normalizeSeasoningList} from './a2743_seasoning_contract_core.js';
import {bottleHeldVisualPlan,isBottleHeldVisualItem} from './bottle_held_visual_core.js';
import {PLATE_ID,PLATE_SKEWERS_KEY} from './a25_plate_recipe_core.js';
import {a25PlateRows,a25RestoreStack} from './a25_plate_recipe_runtime.js';
import {secretVisualState} from './secret_visual_state.js';
import {plateHeldVisualPlan,HELD_VISUAL_INVALID_OWNER,PLATE_HELD_ROW_RADIX} from './plate_held_visual_core.js';
import {SECRET_MODEL_VARIANTS_KEY} from './secret_visual_state_core.js';
import {heldVisualRegistryRevision} from './integration_registry_core.js';

const signatures=new Map();
const platePlans=new Map();
const heldQa=new Map();
let plateSecretReader;
export function configurePlateHeldReader(read){plateSecretReader=read;platePlans.clear();}

function heldQaItem(player,hand,stack,projected){
 const itemId=typeof stack?.typeId==='string'&&/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(stack.typeId)?stack.typeId:null;
 const out={itemId,projected:Array.from({length:8},(_,i)=>projected?.['kaleidoscope_grilling:bottle_'+hand+'_'+i]??null),serverLive:Array.from({length:8},(_,i)=>{try{return player.getProperty('kaleidoscope_grilling:bottle_'+hand+'_'+i)??null}catch{return 'unreadable';}})};
 if(itemId===PLATE_ID)try{
  const raw=getItemProperty(stack,PLATE_SKEWERS_KEY),rows=raw===undefined?[]:JSON.parse(raw);
  if(!Array.isArray(rows)||rows.length>5)throw Error('plate rows');
  out.rows=rows.map(row=>{
   const id=typeof row?.id==='string'&&/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(row.id)?row.id:'invalid';
   const raw=(row?.native?.props??row?.props??{})[SECRET_MODEL_VARIANTS_KEY];let variants=null;
   if(raw!==undefined)try{variants=typeof raw==='string'?JSON.parse(raw):raw;if(!Array.isArray(variants)||variants.length>3||variants.some(v=>!Number.isInteger(v)||v<1||v>9))variants='invalid';}catch{variants='invalid';}
   return {id,modelVariants:variants};
  });
 }catch{out.rows='unreadable';}
 return out;
}

// Existing opt-in only; no item/player metadata writes, names, lore, creator
// fields or player identifiers in output. Internal rate-limit keys are never emitted.
// At most one changed record/second and24 records per opt-in activation.
export function traceHeldProjection(player,projected,phase='ready'){
 try{
  if(player?.hasTag?.('kg_plate_qa')!==true){heldQa.delete(player.id);return;}
  const tick=system.currentTick,state=heldQa.get(player.id)??{next:-1,count:0,last:''};
  if(state.count>=24||tick<state.next)return;
  state.next=tick+20;heldQa.set(player.id,state);
  const record={phase,main:heldQaItem(player,'main',getMainHand(player),projected),off:heldQaItem(player,'off',getOffHand(player),projected)},signature=JSON.stringify(record);
  if(state.last===signature)return;
  state.last=signature;state.count++;console.warn('[Grilling held QA] '+signature);
 }catch{} // Optional diagnostics cannot interrupt the presentation transaction.
}

export function readBottleHeldSeasonings(stack){
 if(!isBottleHeldVisualItem(stack?.typeId))return [];
 const raw=getItemProperty(stack,SEASONING_LIST_KEY);
 if(typeof raw!=='string')return [];
 try{return normalizeSeasoningList(JSON.parse(raw))}catch{return []}
}

export function isDefaultFailedHeldVisual(stack){
 // Existing failures lack Java FailedSkewerSource provenance. A retained
 // custom variant list is known non-default and must not become a bare-stick
 // stand-in. Java's failed shape getter uses that list, not ingredient count.
 // Read only; repairing that family must not discard these values.
 const raw=getItemProperty(stack,SECRET_MODEL_VARIANTS_KEY);if(raw===undefined)return true;
 let values;try{values=typeof raw==='string'?JSON.parse(raw):raw}catch{return false;}
 return Array.isArray(values)&&values.length===0;
}

function readPlateHeldPlan(player,hand,stack){
 // Native stack adapters return new copies. Cache by the authoritative stored
 // snapshot, never object identity or lore/name. Poll one raw property so a
 // consume/swap/in-place content mutation cannot leave a cached presentation.
 const raw=getItemProperty(stack,PLATE_SKEWERS_KEY),revision=heldVisualRegistryRevision(),cached=platePlans.get(player.id)?.[hand];
 if(cached&&cached.raw===raw&&cached.revision===revision)return cached.plan;
 const copies=a25PlateRows(stack).map(row=>{const copy=a25RestoreStack(row);if(!copy)throw Error('Held plate food unavailable');return copy;});
 const plan=plateHeldVisualPlan(copies,plateSecretReader?copy=>secretVisualState(copy,plateSecretReader):undefined,isDefaultFailedHeldVisual);
 const hands=platePlans.get(player.id)??{};hands[hand]={raw,revision,plan};platePlans.set(player.id,hands);
 return plan;
}

function invalidateHeldInput(player,error){
 // A different unreadable plate has the same item identifier as the old one.
 // An opposite-hand input fault can also stall that plate's new plan. Neither
 // old marker may keep admitting stale foods. Clear the output cache
 // before best-effort invalidation so reverting to the last valid plate retries.
 signatures.delete(player.id);platePlans.delete(player.id);
 const failures=[],failedHands=[];
 for(const hand of ['main','off'])try{
  player.setProperty('kaleidoscope_grilling:bottle_'+hand+'_7',HELD_VISUAL_INVALID_OWNER);
 }catch(e){failures.push(hand+' owner: '+e);failedHands.push(hand);}
 for(const hand of failedHands){
  // Pair words admit only0..123²-1. If the owner setter rejects a write,
  // independently invalidate one hand pair instead. Both plate and dynamic
  // bottle guards reject this shared fallback, even if marker7 was not writable.
  for(const word of [5,6])try{
   player.setProperty('kaleidoscope_grilling:bottle_'+hand+'_'+word,PLATE_HELD_ROW_RADIX**2);break;
  }catch(e){failures.push(hand+' pair'+word+': '+e);}
 }
 return failures.length?Error(String(error)+'; held presentation invalidation rejected: '+failures.join('; ')):error;
}

// Derived client properties only; never replace or write a held ItemStack.
export function syncBottleHeld(player){
 const rows={};
 try{for(const [hand,stack] of [['main',getMainHand(player)],['off',getOffHand(player)]]){
  let plan;
  if(stack?.typeId===PLATE_ID)plan=readPlateHeldPlan(player,hand,stack);
  else{
   const hands=platePlans.get(player.id);if(hands){delete hands[hand];if(!Object.keys(hands).length)platePlans.delete(player.id);}
   plan=bottleHeldVisualPlan(stack?.typeId,readBottleHeldSeasonings(stack));
  }
  for(let i=0;i<plan.length;i++)rows['kaleidoscope_grilling:bottle_'+hand+'_'+i]=plan[i];
 }}catch(error){const failure=invalidateHeldInput(player,error);traceHeldProjection(player,undefined,'input_failed');throw failure;}
 const signature=JSON.stringify(rows);
 if(signatures.get(player.id)===signature){traceHeldProjection(player,rows);return;}
 // A failed write can leave some properties updated. Invalidate the old cache
 // before writing, so reverting hands also retries a complete projection.
 signatures.delete(player.id);
 // Neither renderer owns this sentinel. Publish payloads only while both hands
 // are invalid, then release each owner marker last. Failed writes leave a
 // complete retry pending even if the user reverts to the old held items.
 try{
  for(const hand of ['main','off'])player.setProperty('kaleidoscope_grilling:bottle_'+hand+'_7',HELD_VISUAL_INVALID_OWNER);
  for(const [key,value] of Object.entries(rows))if(!key.endsWith('_7'))player.setProperty(key,value);
  for(const hand of ['main','off']){const key='kaleidoscope_grilling:bottle_'+hand+'_7';player.setProperty(key,rows[key]);}
  signatures.set(player.id,signature);
 }catch(error){traceHeldProjection(player,rows,'publish_failed');throw error;}
 traceHeldProjection(player,rows);
}

function syncSafely(player){
 try{syncBottleHeld(player)}catch(error){console.warn('[Grilling held plate/bottle contents] '+error)}
}

world.afterEvents.playerInventoryItemChange.subscribe(e=>{platePlans.delete(e.player.id);system.run(()=>syncSafely(e.player));});
world.afterEvents.playerHotbarSelectedSlotChange.subscribe(e=>{const hands=platePlans.get(e.player.id);if(hands)delete hands.main;system.run(()=>syncSafely(e.player));});
world.afterEvents.playerLeave.subscribe(e=>{signatures.delete(e.playerId);platePlans.delete(e.playerId);heldQa.delete(e.playerId);});
system.runInterval(()=>{for(const player of world.getAllPlayers())syncSafely(player)},5);
