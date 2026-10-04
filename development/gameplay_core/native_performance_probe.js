/** Test-only stationary workload. No player or simulated-player creation. */
import {world,system,ItemStack,BlockPermutation} from '@minecraft/server';
import {performanceRegisterSource} from './a23_oil_world.js';
export function runPerformanceProbe(api){
 system.afterEvents.scriptEventReceive.subscribe(event=>{
  if(event.id==='senluo:performance_sample')console.log('GRILLING_PERF_SAMPLE '+JSON.stringify({label:event.message,tick:system.currentTick,time:Date.now()}));
 });
 system.runTimeout(async()=>{try{
  const dimension=world.getDimension('overworld');
  await world.tickingAreaManager.createTickingArea('grilling-perf',{dimension,from:{x:1024,y:0,z:1024},to:{x:1151,y:100,z:1087}});
  system.runTimeout(()=>{try{
   const grills=[];
   for(let i=0;i<64;i++){
    const p={x:1026+(i%8)*3,y:81,z:1026+Math.floor(i/8)*3};
    dimension.getBlock({...p,y:80}).setType('minecraft:stone');
    const block=dimension.getBlock(p);block.setPermutation(BlockPermutation.resolve('kaleidoscope_grilling:grill'));
    const container=api.inv(block);if(!container)throw Error('native grill container missing');
    for(let slot=0;slot<3;slot++)container.setItem(slot,new ItemStack('kaleidoscope_grilling:raw_beef_skewer',1));
    api.writeState(block,{...api.initialState(),phase:1,flips:1,heatTicks:24000,lit:true});grills.push(p);
   }
   for(let i=0;i<32;i++){
    const x=1060+(i%8)*10,z=1030+Math.floor(i/8)*10,y=81;
    // Identical 7x7 contained surface: source plus 48 flowing cells.
    for(let dx=-4;dx<=4;dx++)for(let dz=-4;dz<=4;dz++){
     dimension.getBlock({x:x+dx,y:y-1,z:z+dz}).setType('minecraft:stone');
     dimension.getBlock({x:x+dx,y,z:z+dz}).setType(Math.abs(dx)===4||Math.abs(dz)===4?'minecraft:stone':'minecraft:air');
     dimension.getBlock({x:x+dx,y:y+1,z:z+dz}).setType('minecraft:air');
    }
    const p={x,y,z};dimension.getBlock(p).setPermutation(BlockPermutation.resolve('kaleidoscope_grilling:premium_chili_oil',{'kaleidoscope_grilling:level':0}));
    if(!performanceRegisterSource(dimension,p,'premium_chili'))throw Error('oil registry setup');
   }
   // Keep the same active stage through a long measurement instead of allowing
   // the workload to go idle after its normal unattended burn deadline.
   system.runInterval(()=>{for(const p of grills){const block=dimension.getBlock(p);api.writeState(block,{...api.initialState(),phase:1,flips:1,heatTicks:24000,lit:true});}},400);
   console.log('GRILLING_PERF_READY '+JSON.stringify({grills:64,grillSlots:192,oilSources:32,containedOilCellsPerSource:49,players:world.getAllPlayers().length,simulatedPlayers:false,plates:0,helperRendering:false,client:false}));
  }catch(error){console.error('GRILLING_PERF_FAIL '+error+' '+error.stack)}},60);
 }catch(error){console.error('GRILLING_PERF_FAIL '+error+' '+error.stack)}},100);
}
