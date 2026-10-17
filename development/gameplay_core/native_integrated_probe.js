// Test-only overlay in an isolated NEW world. No simulated player events.
import {world,system,ItemStack,BlockPermutation} from '@minecraft/server';
import {stationContainer,inspectStationStorage,retireEmptyStationContainer} from './family_station_storage.js';
import {setItemProperty,getItemProperty,setItemLore,getItemLore} from './itemData.js';
import {resolveSecretSmokedId,registerSecretSmoking} from './secret_compat_core.js';
import {resolveSmokingResult,registerSmokingResult} from './a288_parity_contract.js';
const wait=n=>new Promise(resolve=>system.runTimeout(resolve,n));
const assert=(ok,label)=>{if(!ok)throw Error(label);};
world.afterEvents.worldLoad.subscribe(()=>system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');d.runCommand('tickingarea add circle 0 80 64 2 grilling_probe true');await wait(40);
 const results=[];
 for(const [i,type,size] of [[0,'kaleidoscope_grilling:grill',3],[1,'kaleidoscope_grilling:advanced_rack_block',9]]){
  const b=d.getBlock({x:i*4,y:80,z:64});b.setPermutation(BlockPermutation.resolve(type));
  const c=stationContainer(b);assert(c.size===size,'native inventory size');
  const item=new ItemStack('minecraft:stick',3);item.nameTag='PR integration probe';setItemLore(item,['native persistence']);setItemProperty(item,'integration:value',17);c.setItem(0,item);
  await wait(5);const again=stationContainer(b),r=again.getItem(0);assert(r.amount===3&&r.nameTag===item.nameTag,'stack identity');assert(getItemProperty(r,'integration:value')===17&&getItemLore(r)[0]==='native persistence','metadata roundtrip');
  let guarded=false;try{retireEmptyStationContainer(b);}catch{guarded=true;}assert(guarded,'nonempty station retirement must fail');
  results.push({type,slots:again.size,metadata:true,retirementGuard:true});
 }
 assert(registerSmokingResult('integration:raw','integration:cooked'),'legacy registration');assert(resolveSecretSmokedId('integration:raw')==='integration:cooked','one registry legacy to new');
 assert(registerSecretSmoking({input:'integration:raw2',output:'integration:cooked2'}),'modern registration');assert(resolveSmokingResult('integration:raw2')==='integration:cooked2','one registry new to legacy');
 console.log('GRILL_NATIVE_PASS '+JSON.stringify({stations:results,oneRegistry:true,realProcessRestart:false,client:false,simulatedPlayers:false}));
}catch(e){console.error('GRILL_NATIVE_FAIL '+e+' '+e.stack);}},100));
