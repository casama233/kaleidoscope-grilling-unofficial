/** Loaded pepper sources, not all world blocks, drive bounded body-contact work. */
export function contactBlockBounds({center,extent}){
 if(!center||!extent||!['x','y','z'].every(a=>Number.isFinite(center[a])&&Number.isFinite(extent[a])&&extent[a]>=0))return;
 const min={},max={};
 for(const a of ['x','y','z']){min[a]=Math.floor(center[a]-extent[a]+.0001);max[a]=Math.floor(center[a]+extent[a]-.0001);}
 return {min,max};
}
export function contactContains(bounds,position){
 return !!bounds&&['x','y','z'].every(a=>position[a]>=bounds.min[a]&&position[a]<=bounds.max[a]);
}
export class PepperContactWork{
 constructor({entityBudget=16,probeBudget=64,sliceBudget=8,pruneBudget=32,staleTicks=20,cellSize=8,contactInterval=5}={}){
  Object.assign(this,{entityBudget,probeBudget,sliceBudget,pruneBudget,staleTicks,cellSize,contactInterval});
  this.leaves=new Map();this.cells=new Map();this.dimensions=new Map();this.entities=new Map();
  this.entityCursor=undefined;this.leafCursor=undefined;this.recoveries=new Map();this.recoveryCursor=undefined;
 }
 leafKey(d,p){return d+'|'+p.x+'|'+p.y+'|'+p.z;}
 cellKey(d,p){return d+'|'+Math.floor(p.x/this.cellSize)+'|'+Math.floor(p.y/this.cellSize)+'|'+Math.floor(p.z/this.cellSize);}
 hasLeaves(d){return (this.dimensions.get(d)??0)>0;}
 rememberLeaf(d,p,tick){
  const key=this.leafKey(d,p),old=this.leaves.get(key);
  if(old){old.tick=tick;return false;}
  const row={key,dimensionId:d,location:{...p},tick,cell:this.cellKey(d,p)};
  this.leaves.set(key,row);this.dimensions.set(d,(this.dimensions.get(d)??0)+1);
  const bucket=this.cells.get(row.cell)??new Set();bucket.add(key);this.cells.set(row.cell,bucket);return true;
 }
 forgetLeaf(key){
  const row=this.leaves.get(key);if(!row)return;
  this.leaves.delete(key);const bucket=this.cells.get(row.cell);bucket?.delete(key);if(!bucket?.size)this.cells.delete(row.cell);
  const remaining=(this.dimensions.get(row.dimensionId)??1)-1;if(remaining)this.dimensions.set(row.dimensionId,remaining);else this.dimensions.delete(row.dimensionId);
 }
 track(entity){
  // Census handles can unload before their bounded insertion turn.
  let id;try{id=entity?.id;}catch{return false;}
  if(!id)return false;
  const old=this.entities.get(id);
  if(old){if(old.entity!==entity){old.entity=entity;old.task=undefined;old.due=0;old.dimension=undefined;}return false;}
  this.entities.set(id,{id,entity,task:undefined});return true;
 }
 forget(id){this.entities.delete(id);}
 queueRecovery(d,entities){this.recoveries.set(d,{entities,cursor:0});}
 recover(){
  let used=0;
  while(used<this.entityBudget&&this.recoveries.size){
   if(!this.recoveryCursor)this.recoveryCursor=this.recoveries.entries();let next=this.recoveryCursor.next();
   if(next.done){this.recoveryCursor=this.recoveries.entries();next=this.recoveryCursor.next();if(next.done)break;}
   const [d,row]=next.value;used++;
   if(row.cursor<row.entities.length)this.track(row.entities[row.cursor++]);
   if(row.cursor>=row.entities.length)this.recoveries.delete(d);
  }
  return used;
 }
 prune(tick){
  const limit=Math.min(this.pruneBudget,this.leaves.size);let scanned=0;
  while(scanned<limit){
   if(!this.leafCursor)this.leafCursor=this.leaves.values();let next=this.leafCursor.next();
   if(next.done){this.leafCursor=this.leaves.values();next=this.leafCursor.next();if(next.done)break;}
   scanned++;if(tick-next.value.tick>this.staleTicks)this.forgetLeaf(next.value.key);
  }
  return scanned;
 }
 *candidates(d,bounds){
  if(!bounds)return;
  const {min,max}=bounds,s=this.cellSize;
  for(let x=Math.floor(min.x/s);x<=Math.floor(max.x/s);x++)
  for(let y=Math.floor(min.y/s);y<=Math.floor(max.y/s);y++)
  for(let z=Math.floor(min.z/s);z<=Math.floor(max.z/s);z++){
   // Empty buckets consume a work unit too; a huge AABB cannot monopolize a tick.
   yield;
   for(const key of this.cells.get(d+'|'+x+'|'+y+'|'+z)??[]){
    const leaf=this.leaves.get(key);yield leaf&&contactContains(bounds,leaf.location)?leaf:undefined;
   }
  }
 }
 tick(tick,adapter){
  const result={recovered:this.recover(),entities:0,probes:0,blockReads:0,stings:0,pruned:this.prune(tick)};
  const limit=Math.min(this.entityBudget,this.entities.size);
  // Leave the cursor on the next entity when probes run out, so every cohort
  // receives a slice even when entityBudget*sliceBudget exceeds probeBudget.
  while(result.entities<limit&&result.probes<this.probeBudget){
   if(!this.entityCursor)this.entityCursor=this.entities.values();let next=this.entityCursor.next();
   if(next.done){this.entityCursor=this.entities.values();next=this.entityCursor.next();if(next.done)break;}
   const row=next.value,e=row.entity;result.entities++;
   try{
    if(!adapter.valid(e)){this.forget(row.id);continue;}
    const d=adapter.dimension(e);
    if(!this.hasLeaves(d)){row.task=undefined;continue;}
    if(!row.task&&tick<(row.due??0))continue;
    // Component groups can add health later without a new spawn/load event.
    if(!adapter.eligible(e)){row.task=undefined;row.due=tick+this.contactInterval;continue;}
    const bounds=contactBlockBounds(adapter.bounds(e));
    if(!bounds){row.task=undefined;continue;}
    if(row.dimension!==d){row.task=undefined;row.dimension=d;}
    row.task??=this.candidates(d,bounds);
    for(let used=0;used<this.sliceBudget&&result.probes<this.probeBudget;used++){
     result.probes++;const candidate=row.task.next();
     if(candidate.done){row.task=undefined;row.due=tick+this.contactInterval;break;}
     const leaf=candidate.value;
     // The entity may have moved while a large cohort was being processed.
     if(!leaf||this.leaves.get(leaf.key)!==leaf||!contactContains(bounds,leaf.location))continue;
     result.blockReads++;const status=adapter.leaf(d,leaf.location);
     if(status==='missing'){this.forgetLeaf(leaf.key);continue;}
     if(status!=='leaf')continue;
     adapter.sting(e);result.stings++;row.task=undefined;row.due=tick+this.contactInterval;break;
    }
   }catch(error){row.task=undefined;adapter.error?.(error);}
  }
  return result;
 }
}
