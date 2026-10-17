import {world,system,ItemStack,BlockPermutation} from '@minecraft/server';
import {getItemProperty,setItemProperty} from './itemData.js';
import {SECRET_ID,SECRET_COOKED_KEY,SECRET_COOKED_INGREDIENTS_KEY,SKEWER_INGREDIENTS_KEY} from './a24_skewering_core.js';
import {initialState,flip} from './core_logic.js';
import {registerSecretSmoking} from './secret_compat_core.js';
const PHASE='senra_snapshot_probe:phase',POS={x:1030,y:80,z:1030};
function assert(ok,label){if(!ok)throw Error(label);}
export function runFourthFlipNativeProbe(api){
 system.runTimeout(async()=>{
  try{
   const stage=world.getDynamicProperty(PHASE)??0,dimension=world.getDimension('overworld');
   await world.tickingAreaManager.createTickingArea('snapshot-'+stage,{dimension,from:{x:1024,y:0,z:1024},to:{x:1039,y:100,z:1039}});
   system.runTimeout(()=>{
    try{
     const block=dimension.getBlock(POS);
     if(stage===0){
      block.setPermutation(BlockPermutation.resolve('kaleidoscope_grilling:grill'));
      const container=api.inv(block),rows=['minecraft:beef','minecraft:carrot','minecraft:apple'].map(id=>{
       const item=new ItemStack(id,1);item.nameTag='native snapshot '+id;setItemProperty(item,'probe:quality',4);return api.ingredientSnapshot(item,true);
      });
      for(let i=0;i<3;i++){const item=new ItemStack(SECRET_ID,1);item.nameTag='native secret '+i;api.writeSkewerRows(item,rows);setItemProperty(item,'probe:creator','native test');container.setItem(i,item);}
      const before={...initialState(),phase:1,flips:3,heatTicks:1200,lit:false};api.writeState(block,before);
      assert(api.commitGrillFlip(block,before,flip(before).state),'fourth flip commit');
      assert(api.readState(block).phase===2,'cooking phase advanced');
      for(let i=0;i<3;i++){
       const item=container.getItem(i),cache=getItemProperty(item,SECRET_COOKED_INGREDIENTS_KEY),raw=getItemProperty(item,SKEWER_INGREDIENTS_KEY);
       assert(typeof cache==='string'&&JSON.parse(cache)[0].id==='minecraft:cooked_beef','native cooked cache');
       assert(JSON.parse(raw)[0].id==='minecraft:beef','raw rows retained');
       assert(getItemProperty(item,SECRET_COOKED_KEY)!==true,'not prematurely Cooked');
       assert(item.nameTag==='native secret '+i&&getItemProperty(item,'probe:creator')==='native test','outer metadata retained');
       world.setDynamicProperty('senra_snapshot_probe:cache_'+i,cache);world.setDynamicProperty('senra_snapshot_probe:raw_'+i,raw);
      }
      world.setDynamicProperty(PHASE,1);
      console.log('NATIVE_SNAPSHOT_PREPARED '+JSON.stringify({nativeContainer:true,slots:3,fourthFlip:true,uncookedStoredItem:true,rawMetadataPreserved:true,client:false}));
     }else if(stage===1){
      assert(block.typeId==='kaleidoscope_grilling:grill','grill persists after restart');const container=api.inv(block),state=api.readState(block);
      assert(state.phase===2&&state.flips===4,'phase persists after restart');
      registerSecretSmoking({input:'minecraft:beef',output:'minecraft:potato'});
      for(let i=0;i<3;i++){
       const item=container.getItem(i),cache=world.getDynamicProperty('senra_snapshot_probe:cache_'+i),raw=world.getDynamicProperty('senra_snapshot_probe:raw_'+i);
       assert(getItemProperty(item,SECRET_COOKED_INGREDIENTS_KEY)===cache,'cache persists exactly');
       assert(getItemProperty(item,SKEWER_INGREDIENTS_KEY)===raw,'raw persists exactly');
       assert(getItemProperty(item,SECRET_COOKED_KEY)!==true,'stored item stays unfinished');
       assert(api.readEffectiveSkewerRows(item,true)[0].id==='minecraft:cooked_beef','display uses saved cooked cache');
       assert(api.readEffectiveSkewerRows(item,false)[0].id==='minecraft:beef','raw display context retained');
       const output=api.cookedStack(item,state);
       assert(getItemProperty(output,SECRET_COOKED_KEY)===true,'output becomes Cooked');
       assert(getItemProperty(output,SECRET_COOKED_INGREDIENTS_KEY)===cache,'output never recomputes registry');
       assert(output.nameTag===item.nameTag&&getItemProperty(output,'probe:creator')==='native test','output metadata retained');
      }
      world.setDynamicProperty(PHASE,2);
      console.log('NATIVE_SNAPSHOT_RESTART_PASS '+JSON.stringify({nativeContainer:true,slots:3,normalStopRestart:true,exactSnapshotPersistence:true,registryChangeIgnoredAfterSnapshot:true,nativeOutputPreparation:true,playerExtraction:false,client:false,productionWorldMigration:false}));
     }else throw Error('Probe already completed; use a new world');
    }catch(error){console.error('NATIVE_SNAPSHOT_FAIL '+error+' '+error.stack);}
   },60);
  }catch(error){console.error('NATIVE_SNAPSHOT_FAIL '+error+' '+error.stack);}
 },100);
}
