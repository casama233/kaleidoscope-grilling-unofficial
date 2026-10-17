/** Isolated test overlay only. Never shipped in runtime; no players are created. */
import {world,system,ItemStack,ItemLockMode} from '@minecraft/server';
import {readNativeBottles} from './seasoning_native_storage.js';
import {stationContainer} from './family_station_storage.js';
import {writePlacedSeasoningStack} from './a2743_seasoning_block_adapter.js';
import {setItemProperty,getItemProperty,setItemLore,getItemLore,getItemPropertyIds} from './itemData.js';
import {readFoodSeasonings,setFoodSeasonings} from './a2750_food_state_adapter.js';
import {SEASONING_USES_KEY,SEASONING_VARIANT_KEY,BASE_SEASONINGS} from './a2743_seasoning_contract_core.js';
import {specialSeasoningVisualId} from './a2766_special_seasoning_visual_core.js';
const wait=t=>new Promise(resolve=>system.runTimeout(resolve,t));
const assert=(ok,label)=>{if(!ok)throw Error(label)};
const describe=s=>({kind:'special',ingredients:readFoodSeasonings(s),uses:Number(getItemProperty(s,SEASONING_USES_KEY)),variant:Number(getItemProperty(s,SEASONING_VARIANT_KEY))});
const snapshot=s=>({id:s.typeId,amount:s.amount,name:s.nameTag,lore:getItemLore(s),lock:s.lockMode,keep:s.keepOnDeath,place:s.getCanPlaceOn(),destroy:s.getCanDestroy(),properties:Object.fromEntries(getItemPropertyIds(s).sort().map(k=>[k,getItemProperty(s,k)]))});
const stageKey='kaleidoscope_grilling:qa_seasoning_stage',expectedKey='kaleidoscope_grilling:qa_seasoning_expected';
system.runTimeout(async()=>{
 try{
  const d=world.getDimension('overworld');try{d.runCommand('tickingarea add circle 0 80 64 2 seasoning_qa true')}catch{}
  await wait(60);const block=d.getBlock({x:0,y:80,z:64});
  if(world.getDynamicProperty(stageKey)===undefined){
   block.below().setType('minecraft:stone');block.setType('kaleidoscope_grilling:seasoning_bottle_4');
   const current=readNativeBottles(block,describe,()=>{throw Error('Unexpected legacy reconstruction')},{fresh:true});
   const items=[];
   for(let i=0;i<4;i++){
    const item=new ItemStack(specialSeasoningVisualId(i+1,i),1);item.nameTag='Persisted bottle '+i;setItemLore(item,['獨立瓶 '+i,'Keep custom lore']);
    setFoodSeasonings(item,[...BASE_SEASONINGS]);setItemProperty(item,SEASONING_USES_KEY,i+1);setItemProperty(item,SEASONING_VARIANT_KEY,i);
    setItemProperty(item,'qa:boolean',true);setItemProperty(item,'qa:number',7+i);setItemProperty(item,'qa:string','bottle-'+i);setItemProperty(item,'qa:vector',{x:i,y:2,z:3});
    item.keepOnDeath=true;item.lockMode=ItemLockMode.inventory;item.setCanPlaceOn(['minecraft:stone']);item.setCanDestroy(['minecraft:dirt']);
    current.container.setItem(i,item.clone());items.push(item);
   }
   assert(writePlacedSeasoningStack(block,items.map(describe)),'projection write');
   const expected=items.map(snapshot),stored=readNativeBottles(block,describe,()=>{throw Error('Unexpected reconstruction')}).items.map(snapshot);
   assert(JSON.stringify(stored)===JSON.stringify(expected),'same-cycle native item metadata');
   world.setDynamicProperty(expectedKey,JSON.stringify(expected));world.setDynamicProperty(stageKey,1);
   console.log('SEASONING_NATIVE_PASS '+JSON.stringify({stage:'saved',bottles:4,nativeMetadata:true,simulatedPlayers:false}));
  }else{
   const items=readNativeBottles(block,describe,()=>{throw Error('Restart attempted reconstruction')}).items;
   assert(JSON.stringify(items.map(snapshot))===world.getDynamicProperty(expectedKey),'persisted full metadata after process restart');
   const native=stationContainer(block);assert(native.size===4,'four native slots');
   console.log('SEASONING_NATIVE_PASS '+JSON.stringify({stage:'restored',bottles:4,restartPreserved:true,simulatedPlayers:false}));
  }
 }catch(error){console.error('SEASONING_NATIVE_FAIL '+error+' '+error.stack)}
},100);
