/** Isolated test overlay only. No players, no client acceptance claim. */
import {world,system,ItemStack} from '@minecraft/server';
import {stationContainer} from './family_station_storage.js';
import {readGrillState} from './a2740_grill_state_adapter.js';
import {initialState,light,brush,flip,season,outputKind} from './core_logic.js';
import {setItemProperty,getItemProperty,setItemLore,getItemLore} from './itemData.js';
import {readFoodSeasonings,isHotFood} from './a2750_food_state_adapter.js';
import {writeState,outputFor,burnGrillContents} from './main.js';
const wait=t=>new Promise(r=>system.runTimeout(r,t)),check=(ok,label)=>{if(!ok)throw Error(label)};
const key='kaleidoscope_grilling:qa_core_stage',expected='kaleidoscope_grilling:qa_core_expected',ids=['fish','potato_slice','mushroom'];
const snapshot=s=>({id:s.typeId,amount:s.amount,name:s.nameTag,lore:getItemLore(s),marker:getItemProperty(s,'qa:ingredient')});
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');try{d.runCommand('tickingarea add circle 0 80 64 2 core_qa true')}catch{}
 let block;for(let attempt=0;attempt<60;attempt++){await wait(10);try{block=d.getBlock({x:0,y:80,z:64})}catch{}if(block)break;}check(block,'test chunk unavailable');
 if(world.getDynamicProperty(key)===undefined){
  block.below().setType('minecraft:stone');block.setType('kaleidoscope_grilling:grill');const c=stationContainer(block);
  for(let i=0;i<3;i++){const s=new ItemStack('kaleidoscope_grilling:raw_'+ids[i]+'_skewer',1);s.nameTag='Core original '+i;setItemLore(s,['Ingredient metadata '+i]);setItemProperty(s,'qa:ingredient',i);c.setItem(i,s);}
  writeState(block,brush(light(initialState(),true),3,1200).state);
  for(let i=0;i<2;i++){const f=flip(readGrillState(block));check(f.ok,'flip accepted');writeState(block,f.state);check(!flip(readGrillState(block)).ok,'immediate flip rejected');await wait(22);}
  const s=light(readGrillState(block),false);writeState(block,s);check(s.phase===1&&s.flips===2,'mid-cycle state');world.setDynamicProperty(expected,JSON.stringify([0,1,2].map(i=>snapshot(c.getItem(i)))));world.setDynamicProperty(key,1);
  console.log('CORE_NATIVE_PASS '+JSON.stringify({stage:'saved',skewers:3,flips:2,nativeCooldown:true,simulatedPlayers:false}));
 }else{
  const c=stationContainer(block),s=readGrillState(block);check(s.phase===1&&s.flips===2&&!s.lit,'mid-cycle persisted');check(JSON.stringify([0,1,2].map(i=>snapshot(c.getItem(i))))===world.getDynamicProperty(expected),'native stacks persisted');writeState(block,light(s,true));
  for(let i=0;i<2;i++){const f=flip(readGrillState(block));check(f.ok,'remaining flip');writeState(block,f.state);await wait(22);}
  const spices=['kaleidoscope_grilling:canola_powder','kaleidoscope_grilling:cumin_powder','kaleidoscope_grilling:chili_powder'];const cooked=season(readGrillState(block),3,spices);check(cooked.ok,'season accepted');writeState(block,cooked.state);
  for(let i=0;i<3;i++){const out=outputFor(c.getItem(i),readGrillState(block),outputKind(readGrillState(block)));check(out.typeId==='kaleidoscope_grilling:grilled_'+ids[i]+'_skewer','cooked output');check(getItemProperty(out,'qa:ingredient')===i,'output metadata');check(isHotFood(out),'output hot');check(JSON.stringify(readFoodSeasonings(out))===JSON.stringify(spices),'output seasonings');}
  check(burnGrillContents(block,readGrillState(block),light(initialState(),true)),'charcoal transaction');check(c.emptySlotsCount===3,'native grill emptied');check(readGrillState(block).phase===0,'grill reset');
  console.log('CORE_NATIVE_PASS '+JSON.stringify({stage:'restored',skewers:3,totalFlips:4,cookedOutputs:true,heatAndSeasoning:true,charcoalTransaction:true,restartPreserved:true,simulatedPlayers:false}));
 }
}catch(e){console.error('CORE_NATIVE_FAIL '+e+' '+e.stack)}},100);
