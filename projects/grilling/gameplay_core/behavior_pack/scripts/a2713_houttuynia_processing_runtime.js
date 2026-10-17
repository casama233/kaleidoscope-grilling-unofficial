import {system} from '@minecraft/server';
import {KC_READY_EVENT,KC_REGISTER_EVENT,registrationsForReady} from './a2713_houttuynia_processing_core.js';

function registerReady(info){
 for(const payload of registrationsForReady(info)){
  system.sendScriptEvent(KC_REGISTER_EVENT,JSON.stringify(payload));
 }
}

// A2.7.8 owns the single startup api_ping. This listener is loaded before
// that deferred ping runs, so no duplicate ping is needed here.
system.afterEvents.scriptEventReceive.subscribe(ev=>{
 if(ev.id!==KC_READY_EVENT)return;
 try{registerReady(JSON.parse(String(ev.message??'')))}catch{}
});
