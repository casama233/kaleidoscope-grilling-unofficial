import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const listeners=[];let tick=1000;
const world={
 getAbsoluteTime(){return tick},
 afterEvents:{itemCompleteUse:{subscribe(fn){listeners.push(fn)}}}
};
const system={get currentTick(){return tick}};
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Error,Math});
const root=new URL('./',import.meta.url);

const sources={
 roasted:new URL('a2720_roasted_sweet_potato_core.js',root),
 cold:new URL('a2722_cold_houttuynia_core.js',root),
 core:new URL('a2732_standalone_food_effect_core.js',root),
 runtime:new URL('a2732_standalone_food_effect_runtime.js',root)
};
const modules={};
for(const [key,url] of Object.entries(sources)){
 modules[key]=new vm.SourceTextModule(fs.readFileSync(url,'utf8'),{context,identifier:key});
}
const server=new vm.SyntheticModule(['world','system'],function(){
 this.setExport('world',world);this.setExport('system',system);
},{context,identifier:'server'});

await modules.roasted.link(()=>{throw new Error('unexpected import')});
await modules.cold.link(()=>{throw new Error('unexpected import')});
await modules.core.link(async spec=>{
 if(spec==='./a2720_roasted_sweet_potato_core.js')return modules.roasted;
 if(spec==='./a2722_cold_houttuynia_core.js')return modules.cold;
 throw new Error('unexpected core import '+spec);
});
await modules.runtime.link(async spec=>{
 if(spec==='@minecraft/server')return server;
 if(spec==='./a2732_standalone_food_effect_core.js')return modules.core;
 throw new Error('unexpected runtime import '+spec);
});
await modules.runtime.evaluate();

assert.equal(listeners.length,1);

function entity(initial){
 let raw=initial;const native=[];
 return {
  getDynamicProperty(k){assert.equal(k,'kaleidoscope_grilling:a21_fx');return raw},
  setDynamicProperty(k,v){assert.equal(k,'kaleidoscope_grilling:a21_fx');raw=v},
  addEffect(id,duration,options){native.push({id,duration,options})},
  raw(){return raw},
  native(){return native}
 };
}

const p=entity(undefined);
listeners[0]({itemStack:{typeId:'minecraft:apple'},source:p});
assert.equal(p.raw(),undefined);assert.deepEqual(p.native(),[]);

listeners[0]({itemStack:{typeId:'kaleidoscope_grilling:roasted_sweet_potato'},source:p});
let fx=JSON.parse(p.raw());
assert.equal(fx.warmth.until,1600);assert.equal(fx.warmth.amp,0);

tick=1100;
listeners[0]({itemStack:{typeId:'kaleidoscope_grilling:roasted_sweet_potato'},source:p});
fx=JSON.parse(p.raw());assert.equal(fx.warmth.until,1700);

const q=entity(JSON.stringify({warmth:{until:5000,amp:0},numb:{until:3000,amp:0}}));
listeners[0]({itemStack:{typeId:'kaleidoscope_grilling:roasted_sweet_potato'},source:q});
fx=JSON.parse(q.raw());
assert.equal(fx.warmth.until,5000);assert.equal(fx.numb.until,3000);

const c=entity(undefined);
listeners[0]({itemStack:{typeId:'kaleidoscope_grilling:cold_houttuynia'},source:c});
assert.equal(c.native().length,1);
assert.equal(c.native()[0].id,'fire_resistance');
assert.equal(c.native()[0].duration,1200);
assert.equal(c.native()[0].options.showParticles,true);

console.log(JSON.stringify({passed:6,failed:0,scope:'A2.7.32 unified standalone food effect runtime'}));
