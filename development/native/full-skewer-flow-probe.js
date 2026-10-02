/** Isolated QA overlay: native containers/core/output pipeline. No players or use events. */
import {world,system,ItemStack} from '@minecraft/server';
import {recipeTable,appendOutcome,UNFINISHED_ID,SECRET_ID,SKEWER_INGREDIENTS_KEY,SECRET_COOKED_KEY} from './a24_skewering_core.js';
import {initialState,light,brush,flip,season,outputKind} from './core_logic.js';
import {stationContainer} from './family_station_storage.js';
import {readGrillState} from './a2740_grill_state_adapter.js';
import {writeState,outputFor,ingredientSnapshot,writeSkewerRows} from './main.js';
import {buildCookeryOilPot,readCookeryOilPot,planCookeryOilPotConsumption} from './a2734_cookery_oil_pot_adapter.js';
import {BASE_SEASONINGS,SEASONING_USES_KEY} from './a2743_seasoning_contract_core.js';
import {retargetSpecialSeasoningStack} from './a2766_special_seasoning_visual_runtime.js';
import {setFoodSeasonings,readFoodSeasonings,isHotFood,hotUntil} from './a2750_food_state_adapter.js';
import {setItemProperty,getItemProperty} from './itemData.js';
import {commitSteps} from './a277_grill_transaction_core.js';
import {slotWrite} from './rack_transfer_plan.js';
const check=(ok,label)=>{if(!ok)throw Error(label)},wait=t=>new Promise(r=>system.runTimeout(r,t));
const key='kaleidoscope_grilling:qa_full_flow_28';
const snapshot=s=>({id:s.typeId,amount:s.amount,rows:getItemProperty(s,SKEWER_INGREDIENTS_KEY),cooked:getItemProperty(s,SECRET_COOKED_KEY)??false,hotUntil:hotUntil(s),seasoning:readFoodSeasonings(s)});
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');try{d.runCommand('tickingarea add circle 12 80 64 2 full_flow_qa true')}catch{}
 let block;for(let i=0;i<60;i++){await wait(10);try{block=d.getBlock({x:12,y:80,z:64})}catch{}if(block)break}check(block,'chunk unavailable');
 const chest=d.getBlock({x:15,y:80,z:64}),previous=world.getDynamicProperty(key);
 if(previous!==undefined){
  const c=chest.getComponent('minecraft:inventory').container,expected=JSON.parse(previous);
  for(let i=0;i<expected.length;i++)check(JSON.stringify(snapshot(c.getItem(i)))===JSON.stringify(expected[i]),'saved output '+i);
  check(stationContainer(block).emptySlotsCount===3,'empty native grill persisted');check(readGrillState(block).phase===0,'reset phase persisted');
  console.log('FLOW_NATIVE_PASS '+JSON.stringify({stage:'restored',fixedRecipes:19,secretRecipes:1,outputs:20,nativeItemsAndStorage:true,heatAndSeasoningsSaved:true,corePipeline:true,playerUseEvents:false,naturalAcquisition:false,eating:false,restartPreserved:true,players:world.getAllPlayers().length}));return;
 }
 block.below().setType('minecraft:stone');block.setType('kaleidoscope_grilling:grill');chest.setType('minecraft:chest');
 const grill=stationContainer(block),outputs=chest.getComponent('minecraft:inventory').container;
 const recipes=recipeTable().filter(r=>r.cooked).map(r=>({id:r.id,cooked:r.cooked,inputs:r.slots.map(s=>s[0])}));
 recipes.push({id:SECRET_ID,cooked:SECRET_ID,inputs:['minecraft:apple','minecraft:carrot','minecraft:beef']});
 let oilCost=0,seasoningCost=0,flips=0;
 for(let offset=0;offset<recipes.length;offset+=3){
  const batch=recipes.slice(offset,offset+3),n=batch.length;
  for(let i=0;i<n;i++){
   const r=batch[i];let stack=new ItemStack(UNFINISHED_ID),rows=[];
   for(const id of r.inputs){const row=ingredientSnapshot(new ItemStack(id),true),result=appendOutcome(rows,row,row.edible);check(result.ok,'append '+id);rows.push(row);stack=new ItemStack(result.id);writeSkewerRows(stack,rows);check(getItemProperty(stack,SKEWER_INGREDIENTS_KEY)===JSON.stringify(rows),'native threading data '+id)}
   check(stack.typeId===r.id,'threaded result '+r.id);grill.setItem(i,stack);
  }
  writeState(block,light(initialState(),true));
  const oil=buildCookeryOilPot('canola',n),oilPlan=planCookeryOilPotConsumption(oil,n);check(oilPlan.ok,'native oil plan');
  check(readCookeryOilPot(oil).count===n&&oilPlan.next.typeId==='kaleidoscope_cookery:oil_pot','native oil debit');
  const brushed=brush(readGrillState(block),n,1200);check(brushed.ok,'brush');writeState(block,brushed.state);oilCost+=n;
  for(let i=0;i<4;i++){const result=flip(readGrillState(block));check(result.ok,'flip');writeState(block,result.state);flips++;if(i<3){check(!flip(readGrillState(block)).ok,'flip cooldown');await wait(22)}}
  const bottle=new ItemStack('kaleidoscope_grilling:special_seasoning');setFoodSeasonings(bottle,BASE_SEASONINGS);setItemProperty(bottle,SEASONING_USES_KEY,0);
  const nextBottle=retargetSpecialSeasoningStack(bottle,n);check(nextBottle&&getItemProperty(nextBottle,SEASONING_USES_KEY)===n,'native bottle debit');
  check(JSON.stringify(readFoodSeasonings(nextBottle))===JSON.stringify(BASE_SEASONINGS),'native bottle ingredients');
  const seasoned=season(readGrillState(block),n,readFoodSeasonings(nextBottle));check(seasoned.ok,'season');writeState(block,seasoned.state);seasoningCost+=n;
  const steps=[];
  for(let i=0;i<n;i++){const out=outputFor(grill.getItem(i),readGrillState(block),outputKind(readGrillState(block)));check(out.typeId===batch[i].cooked,'cooked result');check(isHotFood(out),'output hot');check(JSON.stringify(readFoodSeasonings(out))===JSON.stringify(BASE_SEASONINGS),'output seasoning');steps.push(slotWrite(grill,i,undefined),slotWrite(outputs,offset+i,out))}
  check(commitSteps(steps).ok,'native container transfer');writeState(block,light(initialState(),false));check(grill.emptySlotsCount===3,'grill cleared');
 }
 check(oilCost===20&&seasoningCost===20&&flips===28,'batch material accounting');
 world.setDynamicProperty(key,JSON.stringify(recipes.map((_r,i)=>snapshot(outputs.getItem(i)))));
 console.log('FLOW_NATIVE_PASS '+JSON.stringify({stage:'saved',fixedRecipes:19,secretRecipes:1,outputs:20,nativeItemsAndStorage:true,heatAndSeasoningsSaved:true,corePipeline:true,oilCost,seasoningCost,flips,playerUseEvents:false,naturalAcquisition:false,eating:false,players:world.getAllPlayers().length}));
}catch(e){console.error('FLOW_NATIVE_FAIL '+e+' '+e.stack)}},160);
