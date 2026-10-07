/** Production event routing; does not certify native callback delivery or rendered output. */
import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import {canonicalFoodId} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/eating_profile_ids.js';
const src=fs.readFileSync('projects/grilling/gameplay_core/behavior_pack/scripts/a25_plate_recipe_runtime.js','utf8'),N='kaleidoscope_grilling:',PLATE=N+'skewer_plate_block',FOOD=N+'grilled_beef_skewer';
function body(name){const start=src.indexOf('function '+name+'(');let end=src.indexOf('{',start)+1,depth=1;while(depth){const c=src[end++];if(c==='{')depth++;if(c==='}')depth--;}return src.slice(start,end);}
function fixture({id=FOOD,target=PLATE,distance=2,rayFault=false,full=false}={}){
 const callbacks={},queued=[];let rayReads=0,transfers=0,nativeStarts=0,held={typeId:id,amount:2};
 const block={typeId:target,location:{x:0,y:1,z:0},dimension:{getBlock:()=>block}},player={selectedSlotIndex:8,isSneaking:false,getBlockFromViewDirection(options){rayReads++;assert.equal(options.maxDistance,6);if(rayFault)throw Error('unreadable view');return distance<=options.maxDistance?{block}:undefined;}};
 const ctx=vm.createContext({canonicalFoodId,FIXED_IDS:new Set([FOOD]),SECRET_ID:N+'secret_skewer',RAW_SKEWER_TAG:'raw',GRILLED_SKEWER_TAG:'cooked',PLATE_BLOCK_ID:PLATE,PLATE_ID:N+'skewer_plate',BOOK_ID:'book',RECIPE_BLOCK_ID:'recipe',COOKERY_TABLE:'table',COOKERY_RECIPE_ITEMS:new Set(),plateQaTrace(){},
 world:{beforeEvents:{itemUse:{subscribe:f=>callbacks.use=f},playerInteractWithBlock:{subscribe:f=>callbacks.block=f}}},system:{run:f=>queued.push(f)},captureInteractionIntent:()=>({hand:'main'}),interactionIntentStillCurrent:()=>true,heldByHand:()=>held,heldOff:()=>undefined,isRecordableStack:()=>false,plateRowsFromItem:()=>[{}],isInitialBlockPress:x=>x!==false,readPlateBlock:()=>Array(full?5:1).fill({}),
 handlePlateBlock(){if(!full){transfers++;held={...held,amount:held.amount-1};}},grillingConfig:()=>({interceptCookeryTableWhenPlacingPlate:true}),message(){},faceName:x=>x});
 const useStart=src.indexOf('world.beforeEvents.itemUse.subscribe'),blockStart=src.indexOf('world.beforeEvents.playerInteractWithBlock.subscribe'),end=src.indexOf('world.beforeEvents.playerBreakBlock.subscribe',blockStart);
 vm.runInContext(body('isSkewer')+'\n'+body('skewerUseTargetsPlate')+'\n'+src.slice(useStart,blockStart)+'\n'+src.slice(blockStart,end),ctx);
 return {player,block,queued,get held(){return held;},get transfers(){return transfers;},get rayReads(){return rayReads;},get nativeStarts(){return nativeStarts;},target(v){block.typeId=v;},use(cancel=false){const e={source:player,itemStack:held,cancel};callbacks.use(e);if(!e.cancel)nativeStarts++;return e;},interact(first=true){const e={player,block,itemStack:held,isFirstEvent:first,blockFace:'up',cancel:false};callbacks.block(e);return e;},flush(){while(queued.length)queued.shift()();}};
}
let cases=0;
for(const order of ['item_first','block_first']){
 const f=fixture();if(order==='item_first'){assert.equal(f.use().cancel,true);f.interact();}else{f.interact();assert.equal(f.use().cancel,true);}f.flush();assert.equal(f.transfers,1);assert.equal(f.held.amount,1);assert.equal(f.use().cancel,true);assert.equal(f.nativeStarts,0);f.interact(false);f.flush();assert.equal(f.transfers,1);cases++;
}
for(const id of [FOOD,FOOD+'_native_plain',N+'secret_skewer',N+'secret_skewer_java_three_alt',N+'secret_skewer_native_plain']){const f=fixture({id});assert.equal(f.use().cancel,true);cases++;}
for(const options of [{target:'minecraft:air'},{target:'minecraft:stone'},{target:PLATE,distance:7},{rayFault:true}]){const f=fixture(options);assert.equal(f.use().cancel,false);assert.equal(f.nativeStarts,1);cases++;}
for(const id of ['minecraft:carrot','minecraft:stone',N+'skewer_plate']){const f=fixture({id});assert.equal(f.use().cancel,false);assert.equal(f.rayReads,0);cases++;}
const full=fixture({full:true});assert(full.use().cancel);full.interact();full.flush();assert.equal(full.held.amount,2);assert.equal(full.transfers,0);cases++;
const cancelled=fixture();assert(cancelled.use(true).cancel);assert.equal(cancelled.rayReads,0);cases++;
const air=fixture();assert(air.use().cancel);air.target('minecraft:air');assert.equal(air.use().cancel,false);assert.equal(air.nativeStarts,1);cases++;
console.log(`Plate use arbitration: ${cases} callback order, aliases, repeat/full plate, bounded target and immediate air-use cases PASS`);
