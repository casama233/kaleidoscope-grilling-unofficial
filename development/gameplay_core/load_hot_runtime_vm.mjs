// Loads current production dependencies; fixtures do not replace transaction or metadata logic.
import fs from 'node:fs';
import vm from 'node:vm';
export async function loadHotRuntime(){
 const properties=new Map(),context=vm.createContext({console,JSON,Map,Set,Object,Array,Number,String,Math,Boolean,Error,Date});
 const world={getAbsoluteTime:()=>1000,getDynamicProperty:k=>properties.get(k),setDynamicProperty:(k,v)=>v===undefined?properties.delete(k):properties.set(k,v)};
 const root=new URL('../../projects/grilling/gameplay_core/behavior_pack/scripts/',import.meta.url),modules=new Map();
 const server=new vm.SyntheticModule(['world'],function(){this.setExport('world',world);},{context,identifier:'@minecraft/server'});
 const load=name=>{if(!modules.has(name))modules.set(name,new vm.SourceTextModule(fs.readFileSync(new URL(name,root),'utf8'),{context,identifier:name}));return modules.get(name);};
 const runtime=load('a23_hot_runtime.js');await runtime.link(spec=>spec==='@minecraft/server'?server:load(spec.replace(/^\.\//,'')));await runtime.evaluate();
 return {hot:runtime.namespace,data:modules.get('itemDataCore.js').namespace};
}
