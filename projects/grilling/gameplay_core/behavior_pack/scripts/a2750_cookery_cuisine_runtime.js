import {world,system,ItemStack} from '@minecraft/server';
import {EMPTY_SEASONING_ID,SEASONING_ID} from './data.js';
import {playerInventory,getMainHand,setMainHand,getHand,isCreative} from './a2735_player_io.js';
import {captureInteractionIntent,interactionIntentStillCurrent} from './interaction_intent.js';
import {readCookeryOilPot} from './a2734_cookery_oil_pot_adapter.js';
import {SEASONING_MAX_USES,SEASONING_USES_KEY} from './a2743_seasoning_contract_core.js';
import {
 readFoodSeasonings,setFoodSeasonings,setHotFood,applyFoodMetadata
} from './a2750_food_state_adapter.js';
import {
 COOKERY_POT_ID,COOKERY_STOCKPOT_ID,COOKERY_FILLED_OIL_POT_ID,
 cuisineStateKey,cuisineStateKeyAt,normalizeCuisineState,stationKind,
 oilTypeFromHeld,planSeasoningUse,inventoryGains,metadataPlan,
 stateBeforeSeasoning,planPotOilTransition
} from './a2750_cookery_cuisine_core.js';

function message(player,text){try{player.onScreenDisplay.setActionBar(text)}catch{}}
function isFirst(event){return event.isFirstEvent!==false}
function readCuisineState(block){
 try{
  const raw=world.getDynamicProperty(cuisineStateKey(block));
  return normalizeCuisineState(typeof raw==='string'?JSON.parse(raw):{});
 }catch{return normalizeCuisineState({})}
}
function writeCuisineState(block,state){
 try{
  const normalized=normalizeCuisineState(state);
  const empty=!normalized.seasoning.length&&!normalized.oilType&&!normalized.lastOutputTick;
  world.setDynamicProperty(cuisineStateKey(block),empty?undefined:JSON.stringify(normalized));return true;
 }catch{return false}
}
function clearCuisineAt(dimensionId,location){
 try{world.setDynamicProperty(cuisineStateKeyAt(dimensionId,location.x,location.y,location.z),undefined);return true}catch{return false}
}
function hostHasOil(block){
 try{return block?.permutation?.getState('kaleidoscope_cookery:has_oil')===true}catch{return false}
}
function primitiveProps(stack){
 const out={};let ids=[];try{ids=stack?.getDynamicPropertyIds()??[]}catch{}
 for(const id of ids)try{
  const value=stack.getDynamicProperty(id);
  if(['string','number','boolean'].includes(typeof value))out[id]=value;
  else if(value&&typeof value==='object'&&Number.isFinite(value.x)&&Number.isFinite(value.y)&&Number.isFinite(value.z))
   out[id]={x:value.x,y:value.y,z:value.z};
 }catch{}
 return out;
}
function descriptor(stack){
 if(!stack)return null;let lore=[],name='',damage=null;
 try{lore=stack.getLore()}catch{}try{name=stack.nameTag??''}catch{}
 try{damage=Number(stack.getComponent('minecraft:durability')?.damage??0)}catch{}
 return {id:stack.typeId,amount:Number(stack.amount)||1,name,lore,props:primitiveProps(stack),damage};
}
function snapshotInventory(player){
 const c=playerInventory(player);if(!c)return [];
 const rows=[];for(let i=0;i<c.size;i++)rows.push(descriptor(c.getItem(i)));return rows;
}
function foodLike(stack){if(!stack)return false;try{return !!stack.getComponent('minecraft:food')}catch{return false}}
function giveCustom(player,stack){
 const c=playerInventory(player);
 if(!c){try{player.dimension.spawnItem(stack,player.location)}catch{};return}
 try{const rem=c.addItem(stack);if(rem)player.dimension.spawnItem(rem,player.location)}
 catch{try{player.dimension.spawnItem(stack,player.location)}catch{}}
}
function rewriteGain(player,gain,plan){
 const c=playerInventory(player);if(!c)return false;
 const current=c.getItem(gain.slot);
 if(!current||current.typeId!==gain.id||current.amount<gain.count||!foodLike(current))return false;
 const custom=current.clone();custom.amount=gain.count;applyFoodMetadata(custom,plan);
 const remain=current.amount-gain.count;
 if(remain>0){current.amount=remain;c.setItem(gain.slot,current);giveCustom(player,custom)}
 else c.setItem(gain.slot,custom);
 return true;
}
function typedHeldOil(stack){
 if(!stack)return '';
 if(stack.typeId===COOKERY_FILLED_OIL_POT_ID){
  const state=readCookeryOilPot(stack);return oilTypeFromHeld(stack.typeId,state?.type??'');
 }
 return oilTypeFromHeld(stack.typeId,'');
}
function readUses(stack){
 try{return Math.max(0,Math.min(SEASONING_MAX_USES,Number(stack?.getDynamicProperty(SEASONING_USES_KEY)??0)|0))}catch{return 0}
}
function setUses(stack,n){
 try{stack.setDynamicProperty(SEASONING_USES_KEY,Math.max(0,Math.min(SEASONING_MAX_USES,n|0)))}catch{}return stack;
}
function applySeasoning(player,block){
 const held=getMainHand(player);if(held?.typeId!==SEASONING_ID)return false;
 const ingredients=readFoodSeasonings(held),uses=readUses(held);
 const plan=planSeasoningUse({ingredients,uses,creative:isCreative(player)});
 if(!plan.ok){message(player,'§7調料瓶內沒有可用調料');return true}
 const state=stateBeforeSeasoning(stationKind(block.typeId),readCuisineState(block),hostHasOil(block));
 if(!writeCuisineState(block,{...state,seasoning:plan.ingredients})){message(player,'§c鍋具調料狀態寫入失敗');return true}
 if(plan.mutate){
  if(plan.replaceEmpty)setMainHand(player,new ItemStack(EMPTY_SEASONING_ID,1));
  else{
   const next=held.clone();setUses(next,plan.nextUses);
   try{
    const lore=next.getLore().filter(x=>!String(x).startsWith('§7Uses:'));
    lore.unshift('§7Uses: '+(SEASONING_MAX_USES-plan.nextUses)+'/'+SEASONING_MAX_USES);next.setLore(lore);
   }catch{}
   setMainHand(player,next);
  }
 }
 try{player.playAnimation('animation.kg_imm.player.season.main',{blendOutTime:.12})}catch{}
 try{player.playSound('kg_imm.season',{volume:.85,pitch:1})}catch{}
 message(player,'§a已向 Cookery 鍋具加入特製調料');return true;
}
function finishHostInteraction(player,dimension,location,kind,beforeInventory,beforeHasOil,candidateOil,stateBefore){
 const block=dimension.getBlock(location),afterInventory=snapshotInventory(player),gains=inventoryGains(beforeInventory,afterInventory);
 const afterHasOil=kind==='pot'&&block?.typeId===COOKERY_POT_ID?hostHasOil(block):false;
 if(kind==='pot'){
  const transition=planPotOilTransition(stateBefore,beforeHasOil,afterHasOil,candidateOil);
  if(transition.changed&&block?.typeId===COOKERY_POT_ID)writeCuisineState(block,transition.state);
 }
 const effective={...stateBefore,oilType:kind==='pot'?(stateBefore.oilType||(beforeHasOil?'default':'')):stateBefore.oilType};
 const plan=metadataPlan(kind,effective);
 let decorated=0;for(const gain of gains)if(rewriteGain(player,gain,plan))decorated++;
 if(decorated>0){
  if(kind==='pot')clearCuisineAt(dimension.id,location);
  else if(block?.typeId===COOKERY_STOCKPOT_ID)writeCuisineState(block,{...stateBefore,lastOutputTick:system.currentTick});
 }
}
world.beforeEvents.playerInteractWithBlock.subscribe(event=>{
 try{
  const kind=stationKind(event.block?.typeId);if(!kind)return;
  const player=event.player,intent=captureInteractionIntent(player,event.itemStack),hand=intent.hand,used=getHand(player,hand);
  if(hand==='main'&&used?.typeId===SEASONING_ID){
   event.cancel=true;if(!isFirst(event))return;const dimension=event.block.dimension,location={...event.block.location};
   system.run(()=>{if(!interactionIntentStillCurrent(player,intent)){message(player,'§7操作已取消：互動後手持物品已改變');return}const block=dimension.getBlock(location);if(block&&stationKind(block.typeId)===kind)applySeasoning(player,block)});return;
  }
  if(!isFirst(event))return;
  const dimension=event.block.dimension,location={...event.block.location};
  const stateBefore=readCuisineState(event.block),beforeInventory=snapshotInventory(player);
  const beforeHasOil=kind==='pot'?hostHasOil(event.block):false,candidateOil=kind==='pot'?typedHeldOil(used):'';
  system.run(()=>finishHostInteraction(player,dimension,location,kind,beforeInventory,beforeHasOil,candidateOil,stateBefore));
 }catch{}
});
world.beforeEvents.playerBreakBlock.subscribe(event=>{
 try{
  if(!stationKind(event.block?.typeId))return;
  const dimensionId=event.block.dimension.id,location={...event.block.location};system.run(()=>clearCuisineAt(dimensionId,location));
 }catch{}
});
world.beforeEvents.explosion.subscribe(event=>{
 try{
  const rows=[];
  for(const block of event.getImpactedBlocks())if(stationKind(block?.typeId))rows.push({dimensionId:block.dimension.id,location:{...block.location}});
  if(rows.length)system.run(()=>{for(const row of rows)clearCuisineAt(row.dimensionId,row.location)});
 }catch{}
});
export function readCuisineExtensionState(block){return readCuisineState(block)}
