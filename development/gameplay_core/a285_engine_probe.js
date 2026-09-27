// Test-world-only native BDS probe. Never packaged or deployed to luosen.
import {world,system,ItemStack} from '@minecraft/server';
import {initialState} from './core_logic.js';
import {grillStateKey,readGrillState} from './a2740_grill_state_adapter.js';
const KEY='kg_probe:a285_initialized';
system.runTimeout(()=>{
 const d=world.getDimension('overworld');
 try{d.runCommand('tickingarea add 0 70 0 31 90 31 kg_a285_probe true')}catch(e){console.warn('[A285 PROBE area] '+e)}
 system.runTimeout(()=>{
  try{
   const restart=!!world.getDynamicProperty(KEY);
   for(let n=0;n<300;n++){
    const b=d.getBlock({x:n%20,y:80,z:Math.floor(n/20)});
    if(!b)throw Error('probe chunk unloaded');
    if(!restart){
     b.setType('kaleidoscope_grilling:grill');
     b.getComponent('minecraft:inventory').container.setItem(0,new ItemStack('kaleidoscope_grilling:raw_beef_skewer',1));
     world.setDynamicProperty(grillStateKey(b),JSON.stringify({...initialState(),lit:true,phase:1,heatTicks:1200}));
    }
   }
   world.setDynamicProperty(KEY,true);
   const before=Array.from({length:300},(_,n)=>readGrillState(d.getBlock({x:n%20,y:80,z:Math.floor(n/20)})).phaseTicks);
   system.runTimeout(()=>{
    let advancing=0,stored=0;
    for(let n=0;n<300;n++){
     const b=d.getBlock({x:n%20,y:80,z:Math.floor(n/20)}),s=readGrillState(b);
     if(s.phaseTicks>before[n])advancing++;
     if(b.getComponent('minecraft:inventory').container.getItem(0)?.typeId==='kaleidoscope_grilling:raw_beef_skewer')stored++;
    }
    console.warn('[A285 PROBE RESULT] '+JSON.stringify({restart,total:300,advancing,stored,pass:advancing===300&&stored===300}));
    // Freeze after the check, retaining slots/state for the real process restart.
    for(let n=0;n<300;n++){
     const b=d.getBlock({x:n%20,y:80,z:Math.floor(n/20)}),s=readGrillState(b);
     world.setDynamicProperty(grillStateKey(b),JSON.stringify({...s,lit:false}));
    }
   },40);
   if(restart)for(let n=0;n<300;n++){
    const b=d.getBlock({x:n%20,y:80,z:Math.floor(n/20)}),s=readGrillState(b);
    world.setDynamicProperty(grillStateKey(b),JSON.stringify({...s,lit:true}));
   }
  }catch(e){console.warn('[A285 PROBE FAIL] '+e+' '+e.stack)}
 },80);
},20);

system.runTimeout(()=>{
 try{
  const d=world.getDimension('overworld');
  for(let x=25;x<=29;x++)for(let z=25;z<=29;z++)d.getBlock({x,y:79,z}).setType('minecraft:stone');
  const leaf=d.getBlock({x:27,y:80,z:26});leaf.setType('kaleidoscope_grilling:pepper_leaves');
  leaf.setPermutation(leaf.permutation.withState('kaleidoscope_grilling:persistent',true));
  const pig=d.spawnEntity('minecraft:pig',{x:26.85,y:80,z:26.5});
  const before=pig.getComponent('minecraft:health').currentValue;
  system.runTimeout(()=>{
   const after=pig.getComponent('minecraft:health').currentValue;
   console.warn('[A285 LEAF RESULT] '+JSON.stringify({before,after,pass:after<before}));pig.remove();
  },20);
 }catch(e){console.warn('[A285 LEAF FAIL] '+e)}
},180);
