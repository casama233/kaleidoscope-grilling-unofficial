import {system} from '@minecraft/server';
import {KC_READY_EVENT,KC_REGISTER_EVENT,registrationsForReady} from './a2718_onion_processing_core.js';

function registerReady(info){
 for(const payload of registrationsForReady(info)){
  system.sendScriptEvent(KC_REGISTER_EVENT,JSON.stringify(payload));
 }
}

// Earlier gameplay slices already own startup API discovery.
// This module only consumes api_ready and never emits another ping.
system.afterEvents.scriptEventReceive.subscribe(ev=>{
 if(ev.id!==KC_READY_EVENT)return;
 try{registerReady(JSON.parse(String(ev.message??'')))}catch{}
});
