import {system} from '@minecraft/server';
import {KC_READY_EVENT,KC_REGISTER_EVENT,registrationsForReady} from './a2711_mantou_chopping_core.js';

function registerReady(info){
 for(const payload of registrationsForReady(info)){
  system.sendScriptEvent(KC_REGISTER_EVENT,JSON.stringify(payload));
 }
}

// A2.7.8 owns the initial API ping. This listener is loaded before that
// system.run callback fires, so adding A2.7.11 does not create duplicate pings.
system.afterEvents.scriptEventReceive.subscribe(ev=>{
 if(ev.id!==KC_READY_EVENT)return;
 try{registerReady(JSON.parse(String(ev.message??'')))}catch{}
});
