/** Executes runtime function bodies with API/storage doubles; no client claims. */
import test from 'node:test';import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
import {commitSteps} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a277_grill_transaction_core.js';
import {secretFood} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a24_skewering_core.js';
const N='kaleidoscope_grilling:',url=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/a25_plate_recipe_runtime.js',import.meta.url),src=fs.readFileSync(url,'utf8');
function fn(name){const start=src.indexOf('function '+name+'(');assert.ok(start>=0,name);let end=src.indexOf('{',start)+1,n=1;for(;n;end++){if(src[end]==='{')n++;if(src[end]==='}')n--}return src.slice(start,end)}
class Stack{constructor(typeId,amount=1){this.typeId=typeId;this.amount=amount;this.props={};this.lore=[]}getTags(){return this.tags??[]}clone(){return Object.assign(new Stack(this.typeId,this.amount),structuredClone({...this}))}}
function fixture({secret=false,full=false,free=false,fault='',missing=false}={}){
 let capturedInventory;let fired=false,off=new Stack(N+'unfinished_skewer',3);const rows=[new Stack(N+'skewer_recipe_book'),new Stack('minecraft:apple',4),full?new Stack('minecraft:stone',64):undefined];
 const original=rows.map(s=>s?.clone()),oldOff=off.clone(),record={resultId:N+(secret?'secret_skewer':'raw_fish_skewer'),recordedStack:{id:N+'secret_skewer',props:{original:'recorded'},lore:[{translate:'test:original_lore'}]}};
 const fail=k=>{if(k===fault&&!fired){fired=true;throw Error('fault '+k)}};
 const bag={size:rows.length,getItem:i=>rows[i]?.clone(),setItem(i,s){rows[i]=s?.clone();fail('slot')},addItem(s){const i=rows.findIndex(x=>!x);if(i<0)return s;rows[i]=s.clone();fail('delivery');return undefined}};
 const holder={name:'tester',id:'test',selectedSlotIndex:0,playSound(){}};
 const ctx=vm.createContext({ItemStack:Stack,SECRET_ID:N+'secret_skewer',UNFINISHED_ID:N+'unfinished_skewer',SKEWER_INGREDIENTS_KEY:N+'skewer_ingredients',SECRET_COOKED_KEY:'cooked',SECRET_COOKED_INGREDIENTS_KEY:'cookedRows',SECRET_CREATOR_KEY:'creator',console:{warn(){}},readBookRecord:()=>record,heldByHand:(_p,h)=>h==='off'?off:bag.getItem(0),heldOff:()=>off,setOff(_p,s){off=s?.clone();fail('off')},mainContainer:()=>bag,bookIngredientSlots:()=>[['minecraft:apple']],planInventoryConsumption:inventory=>{capturedInventory=structuredClone(inventory);return missing?{ok:false,missing:['apple']}:{ok:true,plan:[{slot:1,count:1}]}},creative:()=>free,getItemProperty:(s,k)=>s.props[k],setItemProperty:(s,k,v)=>{if(v===undefined)delete s.props[k];else s.props[k]=v},getItemLore:s=>s.lore,getItemRawLore:s=>s.lore,setItemLore:(s,v)=>s.lore=v,restoreStack:r=>{fail('restore');const s=new Stack(r.id);s.props={...r.props};s.lore=structuredClone(r.lore);return s},commitSteps,message(){},interactionFailure(){},javaInteractionFeedback(){},decrementHand(_p,h,n){if(free)return true;if(!off||off.amount<n)return false;off.amount-=n;fail('off');return true}});
 vm.runInContext(fn('consumePlan')+'\n'+fn('isRecipeStick')+'\n'+fn('craftFromBook')+';this.run=craftFromBook',ctx);
 return {run:()=>ctx.run(holder,rows[0]),rows,original,oldOff,get capturedInventory(){return capturedInventory},get off(){return off}};
}
for(const secret of [false,true])test('book produces '+(secret?'recorded secret':'fixed')+' with empty starter',()=>{const f=fixture({secret});assert.equal(f.run(),true);assert.equal(f.rows[1].amount,3);assert.equal(f.off.amount,2);assert.equal(f.rows[2].typeId,N+(secret?'secret_skewer':'raw_fish_skewer'));if(secret){assert.equal(f.rows[2].props.original,'recorded');assert.deepEqual(f.rows[2].lore[0],{translate:'test:original_lore'});assert.equal(f.rows[2].props.cooked,false);assert.equal(JSON.parse(f.rows[2].props.creator).name,'tester')}});
for(const fault of ['slot','off','delivery'])test('write-after-mutation '+fault+' restores materials/starter/output',()=>{const f=fixture({fault});assert.equal(f.run(),false);assert.deepEqual(f.rows,f.original);assert.deepEqual(f.off,f.oldOff)});
test('full inventory refuses delivery and rolls back inputs',()=>{const f=fixture({full:true});assert.equal(f.run(),false);assert.deepEqual(f.rows,f.original);assert.deepEqual(f.off,f.oldOff)});
test('cannot restore recorded data before any debit',()=>{const f=fixture({secret:true,fault:'restore'});assert.throws(f.run,/restore/);assert.deepEqual(f.rows,f.original);assert.deepEqual(f.off,f.oldOff)});
test('missing ingredient never partially consumes',()=>{const f=fixture({missing:true});assert.equal(f.run(),false);assert.deepEqual(f.rows,f.original);assert.deepEqual(f.off,f.oldOff)});
test('creative mode retains ingredients and starter',()=>{const f=fixture({free:true});assert.equal(f.run(),true);assert.equal(f.rows[1].amount,4);assert.equal(f.off.amount,3)});
test('filled unfinished skewer cannot be consumed as a stick',()=>{const f=fixture();f.off.props[N+'skewer_ingredients']='[{"id":"minecraft:apple"}]';assert.equal(f.run(),false);assert.deepEqual(f.rows,f.original);assert.equal(f.off.amount,3)});
test('plate computes cooked-secret food from cooked rows but duplicates from raw rows',()=>{
 const raw=[{id:'minecraft:potato',nutrition:1,saturation:.3},{id:'minecraft:potato',nutrition:1,saturation:.3},{id:'minecraft:beef',nutrition:3,saturation:.3}],cooked=raw.map((r,i)=>({...r,id:i<2?'minecraft:baked_potato':'minecraft:cooked_beef',nutrition:i<2?5:8}));
 const ctx=vm.createContext({SECRET_ID:N+'secret_skewer',SKEWER_INGREDIENTS_KEY:'raw',SECRET_COOKED_KEY:'cooked',SECRET_COOKED_INGREDIENTS_KEY:'effective',parseRowsProperty:(_s,k)=>k==='raw'?raw:cooked,getItemProperty:()=>true,secretFood});vm.runInContext(fn('skewerFood')+';this.run=skewerFood',ctx);
 const out=ctx.run({typeId:N+'secret_skewer'});assert.equal(out.nutrition,8);assert.equal(out.duplicate,true);
});
test('four-paper blank recipe and one-book reset retain paper economy',()=>{const dir=new URL('../recipes/',url);const blank=JSON.parse(fs.readFileSync(new URL('skewer_recipe_book_blank.json',dir),'utf8'))['minecraft:recipe_shaped'];assert.deepEqual(blank.pattern,['PP','PP']);assert.equal(blank.key.P.item,'minecraft:paper');assert.equal(blank.result.item,N+'skewer_recipe_book');const clear=JSON.parse(fs.readFileSync(new URL('clear_skewer_recipe_book.json',dir),'utf8'))['minecraft:recipe_shapeless'];assert.deepEqual(clear.ingredients,[{item:N+'skewer_recipe_book'}]);assert.equal(clear.result.item,N+'skewer_recipe_book');});
const {recipeTable}=await import('../../projects/grilling/gameplay_core/behavior_pack/scripts/a24_skewering_core.js');
test('all 20 fixed recipe books fit the native 50-character lore-line limit',()=>{const ctx=vm.createContext({ItemStack:Stack,BOOK_ID:N+'skewer_recipe_book',BOOK_RECORD_KEY:'record',cloneOne:s=>s.clone(),getItemLore:s=>s.lore,getItemRawLore:s=>s.lore,setItemLore(s,rows){assert.ok(rows.length<=20);for(const row of rows)assert.ok(row.length<=50,row);s.lore=rows},getItemProperty:(s,k)=>s.props[k],setItemProperty:(s,k,v)=>s.props[k]=v});vm.runInContext(fn('bookItem')+';this.run=bookItem',ctx);for(const recipe of recipeTable()){const s=ctx.run({resultId:recipe.id});assert.equal(JSON.parse(s.props.record).resultId,recipe.id)}});
test('before-event book use schedules work without restricted amount writes',()=>{
 let callback,scheduled=false;const item={typeId:N+'skewer_recipe_book',clone(){return {set amount(_v){throw Error('restricted amount')}}}};
 const ctx=vm.createContext({world:{beforeEvents:{itemUse:{subscribe:f=>callback=f}}},system:{run:f=>{scheduled=true}},PLATE_ID:'plate',BOOK_ID:N+'skewer_recipe_book',COOKERY_RECIPE_ITEMS:new Set(),captureInteractionIntent:()=>({hand:'main'}),interactionStackSignature:()=>'',heldOff:()=>undefined});
 const start=src.indexOf('world.beforeEvents.itemUse.subscribe'),end=src.indexOf('world.beforeEvents.playerInteractWithBlock.subscribe',start);
 vm.runInContext(fn('cloneOne')+'\n'+src.slice(start,end),ctx);const event={source:{},itemStack:item,cancel:false};callback(event);assert.equal(event.cancel,true);assert.equal(scheduled,true);
});
test('oversized plate preflight never debits the inserted skewer',()=>{
 let debits=0,writes=0;const ctx=vm.createContext({PLATE_BLOCK_ID:'plate',heldByHand:()=>({typeId:'skewer'}),readPlateBlock:()=>[],isSkewer:()=>true,stackRow:()=>({id:'skewer'}),plateAdd:()=>({ok:true,rows:[{id:'skewer'}]}),plateItem(){throw Error('32767 bytes')},decrementHand(){debits++;return true},writePlateBlock(){writes++},message(){},interactionFailure(){},javaInteractionFeedback(){}});
 vm.runInContext(fn('handlePlateBlock')+';this.run=handlePlateBlock',ctx);assert.throws(()=>ctx.run({typeId:'plate'},{}),/32767/);assert.equal(debits,0);assert.equal(writes,0);
});
test('oversized plate item cannot clear the world block on break',()=>{
 let clears=0,removed=0;const ctx=vm.createContext({PLATE_BLOCK_ID:'plate',readPlateBlock:()=>[{id:'skewer'}],creative:()=>false,plateItem(){throw Error('32767 bytes')},clearPlateBlock(){clears++}});
 vm.runInContext(fn('breakPlate')+';this.run=breakPlate',ctx);assert.throws(()=>ctx.run({typeId:'plate',x:0,y:0,z:0,dimension:{},setType(){removed++}},{}),/32767/);assert.equal(clears,0);assert.equal(removed,0);
});

test('book planner receives native inventory tags',()=>{const f=fixture();f.rows[1].tags=['example:food'];assert.equal(f.run(),true);assert.deepEqual(f.capturedInventory[1].tags,['example:food']);assert.equal(f.capturedInventory[1].id,'minecraft:apple')});
