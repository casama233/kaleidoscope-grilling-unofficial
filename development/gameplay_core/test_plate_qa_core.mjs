import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createPlateQaLogger} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/plate_qa_core.js';
let cases=0;
function fixture(options={}){
 let time=0,reads=0,on=false;const lines=[];
 const trace=createPlateQaLogger({enabled:()=>on,key:p=>p.id,tick:()=>time,snapshot(){reads++;return {eventType:'kaleidoscope_grilling:skewer_plate',mainType:'kaleidoscope_grilling:skewer_plate',offType:undefined,eventRows:1,mainRows:1,offRows:'not_plate',rawPayload:'private ingredient lore',playerId:'private identity',coords:[1,2,3]};},write:line=>lines.push(line),...options});
 return {trace,lines,get reads(){return reads;},enable(){on=true;},time(v){time=v;}};
}
const f=fixture(),p={id:'never-output-this-id'};
assert.equal(f.trace(p,'start_received',undefined),false);assert.equal(f.reads,0);assert.equal(f.lines.length,0);cases++;
f.enable();assert.equal(f.trace(p,'start_registered',undefined,{session:true,identityMatch:true,stage:'registered',error:'private error',rawPayload:'private payload'}),true);
const out=JSON.parse(f.lines[0].slice('[Grilling plate QA] '.length));assert.equal(out.eventRows,1);assert.equal(out.session,true);assert.equal(out.identityMatch,true);assert.equal(out.stage,'registered');assert.equal(out.offType,'none');
for(const secret of ['never-output','private','coords','rawPayload','playerId','error'])assert(!f.lines[0].includes(secret));cases++;
assert.equal(f.trace(p,'private phase'),false);assert.equal(f.lines.length,1);cases++;
const limited=fixture({perPlayerLimit:2,globalLimit:3,maxPlayers:2});limited.enable();
assert(limited.trace(p,'start_received'));assert(limited.trace(p,'start_received'));assert(!limited.trace(p,'start_received'));
assert(limited.trace({id:'q'},'start_received'));assert(!limited.trace({id:'q'},'start_received'));assert.equal(limited.lines.length,3);cases++;
limited.time(1200);assert(limited.trace(p,'start_received'));assert.equal(limited.lines.length,4);cases++;
const bounded=fixture({maxPlayers:1});bounded.enable();assert(bounded.trace(p,'start_received'));assert(!bounded.trace({id:'q'},'start_received'));cases++;
for(const callback of ['enabled','key','tick','snapshot','write']){
 const broken=fixture({[callback](){throw Error('must not escape');}});broken.enable();assert.doesNotThrow(()=>broken.trace(p,'start_received'));cases++;
}
const invalid=fixture({snapshot:()=>({eventType:'private text and coordinates',mainType:'minecraft:carrot',offType:'minecraft:stone',eventRows:-1,mainRows:100,offRows:'unreadable'})});invalid.enable();invalid.trace(p,'settlement',undefined,{stage:'private error'});
const clean=JSON.parse(invalid.lines[0].slice('[Grilling plate QA] '.length));assert.equal(clean.eventType,'none');assert.equal(clean.eventRows,'not_plate');assert.equal(clean.mainRows,'not_plate');assert.equal(clean.offRows,'unreadable');assert(!('stage' in clean));cases++;
const source=fs.readFileSync('projects/grilling/gameplay_core/behavior_pack/scripts/plate_qa_runtime.js','utf8');
assert(source.includes("player?.hasTag?.('kg_plate_qa')===true"));assert(!/spawn|setDynamicProperty|setEquipment|setCurrentValue|runCommand|sendMessage|setItem\(/.test(source));cases++;
console.log(`Plate QA: ${cases} opt-in, sanitization, bounded logging and failure-isolation scenarios PASS`);
