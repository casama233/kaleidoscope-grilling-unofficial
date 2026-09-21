import {system} from '@minecraft/server';
import {KC_READY_EVENT,KC_REGISTER_EVENT,registrationsForReady} from './a2716_canola_processing_core.js';

function registerReady(info){
 for(const payload of registrationsForReady(info)){
  system.sendScriptEvent(KC_REGISTER_EVENT,JSON.stringify(payload));
 }
}

// Startup API discovery is already owned by earlier gameplay slices.
// This module only consumes api_ready and never emits an additional ping.
system.afterEvents.scriptEventReceive.subscribe(ev=>{
 if(ev.id!==KC_READY_EVENT)return;
 try{registerReady(JSON.parse(String(ev.message??'')))}catch{}
});
