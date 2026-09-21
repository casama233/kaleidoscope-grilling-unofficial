import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const listeners=[],sent=[];
const system={
 afterEvents:{scriptEventReceive:{subscribe(fn){listeners.push(fn)}}},
 sendScriptEvent(id,message){sent.push({id,message})}
};
const context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Boolean,Error});
const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url);
const core=new vm.SourceTextModule(fs.readFileSync(new URL('a2710_mantou_chopping_core.js',root),'utf8'),{context,identifier:'core'});
const rt=new vm.SourceTextModule(fs.readFileSync(new URL('a2710_mantou_chopping_runtime.js',root),'utf8'),{context,identifier:'runtime'});
const server=new vm.SyntheticModule(['system'],function(){this.setExport('system',system)},{context,identifier:'server'});
await rt.link(async spec=>spec==='@minecraft/server'?server:core);
await rt.evaluate();

assert.equal(listeners.length,1);
assert.deepEqual(sent,[]);
listeners[0]({id:'kaleidoscope_cookery:api_ready',message:JSON.stringify({api:1,capabilities:['chopping_board']})});
assert.equal(sent.length,1);
assert.equal(sent[0].id,'kaleidoscope_cookery:register_recipe');
const payload=JSON.parse(sent[0].message);
assert.deepEqual(payload.recipe,{
 id:'kaleidoscope_grilling:chopping_board/raw_mantou_slice',
 input:'kaleidoscope_cookery:mantou',
 result:'kaleidoscope_grilling:raw_mantou_slice',
 count:3,cuts:4
});
const before=sent.length;
listeners[0]({id:'kaleidoscope_cookery:api_ready',message:JSON.stringify({api:1,capabilities:['millstone']})});
assert.equal(sent.length,before);
console.log(JSON.stringify({passed:7,failed:0,scope:'A2.7.10 Cookery mantou chopping registration'}));
