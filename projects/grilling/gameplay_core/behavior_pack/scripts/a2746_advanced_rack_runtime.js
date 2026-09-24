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
 bindingInRange
} from './a2746_advanced_rack_core.js';
import {
 rackContainer,readRackFilters,writeRackFilters,clearRackFilters,
 readRackItems,writeRackItems,clearRackItems,syncRackDisplay
} from './a2746_rack_state_adapter.js';
import {readRackPayloadItem,writeRackPayloadItem} from './a2746_rack_item_codec.js';
import {awardNeatAndOrderly} from './a2756_advancement_event_runtime.js';

const BIND_PREFIX='kaleidoscope_grilling:rack_binding_';

function loc(block){return {x:block.x,y:block.y,z:block.z}}
function tags(stack){try{return stack?.getTags?.()??[]}catch{return []}}
function message(player,text){try{player.onScreenDisplay.setActionBar(text)}catch{}}
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

function insertIntoRack(block,slot,stack,amount=stack?.amount??0){
 const c=rackContainer(block);if(!c||!stack)return 0;
 const filters=readRackFilters(block),filter=filters[slot];
 if(!rackCanPlace(slot,stack.typeId,tags(stack),filter))return 0;
 const stored=c.getItem(slot),room=slotRoom(stored,stack),move=Math.min(room,amount,stack.amount);
 if(move<=0)return 0;
 if(!filters[slot]){
  filters[slot]=rackCanonicalFilter(stack.typeId,tags(stack));
  writeRackFilters(block,filters);
 }
 if(!stored){const next=stack.clone();next.amount=move;c.setItem(slot,next)}
 else{const next=stored.clone();next.amount=stored.amount+move;c.setItem(slot,next)}
 syncRackDisplay(block);return move;
}

function canStoreInInventoryExcept(inv,excluded,stack){
 let remaining=stack.amount;
 for(let i=0;i<Math.min(36,inv?.size??0)&&remaining>0;i++){
  if(i===excluded)continue;
  const stored=inv.getItem(i);
  if(!stored)remaining-=stack.maxAmount;
  else if(stored.isStackableWith(stack))remaining-=Math.max(0,stored.maxAmount-stored.amount);
 }
 return remaining<=0;
}
function storeInInventoryExcept(inv,excluded,stack){
 let remaining=stack.clone();
 for(let i=0;i<Math.min(36,inv?.size??0)&&remaining;i++){
  if(i===excluded)continue;
  const stored=inv.getItem(i);
  if(!stored||!stored.isStackableWith(remaining))continue;
  const move=Math.min(remaining.amount,stored.maxAmount-stored.amount);
  if(move<=0)continue;
  const next=stored.clone();next.amount=stored.amount+move;inv.setItem(i,next);
  if(move>=remaining.amount)remaining=undefined;
  else{const r=remaining.clone();r.amount=remaining.amount-move;remaining=r}
 }
 for(let i=0;i<Math.min(36,inv?.size??0)&&remaining;i++){
  if(i===excluded||inv.getItem(i))continue;
  inv.setItem(i,remaining);remaining=undefined;
 }
 return remaining;
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
   const h=held.clone();h.amount=held.amount+move;inv.setItem(hot,h);
   if(move>=requested.amount)c.setItem(slot,undefined);
   else{const r=requested.clone();r.amount=requested.amount-move;c.setItem(slot,r)}
  }
  writeBinding(player,hot,block,slot);syncRackDisplay(block);return true;
 }

 let returnTarget;
 if(held){
  returnTarget=boundRackForReturn(player,readBinding(player,hot),held,block,slot);
  if(!returnTarget){
   const local=matchingLocalReturnSlot(block,held,slot);
   if(local>=0)returnTarget={block,slot:local};
  }
  if(!returnTarget&&!canStoreInInventoryExcept(inv,hot,held))return false;
 }

 const replacement=requested.clone();
 c.setItem(slot,undefined);
 if(held){
  if(returnTarget)insertIntoRack(returnTarget.block,returnTarget.slot,held,held.amount);
  else storeInInventoryExcept(inv,hot,held);
 }
 inv.setItem(hot,replacement);
 writeBinding(player,hot,block,slot);syncRackDisplay(block);
 return true;
}

function depositSelected(player,block,slot){
 const held=getMainHand(player);if(!held)return false;
 const moved=insertIntoRack(block,slot,held,held.amount);if(moved<=0)return false;
 if(moved>=held.amount)setMainHand(player,undefined);
 else{const next=held.clone();next.amount=held.amount-moved;setMainHand(player,next)}
 return true;
}

function withdrawToInventory(player,block,slot){
 const c=rackContainer(block),stored=c?.getItem(slot),inv=playerInventory(player);if(!c||!stored||!inv)return false;
 const remainder=inv.addItem(stored.clone());
 if(!remainder)c.setItem(slot,undefined);else c.setItem(slot,remainder);
 syncRackDisplay(block);return !remainder||remainder.amount<stored.amount;
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
  const move=insertIntoRack(block,binding.slot,stack,stack.amount);
  if(move<=0)continue;
  if(move>=stack.amount)inv.setItem(hot,undefined);else{const next=stack.clone();next.amount=stack.amount-move;inv.setItem(hot,next)}
  clearBinding(player,hot);changed=true;
 }
 for(let i=0;i<Math.min(36,inv.size);i++){
  const stack=inv.getItem(i);if(!stack)continue;
  if(i<9&&readBinding(player,i))continue;
  const slot=findMatchingSlotWithRoom(block,stack);if(slot<0)continue;
  const move=insertIntoRack(block,slot,stack,stack.amount);if(move<=0)continue;
  if(move>=stack.amount)inv.setItem(i,undefined);else{const next=stack.clone();next.amount=stack.amount-move;inv.setItem(i,next)}
  changed=true;
 }
 return changed;
}

function filterLabel(filter){
 if(!filter)return '§8無篩選';
 if(filter.category==='oil_pot')return '§7油壺';
 if(filter.category==='seasoning_bottle')return '§7調料瓶';
 return '§7'+filter.typeId;
}
function slotButton(slot,stored,filter){
 const kind=slot<5?'§6調料':'§b工具';
 if(stored){
  let key;try{key=stored.localizationKey}catch{}
  return {rawtext:[{text:kind+' '+(slot+1)+' §8| §f'},key?{translate:key}:{text:stored.typeId},{text:' ×'+stored.amount}]};
 }
 return {text:kind+' '+(slot+1)+' §8| §8空 §7['+filterLabel(filter).replace(/§./g,'')+']'};
}

async function openSlotForm(player,dimension,location,slot){
 const block=resolveRack(dimension,location);if(!block||!rackInUseRange(player,block))return;
 const c=rackContainer(block),filters=readRackFilters(block),stored=c?.getItem(slot);
 const form=new ActionFormData().title({translate:'container.kaleidoscope_grilling.advanced_rack'});
 form.body('§7槽位 '+(slot+1)+' · '+(slot<5?'調料':'工具')+'\n'+filterLabel(filters[slot]));
 form.button('§e與目前快捷欄交換');
 form.button('§a存入目前快捷欄物品');
 form.button('§b取回到背包');
 form.button('§c清除篩選（槽位需為空）');
 form.button('§7返回');
 let r;try{r=await form.show(player)}catch{return}
 if(r.canceled)return;
 const live=resolveRack(dimension,location);if(!live||!rackInUseRange(player,live)){message(player,'§7距離廚具架太遠，操作已取消');return;}
 if(r.selection===0){if(!swapWithHotbar(player,live,slot))message(player,'§c無法交換：請確認槽位分類與背包空間')}
 else if(r.selection===1){if(!depositSelected(player,live,slot))message(player,'§c無法存入：物品分類或篩選不符合')}
 else if(r.selection===2){if(!withdrawToInventory(player,live,slot))message(player,'§c背包沒有足夠空間')}
 else if(r.selection===3){
  const lc=rackContainer(live),lf=readRackFilters(live);
  if(lc?.getItem(slot))message(player,'§c槽位有物品時不能清除篩選');
  else{lf[slot]=null;writeRackFilters(live,lf);message(player,'§a已清除槽位 '+(slot+1)+' 的篩選')}
 }else if(r.selection===4){system.run(()=>openRackForm(player,dimension,location))}
}

export async function openRackForm(player,dimension,location){
 const block=resolveRack(dimension,location);if(!block||!rackInUseRange(player,block))return;
 const c=rackContainer(block),filters=readRackFilters(block);if(!c)return;
 const form=new ActionFormData().title({translate:'container.kaleidoscope_grilling.advanced_rack'});
 form.body({translate:'ui.kaleidoscope_grilling.advanced_rack.hint'});
 for(let i=0;i<RACK_COMPARTMENTS;i++)form.button(slotButton(i,c.getItem(i),filters[i]));
 form.button({translate:'ui.kaleidoscope_grilling.advanced_rack.deposit'});
 let r;try{r=await form.show(player)}catch{return}
 if(r.canceled)return;
 if(r.selection>=0&&r.selection<RACK_COMPARTMENTS)system.run(()=>openSlotForm(player,dimension,location,r.selection));
 else if(r.selection===RACK_COMPARTMENTS){
  const live=resolveRack(dimension,location);
  if(live&&!rackInUseRange(player,live)){message(player,'§7距離廚具架太遠，操作已取消');return}
  if(live&&depositMatching(player,live))message(player,'§a已存入所有符合既有篩選的物品');
  else message(player,'§7沒有可存入的符合物品');
 }
}

function restorePlacedRack(block,item){
 const payload=readRackPayloadItem(item);
 writeRackItems(block,payload.items);
 writeRackFilters(block,payload.filters);
 syncRackDisplay(block);
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
 const dimension=block.dimension,location=loc(block),item=createRackDrop(block);
 clearRackItems(block);clearRackFilters(block);
 try{block.setType('minecraft:air')}catch{return false}
 if(drop)try{dimension.spawnItem(item,{x:location.x+.5,y:location.y+.35,z:location.z+.5})}catch{}
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
  if(event.isFirstEvent!==false){const p=event.player,d=event.block.dimension,l=loc(event.block);system.run(()=>openRackForm(p,d,l))}
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
   if(!rack)message(player,'§c附近 8 格內找不到高級廚具架');
   else openRackForm(player,rack.dimension,loc(rack));
  });
 });
});
