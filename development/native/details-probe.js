import {world,system} from '@minecraft/server';
import {nativeDragonHealth} from './dragon_native_health.js';
import {finishedFoodMeta} from './food_finish_core.js';
const need=(v,message)=>{if(!v)throw Error(message)};
const wait=ticks=>new Promise(resolve=>system.runTimeout(resolve,ticks));
async function run(){
 let e;
 try{
  need(world.getAllPlayers().length===0,'unexpected player');
  const d=world.getDimension('overworld');e=d.spawnEntity('kaleidoscope_grilling:native_health_probe',{x:0,y:81,z:64});
  e.setProperty('kaleidoscope_grilling:eat_profile',4);e.setProperty('kaleidoscope_grilling:eat_hand',2);e.setProperty('kaleidoscope_grilling:secret_off_2',213);await wait(2);need(e.getProperty('kaleidoscope_grilling:eat_profile')===4,'shared profile property');
  need(e.getProperty('kaleidoscope_grilling:eat_hand')===2&&e.getProperty('kaleidoscope_grilling:secret_off_2')===213,'hand and ingredient properties');
  let hp=e.getComponent('minecraft:health');hp.setCurrentValue(10);
  nativeDragonHealth(e,0,{heal:true});await wait(4);hp=e.getComponent('minecraft:health');
  need(hp.effectiveMax===26&&hp.currentValue===16,'first native maximum/heal '+hp.effectiveMax+'/'+hp.currentValue);
  hp.resetToMaxValue();e.applyDamage(8);await wait(2);need(hp.currentValue===18,'native injury');
  hp.resetToMaxValue();need(hp.currentValue===26,'repeat healing max26');await wait(12);
  e.applyDamage(8);await wait(2);need(hp.currentValue===18,'second native injury');
  nativeDragonHealth(e,1,{heal:true});await wait(4);hp=e.getComponent('minecraft:health');
  need(hp.effectiveMax===30&&hp.currentValue===22,'upgrade native delta '+hp.effectiveMax+'/'+hp.currentValue);
  nativeDragonHealth(e,1,{heal:true});await wait(2);need(hp.currentValue===22,'refresh healed again');
  nativeDragonHealth(e,undefined);await wait(4);hp=e.getComponent('minecraft:health');
  need(hp.effectiveMax===20&&hp.currentValue===20,'expire native restore '+hp.effectiveMax+'/'+hp.currentValue);
  hp.setCurrentValue(10);nativeDragonHealth(e,0,{heal:true});nativeDragonHealth(e,1,{heal:true});await wait(4);hp=e.getComponent('minecraft:health');
  need(hp.effectiveMax===30&&hp.currentValue===20,'same tick upgrade loses initial heal '+hp.effectiveMax+'/'+hp.currentValue);
  nativeDragonHealth(e,undefined);await wait(4);
  const meta={hot:true,hotUntil:world.getAbsoluteTime()+1,seasonings:['salt']};
  await wait(2);need(finishedFoodMeta(meta,world.getAbsoluteTime()).hot===false,'finish stale hot');
  e.remove();e=undefined;
  console.warn('DETAILS_NATIVE_PASS '+JSON.stringify({players:0,simulated_players:false,client:false,native_component_groups:true,native_max_health:[20,26,30],repeat_damage_and_heal:true,upgrade_heals_difference:true,same_tick_upgrade_preserves_initial_heal:true,refresh_does_not_heal:true,expiry_restores_base:true,eating_property:4,eat_hand_property:2,secret_visual_property:213,finish_expiry:true,player_events:false,rendered_motion:false}));
 }catch(error){try{e?.remove()}catch{};console.warn('DETAILS_NATIVE_FAIL '+error)}
}
system.runTimeout(run,100);
