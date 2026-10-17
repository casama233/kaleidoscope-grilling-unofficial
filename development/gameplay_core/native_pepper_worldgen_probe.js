/** Independent new world generation and persistence probe; never a player simulator. */
import {world,system,BlockVolume} from '@minecraft/server';
const LOG='kaleidoscope_grilling:pepper_log',LEAVES='kaleidoscope_grilling:pepper_leaves';
const KEY='senluo:pepper_native_probe';
const pause=ticks=>new Promise(resolve=>system.runTimeout(resolve,ticks));
function snapshot(d,base){
 const logs=[],leaves=[];
 for(let y=0;y<=6;y++)for(let x=-1;x<=1;x++)for(let z=-1;z<=1;z++){
  const p={x:base.x+x,y:base.y+y,z:base.z+z},b=d.getBlock(p);
  if(b.typeId===LOG)logs.push(p);
  if(b.typeId===LEAVES)leaves.push({...p,fruit:b.permutation.getState('kaleidoscope_grilling:has_pepper'),persistent:b.permutation.getState('kaleidoscope_grilling:persistent')});
 }
 return {base,logs,leaves};
}
export function runPepperNativeProbe(){system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld'),saved=world.getDynamicProperty(KEY);
 if(saved){
  const old=JSON.parse(saved);await world.tickingAreaManager.createTickingArea('pepper-restart',{dimension:d,from:old.from,to:old.to});await pause(40);
  const next=snapshot(d,old.tree.base);
  if(JSON.stringify(next.logs)!==JSON.stringify(old.tree.logs)||JSON.stringify(next.leaves.map(({fruit,...rest})=>rest))!==JSON.stringify(old.tree.leaves.map(({fruit,...rest})=>rest)))throw Error('natural tree geometry changed across stop/restart');
  for(const leaf of old.tree.leaves.filter(l=>l.fruit))if(!d.getBlock(leaf).permutation.getState('kaleidoscope_grilling:has_pepper'))throw Error('natural fruit state lost');
  console.log('NATIVE_PEPPER_RESTART_PASS '+JSON.stringify({tree:next,players:world.getAllPlayers().length,client:false}));return;
 }
 console.log('NATIVE_PEPPER_CAPABILITIES '+JSON.stringify({calculateClosestBiomeFromSeed:typeof d.calculateClosestBiomeFromSeed,getGeneratedStructures:typeof d.getGeneratedStructures}));
 for(let attempt=0;attempt<4;attempt++){
  const center=d.calculateClosestBiomeFromSeed({x:8192+attempt*2048,y:80,z:8192},'minecraft:forest');if(!center)continue;
  const x=Math.floor(center.x/16)*16-64,z=Math.floor(center.z/16)*16-64;
  const from={x,y:-64,z},to={x:x+127,y:319,z:z+127},area='pepper-natural-'+attempt;
  await world.tickingAreaManager.createTickingArea(area,{dimension:d,from,to});await pause(100);
  const bases=[];
  for(let cx=x;cx<x+128;cx+=16)for(let cz=z;cz<z+128;cz+=16){
   for(let y=48;y<192;y+=16){
    const volume=d.getBlocks(new BlockVolume({x:cx,y,z:cz},{x:cx+15,y:y+15,z:cz+15}),{includeTypes:[LOG]});
    for(const pos of volume.getBlockLocationIterator())if(d.getBlock({...pos,y:pos.y-1}).typeId!==LOG)bases.push(pos);
   }
   await pause(1);
  }
  console.log('NATIVE_PEPPER_REGION '+JSON.stringify({attempt,center,from,to,naturalBases:bases.length}));
  for(const base of bases){
   const tree=snapshot(d,base);
   if(tree.logs.length<3||tree.leaves.length<13)continue;
   if(!tree.leaves.some(l=>l.fruit))continue;
   world.setDynamicProperty(KEY,JSON.stringify({from,to,tree}));
   console.log('NATIVE_PEPPER_PREPARED '+JSON.stringify({tree,attempt,naturalBases:bases.length,scriptPlacedTrees:0,players:world.getAllPlayers().length,client:false}));return;
  }
  await world.tickingAreaManager.removeTickingArea(area);
 }
 throw Error('no complete naturally generated fruiting pepper tree found in four forest regions');
}catch(error){console.error('NATIVE_PEPPER_FAIL '+error+' '+error.stack)}},100);}
