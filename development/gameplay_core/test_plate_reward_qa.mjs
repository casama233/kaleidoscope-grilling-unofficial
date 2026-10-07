import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
import {createPlateQaLogger} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/plate_qa_core.js';
const source=fs.readFileSync('projects/grilling/gameplay_core/behavior_pack/scripts/main.js','utf8');
function body(name){const start=source.indexOf('function '+name+'(');let end=source.indexOf('{',start)+1,depth=1;while(depth){const c=source[end++];if(c==='{')depth++;if(c==='}')depth--;}return source.slice(start,end);}
function fixture(fault='',enabled=true){
 const logs=[],writes=[],error=Object.assign(new Error('must never be logged'),{name:'ArgumentOutOfBoundsError'});
 const h={currentValue:10,effectiveMax:20,setCurrentValue(value){writes.push(['hunger',value]);if(fault==='hunger_write')throw error;this.currentValue=Math.fround(value);return true;}};
 const sat={currentValue:0,effectiveMax:20,setCurrentValue(value){writes.push(['saturation',value]);if(fault==='saturation_write')throw error;this.currentValue=Math.fround(value);return true;}};
 const trace=createPlateQaLogger({enabled:()=>enabled,key:()=> 'private',tick:()=>100,snapshot:()=>({}),write:line=>logs.push(JSON.parse(line.slice('[Grilling plate QA] '.length)))});
 const ctx=vm.createContext({plateQaTrace:trace,dynamicFood(){if(fault==='facts')throw error;return {nutrition:3,saturation:.3923076923076923};},grillingConfig:()=>({saturationMultiplier:1.25})});
 vm.runInContext(body('addSecretNutrition')+'\n'+body('addNestedNutrition'),ctx);
 const player={getComponent(id){if(fault==='components')throw error;return id.endsWith('hunger')?h:sat;}};
 return {logs,writes,error,h,sat,run:()=>ctx.addNestedNutrition(player,{},{}),direct:()=>ctx.addSecretNutrition(player,{},{}),ctx};
}
let cases=0;
for(const enabled of [false,true]){const f=fixture('',enabled);f.run();assert.equal(f.h.currentValue,13);assert.equal(f.sat.currentValue,Math.fround(2.3538461538461535));assert.deepEqual(f.writes,[['hunger',13],['saturation',3*.3923076923076923*2]]);assert.equal(f.logs.length,enabled?7:0);cases++;}
for(const fault of ['facts','components','hunger_write','saturation_write']){const f=fixture(fault);assert.throws(f.run,e=>e===f.error);const last=f.logs.at(-1);assert.equal(last.stage,'reward_failed');assert.equal(last.operation,fault);assert.equal(last.errorName,'ArgumentOutOfBoundsError');assert.equal(last.errorCategory,'native_bounds');assert(!JSON.stringify(f.logs).includes('must never'));cases++;}
const direct=fixture();direct.direct();assert.equal(direct.logs.length,0);assert.equal(direct.h.currentValue,13);cases++;
let called=false;const disabled=createPlateQaLogger({enabled:()=>false,key(){assert.fail()},tick(){assert.fail()},snapshot(){assert.fail()},write(){assert.fail()}});assert.equal(disabled({},'reward_detail',{},()=>{called=true;throw Error('no read') }),false);assert.equal(called,false);cases++;
const privacy=[];const trace=createPlateQaLogger({enabled:()=>true,key:()=> 'private key',tick:()=>0,snapshot:()=>({}),write:l=>privacy.push(l)});trace({},'reward_detail',{},()=>({stage:'reward_failed',operation:'saturation_write',errorName:'private.namespace.TypeError',errorMessage:'private payload',hungerTarget:NaN,saturationTarget:Infinity,nutrition:3}));const safe=JSON.parse(privacy[0].slice('[Grilling plate QA] '.length));assert.equal(safe.errorName,'TypeError');assert.equal(safe.hungerTarget,'non_finite_or_out_of_bounds');assert.equal(safe.saturationTarget,'non_finite_or_out_of_bounds');assert(!privacy[0].includes('private'));cases++;
console.log(`Plate reward QA: ${cases} numeric trace, lazy gating, identical error rethrow and unchanged write scenarios PASS`);
