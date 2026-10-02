import {captureSkewerMetadata,restoreSkewerMetadata,metadataSignature} from './skewer_item_snapshot.js';
import {decodePlateStorage,verifiedPlateStep,commitPlateSteps,plateFacingFromYaw} from './plate_transaction_core.js';
import {commitSteps} from './a277_grill_transaction_core.js';
import {getItemProperty,setItemProperty,getItemPropertyIds,getItemLore,getItemRawLore,setItemLore} from './itemData.js';
import {hasSolidTop} from './blockSupport.js';
import {interactionFeedback} from './a283_interaction_feedback.js';
import {world,system,ItemStack,EnchantmentType} from '@minecraft/server';
import {
 UNFINISHED_ID,SECRET_ID,SKEWER_INGREDIENTS_KEY,SECRET_COOKED_KEY,SECRET_COOKED_INGREDIENTS_KEY,SECRET_CREATOR_KEY,secretFood,recipeTable
} from './a24_skewering_core.js';
import {RAW_SKEWER_TAG,GRILLED_SKEWER_TAG} from './skewer_compat_core.js';
import {
 PLATE_ID,PLATE_BLOCK_ID,BOOK_ID,RECIPE_BLOCK_ID,PLATE_SKEWERS_KEY,BOOK_RECORD_KEY,PLATE_CAPACITY,
 normalizePlateRows,plateAdd,plateRemoveLast,isRecordableRecipe,makeBookRecord,bookIngredientSlots,planInventoryConsumption
} from './a25_plate_recipe_core.js';
import {playerInventory as mainContainer,getMainHand as heldMain,setMainHand as setMain,getOffHand as heldOff,setOffHand as setOff,getHand as heldByHand,setHand,isCreative as creative,captureWritableHand} from './a2735_player_io.js';
import {isInitialBlockPress} from './a275_grill_input_core.js';
import {stackIntentSignature as interactionStackSignature} from './a2762_interaction_intent_core.js';
import {captureInteractionIntent,interactionIntentStillCurrent} from './a2762_interaction_intent_adapter.js';

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
const message=interactionFeedback;
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
 const out={};let ids=[];try{ids=getItemPropertyIds(stack)}catch{}
 for(const id of ids)try{
  const value=getItemProperty(stack,id);
  if(['string','number','boolean'].includes(typeof value))out[id]=value;
  else if(value&&typeof value==='object'&&Number.isFinite(value.x)&&Number.isFinite(value.y)&&Number.isFinite(value.z))out[id]={x:value.x,y:value.y,z:value.z};
 }catch{}
 return out;
}
function parseRowsProperty(stack,key,limit=5){
 try{
  const raw=getItemProperty(stack,key);if(typeof raw!=='string')return [];
  const rows=JSON.parse(raw);return Array.isArray(rows)?rows.filter(x=>x&&typeof x.id==='string').slice(0,limit):[];
 }catch{return []}
}
function skewerFood(stack){
 if(!stack)return {nutrition:0,saturation:0};
 if(stack.typeId===SECRET_ID){
  const rows=parseRowsProperty(stack,SKEWER_INGREDIENTS_KEY,3);
  let cooked=false;try{cooked=getItemProperty(stack,SECRET_COOKED_KEY)===true}catch{}
  const cookedRows=cooked?parseRowsProperty(stack,SECRET_COOKED_INGREDIENTS_KEY,3):[];
  return secretFood(cookedRows.length?cookedRows:rows,cooked,rows);
 }
 try{const food=stack.getComponent('minecraft:food');return {nutrition:Math.max(0,Number(food?.nutrition)||0),saturation:Math.max(0,Number(food?.saturationModifier)||0)}}catch{return {nutrition:0,saturation:0}}
}
function stackRow(stack){
 const food=skewerFood(stack),props=primitiveProps(stack);let lore=[],name='';
 try{lore=getItemLore(stack)}catch{}try{name=stack.nameTag??''}catch{}
 return {id:stack.typeId,native:captureSkewerMetadata(stack),nutrition:food.nutrition,saturation:food.saturation};
}
function restoreStack(row){
 if(!row||typeof row.id!=='string')return undefined;
 if(row.native&&row.native.id!==row.id)throw Error('Grilling: recorded identity mismatch');
 if(row.native)return restoreSkewerMetadata(row.native,(id,n)=>new ItemStack(id,n),id=>new EnchantmentType(id));
 const out=new ItemStack(row.id,1),props=row.props&&typeof row.props==='object'?row.props:{},lore=Array.isArray(row.lore)?row.lore:[];
 if(row.name)out.nameTag=row.name;setItemLore(out,lore);
 for(const [id,value] of Object.entries(props))setItemProperty(out,id,value);
 if((out.nameTag??'')!==(row.name??'')||JSON.stringify(getItemLore(out))!==JSON.stringify(lore))throw Error('Grilling: legacy skewer metadata readback differs');
 for(const [id,value] of Object.entries(props))if(JSON.stringify(getItemProperty(out,id))!==JSON.stringify(value))throw Error('Grilling: legacy skewer property readback differs');
 return out;
}
function isSkewer(stack){
 if(!stack)return false;
 if(FIXED_IDS.has(stack.typeId)||stack.typeId===SECRET_ID)return true;
 try{return !!(stack.hasTag?.(RAW_SKEWER_TAG)||stack.hasTag?.(GRILLED_SKEWER_TAG))}catch{return false}
}
function skewerIngredientIds(stack){return parseRowsProperty(stack,SKEWER_INGREDIENTS_KEY,3).map(x=>x.id)}
function isRecordableStack(stack){
 if(!stack)return false;const ingredients=skewerIngredientIds(stack);
 return isRecordableRecipe(stack.typeId,ingredients.length);
}
function plateRowsFromItem(stack){return normalizePlateRows(parseRowsProperty(stack,PLATE_SKEWERS_KEY,PLATE_CAPACITY))}
function plateItem(rows,template){
 const clean=normalizePlateRows(rows);let out;
 try{out=template?.typeId===PLATE_ID?cloneOne(template):new ItemStack(PLATE_ID,1)}catch{return undefined}
 let lore=[];try{lore=getItemRawLore(out).filter(x=>!(typeof x==='string'?x:x?.text??'').startsWith('§7Skewers:'))}catch{}
 lore.push('§7Skewers: '+clean.length+'/'+PLATE_CAPACITY);
 setItemLore(out,lore);const value=JSON.stringify(clean);setItemProperty(out,PLATE_SKEWERS_KEY,value);
 if(getItemProperty(out,PLATE_SKEWERS_KEY)!==value)throw Error('Grilling: plate contents were not saved');
 return out;
}
const plateFaults=new Set();
function plateFaultKey(block){return posKey(PLATE_PREFIX,block)+'_transaction_fault'}
function assertPlateAvailable(block){
 const key=plateFaultKey(block);
 if(plateFaults.has(key)||world.getDynamicProperty(key)!==undefined)throw Error('Grilling: plate transaction quarantined');
}
function quarantinePlate(block,reason){
 const key=plateFaultKey(block);plateFaults.add(key);
 world.setDynamicProperty(key,String(reason));
 if(world.getDynamicProperty(key)!==String(reason))throw Error('Grilling: plate quarantine did not persist');
}
function readPlateBlock(block){
 assertPlateAvailable(block);
 return normalizePlateRows(decodePlateStorage(world.getDynamicProperty(posKey(PLATE_PREFIX,block))));
}
function plateStorageStep(block,rows){
 assertPlateAvailable(block);
 const key=posKey(PLATE_PREFIX,block),before=world.getDynamicProperty(key);
 decodePlateStorage(before);decodePlateStorage(JSON.stringify(rows));
 const step=verifiedPlateStep({read:()=>world.getDynamicProperty(key),write:value=>world.setDynamicProperty(key,value),before,after:JSON.stringify(normalizePlateRows(rows))});
 return {
  apply(){step.apply();syncPlateCount(block,rows.length)},
  rollback(){step.rollback();if(block.typeId===PLATE_BLOCK_ID)syncPlateCount(block,decodePlateStorage(before).length)}
 };
}
function plateHandStep(captured,next){
 const signature=stack=>stack?metadataSignature({amount:stack.amount,...captureSkewerMetadata(stack)}):'';
 return verifiedPlateStep({read:captured.read,write:stack=>captured.write(stack?.clone()),before:captured.before,after:next,signature});
}
function plateTransaction(block,steps){
 const result=commitPlateSteps(steps,reason=>quarantinePlate(block,reason));
 if(!result.ok)console.warn('[Grilling plate transaction] '+result.error);
 return result.ok;
}
function syncPlateCount(block,count){
 const expected=Math.max(0,Math.min(5,count|0));
 block.setPermutation(block.permutation.withState('kaleidoscope_grilling:plate_count',expected));
 if(block.permutation.getState('kaleidoscope_grilling:plate_count')!==expected)throw Error('Grilling: plate count rejected');
}
function writePlateBlock(block,rows){
 const clean=normalizePlateRows(rows),value=JSON.stringify(clean);world.setDynamicProperty(posKey(PLATE_PREFIX,block),value);
 if(world.getDynamicProperty(posKey(PLATE_PREFIX,block))!==value)throw Error('Grilling: plate block write rejected');syncPlateCount(block,clean.length);
}
function clearPlateBlock(block){world.setDynamicProperty(posKey(PLATE_PREFIX,block))}
function readBookRecord(book){
 try{
  const raw=getItemProperty(book,BOOK_RECORD_KEY);if(typeof raw!=='string')return null;
  const record=JSON.parse(raw);
  return record&&typeof record.resultId==='string'?record:null;
 }catch{return null}
}
function bookItem(record,recordedStack,template){
 let out;try{out=template?.typeId===BOOK_ID?cloneOne(template):new ItemStack(BOOK_ID,1)}catch{return undefined}
 const value=record?{...record,recordedStack:recordedStack??record.recordedStack??null}:null;
 let lore=[];try{lore=getItemRawLore(out).filter(x=>!(typeof x==='string'?x:x?.text??'').startsWith('§7Recipe:'))}catch{}
 lore.push(value?('§7Recipe: '+value.resultId.replace(/^.*:/,'')).slice(0,50):'§7Recipe: <empty>');
 setItemLore(out,lore);const serialized=value?JSON.stringify(value):undefined;setItemProperty(out,BOOK_RECORD_KEY,serialized);
 if(getItemProperty(out,BOOK_RECORD_KEY)!==serialized)throw Error('Grilling: recipe record was not saved');
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
 if(support.typeId!==COOKERY_TABLE&&!hasSolidTop(support))return false;
 const target=blockAtOffset(support,{x:0,y:1,z:0});if(!isAirReplaceable(target))return false;
 let rows=[];
 if(source?.typeId===PLATE_ID)rows=plateRowsFromItem(source);
 else if(isSkewer(source))rows=[stackRow(source)];
 else return false;
 if(!rows.length)return false;
 if(!plateItem(rows))throw Error('Grilling: plate contents cannot be packed');
 assertPlateAvailable(target);
 if(world.getDynamicProperty(posKey(PLATE_PREFIX,target))!==undefined)throw Error('Grilling: orphaned plate contents require recovery');
 const captured=captureWritableHand(player,hand),before=target.permutation,facing=plateFacingFromYaw(player.getRotation().y);
 if(interactionStackSignature(captured.before)!==interactionStackSignature(source))return false;
 const next=captured.before?.clone();if(!next)return false;
 const remainder=next.amount===1?undefined:next;if(remainder)remainder.amount--;
 const place={apply(){target.setType(PLATE_BLOCK_ID);target.setPermutation(target.permutation.withState('minecraft:cardinal_direction',facing));if(target.typeId!==PLATE_BLOCK_ID||target.permutation.getState('minecraft:cardinal_direction')!==facing)throw Error('Grilling: plate placement rejected')},rollback(){target.setPermutation(before);if(target.typeId!==before.type.id||metadataSignature(target.permutation.getAllStates())!==metadataSignature(before.getAllStates()))throw Error('Grilling: plate placement rollback rejected')}};
 if(!plateTransaction(target,[place,plateStorageStep(target,rows),...(creative(player)?[]:[plateHandStep(captured,remainder)])]))return false;
 try{target.dimension.playSound('dig.wood',target.location,{volume:.8,pitch:1})}catch{}
 return true;
}
function handlePlateBlock(block,player,hand='main'){
 if(!block||block.typeId!==PLATE_BLOCK_ID)return;
 const held=heldByHand(player,hand),rows=readPlateBlock(block);
 if(held&&isSkewer(held)){
  if(player.isSneaking&&hand==='off')return;
  const added=plateAdd(rows,stackRow(held));if(!added.ok){message(player,'§e烤串盤已滿 5/5');return}
  if(!plateItem(added.rows))throw Error('Grilling: plate could not be reconstructed'); // Preflight item storage limits before taking any skewer.
  const captured=captureWritableHand(player,hand),next=captured.before?.clone();if(!next)return;
  const remainder=next.amount===1?undefined:next;if(remainder)remainder.amount--;
  if(!plateTransaction(block,[plateStorageStep(block,added.rows),...(creative(player)?[]:[plateHandStep(captured,remainder)])]))return;
  try{block.dimension.playSound('random.pop',block.location,{volume:.7,pitch:1.1})}catch{};return;
 }
 if(held)return;
 const removed=plateRemoveLast(rows);if(!removed.ok)return;
 const stack=restoreStack(removed.removed);if(!stack)return;
 const captured=captureWritableHand(player,hand);if(captured.before)return;
 if(!plateTransaction(block,[plateStorageStep(block,removed.rows),plateHandStep(captured,stack)]))return;
 try{block.dimension.playSound('random.pop',block.location,{volume:.7,pitch:.9})}catch{}
}
function breakPlate(block,player){
 if(!block||block.typeId!==PLATE_BLOCK_ID)return false;
 const rows=readPlateBlock(block),loc={x:block.x+.5,y:block.y+.35,z:block.z+.5},dim=block.dimension,before=block.permutation;
 const drop=!creative(player)&&rows.length?plateItem(rows):undefined;
 if(!creative(player)&&rows.length&&!drop)throw Error('Grilling: plate drop could not be packed');
 const signature=s=>s?metadataSignature({amount:s.amount,...captureSkewerMetadata(s)}):'';
 let escrow;
 const delivery={
  apply(){
   if(!drop)return;
   try{
    escrow=dim.spawnItem(drop,loc);
    if(!escrow?.isValid||signature(escrow.getComponent('minecraft:item')?.itemStack)!==signature(drop))throw Error('Grilling: plate drop readback differs');
   }catch(error){
    // A spawn call can fail after creating an inaccessible item. Never retry
    // automatically when no returned entity exists to confirm its removal.
    if(!escrow)quarantinePlate(block,'plate drop spawn outcome unknown');
    throw error;
   }
  },
  rollback(){
   if(!escrow)return;
   try{if(escrow.isValid)escrow.remove()}catch(error){if(escrow.isValid)throw error}
   if(escrow.isValid)throw Error('Grilling: plate drop cleanup unconfirmed');
  }
 };
 const key=posKey(PLATE_PREFIX,block),raw=world.getDynamicProperty(key);
 const clear=verifiedPlateStep({read:()=>world.getDynamicProperty(key),write:value=>world.setDynamicProperty(key,value),before:raw,after:undefined});
 const remove={
  apply(){block.setType('minecraft:air');if(block.typeId!=='minecraft:air')throw Error('Grilling: plate removal rejected')},
  rollback(){block.setPermutation(before);if(block.typeId!==before.type.id||metadataSignature(block.permutation.getAllStates())!==metadataSignature(before.getAllStates()))throw Error('Grilling: plate removal rollback rejected')}
 };
 return plateTransaction(block,[delivery,clear,remove]);
}
function recordBookFromSkewer(player,book,skewer,hand='main'){
 const custom=skewerIngredientIds(skewer),record=makeBookRecord(skewer.typeId,custom);
 if(!record){message(player,'§c這根串不能記錄成配方');return false}
 const out=bookItem(record,stackRow(skewer),book);if(!out)return false;
 const before=heldByHand(player,hand)?.clone();
 const result=commitSteps([{apply(){setHand(player,hand,out);if(interactionStackSignature(heldByHand(player,hand))!==interactionStackSignature(out))throw Error('Recipe hand write rejected')},rollback(){setHand(player,hand,before)}}]);
 if(!result.ok){console.warn('[Grilling record recipe] '+result.error+'; rollback errors='+result.rollbackErrors);return false}
 return true;
}
function consumePlan(player,plan){
 if(creative(player))return true;const c=mainContainer(player);if(!c)return false;
 for(const x of plan){const s=c.getItem(x.slot);if(!s||s.amount<x.count)return false}
 for(const x of plan){const s=c.getItem(x.slot);if(s.amount===x.count)c.setItem(x.slot,undefined);else{s.amount-=x.count;c.setItem(x.slot,s)}}return true;
}
function isRecipeStick(stack){
 if(stack?.typeId==='minecraft:stick')return true;
 if(stack?.typeId!==UNFINISHED_ID)return false;
 const raw=getItemProperty(stack,SKEWER_INGREDIENTS_KEY);
 return raw===undefined||(typeof raw==='string'&&raw.trim()==='[]');
}
function craftFromBook(player,book,stickHand='off'){
 const record=readBookRecord(book);if(!record){message(player,'§7這本烤串食譜尚未記錄配方');return false}
 const stick=heldByHand(player,stickHand);if(!isRecipeStick(stick)){message(player,'§e需要木棍或空的未完成烤串');return false}
 const slots=bookIngredientSlots(record);if(!slots)return false;
 const c=mainContainer(player);if(!c)return false;
 const before=Array.from({length:c.size},(_,i)=>c.getItem(i)?.clone()),oldOff=heldOff(player)?.clone();
 const inventory=before.map(s=>s?{id:s.typeId,count:s.amount,tags:s.getTags?.()??[]}:null);
 const planned=planInventoryConsumption(inventory,slots,[player.selectedSlotIndex]);
 if(!planned.ok){message(player,'§c缺少配方材料：'+(planned.missing??[]).join('/'));return false}
 // Java intentionally copies the recorded secret recipe, not newly consumed metadata.
 let output;
 if(record.resultId===SECRET_ID&&record.recordedStack){
  output=restoreStack(record.recordedStack);
  if(output){
   setItemProperty(output,SECRET_COOKED_KEY,false);
   setItemProperty(output,SECRET_CREATOR_KEY,JSON.stringify({name:player.name,id:player.id}));
   const lore=getItemRawLore(output).filter(x=>!(typeof x==='string'?x:x?.text??'').startsWith('§7製作者:'));lore.push('§7製作者: '+player.name);setItemLore(output,lore);
  }
 }else if(record.resultId!==SECRET_ID)output=new ItemStack(record.resultId,1);
 if(!output)return false;
 const result=commitSteps([{
  apply(){
   if(!consumePlan(player,planned.plan)||!decrementHand(player,stickHand,1))throw Error('Recipe inputs changed');
   const leftover=c.addItem(output);if(leftover)throw Error('Make inventory space for the skewer');
  },
  rollback(){
   let failures=0;
   for(let i=0;i<before.length;i++)try{c.setItem(i,before[i])}catch{failures++}
   try{setOff(player,oldOff)}catch{failures++}
   if(failures)throw Error('Recipe rollback failed for '+failures+' writes');
  }
 }]);
 if(!result.ok){console.warn('[Grilling recipe] '+result.error+'; rollback errors='+result.rollbackErrors);message(player,'§c製作未完成，已嘗試回復材料；請預留背包空位');return false}
 try{player.playSound('random.levelup',{volume:.45,pitch:1.5})}catch{}return true;
}
function handleBookAir(player,item){
 const main=heldMain(player),off=heldOff(player),hand=main?.typeId===BOOK_ID?'main':off?.typeId===BOOK_ID?'off':null;if(!hand)return;
 const book=hand==='main'?main:off,record=readBookRecord(book);
 if(record&&isRecipeStick(heldOff(player))&&hand==='main'){craftFromBook(player,book);return}
 if(!record&&hand==='main'&&isRecordableStack(off)){recordBookFromSkewer(player,book,off,'main');return}
 message(player,record?'§7副手放空的未完成烤串即可按使用鍵自動取料製作':'§7副手放一根完整生串，再按使用鍵記錄配方');
}
function convertCookeryRecipe(player){
 const main=heldMain(player),off=heldOff(player);if(!main||!COOKERY_RECIPE_ITEMS.has(main.typeId)||!isRecordableStack(off))return false;
 const custom=skewerIngredientIds(off),record=makeBookRecord(off.typeId,custom);if(!record)return false;
 const out=bookItem(record,stackRow(off));if(!creative(player)){
  if(main.amount<=1)setMain(player,undefined);else{main.amount-=1;setMain(player,main)}
 }
 give(player,out);return true;
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
 if(isRecipeStick(held)&&book){craftFromBook(player,book,hand);return}
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
  if(e.cancel)return;const id=e.itemStack?.typeId,p=e.source;
  if(id===PLATE_ID&&plateRowsFromItem(e.itemStack).length===0){e.cancel=true;message(p,'§7空烤串盤不能食用');return}
  const intent=captureInteractionIntent(p,e.itemStack);if(intent.hand!=='main')return;
  if(COOKERY_RECIPE_ITEMS.has(id)&&isRecordableStack(heldOff(p))){
   e.cancel=true;const offSignature=interactionStackSignature(heldOff(p));
   system.run(()=>{if(!interactionIntentStillCurrent(p,intent)||interactionStackSignature(heldOff(p))!==offSignature){message(p,'§7操作已取消：食譜或副手烤串已變更');return}convertCookeryRecipe(p)});return;
  }
  if(id!==BOOK_ID)return;e.cancel=true;const offSignature=interactionStackSignature(heldOff(p));
  system.run(()=>{if(!interactionIntentStillCurrent(p,intent)||interactionStackSignature(heldOff(p))!==offSignature){message(p,'§7操作已取消：食譜書或副手材料已變更');return}handleBookAir(p)});
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
   if(item&&!isRecipeStick(item))return;
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
world.beforeEvents.explosion.subscribe(e=>{
 if(e.cancel)return;
 const keep=[],plates=[];
 for(const block of e.getImpactedBlocks()){
  if(block.typeId===PLATE_BLOCK_ID)plates.push({dimension:block.dimension,location:{...block.location}});
  else keep.push(block);
 }
 if(!plates.length)return;
 e.setImpactedBlocks(keep);
 system.run(()=>{
  // Another before-event subscriber may cancel after this one. Do not settle a
  // cancelled or unreadable event; no storage/drop mutation has happened yet.
  try{if(e.cancel!==false)return}catch(error){console.warn('[Grilling plate explosion status] '+error);return}
  for(const row of plates)try{breakPlate(row.dimension.getBlock(row.location))}catch(error){console.warn('[Grilling plate explosion recovery] '+error)}
 });
});
function recipeSupport(block){
 try{
  const f=String(block.permutation.getState('minecraft:cardinal_direction')??'').toLowerCase(),op={north:{x:0,y:0,z:1},south:{x:0,y:0,z:-1},west:{x:1,y:0,z:0},east:{x:-1,y:0,z:0}}[f];
  return op?blockAtOffset(block,op):undefined;
 }catch{return undefined}
}
function detachUnsupportedRecipe(block){
 if(!block||block.typeId!==RECIPE_BLOCK_ID)return;const support=recipeSupport(block);if(hasSolidTop(support))return;
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
