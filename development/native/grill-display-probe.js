/** Test overlay in an independent world only. No players or client claims. */
import {world,system,ItemStack} from '@minecraft/server';
import {stationContainer,peekStationContainer,storageKey} from './family_station_storage.js';
import {syncGrillDisplay,grillDisplayHelperCount} from './grill_visual_runtime.js';
import {GRILL_FOOD_ENTITY,grillVisualStage} from './grill_visual_core.js';
import {GRILL_MODEL_INDEX} from './grill_visual_data.js';
import {writeState} from './main.js';
import {initialState} from './core_logic.js';
import {setItemProperty,getItemProperty,setItemLore,getItemRawLore} from './itemData.js';
const NS='kaleidoscope_grilling:',stageKey=NS+'qa_display_stage',savedKey=NS+'qa_display_snapshot';
const wait=t=>new Promise(r=>system.runTimeout(r,t));
const check=(value,label)=>{if(!value)throw Error(label);};
const snapshot=s=>({id:s.typeId,amount:s.amount,name:s.nameTag,lore:getItemRawLore(s),marker:getItemProperty(s,'qa:original')});
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');try{d.runCommand('tickingarea add circle 96 80 64 2 display_qa true');}catch{}
 let b;for(let i=0;i<60;i++){await wait(10);try{b=d.getBlock({x:96,y:80,z:64});}catch{}if(b)break;}check(b,'test chunk unavailable');
 const viewer=[{dimensionId:d.id,x:96,y:80,z:64}],helpers=()=>d.getEntities({type:GRILL_FOOD_ENTITY,location:{x:96.5,y:80,z:64.5},maxDistance:3});
 if(world.getDynamicProperty(stageKey)===undefined){
  b.below().setType('minecraft:stone');b.setType(NS+'grill');const c=stationContainer(b);
  for(let i=0;i<3;i++){const s=new ItemStack(Object.keys(GRILL_MODEL_INDEX)[i]);s.nameTag='Native original '+i;setItemLore(s,[{rawtext:[{translate:'other:keepsake'},{text:' '+i}]}]);setItemProperty(s,'qa:original',i);c.setItem(i,s);}
  const before=JSON.stringify([0,1,2].map(i=>snapshot(c.getItem(i)))),ledger=world.getDynamicProperty(storageKey(b));
  syncGrillDisplay(b,viewer);await wait(1);check(helpers().length===3,'three real slots rendered');check(grillDisplayHelperCount()===3,'three controller handles');
  const originalIds=helpers().map(e=>e.id).sort();let stages=0;
  for(const [phase,flips]of [[0,0],[1,0],[1,1],[1,2],[2,4],[3,4]]){
   const state={...initialState(),phase,flips};writeState(b,state);syncGrillDisplay(b,viewer);await wait(1);
   const actual=helpers().map(e=>e.getProperty(NS+'model')).sort((a,b)=>a-b),expected=[0,1,2].map(i=>i*6+grillVisualStage(state));
   check(JSON.stringify(actual)===JSON.stringify(expected),'native synced stage '+phase+'/'+flips);
   check(helpers().every(e=>e.getProperty(NS+'ready')===true&&e.getProperty(NS+'flips')===flips),'ready and flip properties');stages++;
  }
  check(JSON.stringify(helpers().map(e=>e.id).sort())===JSON.stringify(originalIds),'model changes reuse same entities');
  const directions=[];
  for(const direction of ['north','east','south','west']){
   b.setPermutation(b.permutation.withState('minecraft:cardinal_direction',direction));syncGrillDisplay(b,viewer);await wait(1);
   const row=helpers().find(e=>Math.floor(e.getProperty(NS+'model')/6)===0);
   directions.push({direction,location:row.location,rotation:row.getRotation()});
  }
  check(JSON.stringify([0,1,2].map(i=>snapshot(c.getItem(i))))===before,'display never mutates items');
  check(world.getDynamicProperty(storageKey(b))===ledger,'display never rewrites owner ledger');
  c.setItem(1,undefined);syncGrillDisplay(b,viewer);await wait(1);check(helpers().length===2,'empty middle slot removed');
  const original=new ItemStack(Object.keys(GRILL_MODEL_INDEX)[1]);original.nameTag='Native original 1';setItemLore(original,[{rawtext:[{translate:'other:keepsake'},{text:' 1'}]}]);setItemProperty(original,'qa:original',1);c.setItem(1,original);
  syncGrillDisplay(b,[]);check(helpers().length===0,'no audience removes displays');
  writeState(b,{...initialState(),phase:1,flips:2});world.setDynamicProperty(savedKey,before);world.setDynamicProperty(stageKey,1);
  await wait(25);check(helpers().length===0,'empty audience stays quiet');
  console.log('DISPLAY_NATIVE_PASS '+JSON.stringify({stage:'saved',nativeSlots:3,stageTransitions:stages,directions,contentsPreserved:true,ownerLedgerUnchanged:true,emptyMiddleRemoved:true,explicitEmptyAudienceQuiet:true,simulatedPlayers:false,client:false}));
 }else{
  const c=peekStationContainer(b);check(c,'restored backing inventory');check(JSON.stringify([0,1,2].map(i=>snapshot(c.getItem(i))))===world.getDynamicProperty(savedKey),'native item metadata survived restart');
  check(helpers().length===0,'transient displays not saved');syncGrillDisplay(b,viewer);await wait(1);check(helpers().length===3,'restored inventory regenerates three displays');
  check(helpers().every(e=>e.getProperty(NS+'flips')===2),'saved flip restored');
  b.setType('minecraft:air');await wait(25);check(helpers().length===0,'destroyed grill helper cleanup');
  check(c.getItem(0)&&c.getItem(1)&&c.getItem(2),'render cleanup preserves backing items for recovery');
  console.log('DISPLAY_NATIVE_PASS '+JSON.stringify({stage:'restored',nativeSlots:3,nativeMetadataPersisted:true,transientHelpersRegenerated:true,restoredFlips:2,destroyCleanup:true,backingPreserved:true,simulatedPlayers:false,client:false}));
 }
}catch(error){console.error('DISPLAY_NATIVE_FAIL '+error+' '+error.stack);}},100);
