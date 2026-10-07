import {canonicalFoodId} from './eating_profile_ids.js';
import {ITEM_ID} from './integration_stack_core.js';
import {SECRET_VISUAL_SLOTS} from './secret_visual_catalog.js';
const registry={producers:new Map(),projections:new Map(),held:new Map()};
let heldRevision=0;
// Local derived-cache dependency only. This is neither persisted nor a player
// property, and replay/unrelated registrations do not change the generation.
export const heldVisualRegistryRevision=()=>heldRevision;
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
 const result=install(registry.held,raw.itemId,{itemId:raw.itemId,referenceItemId:raw.referenceItemId},128);
 if(!result.replayed)heldRevision++;
 return result;
}
export const secretVisualIndex=id=>SECRET_VISUAL_SLOTS[registry.held.get(id)?.referenceItemId??canonicalFoodId(id)]??0;
// Held snapshot rows are copies so callers cannot bypass revision tracking by
// mutating an exposed reference. Their fields are immutable strings.
export function integrationRegistrySnapshot(){return Object.fromEntries(Object.entries(registry).map(([k,m])=>[k,[...m.values()].map(row=>k==='held'?{...row}:row)]));}
const heldSignature=()=>JSON.stringify([...registry.held].sort(([a],[b])=>a<b?-1:a>b?1:0));
export function restoreIntegrationRegistry(raw){
 const before=heldSignature(),revision=heldRevision;
 resetIntegrationRegistry();try{
  if(!raw||!['producers','projections','held'].every(k=>Array.isArray(raw[k])))throw Error('registry schema');
  for(const row of raw.producers)registerProducer(row);for(const row of raw.projections)registerProjectionDescriptor(row);for(const row of raw.held)registerHeldVisual(row);
 }catch(e){resetIntegrationRegistry();throw e;}finally{
  // Restoration is synchronous. Advance only for its final held mapping,
  // preserving caches across replay/order changes and unrelated API rollback.
  heldRevision=revision+(heldSignature()===before?0:1);
 }
}
export function resetIntegrationRegistry(){if(registry.held.size)heldRevision++;for(const map of Object.values(registry))map.clear();}
