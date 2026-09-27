// API adapter test only: does not claim Minecraft UI acceptance.
import assert from 'node:assert/strict';
import fs from 'node:fs';
const path=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const calls=[];let leave;
globalThis.__kgFeedbackMock={world:{afterEvents:{playerLeave:{subscribe(fn){leave=fn}}}},system:{currentTick:0}};
let source=fs.readFileSync(new URL('a283_interaction_feedback.js',path),'utf8');
source=source.replace("import {world,system} from '@minecraft/server';",'const {world,system}=globalThis.__kgFeedbackMock;');
const {interactionFeedback}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const player={id:'one',onScreenDisplay:{setActionBar(text){calls.push(text)}}};
assert.equal(calls.length,0);
interactionFeedback(player,'missing oil');
for(let tick=1;tick<60;tick++){globalThis.__kgFeedbackMock.system.currentTick=tick;interactionFeedback(player,'missing oil')}
assert.deepEqual(calls,['missing oil']);
globalThis.__kgFeedbackMock.system.currentTick=60;interactionFeedback(player,'inventory full');
assert.equal(calls.length,2);leave({playerId:'one'});interactionFeedback(player,'missing oil');assert.equal(calls.length,3);
const {registerCrosshairHudProvider}=await import(new URL('a2739_crosshair_hud_runtime.js',path));
let probes=0;assert.equal(registerCrosshairHudProvider({id:'test',probe(){probes++}}),true);assert.equal(probes,0);
delete globalThis.__kgFeedbackMock;
console.log('PASS: no passive HUD, failure throttling, leave cleanup');
