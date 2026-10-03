import {ITEM_ID} from './integration_stack_core.js';
import {SECRET_VISUAL_SLOTS} from './secret_visual_catalog.js';
const registry={producers:new Map(),projections:new Map(),held:new Map()};
function install(map,key,value,limit){
 const old=map.get(key);if(old){if(JSON.stringify(old)!==JSON.stringify(value))throw Error('registration conflict');return {replayed:true};}
 if(map.size>=limit)throw Error('registration capacity');map.set(key,value);return {replayed:false};
}
export function registerProducer(raw){
 if(!ITEM_ID.test(raw?.producerId??'')||!Array.isArray(raw.items)||!raw.items.length||raw.items.length>64||raw.items.some(x=>!ITEM_ID.test(x))||!Array.isArray(raw.kinds)||!raw.kinds.length||raw.kinds.some(x=>!['cuisine','furnace','smoker','fresh_fortress'].includes(x)))throw Error('producer schema');
 return install(registry.producers,raw.producerId,{producerId:raw.producerId,items:[...new Set(raw.items)].sort(),kinds:[...new Set(raw.kinds)].sort()},32);
}
export function producerFor(id,kind,itemId){const p=registry.producers.get(id);if(!p||!p.kinds.includes(kind)||itemId&&!p.items.includes(itemId))throw Error('producer not registered for this output');return p;}
export function registerProjectionDescriptor(raw){
 if(!ITEM_ID.test(raw?.itemId??'')||!ITEM_ID.test(raw.provider??'')||raw.defaultData!==undefined&&(!Number.isInteger(raw.defaultData)||raw.defaultData<0||raw.defaultData>32767))throw Error('projection registration schema');
 return install(registry.projections,raw.itemId,{itemId:raw.itemId,provider:raw.provider,...(raw.defaultData===undefined?{}:{defaultData:raw.defaultData})},128);
}
export const projectionDescriptorFor=id=>registry.projections.get(id);
export function registerHeldVisual(raw){
 if(!ITEM_ID.test(raw?.itemId??'')||!SECRET_VISUAL_SLOTS[raw.referenceItemId])throw Error('held visual requires a catalog reference; new textures require a resource release');
 return install(registry.held,raw.itemId,{itemId:raw.itemId,referenceItemId:raw.referenceItemId},128);
}
export const secretVisualIndex=id=>SECRET_VISUAL_SLOTS[registry.held.get(id)?.referenceItemId??id]??0;
export function integrationRegistrySnapshot(){return Object.fromEntries(Object.entries(registry).map(([k,m])=>[k,[...m.values()]]));}
export function restoreIntegrationRegistry(raw){
 resetIntegrationRegistry();try{
  if(!raw||!['producers','projections','held'].every(k=>Array.isArray(raw[k])))throw Error('registry schema');
  for(const row of raw.producers)registerProducer(row);for(const row of raw.projections)registerProjectionDescriptor(row);for(const row of raw.held)registerHeldVisual(row);
 }catch(e){resetIntegrationRegistry();throw e;}
}
export function resetIntegrationRegistry(){for(const map of Object.values(registry))map.clear();}
