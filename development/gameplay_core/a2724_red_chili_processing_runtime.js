import {system} from '@minecraft/server';
import {KC_READY_EVENT,KC_REGISTER_EVENT,registrationsForReady} from './a2724_red_chili_processing_core.js';

function registerReady(info){
 for(const payload of registrationsForReady(info)){
  system.sendScriptEvent(KC_REGISTER_EVENT,JSON.stringify(payload));
 }
}

// Startup discovery is owned by the original Cookery bridge.
// This slice only consumes api_ready, avoiding duplicate API pings.
system.afterEvents.scriptEventReceive.subscribe(ev=>{
 if(ev.id!==KC_READY_EVENT)return;
 try{registerReady(JSON.parse(String(ev.message??'')))}catch{}
});
