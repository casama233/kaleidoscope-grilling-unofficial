/** Persistent native ItemStacks for the two Grilling-owned stations.
 * The ledger belongs to this BP. It never reads Cookery's private properties.
 * Helpers are inventories, NOT disposable visual entities. Never regenerate a
 * missing/corrupt linked inventory as an empty one, or garbage-collect its items.
 */
import {world,system} from '@minecraft/server';
export const STORAGE_PREFIX='kaleidoscope_grilling:storage_v1/';
export const STORAGE_OWNER='kaleidoscope_grilling:storage_owner_v1';
export const STORAGE_TYPES=Object.freeze({
 'kaleidoscope_grilling:grill':Object.freeze({slots:3,entity:'kaleidoscope_grilling:inventory_grill_v1'}),
 'kaleidoscope_grilling:advanced_rack_block':Object.freeze({slots:9,entity:'kaleidoscope_grilling:inventory_rack_v1'})
});
export class StorageUnavailable extends Error {
 constructor(reason){super('Grilling storage unavailable: '+reason);this.name='StorageUnavailable';}
}
const fail=reason=>{throw new StorageUnavailable(reason);};
export function storageKey(block){
 const {x,y,z}=block.location;
 if(![x,y,z].every(Number.isSafeInteger))fail('non-block coordinates');
 return STORAGE_PREFIX+block.dimension.id+'/'+x+'/'+y+'/'+z;
}
const anchor=block=>({x:block.location.x+.5,y:block.location.y+.25,z:block.location.z+.5});
function readRecord(block){
 const key=storageKey(block),raw=world.getDynamicProperty(key);
 if(raw===undefined)return undefined;
 if(typeof raw!=='string')fail('invalid ledger type');
 let r;try{r=JSON.parse(raw)}catch{fail('invalid ledger JSON')}
 if(!r||r.v!==1||r.key!==key||!Object.hasOwn(STORAGE_TYPES,r.block)||typeof r.entity!=='string'||!r.entity||typeof r.token!=='string'||!r.token)fail('invalid ledger schema');
 return r;
}
function ownership(entity){
 let value;try{value=entity.getDynamicProperty(STORAGE_OWNER)}catch{fail('owner unreadable')}
 if(typeof value!=='string')return undefined;
 try{return JSON.parse(value)}catch{fail('owner malformed')}
}
function container(entity,owner,block){
 const rule=STORAGE_TYPES[owner.block],mark=ownership(entity),pos=anchor(block),actual=entity.location;
 if(entity.typeId!==rule.entity||entity.dimension.id!==block.dimension.id||!mark||mark.v!==1||mark.key!==owner.key||mark.block!==owner.block||mark.token!==owner.token)fail('inventory owner mismatch');
 if(Math.hypot(actual.x-pos.x,actual.y-pos.y,actual.z-pos.z)>.05)fail('inventory moved; refusing reassignment');
 const c=entity.getComponent('minecraft:inventory')?.container;
 if(!c||c.size!==rule.slots)fail('wrong or absent native inventory');
 return c;
}
function candidates(block,type){
 const key=storageKey(block);
 return block.dimension.getEntities({type,location:anchor(block),maxDistance:.1}).filter(e=>ownership(e)?.key===key);
}
function resolve(block,r,rebind=true){
 let entity=world.getEntity(r.entity);
 if(!entity){
  const found=candidates(block,STORAGE_TYPES[r.block].entity).filter(e=>ownership(e)?.token===r.token);
  if(found.length!==1)fail(found.length?'duplicate backing inventories':'linked inventory is unavailable; contents not reset');
  entity=found[0];
  // Native IDs normally persist. Rebind only to the exact persisted owner token.
  container(entity,r,block);const next={...r,entity:entity.id};
  if(rebind)world.setDynamicProperty(r.key,JSON.stringify(next));r=next;
 }
 return {entity,c:container(entity,r,block)};
}
function commitNewRecord(block,entity,mark){
 const r={...mark,entity:entity.id};
 const c=container(entity,r,block);
 world.setDynamicProperty(r.key,JSON.stringify(r));
 if(world.getDynamicProperty(r.key)!==JSON.stringify(r))fail('ledger commit not confirmed');
 return c;
}
export function stationContainer(block){
 if(!block)return undefined;
 const rule=STORAGE_TYPES[block.typeId];if(!rule)return undefined;
 const r=readRecord(block);
 if(r?.quarantine)fail('transaction quarantined; manual recovery required');
 let native;try{native=block.getComponent('minecraft:inventory')?.container}catch{}
 if(native){
  if(r)fail('both legacy native and managed inventory present; migration required');
  if(native.size!==rule.slots)fail('legacy native inventory size mismatch');
  return native;
 }
 if(r){if(r.block!==block.typeId)fail('coordinate still belongs to another station');return resolve(block,r).c;}
 const found=Object.values(STORAGE_TYPES).flatMap(t=>candidates(block,t.entity));
 if(found.length>1)fail('multiple orphan inventories; never merge or delete automatically');
 if(found.length===1){
  const mark=ownership(found[0]);
  if(!mark||mark.v!==1||mark.block!==block.typeId||typeof mark.token!=='string'||!mark.token)fail('unrecognized orphan inventory');
  return commitNewRecord(block,found[0],mark);
 }
 const entity=block.dimension.spawnEntity(rule.entity,anchor(block));
 const mark={v:1,key:storageKey(block),block:block.typeId,token:entity.id+':'+system.currentTick};
 try{
  entity.setDynamicProperty(STORAGE_OWNER,JSON.stringify(mark));
  return commitNewRecord(block,entity,mark);
 }catch(error){
  // This fresh helper has never been returned to a caller. Do not delete any
  // pre-existing helper, and do not remove a record whose commit succeeded.
  if(world.getDynamicProperty(mark.key)===undefined){try{entity.remove()}catch{}}
  throw error;
 }
}
/** Call AFTER the station was removed and AFTER its item transaction succeeded. */
export function retireEmptyStationContainer(block){
 const r=readRecord(block);if(!r)return true;
 if(r.quarantine)fail('transaction quarantined; not retiring inventory');
 if(block.typeId===r.block)fail('station is still present');
 const {entity,c}=resolve(block,r);
 for(let i=0;i<c.size;i++)if(c.getItem(i))fail('refusing to retire nonempty inventory');
 entity.remove();
 world.setDynamicProperty(r.key,undefined);
 if(world.getDynamicProperty(r.key)!==undefined)fail('retired ledger not cleared');
 return true;
}
/** Inspection creates no helpers and transfers no items. */
export function inspectStationStorage(block){
 const r=readRecord(block);
 if(!r)return {linked:false};
 if(r.quarantine)return {linked:true,quarantine:r.quarantine,block:r.block,entity:r.entity};
 const {entity,c}=resolve(block,r,false);
 return {linked:true,block:r.block,entity:entity.id,slots:c.size,occupied:c.size-c.emptySlotsCount};
}

/** Quarantine an ambiguous rollback; preserve the backing inventory for recovery. */
export function quarantineStation(block,reason){
 const r=readRecord(block);if(!r)fail('cannot quarantine absent ledger');
 const next={...r,quarantine:String(reason).slice(0,240)};
 world.setDynamicProperty(r.key,JSON.stringify(next));
 if(world.getDynamicProperty(r.key)!==JSON.stringify(next))fail('quarantine not persisted');
}
