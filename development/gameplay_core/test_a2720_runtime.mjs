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
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a2720_roasted_sweet_potato_core.js',root),'utf8'),{context,identifier:'core'});
const rt=new vm.SourceTextModule(fs.readFileSync(new URL('a2720_roasted_sweet_potato_runtime.js',root),'utf8'),{context,identifier:'runtime'});
const server=new vm.SyntheticModule(['world','system'],function(){this.setExport('world',world);this.setExport('system',system)},{context,identifier:'server'});
await rt.link(async spec=>spec==='@minecraft/server'?server:core);
await rt.evaluate();
assert.equal(listeners.length,1);

function entity(initial){
 let raw=initial;
 return {
  getDynamicProperty(k){assert.equal(k,'kaleidoscope_grilling:a21_fx');return raw},
  setDynamicProperty(k,v){assert.equal(k,'kaleidoscope_grilling:a21_fx');raw=v},
  raw(){return raw}
 };
}
const p=entity(undefined);
listeners[0]({itemStack:{typeId:'minecraft:apple'},source:p});assert.equal(p.raw(),undefined);
listeners[0]({itemStack:{typeId:'kaleidoscope_grilling:roasted_sweet_potato'},source:p});
let fx=JSON.parse(p.raw());assert.equal(fx.warmth.until,1600);assert.equal(fx.warmth.amp,0);

tick=1100;listeners[0]({itemStack:{typeId:'kaleidoscope_grilling:roasted_sweet_potato'},source:p});
fx=JSON.parse(p.raw());assert.equal(fx.warmth.until,1700);

const q=entity(JSON.stringify({warmth:{until:5000,amp:0},numb:{until:3000,amp:0}}));
listeners[0]({itemStack:{typeId:'kaleidoscope_grilling:roasted_sweet_potato'},source:q});
fx=JSON.parse(q.raw());assert.equal(fx.warmth.until,5000);assert.equal(fx.numb.until,3000);
console.log(JSON.stringify({passed:5,failed:0,scope:'A2.7.20 roasted sweet potato warmth runtime'}));
