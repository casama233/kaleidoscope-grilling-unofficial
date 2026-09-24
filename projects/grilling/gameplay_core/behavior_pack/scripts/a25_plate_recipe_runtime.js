import {world,system,ItemStack} from '@minecraft/server';
import {
 SECRET_ID,SKEWER_INGREDIENTS_KEY,SECRET_COOKED_KEY,SECRET_CREATOR_KEY,secretFood,recipeTable
} from './a24_skewering_core.js';
import {
 PLATE_ID,PLATE_BLOCK_ID,BOOK_ID,RECIPE_BLOCK_ID,PLATE_SKEWERS_KEY,BOOK_RECORD_KEY,PLATE_CAPACITY,
 normalizePlateRows,plateAdd,plateRemoveLast,isRecordableRecipe,makeBookRecord,bookIngredientSlots,planInventoryConsumption
} from './a25_plate_recipe_core.js';
import {playerInventory as mainContainer,getMainHand as heldMain,setMainHand as setMain,getOffHand as heldOff,setOffHand as setOff,getHand as heldByHand,setHand,isCreative as creative} from './a2735_player_io.js';
import {isInitialBlockPress} from './a275_grill_input_core.js';
import {captureInteractionIntent,interactionIntentStillCurrent} from './interaction_intent.js';

const COOKERY_RECIPE_ITEMS=new Set([
 'kaleidoscope_cookery:recipe_block',
 'kaleidoscope_cookery:recipe',
 'kaleidoscope_cookery:recipe_item'
]);
const COOKERY_TABLE='kaleidoscope_cookery:table';
const PLATE_PREFIX='kaleidoscope_grilling:a25_plate_';
const RECIPE_PREFIX='kaleidoscope_grilling:a25_recipe_';
const FIXED_IDS=new Set();
for(const r of recipeTable()){FIXED_IDS.add(r.id);if(r.cooked)FIXED_IDS.add(r.cooked)}
for(const id of ['kaleidoscope_grilling:mysterious_skewer','kaleidoscope_grilling:dark_grilling'])FIXED_IDS.add(id);

function enc(n){return n<0?'m'+Math.abs(n):'p'+n}
function posKey(prefix,block){return prefix+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z)}
function message(player,text){try{player.onScreenDisplay.setActionBar(text)}catch{}}
function cloneOne(stack){const out=stack.clone();out.amount=1;return out}
function decrementMain(player,count=1){
 if(creative(player))return true;const s=heldMain(player);if(!s||s.amount<count)return false;
 if(s.amount===count)setMain(player,undefined);else{s.amount-=count;setMain(player,s)}return true;
}
function decrementOff(player,count=1){
 if(creative(player))return true;const s=heldOff(player);if(!s||s.amount<count)return false;
 if(s.amount===count)setOff(player,undefined);else{s.amount-=count;setOff(player,s)}return true;
}
function decrementHand(player,hand,count=1){
 if(creative(player))return true;const s=heldByHand(player,hand);if(!s||s.amount<count)return false;
 if(s.amount===count)setHand(player,hand,undefined);else{s.amount-=count;setHand(player,hand,s)}return true;
}
function give(player,stack){
 if(!stack)return;const c=mainContainer(player);if(!c){player.dimension.spawnItem(stack,player.location);return}
 try{const rem=c.addItem(stack);if(rem)player.dimension.spawnItem(rem,player.location)}catch{player.dimension.spawnItem(stack,player.location)}
}
function primitiveProps(stack){
 const out={};let ids=[];try{ids=stack.getDynamicPropertyIds()}catch{}
 for(const id of ids)try{
  const value=stack.getDynamicProperty(id);
  if(['string','number','boolean'].includes(typeof value))out[id]=value;
  else if(value&&typeof value==='object'&&Number.isFinite(value.x)&&Number.isFinite(value.y)&&Number.isFinite(value.z))out[id]={x:value.x,y:value.y,z:value.z};
 }catch{}
 return out;
}
function parseRowsProperty(stack,key,limit=5){
 try{
  const raw=stack?.getDynamicProperty(key);if(typeof raw!=='string')return [];
  const rows=JSON.parse(raw);return Array.isArray(rows)?rows.filter(x=>x&&typeof x.id==='string').slice(0,limit):[];
 }catch{return []}
}
function skewerFood(stack){
 if(!stack)return {nutrition:0,saturation:0};
 if(stack.typeId===SECRET_ID){
  const rows=parseRowsProperty(stack,SKEWER_INGREDIENTS_KEY,3);
  let cooked=false;try{cooked=stack.getDynamicProperty(SECRET_COOKED_KEY)===true}catch{}
  return secretFood(rows,cooked);
 }
 try{const food=stack.getComponent('minecraft:food');return {nutrition:Math.max(0,Number(food?.nutrition)||0),saturation:Math.max(0,Number(food?.saturationModifier)||0)}}catch{return {nutrition:0,saturation:0}}
}
function stackRow(stack){
 const food=skewerFood(stack),props=primitiveProps(stack);let lore=[],name='';
 try{lore=stack.getLore()}catch{}try{name=stack.nameTag??''}catch{}
 return {id:stack.typeId,name,lore,props,nutrition:food.nutrition,saturation:food.saturation};
}
function restoreStack(row){
 if(!row||typeof row.id!=='string')return undefined;let out;try{out=new ItemStack(row.id,1)}catch{return undefined}
 try{if(row.name)out.nameTag=row.name}catch{}
 const props=row.props&&typeof row.props==='object'?row.props:{},keys=Object.keys(props);
 try{if(Array.isArray(row.lore)&&row.lore.length)out.setLore(row.lore);else if(keys.length)out.setLore(['§r'])}catch{}
 for(const id of keys)try{out.setDynamicProperty(id,props[id])}catch{}
 return out;
}
function isSkewer(stack){return !!stack&&(FIXED_IDS.has(stack.typeId)||stack.typeId===SECRET_ID)}
function skewerIngredientIds(stack){return parseRowsProperty(stack,SKEWER_INGREDIENTS_KEY,3).map(x=>x.id)}
function isRecordableStack(stack){
 if(!stack)return false;const ingredients=skewerIngredientIds(stack);
 return isRecordableRecipe(stack.typeId,ingredients.length);
}
function plateRowsFromItem(stack){return normalizePlateRows(parseRowsProperty(stack,PLATE_SKEWERS_KEY,PLATE_CAPACITY))}
function plateItem(rows,template){
 const clean=normalizePlateRows(rows);let out;
 try{out=template?.typeId===PLATE_ID?cloneOne(template):new ItemStack(PLATE_ID,1)}catch{return undefined}
 let lore=[];try{lore=out.getLore().filter(x=>!String(x).startsWith('§7Skewers:'))}catch{}
 lore.push('§7Skewers: '+clean.length+'/'+PLATE_CAPACITY);
 try{out.setLore(lore);out.setDynamicProperty(PLATE_SKEWERS_KEY,JSON.stringify(clean))}catch{}
 return out;
}
function readPlateBlock(block){
 try{const raw=world.getDynamicProperty(posKey(PLATE_PREFIX,block));return normalizePlateRows(typeof raw==='string'?JSON.parse(raw):[])}catch{return []}
}
function syncPlateCount(block,count){
 try{block.setPermutation(block.permutation.withState('kaleidoscope_grilling:plate_count',Math.max(0,Math.min(5,count|0))))}catch{}
}
function writePlateBlock(block,rows){
 const clean=normalizePlateRows(rows);world.setDynamicProperty(posKey(PLATE_PREFIX,block),JSON.stringify(clean));syncPlateCount(block,clean.length);
}
function clearPlateBlock(block){world.setDynamicProperty(posKey(PLATE_PREFIX,block))}
function readBookRecord(book){
 try{
  const raw=book?.getDynamicProperty(BOOK_RECORD_KEY);if(typeof raw!=='string')return null;
  const record=JSON.parse(raw);
  return record&&typeof record.resultId==='string'?record:null;
 }catch{return null}
}
function bookItem(record,recordedStack,template){
 let out;try{out=template?.typeId===BOOK_ID?cloneOne(template):new ItemStack(BOOK_ID,1)}catch{return undefined}
 const value=record?{...record,recordedStack:recordedStack??record.recordedStack??null}:null;
 let lore=[];try{lore=out.getLore().filter(x=>!String(x).startsWith('§7Recipe:'))}catch{}
 lore.push(value?'§7Recipe: '+value.resultId:'§7Recipe: <empty>');
 try{out.setLore(lore);out.setDynamicProperty(BOOK_RECORD_KEY,value?JSON.stringify(value):undefined)}catch{}
 return out;
}
function readRecipeBlock(block){
 try{const raw=world.getDynamicProperty(posKey(RECIPE_PREFIX,block));return typeof raw==='string'?JSON.parse(raw):null}catch{return null}
}
function writeRecipeBlock(block,book){world.setDynamicProperty(posKey(RECIPE_PREFIX,block),JSON.stringify(stackRow(book)))}
function clearRecipeBlock(block){world.setDynamicProperty(posKey(RECIPE_PREFIX,block))}
function faceName(face){return String(face??'').toLowerCase()}
function faceOffset(face){
 switch(faceName(face)){case'north':return{x:0,y:0,z:-1};case'south':return{x:0,y:0,z:1};case'west':return{x:-1,y:0,z:0};case'east':return{x:1,y:0,z:0};case'up':return{x:0,y:1,z:0};case'down':return{x:0,y:-1,z:0};default:return null}
}
function blockAtOffset(block,off){return off?block.dimension.getBlock({x:block.x+off.x,y:block.y+off.y,z:block.z+off.z}):undefined}
function isAirReplaceable(block){return !!block&&['minecraft:air','minecraft:short_grass','minecraft:tall_grass','minecraft:snow_layer'].includes(block.typeId)}
function setFacing(block,face){
 const f=faceName(face);if(!['north','south','west','east'].includes(f))return;
 try{block.setPermutation(block.permutation.withState('minecraft:cardinal_direction',f))}catch{}
}
function placePlateOn(support,face,player,source,hand='main'){
 if(faceName(face)!=='up'||!player.isSneaking)return false;
 if(support.typeId!==COOKERY_TABLE&&!(support.isSolid??false))return false;
 const target=blockAtOffset(support,{x:0,y:1,z:0});if(!isAirReplaceable(target))return false;
 let rows=[];
 if(source?.typeId===PLATE_ID)rows=plateRowsFromItem(source);
 else if(isSkewer(source))rows=[stackRow(source)];
 else return false;
 if(!rows.length)return false;
 target.setType(PLATE_BLOCK_ID);writePlateBlock(target,rows);decrementHand(player,hand,1);
 try{target.dimension.playSound('dig.wood',target.location,{volume:.8,pitch:1})}catch{}
 return true;
}
function handlePlateBlock(block,player,hand='main'){
 if(!block||block.typeId!==PLATE_BLOCK_ID)return;
 const held=heldByHand(player,hand),rows=readPlateBlock(block);
 if(held&&isSkewer(held)){
  if(player.isSneaking&&hand==='off')return;
  const added=plateAdd(rows,stackRow(held));if(!added.ok){message(player,'§e烤串盤已滿 5/5');return}
  if(!decrementHand(player,hand,1))return;writePlateBlock(block,added.rows);
  try{block.dimension.playSound('random.pop',block.location,{volume:.7,pitch:1.1})}catch{};return;
 }
 if(held)return;
 const removed=plateRemoveLast(rows);if(!removed.ok)return;
 const stack=restoreStack(removed.removed);if(!stack)return;setHand(player,hand,stack);writePlateBlock(block,removed.rows);
 try{block.dimension.playSound('random.pop',block.location,{volume:.7,pitch:.9})}catch{}
}
function breakPlate(block,player){
 if(!block||block.typeId!==PLATE_BLOCK_ID)return;const rows=readPlateBlock(block),loc={x:block.x+.5,y:block.y+.35,z:block.z+.5},dim=block.dimension;
 clearPlateBlock(block);block.setType('minecraft:air');
 if(!creative(player)&&rows.length){const drop=plateItem(rows);if(drop)dim.spawnItem(drop,loc)}
}
function recordBookFromSkewer(player,book,skewer,hand='main'){
 const custom=skewerIngredientIds(skewer),record=makeBookRecord(skewer.typeId,custom);
 if(!record){message(player,'§c這根串不能記錄成配方');return false}
 const out=bookItem(record,stackRow(skewer),book);if(!out)return false;
 if(hand==='off')setOff(player,out);else setMain(player,out);
 message(player,'§a已記錄烤串配方：'+record.resultId);return true;
}
function consumePlan(player,plan){
 if(creative(player))return true;const c=mainContainer(player);if(!c)return false;
 for(const x of plan){const s=c.getItem(x.slot);if(!s||s.amount<x.count)return false}
 for(const x of plan){const s=c.getItem(x.slot);if(s.amount===x.count)c.setItem(x.slot,undefined);else{s.amount-=x.count;c.setItem(x.slot,s)}}return true;
}
function craftFromBook(player,book,stickHand='off'){
 const record=readBookRecord(book);if(!record){message(player,'§7這本烤串食譜尚未記錄配方');return false}
 const stick=stickHand==='main'?heldMain(player):heldOff(player);if(stick?.typeId!=='minecraft:stick'){message(player,stickHand==='main'?'§e主手需要木棍':'§e副手需要木棍');return false}
 const slots=bookIngredientSlots(record);if(!slots)return false;
 const c=mainContainer(player),inventory=[];if(!c)return false;
 for(let i=0;i<c.size;i++){const s=c.getItem(i);inventory.push(s?{id:s.typeId,count:s.amount}:null)}
 const planned=planInventoryConsumption(inventory,slots,[player.selectedSlotIndex]);
 if(!planned.ok){message(player,'§c缺少配方材料：'+(planned.missing??[]).join('/'));return false}
 if(!consumePlan(player,planned.plan)||!(stickHand==='main'?decrementMain(player,1):decrementOff(player,1)))return false;
 let output;
 if(record.resultId===SECRET_ID&&record.recordedStack){
  output=restoreStack(record.recordedStack);
  if(output){
   try{output.setDynamicProperty(SECRET_COOKED_KEY,false);output.setDynamicProperty(SECRET_CREATOR_KEY,player.name)}catch{}
   try{const lore=output.getLore().filter(x=>!String(x).startsWith('§7製作者:'));lore.push('§7製作者: '+player.name);output.setLore(lore)}catch{}
  }
 }else try{output=new ItemStack(record.resultId,1)}catch{}
 if(!output)return false;give(player,output);
 try{player.playSound('random.levelup',{volume:.45,pitch:1.5})}catch{}message(player,'§a烤串配方製作完成');return true;
}
function handleBookAir(player,item){
 const main=heldMain(player),off=heldOff(player),hand=main?.typeId===BOOK_ID?'main':off?.typeId===BOOK_ID?'off':null;if(!hand)return;
 const book=hand==='main'?main:off,record=readBookRecord(book);
 if(record&&heldOff(player)?.typeId==='minecraft:stick'&&hand==='main'){craftFromBook(player,book);return}
 if(!record&&hand==='main'&&isRecordableStack(off)){recordBookFromSkewer(player,book,off,'main');return}
 message(player,record?'§7副手放木棍即可按使用鍵自動取料製作':'§7副手放一根完整生串，再按使用鍵記錄配方');
}
function convertCookeryRecipe(player){
 const main=heldMain(player),off=heldOff(player);if(!main||!COOKERY_RECIPE_ITEMS.has(main.typeId)||!isRecordableStack(off))return false;
 const custom=skewerIngredientIds(off),record=makeBookRecord(off.typeId,custom);if(!record)return false;
 const out=bookItem(record,stackRow(off));if(!creative(player)){
  if(main.amount<=1)setMain(player,undefined);else{main.amount-=1;setMain(player,main)}
 }
 give(player,out);message(player,'§aCookery 空白食譜已記錄為烤串食譜');return true;
}
function placeRecipeBlock(support,face,player,book,hand='main'){
 const f=faceName(face);if(!['north','south','west','east'].includes(f))return false;
 const record=readBookRecord(book);if(!record){message(player,'§c空白烤串食譜不能貼牆');return true}
 const target=blockAtOffset(support,faceOffset(face));if(!isAirReplaceable(target))return false;
 target.setType(RECIPE_BLOCK_ID);setFacing(target,f);writeRecipeBlock(target,book);decrementHand(player,hand,1);
 try{target.dimension.playSound('random.pop',target.location,{volume:.6,pitch:1})}catch{}return true;
}
function handleRecipeBlock(block,player,hand='main'){
 if(!block||block.typeId!==RECIPE_BLOCK_ID)return;
 const row=readRecipeBlock(block),book=restoreStack(row),held=heldByHand(player,hand);
 if(held?.typeId==='minecraft:stick'&&book){craftFromBook(player,book,hand);return}
 if(held)return;
 clearRecipeBlock(block);block.setType('minecraft:air');if(book)give(player,book);
 try{block.dimension.playSound('random.pop',block.location,{volume:.6,pitch:.9})}catch{}
}
function breakRecipe(block,player){
 if(!block||block.typeId!==RECIPE_BLOCK_ID)return;const row=readRecipeBlock(block),book=restoreStack(row),loc={x:block.x+.5,y:block.y+.5,z:block.z+.5},dim=block.dimension;
 clearRecipeBlock(block);block.setType('minecraft:air');if(!creative(player)&&book)dim.spawnItem(book,loc);
}

world.beforeEvents.itemUse.subscribe(e=>{
 try{
  const id=e.itemStack?.typeId;
  if(id===PLATE_ID&&plateRowsFromItem(e.itemStack).length===0){e.cancel=true;message(e.source,'§7空烤串盤不能食用');return}
  if(COOKERY_RECIPE_ITEMS.has(id)&&isRecordableStack(heldOff(e.source))){e.cancel=true;const p=e.source;system.run(()=>convertCookeryRecipe(p));return}
  if(id!==BOOK_ID)return;e.cancel=true;const p=e.source,item=cloneOne(e.itemStack);system.run(()=>handleBookAir(p,item));
 }catch{}
});

world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 try{
  const block=e.block,p=e.player,intent=captureInteractionIntent(p,e.itemStack),hand=intent.hand,item=heldByHand(p,hand),first=isInitialBlockPress(e.isFirstEvent);
  const defer=fn=>system.run(()=>{if(!interactionIntentStillCurrent(p,intent)){message(p,'§7操作已取消：互動後手持物品已改變');return}fn()});
  if(block.typeId===PLATE_BLOCK_ID){
   if(item&&isSkewer(item)&&p.isSneaking&&hand==='off')return;
   if(!item&&readPlateBlock(block).length===0)return;
   e.cancel=true;if(!first)return;const loc={...block.location},dim=block.dimension;defer(()=>handlePlateBlock(dim.getBlock(loc),p,hand));return;
  }
  if(block.typeId===RECIPE_BLOCK_ID){
   if(item&&item.typeId!=='minecraft:stick')return;
   e.cancel=true;if(!first)return;const loc={...block.location},dim=block.dimension;defer(()=>handleRecipeBlock(dim.getBlock(loc),p,hand));return;
  }
  if(p.isSneaking&&hand==='main'&&item&&COOKERY_RECIPE_ITEMS.has(item.typeId)&&isRecordableStack(heldOff(p))){
   e.cancel=true;if(!first)return;defer(()=>convertCookeryRecipe(p));return;
  }
  if(p.isSneaking&&item&&(item.typeId===PLATE_ID||isSkewer(item))&&faceName(e.blockFace)==='up'){
   if(isSkewer(item)&&hand!=='main')return;
   const loc={...block.location},dim=block.dimension,face=e.blockFace;e.cancel=true;if(!first)return;defer(()=>placePlateOn(dim.getBlock(loc),face,p,heldByHand(p,hand),hand));return;
  }
  if(item?.typeId===BOOK_ID&&['north','south','west','east'].includes(faceName(e.blockFace))){
   const loc={...block.location},dim=block.dimension,face=e.blockFace;e.cancel=true;if(!first)return;defer(()=>placeRecipeBlock(dim.getBlock(loc),face,p,heldByHand(p,hand),hand));return;
  }
 }catch{}
});

world.beforeEvents.playerBreakBlock.subscribe(e=>{
 try{
  if(e.block.typeId===PLATE_BLOCK_ID){e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>breakPlate(dim.getBlock(loc),p));return}
  if(e.block.typeId===RECIPE_BLOCK_ID){e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>breakRecipe(dim.getBlock(loc),p));return}
 }catch{}
});
function recipeSupport(block){
 try{
  const f=String(block.permutation.getState('minecraft:cardinal_direction')??'').toLowerCase(),op={north:{x:0,y:0,z:1},south:{x:0,y:0,z:-1},west:{x:1,y:0,z:0},east:{x:-1,y:0,z:0}}[f];
  return op?blockAtOffset(block,op):undefined;
 }catch{return undefined}
}
function detachUnsupportedRecipe(block){
 if(!block||block.typeId!==RECIPE_BLOCK_ID)return;const support=recipeSupport(block);if(support?.isSolid)return;
 const row=readRecipeBlock(block),book=restoreStack(row),dim=block.dimension,loc={x:block.x+.5,y:block.y+.5,z:block.z+.5};
 clearRecipeBlock(block);block.setType('minecraft:air');if(book)dim.spawnItem(book,loc);
}
world.afterEvents.playerBreakBlock.subscribe(e=>{
 try{
  const dim=e.block.dimension,loc={...e.block.location};system.run(()=>{
   for(const off of [{x:1,y:0,z:0},{x:-1,y:0,z:0},{x:0,y:0,z:1},{x:0,y:0,z:-1}]){
    const b=dim.getBlock({x:loc.x+off.x,y:loc.y,z:loc.z+off.z});if(b?.typeId===RECIPE_BLOCK_ID)detachUnsupportedRecipe(b);
   }
  });
 }catch{}
});

export function a25ReadPlateBlock(block){return readPlateBlock(block)}
export function a25ReadRecipeBlockSnapshot(block){
 const row=readRecipeBlock(block),book=restoreStack(row);if(!book)return null;
 const record=readBookRecord(book);if(!record||typeof record.resultId!=='string'||!record.resultId)return null;
 const slots=bookIngredientSlots(record);
 return {resultId:record.resultId,ingredientSlots:Array.isArray(slots)?slots.map(slot=>[...slot]):[]};
}
export function a25PlateRows(stack){return plateRowsFromItem(stack)}
export function a25PlateItem(rows,template){return plateItem(rows,template)}
export function a25RestoreStack(row){return restoreStack(row)}
export function a25StackRow(stack){return stackRow(stack)}
