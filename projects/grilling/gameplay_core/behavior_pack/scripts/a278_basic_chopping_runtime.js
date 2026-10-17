import {system} from '@minecraft/server';
import {KC_READY_EVENT,KC_PING_EVENT,KC_REGISTER_EVENT,SOURCE,registrationsForReady} from './a278_basic_chopping_core.js';

function registerReady(info){
 for(const payload of registrationsForReady(info)){
  system.sendScriptEvent(KC_REGISTER_EVENT,JSON.stringify(payload));
 }
}
system.afterEvents.scriptEventReceive.subscribe(ev=>{
 if(ev.id!==KC_READY_EVENT)return;
 try{registerReady(JSON.parse(String(ev.message??'')))}catch{}
});
system.run(()=>{try{system.sendScriptEvent(KC_PING_EVENT,SOURCE)}catch{}});
