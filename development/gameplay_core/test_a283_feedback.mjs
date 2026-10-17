// API adapter test only: does not claim Minecraft UI acceptance.
import assert from 'node:assert/strict';
import fs from 'node:fs';
const path=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const calls=[],warnings=[];let leave;
globalThis.__kgFeedbackMock={world:{afterEvents:{playerLeave:{subscribe(fn){leave=fn}}}},system:{currentTick:0}};
let source=fs.readFileSync(new URL('a283_interaction_feedback.js',path),'utf8');
source=source.replace("import {world,system} from '@minecraft/server';",'const {world,system}=globalThis.__kgFeedbackMock;');
source=source.replace("'./interaction_feedback_core.js'",JSON.stringify(new URL('interaction_feedback_core.js',path).href));
globalThis.__kgFeedbackMock.console={warn:text=>warnings.push(text)};
source=source.replace('console.warn','globalThis.__kgFeedbackMock.console.warn');
const {interactionFeedback,interactionFailure,eatingProgress}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const player={id:'one',onScreenDisplay:{setActionBar(text){calls.push(text)}}};
assert.equal(calls.length,0);
for(let tick=0;tick<1200;tick++){
 globalThis.__kgFeedbackMock.system.currentTick=tick;
 for(const hint of ['missing oil','waiting seasoning','flip cooldown','press 1/4','recipe hint'])interactionFeedback(player,hint);
 eatingProgress(player,'■■■□□');eatingProgress(player,'');
}
assert.deepEqual(calls,[],'ordinary play, eating and completion never write or clear the shared actionbar');
interactionFailure(player,'storage unavailable');
for(let tick=1200;tick<2400;tick++){
 globalThis.__kgFeedbackMock.system.currentTick=tick;
 interactionFailure(player,tick%2?'rollback failed':'storage unavailable');
}
assert.equal(calls.length,0,'unexpected storage faults do not invent Java actionbar messages');
assert.equal(warnings.length,1,'held/repeated failures do not flood operator diagnostics');
globalThis.__kgFeedbackMock.system.currentTick=2498;interactionFailure(player,'storage unavailable');
assert.equal(warnings.length,1,'99 ticks without attempts is still quiet');
globalThis.__kgFeedbackMock.system.currentTick=2598;interactionFailure(player,'storage unavailable');
assert.equal(warnings.length,2,'a new attempt after five quiet seconds can log a failure');
leave({playerId:'one'});interactionFailure(player,'storage unavailable');assert.equal(warnings.length,3);
const {registerCrosshairHudProvider}=await import(new URL('a2739_crosshair_hud_runtime.js',path));
let probes=0;assert.equal(registerCrosshairHudProvider({id:'test',probe(){probes++}}),true);assert.equal(probes,0);
delete globalThis.__kgFeedbackMock;
console.log('PASS: normal interactions and eating are silent; failures require quiet gestures; leave cleanup');
