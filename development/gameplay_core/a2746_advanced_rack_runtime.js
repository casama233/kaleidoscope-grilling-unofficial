import {markStationContentsDirty} from './station_contents_visual_runtime.js';
import {planRackInsert,commitRackTransfer,depositInventorySlot} from './rack_transactions.js';
import {slotWrite,remainderOf,planInventoryInsert} from './rack_transfer_plan.js';
import {retireEmptyStationContainer,quarantineStation} from './family_station_storage.js';
import {rackSlotAtHit} from './a285_rack_quick_pick.js';
import {captureInteractionIntent,interactionIntentStillCurrent} from './a2762_interaction_intent_adapter.js';
import {interactionFeedback} from './a283_interaction_feedback.js';
import {
 world,system,ItemStack,CommandPermissionLevel
} from '@minecraft/server';
import {ActionFormData} from '@minecraft/server-ui';
import {
 playerInventory,getMainHand,setMainHand,isCreative as creative
} from './a2735_player_io.js';
import {
 ADVANCED_RACK_ITEM_ID,ADVANCED_RACK_BLOCK_ID,RACK_COMPARTMENTS,RACK_RANGE,
 rackPlacementCandidates,rackCanPlace,rackCanonicalFilter,rackFilterMatches,
 bindingInRange,RACK_PAYLOAD_KEY
} from './a2746_advanced_rack_core.js';
import {
 rackContainer,readRackFilters,writeRackFilters,clearRackFilters,
 readRackItems,writeRackItems,clearRackItems,syncRackDisplay
} from './a2746_rack_state_adapter.js';
import {readRackPayloadItem,writeRackPayloadItem,encodeRackPayload} from './a2746_rack_item_codec.js';
import {awardNeatAndOrderly} from './a2756_advancement_event_runtime.js';

const BIND_PREFIX='kaleidoscope_grilling:rack_binding_';

function loc(block){return {x:block.x,y:block.y,z:block.z}}
function tags(stack){try{return stack?.getTags?.()??[]}catch{return []}}
const message=interactionFeedback;
function resolveRack(dimension,location){
 try{const b=dimension.getBlock(location);return b?.typeId===ADVANCED_RACK_BLOCK_ID?b:undefined}catch{return undefined}
}
function rackInUseRange(player,block){
 if(!player||!block||player.dimension.id!==block.dimension.id)return false;
 const dx=block.x+.5-player.location.x,dy=block.y+.5-player.location.y,dz=block.z+.5-player.location.z;
 return dx*dx+dy*dy+dz*dz<=64;
}
function bindingKey(slot){return BIND_PREFIX+slot}
function readBinding(player,hotbarSlot){
 try{
  const raw=player.getDynamicProperty(bindingKey(hotbarSlot));
  if(typeof raw!=='string')return undefined;
  const b=JSON.parse(raw);
  return b&&Number.isInteger(b.slot)?b:undefined;
 }catch{return undefined}
}
function writeBinding(player,hotbarSlot,block,slot){
 try{
  player.setDynamicProperty(bindingKey(hotbarSlot),JSON.stringify({
   dimension:block.dimension.id,x:block.x,y:block.y,z:block.z,slot
  }));
 }catch{}
}
function clearBinding(player,hotbarSlot){try{player.setDynamicProperty(bindingKey(hotbarSlot),undefined)}catch{}}

function slotRoom(stored,stack){
 if(!stored)return stack.maxAmount;
 if(!stored.isStackableWith(stack))return 0;
 return Math.max(0,stored.maxAmount-stored.amount);
}

function matchingLocalReturnSlot(block,stack,excluded){
 const c=rackContainer(block),filters=readRackFilters(block);if(!c)return -1;
 for(let i=0;i<RACK_COMPARTMENTS;i++){
  if(i===excluded||!filters[i])continue;
  if(!rackCanPlace(i,stack.typeId,tags(stack),filters[i]))continue;
  if(slotRoom(c.getItem(i),stack)>=stack.amount)return i;
 }
 return -1;
}

function boundRackForReturn(player,binding,stack,targetBlock,targetSlot){
 if(!binding||!bindingInRange(binding,player.dimension.id,player.location,RACK_RANGE))return undefined;
 const block=resolveRack(player.dimension,{x:binding.x,y:binding.y,z:binding.z});
 if(!block||(block.x===targetBlock.x&&block.y===targetBlock.y&&block.z===targetBlock.z&&binding.slot===targetSlot))return undefined;
 const c=rackContainer(block),filters=readRackFilters(block),slot=binding.slot;
 if(!c||!rackCanPlace(slot,stack.typeId,tags(stack),filters[slot]))return undefined;
 return slotRoom(c.getItem(slot),stack)>=stack.amount?{block,slot}:undefined;
}

function swapWithHotbar(player,block,slot){
 const c=rackContainer(block),requested=c?.getItem(slot);if(!c||!requested)return false;
 const inv=playerInventory(player),hot=player.selectedSlotIndex,held=inv?.getItem(hot);if(!inv)return false;
 if(held&&held.isStackableWith(requested)){
  const move=Math.min(requested.amount,held.maxAmount-held.amount);
  if(move>0){
   const h=held.clone();h.amount+=move;
   if(!commitRackTransfer([block],[slotWrite(inv,hot,h),slotWrite(c,slot,remainderOf(requested,move))]))return false;
  }
  writeBinding(player,hot,block,slot);return true;
 }
 const blocks=[block],steps=[slotWrite(c,slot,undefined)];
 if(held){
  let target=boundRackForReturn(player,readBinding(player,hot),held,block,slot);
  if(!target){const local=matchingLocalReturnSlot(block,held,slot);if(local>=0)target={block,slot:local};}
  if(target){
   const plan=planRackInsert(target.block,target.slot,held);
   if(!plan||plan.moved!==held.amount)return false;
   steps.push(...plan.steps);blocks.push(target.block);
  }else{
   const plan=planInventoryInsert(inv,held,hot);if(plan.remainder)return false;
   steps.push(...plan.steps);
  }
 }
 steps.push(slotWrite(inv,hot,requested));
 if(!commitRackTransfer(blocks,steps))return false;
 writeBinding(player,hot,block,slot);return true;
}

function depositSelected(player,block,slot){
 const inv=playerInventory(player),index=player.selectedSlotIndex;
 return !!inv&&depositInventorySlot(inv,index,block,slot)>0;
}

function withdrawToInventory(player,block,slot){
 const c=rackContainer(block),stored=c?.getItem(slot),inv=playerInventory(player);if(!c||!stored||!inv)return false;
 const plan=planInventoryInsert(inv,stored);if(!plan.moved)return false;
 return commitRackTransfer([block],[...plan.steps,slotWrite(c,slot,plan.remainder)]);
}

function findMatchingSlotWithRoom(block,stack){
 const c=rackContainer(block),filters=readRackFilters(block);if(!c)return -1;
 for(let i=0;i<RACK_COMPARTMENTS;i++){
  if(!filters[i]||!rackCanPlace(i,stack.typeId,tags(stack),filters[i]))continue;
  if(slotRoom(c.getItem(i),stack)>0)return i;
 }
 return -1;
}

function depositMatching(player,block){
 const inv=playerInventory(player);if(!inv)return false;
 let changed=false;
 for(let hot=0;hot<9;hot++){
  const stack=inv.getItem(hot),binding=readBinding(player,hot);
  if(!stack||!binding)continue;
  if(binding.dimension!==block.dimension.id||binding.x!==block.x||binding.y!==block.y||binding.z!==block.z)continue;
  const move=depositInventorySlot(inv,hot,block,binding.slot);
  if(move<=0)continue;
  clearBinding(player,hot);changed=true;
 }
 for(let i=0;i<Math.min(36,inv.size);i++){
  const stack=inv.getItem(i);if(!stack)continue;
  if(i<9&&readBinding(player,i))continue;
  const slot=findMatchingSlotWithRoom(block,stack);if(slot<0)continue;
  const move=depositInventorySlot(inv,i,block,slot);if(move<=0)continue;
  changed=true;
 }
 return changed;
}

const ui=(key,withArgs=[])=>({translate:'ui.kaleidoscope_grilling.advanced_rack.'+key,with:withArgs});
function filterLabel(filter){
 if(!filter)return ui('no_filter');
 if(filter.category==='oil_pot')return ui('oil_pot');
 if(filter.category==='seasoning_bottle')return ui('seasoning_bottle');
 return {text:filter.typeId};
}
function slotButton(slot,stored,filter){
 const parts=[ui(slot<5?'seasoning':'tool'),{text:' '+(slot+1)+' §8| §f'}];
 if(stored){let key;try{key=stored.localizationKey}catch{};parts.push(key?{translate:key}:{text:stored.typeId},{text:' ×'+stored.amount});}
 else parts.push(ui('empty'),{text:' §7['},filterLabel(filter),{text:']'});
 return {rawtext:parts};
}

async function openSlotForm(player,dimension,location,slot){
 const block=resolveRack(dimension,location);if(!block||!rackInUseRange(player,block))return;
 const c=rackContainer(block),filters=readRackFilters(block),stored=c?.getItem(slot);
 const form=new ActionFormData().title({translate:'container.kaleidoscope_grilling.advanced_rack'});
 form.body({rawtext:[ui('slot',[String(slot+1)]),{text:' · '},ui(slot<5?'seasoning':'tool'),{text:'\n'},filterLabel(filters[slot])]});
 form.button(ui('swap'));
 form.button(ui('insert'));
 form.button(ui('withdraw'));
 form.button(ui('clear_filter'));
 form.button(ui('back'));
 let r;try{r=await form.show(player)}catch{return}
 if(r.canceled)return;
 const live=resolveRack(dimension,location);if(!live||!rackInUseRange(player,live)){message(player,ui('too_far'));return;}
 if(r.selection===0){if(!swapWithHotbar(player,live,slot))message(player,ui('swap_failed'))}
 else if(r.selection===1){if(!depositSelected(player,live,slot))message(player,ui('insert_failed'))}
 else if(r.selection===2){if(!withdrawToInventory(player,live,slot))message(player,ui('inventory_full'))}
 else if(r.selection===3){
  const lc=rackContainer(live),lf=readRackFilters(live);
  if(lc?.getItem(slot))message(player,ui('filter_occupied'));
  else{lf[slot]=null;writeRackFilters(live,lf);}
 }else if(r.selection===4){system.run(()=>openRackForm(player,dimension,location))}
}

export async function openRackForm(player,dimension,location){
 const block=resolveRack(dimension,location);if(!block||!rackInUseRange(player,block))return;
 const c=rackContainer(block),filters=readRackFilters(block);if(!c)return;
 const form=new ActionFormData().title({translate:'container.kaleidoscope_grilling.advanced_rack'});
 form.body({translate:'ui.kaleidoscope_grilling.advanced_rack.hint'});
 for(let i=0;i<RACK_COMPARTMENTS;i++)form.button(slotButton(i,c.getItem(i),filters[i]));
 form.button({translate:'ui.kaleidoscope_grilling.advanced_rack.deposit'});
 form.button(ui('manage'));
 let r;try{r=await form.show(player)}catch{return}
 if(r.canceled)return;
 if(r.selection>=0&&r.selection<RACK_COMPARTMENTS){
  const live=resolveRack(dimension,location);if(live&&!rackInUseRange(player,live)){message(player,ui('too_far'));return;}if(live){if(!swapWithHotbar(player,live,r.selection))message(player,ui('swap_failed'));markStationContentsDirty(live);}
 }else if(r.selection===RACK_COMPARTMENTS+1)system.run(()=>openRackManagement(player,dimension,location));
 else if(r.selection===RACK_COMPARTMENTS){
  const live=resolveRack(dimension,location);
  if(live&&!rackInUseRange(player,live)){message(player,ui('too_far'));return}
  if(!live||!depositMatching(player,live))message(player,ui('no_match'));
 }
}

async function openRackManagement(player,dimension,location){
 const block=resolveRack(dimension,location);if(!block||!rackInUseRange(player,block))return;
 const c=rackContainer(block),filters=readRackFilters(block);if(!c)return;
 const form=new ActionFormData().title(ui('manage'));
 for(let i=0;i<RACK_COMPARTMENTS;i++)form.button(slotButton(i,c.getItem(i),filters[i]));
 let r;try{r=await form.show(player)}catch{return}
 if(!r.canceled&&r.selection>=0&&r.selection<RACK_COMPARTMENTS)system.run(()=>openSlotForm(player,dimension,location,r.selection));
}

function restorePlacedRack(block,item){
 const raw=item.getDynamicProperty(RACK_PAYLOAD_KEY),payload=readRackPayloadItem(item);
 if(raw!==undefined&&encodeRackPayload(payload.items,payload.filters)!==raw)
  throw new Error('Packed rack metadata cannot round-trip; refusing partial restore');
 const existing=readRackItems(block);
 if(existing.some(Boolean))throw new Error('Refusing to overwrite occupied backing inventory');
 if(!writeRackItems(block,payload.items)||!writeRackFilters(block,payload.filters)){
  quarantineStation(block,'packed placement commit incomplete');
  throw new Error('Packed rack restore incomplete; inventory quarantined');
 }
 syncRackDisplay(block);markStationContentsDirty(block);return true;
}

function scheduleRackPlacement(event){
 if(event.isFirstEvent===false||event.itemStack?.typeId!==ADVANCED_RACK_ITEM_ID)return;
 const snapshot=event.itemStack.clone(),dimension=event.block.dimension,player=event.player;
 const candidates=rackPlacementCandidates(event.block.location,event.blockFace)
  .map(location=>({location,wasRack:dimension.getBlock(location)?.typeId===ADVANCED_RACK_BLOCK_ID}));
 system.run(()=>{
  for(const row of candidates){
   if(row.wasRack)continue;
   const block=dimension.getBlock(row.location);
   if(block?.typeId===ADVANCED_RACK_BLOCK_ID){restorePlacedRack(block,snapshot);awardNeatAndOrderly(player);return}
  }
 });
}

function createRackDrop(block){
 const items=readRackItems(block),filters=readRackFilters(block);
 const drop=new ItemStack(ADVANCED_RACK_ITEM_ID,1);
 return writeRackPayloadItem(drop,items,filters);
}
function manuallyBreakRack(block,drop=true){
 if(!block||block.typeId!==ADVANCED_RACK_BLOCK_ID)return false;
 const dimension=block.dimension,location=loc(block),permutation=block.permutation;
 let items,filters,item,escrow;
 try{
  items=readRackItems(block);filters=readRackFilters(block);
  const raw=encodeRackPayload(items,filters);
  item=writeRackPayloadItem(new ItemStack(ADVANCED_RACK_ITEM_ID,1),items,filters);
  if(item.getDynamicProperty(RACK_PAYLOAD_KEY)!==raw)throw new Error('Packed rack payload was not saved');
  const check=readRackPayloadItem(item);
  if(encodeRackPayload(check.items,check.filters)!==raw)throw new Error('Rack item metadata cannot round-trip');
  if(drop)escrow=dimension.spawnItem(item,{x:location.x+.5,y:location.y+.35,z:location.z+.5});
 }catch(error){console.warn('[Grilling rack break preparation] '+error);return false}
 try{
  if(!clearRackItems(block)||!clearRackFilters(block))throw new Error('rack state commit failed');
  block.setType('minecraft:air');
 }catch(error){
  try{escrow?.remove()}catch(cleanup){quarantineStation(block,'escrow removal unconfirmed');console.warn('[Grilling rack quarantine] '+cleanup);return false}
  try{const live=dimension.getBlock(location);live.setPermutation(permutation);if(!writeRackItems(live,items)||!writeRackFilters(live,filters))throw new Error('rollback commit failed')}catch(restore){quarantineStation(block,'rollback incomplete');console.warn('[Grilling rack rollback] '+restore)}
  console.warn('[Grilling rack break] '+error);return false;
 }
 try{retireEmptyStationContainer(dimension.getBlock(location))}catch(error){console.warn('[Grilling storage retirement] '+error)}
 return true;
}

function nearestRack(player){
 const d=player.dimension,p=player.location;let best,bestD=RACK_RANGE*RACK_RANGE+.001;
 const ox=Math.floor(p.x),oy=Math.floor(p.y),oz=Math.floor(p.z);
 for(let x=ox-RACK_RANGE;x<=ox+RACK_RANGE;x++)for(let y=oy-RACK_RANGE;y<=oy+RACK_RANGE;y++)for(let z=oz-RACK_RANGE;z<=oz+RACK_RANGE;z++){
  const dx=x+.5-p.x,dy=y+.5-p.y,dz=z+.5-p.z,d2=dx*dx+dy*dy+dz*dz;
  if(d2>bestD)continue;
  const b=d.getBlock({x,y,z});if(b?.typeId!==ADVANCED_RACK_BLOCK_ID)continue;
  best=b;bestD=d2;
 }
 return best;
}

world.beforeEvents.playerInteractWithBlock.subscribe(event=>{
 if(event.cancel)return;
 if(event.block.typeId===ADVANCED_RACK_BLOCK_ID){
  event.cancel=true;
  if(event.isFirstEvent!==false){
   const p=event.player,d=event.block.dimension,l=loc(event.block);
   if(p.isSneaking){
    const slot=rackSlotAtHit(event.block.permutation.getState('minecraft:cardinal_direction'),event.faceLocation),intent=captureInteractionIntent(p,event.itemStack);
    system.run(()=>{
     const live=resolveRack(d,l);if(slot<0||!live||!rackInUseRange(p,live)||!interactionIntentStillCurrent(p,intent))return;
     if(!swapWithHotbar(p,live,slot))message(p,ui('slot_unavailable'));
    });
   }else system.run(()=>openRackForm(p,d,l));
  }
  return;
 }
 try{scheduleRackPlacement(event)}catch{}
});
world.beforeEvents.playerBreakBlock.subscribe(event=>{
 if(event.block.typeId!==ADVANCED_RACK_BLOCK_ID)return;
 event.cancel=true;const block=event.block,drop=!creative(event.player);
 system.run(()=>manuallyBreakRack(block,drop));
});
world.beforeEvents.explosion.subscribe(event=>{
 const keep=[],racks=[];
 for(const block of event.getImpactedBlocks()){
  if(block.typeId===ADVANCED_RACK_BLOCK_ID)racks.push(block);else keep.push(block);
 }
 if(!racks.length)return;
 event.setImpactedBlocks(keep);system.run(()=>{for(const block of racks)manuallyBreakRack(block,true)});
});

system.beforeEvents.startup.subscribe(event=>{
 event.customCommandRegistry.registerCommand({
  name:'kaleidoscope_grilling:rack',
  description:'Open the nearest Advanced Rack within 8 blocks',
  permissionLevel:CommandPermissionLevel.Any,
  cheatsRequired:false
 },origin=>{
  const player=origin.sourceEntity;
  if(!player||player.typeId!=='minecraft:player')return;
  system.run(()=>{
   const rack=nearestRack(player);
   if(!rack)message(player,ui('not_found'));
   else openRackForm(player,rack.dimension,loc(rack));
  });
 });
});
