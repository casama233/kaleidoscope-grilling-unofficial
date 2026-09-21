import {world,system,GameMode,EquipmentSlot} from '@minecraft/server';
import {
 BOARD_ID,BEEF_ID,BEEF_CHUNKS_ID,
 stationKey,canonicalBeefState,classifyBoardState,overrideBuiltInBeefState,interactionDecision
} from './a279_beef_board_core.js';

function pos(block){
 const l=block?.location??block;
 return {x:Number(l?.x??0),y:Number(l?.y??0),z:Number(l?.z??0)};
}
function keyFor(block){
 const p=pos(block);
 return stationKey(block.dimension.id,p.x,p.y,p.z);
}
function rawState(block){try{return world.getDynamicProperty(keyFor(block))}catch{return undefined}}
function parseState(raw){
 if(raw===undefined||raw===null||raw==='')return {};
 try{return JSON.parse(String(raw))}catch{return {}}
}
function readState(block){return parseState(rawState(block))}
function mainSlot(player){try{return player.getComponent('minecraft:equippable')?.getEquipmentSlot(EquipmentSlot.Mainhand)}catch{return undefined}}
function heldMain(player){const s=mainSlot(player);try{return s?.hasItem()?s.getItem():undefined}catch{return undefined}}
function primitiveProps(stack){
 const out={};let ids=[];try{ids=stack.getDynamicPropertyIds()}catch{}
 for(const id of ids.sort())try{
  const v=stack.getDynamicProperty(id);
  if(['string','number','boolean'].includes(typeof v))out[id]=v;
  else if(v&&typeof v==='object'&&Number.isFinite(v.x)&&Number.isFinite(v.y)&&Number.isFinite(v.z))out[id]={x:v.x,y:v.y,z:v.z};
 }catch{}
 return out;
}
function signature(stack){
 if(!stack)return null;
 let lore=[];try{lore=stack.getLore()}catch{}
 let name='';try{name=stack.nameTag??''}catch{}
 return JSON.stringify({id:stack.typeId,amount:Number(stack.amount)||1,name,lore,props:primitiveProps(stack)});
}
function captureIntent(player,stack){
 return {selectedSlot:Number(player.selectedSlotIndex??0),signature:signature(stack)};
}
function intentCurrent(player,intent){
 return Number(player.selectedSlotIndex??0)===intent.selectedSlot&&signature(heldMain(player))===intent.signature;
}
function creative(player){try{return player.getGameMode()===GameMode.Creative}catch{return false}}
function setMain(player,stack){
 const s=mainSlot(player);if(!s)throw new Error('missing main-hand slot');
 s.setItem(stack);
}
function mainMatches(player,expected){
 const now=heldMain(player);
 if(!expected)return !now;
 return !!now&&now.typeId===expected.typeId&&Number(now.amount)===Number(expected.amount)&&signature(now)===signature(expected);
}
function writeStateRaw(block,value){world.setDynamicProperty(keyFor(block),value)}
function writeState(block,state){writeStateRaw(block,JSON.stringify(state))}
function verifyCanonical(block){if(classifyBoardState(readState(block))!=='canonical_beef')throw new Error('station state verification failed')}
function applyBeefVisual(block,cuts=0){
 let p=block.permutation
  .withState('kaleidoscope_cookery:board_has_food',true)
  .withState('kaleidoscope_cookery:board_model',0)
  .withState('kaleidoscope_cookery:extension_board_model',0)
  .withState('kaleidoscope_cookery:cut_stage',Math.max(0,Math.min(5,Number(cuts)||0)));
 block.setPermutation(p);
 const q=block.permutation;
 if(q.getState('kaleidoscope_cookery:board_has_food')!==true
   ||q.getState('kaleidoscope_cookery:board_model')!==0
   ||q.getState('kaleidoscope_cookery:extension_board_model')!==0)throw new Error('board visual verification failed');
}
function patchBuiltIn(block){
 const state=readState(block),next=overrideBuiltInBeefState(state);
 if(!next)return false;
 try{writeState(block,next);verifyCanonical(block);return true}
 catch(error){try{writeState(block,state)}catch{};try{console.warn('[Kaleidoscope Grilling] beef board migration failed: '+error)}catch{};return false}
}
function commitEmpty(block,player,intent){
 const beforeRaw=rawState(block),beforeState=parseState(beforeRaw),kind=classifyBoardState(beforeState);
 if(kind==='builtin_beef')return patchBuiltIn(block);
 if(kind==='canonical_beef')return true;
 if(kind!=='empty'||!intentCurrent(player,intent))return false;
 const current=heldMain(player);if(current?.typeId!==BEEF_ID)return false;
 const beforeHand=current.clone(),beforePermutation=block.permutation,isCreative=creative(player);
 let nextHand;
 if(!isCreative){
  if(Number(beforeHand.amount)<=1)nextHand=undefined;
  else{nextHand=beforeHand.clone();nextHand.amount=Number(nextHand.amount)-1}
 }
 try{
  writeState(block,canonicalBeefState());
  verifyCanonical(block);
  applyBeefVisual(block,0);
  if(!isCreative){
   setMain(player,nextHand);
   if(!mainMatches(player,nextHand))throw new Error('main-hand verification failed');
  }
  try{player.playSound('dig.wood',{pitch:1.2})}catch{}
  return true;
 }catch(error){
  let rollbackErrors=0;
  if(!isCreative)try{setMain(player,beforeHand)}catch{rollbackErrors++}
  try{writeStateRaw(block,beforeRaw)}catch{rollbackErrors++}
  try{block.setPermutation(beforePermutation)}catch{rollbackErrors++}
  try{console.warn(`[Kaleidoscope Grilling] beef board transaction rolled back (${rollbackErrors} rollback errors): ${error}`)}catch{}
  return false;
 }
}
function scheduleInsert(event){
 const player=event.player,dimension=event.block.dimension,location=pos(event.block),stack=heldMain(player),intent=captureIntent(player,stack);
 system.run(()=>{
  try{
   const block=dimension.getBlock(location);
   if(!block||block.typeId!==BOARD_ID)return;
   commitEmpty(block,player,intent);
  }catch{}
 });
}
function scheduleMigration(event){
 const dimension=event.block.dimension,location=pos(event.block);
 system.run(()=>{
  try{
   const block=dimension.getBlock(location);
   if(block?.typeId===BOARD_ID)patchBuiltIn(block);
  }catch{}
 });
}

export function tryScheduleBeefBoardOverride(event){
 try{
  if(event?.cancel===true)return false;
  const block=event?.block,player=event?.player;if(!block||!player)return false;
  const state=readState(block),main=heldMain(player);
  const decision=interactionDecision({
   blockId:block.typeId,state,mainId:main?.typeId??'',eventId:event.itemStack?.typeId??'',isFirstEvent:event.isFirstEvent
  });
  if(decision==='ignore')return false;
  event.cancel=true;
  if(decision==='insert')scheduleInsert(event);
  else if(decision==='migrate')scheduleMigration(event);
  return true;
 }catch{return false}
}
