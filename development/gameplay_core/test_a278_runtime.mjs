import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const listeners=[],sent=[];
const system={
 afterEvents:{scriptEventReceive:{subscribe(fn){listeners.push(fn)}}},
 sendScriptEvent(id,message){sent.push({id,message})},
 run(fn){fn()}
};
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Error});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a278_basic_chopping_core.js',root),'utf8'),{context,identifier:'core'});
const rt=new vm.SourceTextModule(fs.readFileSync(new URL('a278_basic_chopping_runtime.js',root),'utf8'),{context,identifier:'runtime'});
const server=new vm.SyntheticModule(['system'],function(){this.setExport('system',system)},{context,identifier:'server'});
await rt.link(async spec=>spec==='@minecraft/server'?server:core);
await rt.evaluate();
assert.equal(listeners.length,1);
assert.deepEqual(sent,[{id:'kaleidoscope_cookery:api_ping',message:'kaleidoscope_grilling'}]);
listeners[0]({id:'kaleidoscope_cookery:api_ready',message:JSON.stringify({api:1,capabilities:['chopping_board']})});
const regs=sent.slice(1).map(x=>({id:x.id,payload:JSON.parse(x.message)}));
assert.equal(regs.length,2);
assert.ok(regs.every(x=>x.id==='kaleidoscope_cookery:register_recipe'));
assert.deepEqual(regs.map(x=>x.payload.recipe.input).sort(),['minecraft:carrot','minecraft:potato']);
const before=sent.length;
listeners[0]({id:'kaleidoscope_cookery:api_ready',message:JSON.stringify({api:1,capabilities:['millstone']})});
assert.equal(sent.length,before);
console.log(JSON.stringify({passed:7,failed:0,scope:'A2.7.8 public Cookery chopping-board registration'}));
