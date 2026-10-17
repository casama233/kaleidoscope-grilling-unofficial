import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const listeners=[];const sent=[];const queued=[];
const system={
 afterEvents:{scriptEventReceive:{subscribe(fn){listeners.push(fn)}}},
 sendScriptEvent(id,message){sent.push({id,message})},
 run(fn){queued.push(fn);fn()}
};
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Error});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a272_cookery_processing_core.js',root),'utf8'),{context,identifier:'core'});
const rt=new vm.SourceTextModule(fs.readFileSync(new URL('a272_cookery_processing_runtime.js',root),'utf8'),{context,identifier:'runtime'});
const server=new vm.SyntheticModule(['system'],function(){this.setExport('system',system)},{context,identifier:'server'});
await rt.link(async spec=>spec==='@minecraft/server'?server:core);
await rt.evaluate();

assert.equal(listeners.length,1);
assert.deepEqual(sent.map(x=>[x.id,x.message]),[['kaleidoscope_cookery:api_ping','kaleidoscope_grilling']]);

function ready(payload){listeners[0]({id:'kaleidoscope_cookery:api_ready',message:JSON.stringify(payload)})}
ready({api:1,capabilities:['chopping_board','millstone']});
let regs=sent.filter(x=>x.id==='kaleidoscope_cookery:register_recipe').map(x=>JSON.parse(x.message));
assert.equal(regs.length,2);
assert.deepEqual(regs.map(x=>x.kind).sort(),['chopping_board','millstone']);
assert.equal(regs.find(x=>x.kind==='chopping_board').recipe.cuts,4);
assert.deepEqual(regs.find(x=>x.kind==='millstone').recipe.outputs,[{id:'kaleidoscope_grilling:sweet_potato_powder',count:1,chance:1}]);

const before=sent.length;
ready({api:1,capabilities:['chopping_board']});
const one=sent.slice(before).filter(x=>x.id==='kaleidoscope_cookery:register_recipe').map(x=>JSON.parse(x.message));
assert.equal(one.length,1);assert.equal(one[0].kind,'chopping_board');

const beforeMissing=sent.length;
ready({api:1});
assert.equal(sent.length,beforeMissing);
ready({api:99,capabilities:['chopping_board','millstone']});
assert.equal(sent.length,beforeMissing);
listeners[0]({id:'other:ready',message:'{}'});
assert.equal(sent.length,beforeMissing);

console.log(JSON.stringify({passed:10,failed:0,scope:'A2.7.2 Cookery public Script Event handshake and capability-gated recipe registration; no Minecraft/BDS engine acceptance'}));
