/** Isolated overlay: native audio API and RawMessage persistence, zero players. */
import {world,system,ItemStack} from '@minecraft/server';
import {createGrillAudioController} from './immersion_audio_core.js';
import {blockSound} from './immersion_audio_runtime.js';
import {setHotFood,refreshHotLore} from './a2750_food_state_adapter.js';
import {HEAT_NAME_KEY} from './localized_lore_core.js';
const check=(ok,label)=>{if(!ok)throw Error(label)},wait=t=>new Promise(r=>system.runTimeout(r,t));
const key='kaleidoscope_grilling:qa_audio28';
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');d.runCommand('tickingarea add circle 0 80 64 2 audio_qa true');
 let block;for(let n=0;n<60;n++){await wait(10);try{block=d.getBlock({x:6,y:80,z:64})}catch{}if(block)break}check(block,'chunk unavailable');
 const events=['grill_loop','grill_flip','season','action_success','pickup_item','skewer_disassemble','seasoning_bottle_place','seasoning_bottle_stack','shake_seasoning','one_skewer_eat','two_skewer_eat','three_skewer_eat','four_skewer_eat'];
 for(const event of events){const handle=blockSound(block,event);check(handle&&typeof handle.stop==='function','native sound handle '+event);handle.stop()}
 let started=0,stopped=0;const audio=createGrillAudioController({play:()=>{const handle=d.playSound('kg_imm.grill_loop',{x:6,y:80,z:64});started++;return {stop(){handle.stop();stopped++}}}});
 audio.update('a',{},true,0);audio.update('b',{},true,0);audio.update('a',{},false,1);check(started===2&&stopped===1&&audio.size===1,'individual stop');
 audio.update('b',{},true,569);check(started===3&&stopped===2,'native renewal');audio.sweep(578);check(audio.size===0&&stopped===3,'native unload cleanup');
 d.spawnParticle('minecraft:villager_happy',{x:6,y:81,z:64});
 const previous=world.getDynamicProperty(key),foreign={rawtext:[{text:'§c🔥 '},{translate:'item.apple.name'}]};
 if(previous===undefined){
  block.setType('minecraft:chest');const stack=new ItemStack('kaleidoscope_grilling:grilled_fish_skewer');stack.setLore([foreign]);setHotFood(stack,6000);refreshHotLore(stack);
  const lore=stack.getRawLore();check(JSON.stringify(lore[0])===JSON.stringify(foreign),'foreign raw lore');check(lore.some(l=>l.rawtext?.some(r=>r.translate===HEAT_NAME_KEY)),'translated heat lore');
  block.getComponent('minecraft:inventory').container.setItem(0,stack);world.setDynamicProperty(key,JSON.stringify(lore));
 }else{
  const stack=block.getComponent('minecraft:inventory').container.getItem(0);check(stack,'saved heat item');refreshHotLore(stack);const lore=stack.getRawLore();
  check(JSON.stringify(lore[0])===JSON.stringify(foreign),'foreign raw lore after restart');check(lore.some(l=>l.rawtext?.some(r=>r.translate===HEAT_NAME_KEY)),'translated heat after restart');
 }
 console.log('IMMERSION_NATIVE_PASS '+JSON.stringify({stage:previous===undefined?'saved':'restored',originalEvents:13,nativeSoundHandles:true,individualStop:true,renewal:true,unloadCleanup:true,completionParticleApi:true,rawTranslatedHeatLore:true,restartPreserved:previous!==undefined,simulatedPlayers:false,client:false}));
}catch(e){console.error('IMMERSION_NATIVE_FAIL '+e+' '+e.stack)}},140);
