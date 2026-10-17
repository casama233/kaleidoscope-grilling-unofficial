import {canonicalFoodId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_profile_ids.js';
/** Executes runtime function bodies with API/storage doubles; no client claims. */
import test from 'node:test';import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
import {commitSteps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
import {nativeItemSignature,ownedItemStep,planOwnedInventoryDelivery,commitPlayerItemTransaction} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/owned_item_transaction_core.js';
import {secretFood,recipeTable,SECRET_ID} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a24_skewering_core.js';
import {PLATE_ID,PLATE_BLOCK_ID,BOOK_ID} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a25_plate_recipe_core.js';
import {RAW_SKEWER_TAG,GRILLED_SKEWER_TAG} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/skewer_compat_core.js';
import {creatorLore} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/localized_lore_core.js';
const N='kaleidoscope_grilling:',url=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/a25_plate_recipe_runtime.js',import.meta.url),src=fs.readFileSync(url,'utf8');
function fn(name,code=src){const start=code.indexOf('function '+name+'(');assert.ok(start>=0,name);let end=code.indexOf('{',start)+1,n=1;for(;n;end++){if(code[end]==='{')n++;if(code[end]==='}')n--}return code.slice(start,end)}
const hotSource=fs.readFileSync(new URL('a23_hot_runtime.js',url),'utf8'),authorCleanup=fn('norm',hotSource)+'\n'+fn('withoutAutomaticCreatorLore',hotSource);
class Stack{
 constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.maxAmount=64;this.props={};this.lore=[];this.keepOnDeath=false;this.lockMode='none'}
 getTags(){return this.tags??[]}clone(){return Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}))}
 getComponent(){return undefined}getRawLore(){return this.lore}getLore(){return this.lore}getCanDestroy(){return this.canDestroy??[]}getCanPlaceOn(){return this.canPlaceOn??[]}
 getDynamicPropertyIds(){return Object.keys(this.props)}getDynamicProperty(key){return this.props[key]}
 isStackableWith(other){const a=this.clone(),b=other.clone();a.amount=1;b.amount=1;return nativeItemSignature(a)===nativeItemSignature(b)}
}
function fixture({secret=false,full=false,free=false,fault='',missing=false,previousCreator}={}){
 let capturedInventory;const cleanupCreators=[],drops=[],dp=new Map();let fired=false,off=new Stack(N+'unfinished_skewer',3);const rows=[new Stack(N+'skewer_recipe_book'),new Stack('minecraft:apple',4),full?new Stack('minecraft:stone',64):undefined];
 const original=rows.map(s=>s?.clone()),oldOff=off.clone(),record={resultId:N+(secret?'secret_skewer':'raw_fish_skewer'),recordedStack:{id:N+'secret_skewer',props:{original:'recorded'},lore:[{translate:'test:original_lore'}]}};
 if(previousCreator){record.recordedStack.props.creator=JSON.stringify(previousCreator);record.recordedStack.lore.push(creatorLore(previousCreator.name),{text:'§7製作者: '+previousCreator.name},'§7製作者: '+previousCreator.name+' custom');}
 const fail=k=>{if(k===fault&&!fired){fired=true;throw Error('fault '+k)}};
 const bag={size:rows.length,getItem:i=>rows[i]?.clone(),setItem(i,s){rows[i]=s?.clone();if(i===2&&s&&fault==='foreign-output'){rows[i].nameTag='foreign owner';throw Error('foreign output')}fail(i===2?'delivery':'slot')}};
 const world={getDynamicProperty:key=>dp.get(key),setDynamicProperty(key,value){if(value===undefined)dp.delete(key);else dp.set(key,value);if(value!==undefined)fail('receipt')}};
 const dimension={spawnItem(stack){
  fail('spawn-before');const entity={stack:stack.clone(),isValid:true,getComponent(){fail('drop-readback');return {itemStack:this.stack.clone()}},remove(){if(fault==='cleanup')throw Error('cleanup');this.isValid=false;drops.splice(drops.indexOf(this),1)}};
  drops.push(entity);fail('spawn-after');
  if(fault==='cleanup'){let first=true;entity.getComponent=function(){if(first){first=false;throw Error('drop readback')}return {itemStack:this.stack.clone()}}}
  return entity;
 }};
 const holder={name:'tester',id:'test',selectedSlotIndex:0,dimension,location:{x:0,y:64,z:0},playSound(){}};
 const context={canonicalFoodId,creatorLore,onCreatorCleanup:stack=>cleanupCreators.push(stack.props.creator),forgetEatingItem(){},ItemStack:Stack,SECRET_ID:N+'secret_skewer',UNFINISHED_ID:N+'unfinished_skewer',SKEWER_INGREDIENTS_KEY:N+'skewer_ingredients',SECRET_COOKED_KEY:'cooked',SECRET_COOKED_INGREDIENTS_KEY:'cookedRows',SECRET_CREATOR_KEY:'creator',world,system:{currentTick:1},console:{warn(){}},readBookRecord:()=>record,heldByHand:(_p,h)=>h==='off'?off:bag.getItem(0),heldOff:()=>off,setOff(_p,s){off=s?.clone();fail('off')},mainContainer:()=>bag,
 captureWritableHand(_p,hand){const read=()=>hand==='off'?off?.clone():bag.getItem(0);return {before:read(),read,write(stack){if(hand==='off'){off=stack?.clone();fail('off')}else bag.setItem(0,stack)}}},
 bookIngredientSlots:()=>[['minecraft:apple']],planInventoryConsumption:inventory=>{capturedInventory=structuredClone(inventory);return missing?{ok:false,missing:['apple']}:{ok:true,plan:[{slot:1,count:1}]}},creative:()=>free,getItemProperty:(s,k)=>s.props[k],setItemProperty:(s,k,v)=>{if(v===undefined)delete s.props[k];else s.props[k]=v},getItemLore:s=>s.lore,getItemRawLore:s=>s.lore,setItemLore:(s,v)=>s.lore=v,restoreStack:r=>{fail('restore');const s=new Stack(r.id);s.props={...r.props};s.lore=structuredClone(r.lore);return s},commitSteps,nativeItemSignature,ownedItemStep,planOwnedInventoryDelivery,commitPlayerItemTransaction,itemTranslationKey:id=>id,useSound(){},message(){},interactionFailure(){},javaInteractionFeedback(){}};
 function load(){const ctx=vm.createContext({...context,world:{...world}});vm.runInContext(authorCleanup+'\nconst recordedAuthorCleanup=withoutAutomaticCreatorLore;withoutAutomaticCreatorLore=(...args)=>{onCreatorCleanup(args[0]);return recordedAuthorCleanup(...args)};\n'+fn('isRecipeStick')+'\n'+fn('recipeCraftSteps')+'\n'+fn('craftFromBook')+';this.run=craftFromBook',ctx);return ctx}
 let ctx=load();return {run:()=>ctx.run(holder,rows[0]),reload(){ctx=load()},rows,original,oldOff,cleanupCreators,drops,dp,get capturedInventory(){return capturedInventory},get off(){return off}};
}
for(const secret of [false,true])test('book produces '+(secret?'recorded secret':'fixed')+' with empty starter',()=>{const f=fixture({secret});assert.equal(f.run(),true);assert.equal(f.rows[1].amount,3);assert.equal(f.off.amount,2);assert.equal(f.rows[2].typeId,N+(secret?'secret_skewer':'raw_fish_skewer'));if(secret){assert.equal(f.rows[2].props.original,'recorded');assert.deepEqual(f.rows[2].lore[0],{translate:'test:original_lore'});assert.equal(f.rows[2].props.cooked,false);assert.equal(JSON.parse(f.rows[2].props.creator).name,'tester')}});
for(const fault of ['slot','off','delivery'])test('write-after-mutation '+fault+' restores materials/starter/output',()=>{const f=fixture({fault});assert.equal(f.run(),false);assert.deepEqual(f.rows,f.original);assert.deepEqual(f.off,f.oldOff)});
for(const secret of [false,true])test('full inventory drops exactly one '+(secret?'recorded secret':'fixed')+' result like Java',()=>{const f=fixture({full:true,secret});assert.equal(f.run(),true);assert.equal(f.rows[1].amount,3);assert.equal(f.off.amount,2);assert.equal(f.rows[2].typeId,'minecraft:stone');assert.equal(f.drops.length,1);const output=f.drops[0].stack;assert.equal(output.typeId,N+(secret?'secret_skewer':'raw_fish_skewer'));assert.equal(output.amount,1);if(secret){assert.equal(output.props.original,'recorded');assert.equal(JSON.parse(output.props.creator).name,'tester');assert.deepEqual(output.lore[0],{translate:'test:original_lore'})}assert.equal(f.dp.size,0)});
test('delivery uses slots freed by ingredients and compatible partial stacks before dropping',()=>{
 const freed=fixture({full:true});freed.rows[1].amount=1;assert.equal(freed.run(),true);assert.equal(freed.rows[1].typeId,N+'raw_fish_skewer');assert.equal(freed.rows[1].amount,1);assert.equal(freed.drops.length,0);
 const merged=fixture({full:true});merged.rows[2]=new Stack(N+'raw_fish_skewer',63);assert.equal(merged.run(),true);assert.equal(merged.rows[2].amount,64);assert.equal(merged.rows[1].amount,3);assert.equal(merged.drops.length,0);
});
test('craft receipt failure prevents any native input or output change',()=>{const f=fixture({fault:'receipt'});assert.throws(f.run,/receipt/);assert.deepEqual(f.rows,f.original);assert.deepEqual(f.off,f.oldOff);assert.equal(f.drops.length,0)});
test('known dropped output is removed before refund on readback failure',()=>{const f=fixture({full:true,fault:'drop-readback'});assert.equal(f.run(),false);assert.deepEqual(f.rows,f.original);assert.deepEqual(f.off,f.oldOff);assert.equal(f.drops.length,0);assert.equal(f.dp.size,0);assert.equal(f.run(),true);assert.equal(f.drops.length,1)});
for(const fault of ['spawn-before','spawn-after','cleanup','foreign-output'])test('uncertain '+fault+' retains input debit, foreign ownership and retry quarantine',()=>{
 const f=fixture({full:fault!=='foreign-output',fault});assert.equal(f.run(),false);assert.equal(f.rows[1].amount,3);assert.equal(f.off.amount,2);assert.equal(f.dp.size,1);
 if(fault==='foreign-output')assert.equal(f.rows[2].nameTag,'foreign owner');
 const count=f.drops.length;assert.throws(f.run,/requires recovery/);f.reload();assert.throws(f.run,/requires recovery/);assert.equal(f.drops.length,count);assert.equal(f.rows[1].amount,3);assert.equal(f.off.amount,2);
});
test('recipe author cleanup sees the prior author before replacement and writes canonical new-author lore',()=>{
 const previous={name:'original cook',id:'old-id'},f=fixture({secret:true,previousCreator:previous});assert.equal(f.run(),true);
 assert.deepEqual(f.cleanupCreators,[JSON.stringify(previous)]);assert.deepEqual(JSON.parse(f.rows[2].props.creator),{name:'tester',id:'test'});
 assert.deepEqual(f.rows[2].lore.at(-1),creatorLore('tester'));assert.deepEqual(f.rows[2].lore[0],{translate:'test:original_lore'});
 assert.equal(f.rows[2].lore.length,3);assert.equal(f.rows[2].lore[1],'§7製作者: original cook custom');
});
test('cannot restore recorded data before any debit',()=>{const f=fixture({secret:true,fault:'restore'});assert.throws(f.run,/restore/);assert.deepEqual(f.rows,f.original);assert.deepEqual(f.off,f.oldOff)});
test('missing ingredient never partially consumes',()=>{const f=fixture({missing:true});assert.equal(f.run(),false);assert.deepEqual(f.rows,f.original);assert.deepEqual(f.off,f.oldOff)});
test('creative mode retains ingredients and starter',()=>{const f=fixture({free:true});assert.equal(f.run(),true);assert.equal(f.rows[1].amount,4);assert.equal(f.off.amount,3)});
test('filled unfinished skewer cannot be consumed as a stick',()=>{const f=fixture();f.off.props[N+'skewer_ingredients']='[{"id":"minecraft:apple"}]';assert.equal(f.run(),false);assert.deepEqual(f.rows,f.original);assert.equal(f.off.amount,3)});
test('plate computes cooked-secret food from cooked rows but duplicates from raw rows',()=>{
 const raw=[{id:'minecraft:potato',nutrition:1,saturation:.3},{id:'minecraft:potato',nutrition:1,saturation:.3},{id:'minecraft:beef',nutrition:3,saturation:.3}],cooked=raw.map((r,i)=>({...r,id:i<2?'minecraft:baked_potato':'minecraft:cooked_beef',nutrition:i<2?5:8}));
 const ctx=vm.createContext({canonicalFoodId,forgetEatingItem(){},SECRET_ID:N+'secret_skewer',SKEWER_INGREDIENTS_KEY:'raw',SECRET_COOKED_KEY:'cooked',SECRET_COOKED_INGREDIENTS_KEY:'effective',parseRowsProperty:(_s,k)=>k==='raw'?raw:cooked,getItemProperty:()=>true,secretFood});vm.runInContext(fn('skewerFood')+';this.run=skewerFood',ctx);
 const out=ctx.run({typeId:N+'secret_skewer'});assert.equal(out.nutrition,8);assert.equal(out.duplicate,true);
});
test('four-paper blank recipe and one-book reset retain paper economy',()=>{const dir=new URL('../recipes/',url);const blank=JSON.parse(fs.readFileSync(new URL('skewer_recipe_book_blank.json',dir),'utf8'))['minecraft:recipe_shaped'];assert.deepEqual(blank.pattern,['PP','PP']);assert.equal(blank.key.P.item,'minecraft:paper');assert.equal(blank.result.item,N+'skewer_recipe_book');const clear=JSON.parse(fs.readFileSync(new URL('clear_skewer_recipe_book.json',dir),'utf8'))['minecraft:recipe_shapeless'];assert.deepEqual(clear.ingredients,[{item:N+'skewer_recipe_book'}]);assert.equal(clear.result.item,N+'skewer_recipe_book');});
test('all 20 fixed recipe books fit the native 50-character lore-line limit',()=>{const ctx=vm.createContext({canonicalFoodId,forgetEatingItem(){},ItemStack:Stack,BOOK_ID:N+'skewer_recipe_book',BOOK_RECORD_KEY:'record',cloneOne:s=>s.clone(),getItemLore:s=>s.lore,getItemRawLore:s=>s.lore,setItemLore(s,rows){assert.ok(rows.length<=20);for(const row of rows)assert.ok(row.length<=50,row);s.lore=rows},getItemProperty:(s,k)=>s.props[k],setItemProperty:(s,k,v)=>s.props[k]=v});vm.runInContext(fn('bookItem')+';this.run=bookItem',ctx);for(const recipe of recipeTable()){const s=ctx.run({resultId:recipe.id});assert.equal(JSON.parse(s.props.record).resultId,recipe.id)}});
test('before-event book use schedules work without restricted amount writes',()=>{
 let callback,scheduled=false;const item={typeId:N+'skewer_recipe_book',clone(){return {set amount(_v){throw Error('restricted amount')}}}};
 const ctx=vm.createContext({canonicalFoodId,forgetEatingItem(){},recipeTable,SECRET_ID,RAW_SKEWER_TAG,GRILLED_SKEWER_TAG,world:{beforeEvents:{itemUse:{subscribe:f=>callback=f}}},system:{run:f=>{scheduled=true}},PLATE_ID,PLATE_BLOCK_ID,BOOK_ID,COOKERY_RECIPE_ITEMS:new Set(),captureInteractionIntent:()=>({hand:'main'}),interactionStackSignature:()=>'',heldOff:()=>undefined});
 const start=src.indexOf('world.beforeEvents.itemUse.subscribe'),end=src.indexOf('world.beforeEvents.playerInteractWithBlock.subscribe',start);
 const classificationStart=src.indexOf('const FIXED_IDS=new Set();'),classificationEnd=src.indexOf('function enc(',classificationStart);
 vm.runInContext(src.slice(classificationStart,classificationEnd)+'\n'+fn('isSkewer')+'\n'+fn('skewerUseTargetsPlate')+'\n'+fn('cloneOne')+'\n'+src.slice(start,end),ctx);const event={source:{},itemStack:item,cancel:false};callback(event);assert.equal(event.cancel,true);assert.equal(scheduled,true);
});
test('oversized plate preflight never debits the inserted skewer',()=>{
 let debits=0,writes=0;const ctx=vm.createContext({canonicalFoodId,forgetEatingItem(){},PLATE_BLOCK_ID:'plate',heldByHand:()=>({typeId:'skewer'}),readPlateBlock:()=>[],isSkewer:()=>true,stackRow:()=>({id:'skewer'}),plateAdd:()=>({ok:true,rows:[{id:'skewer'}]}),plateItem(){throw Error('32767 bytes')},decrementHand(){debits++;return true},writePlateBlock(){writes++},useSound(){},message(){},interactionFailure(){},javaInteractionFeedback(){}});
 vm.runInContext(fn('handlePlateBlock')+';this.run=handlePlateBlock',ctx);assert.throws(()=>ctx.run({typeId:'plate'},{}),/32767/);assert.equal(debits,0);assert.equal(writes,0);
});
test('oversized plate item cannot clear the world block on break',()=>{
 let clears=0,removed=0;const ctx=vm.createContext({canonicalFoodId,forgetEatingItem(){},PLATE_BLOCK_ID:'plate',readPlateBlock:()=>[{id:'skewer'}],creative:()=>false,plateItem(){throw Error('32767 bytes')},clearPlateBlock(){clears++}});
 vm.runInContext(fn('breakPlate')+';this.run=breakPlate',ctx);assert.throws(()=>ctx.run({typeId:'plate',x:0,y:0,z:0,dimension:{},setType(){removed++}},{}),/32767/);assert.equal(clears,0);assert.equal(removed,0);
});

test('book planner receives native inventory tags',()=>{const f=fixture();f.rows[1].tags=['example:food'];assert.equal(f.run(),true);assert.deepEqual(f.capturedInventory[1].tags,['example:food']);assert.equal(f.capturedInventory[1].id,'minecraft:apple')});
