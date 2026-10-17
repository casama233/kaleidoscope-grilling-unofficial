/** Only nearby targets enter the round-robin; changed targets go first. */
export class VisualTargetQueue{
 constructor(){this.targets=new Map();this.cells=new Map();this.dirty=new Set();this.urgent=new Set();this.visible=new Set();this.active=[];this.cursor=0;this.cleanup=new Set();this.viewers=[];this.cleanupTurn=false;}
 cell(row){return row.dimensionId+'|'+Math.floor(row.location.x/64)+'|'+Math.floor(row.location.z/64);}
 add(key,row){if(this.targets.has(key))return false;this.targets.set(key,row);const cell=this.cell(row);if(!this.cells.has(cell))this.cells.set(cell,new Set());this.cells.get(cell).add(key);this.mark(key);return true;}
 remove(key){const row=this.targets.get(key);if(!row)return;const cell=this.cell(row),set=this.cells.get(cell);set?.delete(key);if(!set?.size)this.cells.delete(cell);this.targets.delete(key);this.dirty.delete(key);this.urgent.delete(key);this.visible.delete(key);this.cleanup.delete(key);}
 mark(key){const r=this.targets.get(key);if(!r)return;if(!this.visible.has(key)&&this.viewers.some(p=>p.dimensionId===r.dimensionId&&Math.hypot(p.x-r.location.x,p.y-r.location.y,p.z-r.location.z)<=48)){this.visible.add(key);this.active.push(key)}if(this.visible.has(key))this.urgent.add(key);}
 observe(viewers){
  this.viewers=viewers;const next=new Set();
  for(const p of viewers)for(let x=Math.floor((p.x-48)/64);x<=Math.floor((p.x+48)/64);x++)for(let z=Math.floor((p.z-48)/64);z<=Math.floor((p.z+48)/64);z++){
   for(const key of this.cells.get(p.dimensionId+'|'+x+'|'+z)??[]){const r=this.targets.get(key),l=r?.location;if(l&&Math.hypot(p.x-l.x,p.y-l.y,p.z-l.z)<=48)next.add(key);}
  }
  for(const key of this.visible)if(!next.has(key)){this.cleanup.add(key);this.dirty.delete(key);this.urgent.delete(key)}
  for(const key of next)if(!this.visible.has(key))this.dirty.add(key);
  this.visible=next;this.active=[...next];this.cursor%=Math.max(1,this.active.length);
 }
 take(budget){
  const out=[],seen=new Set();
  if(budget===1&&this.cleanup.size){this.cleanupTurn=!this.cleanupTurn;if(!this.active.length||this.cleanupTurn){const key=this.cleanup.values().next().value;this.cleanup.delete(key);return this.targets.has(key)?[key]:[];}}const push=key=>{if(seen.has(key)||!this.targets.has(key))return;seen.add(key);out.push(key);};
  // Half the budget is reserved for cleanup/fair scanning so continuous edits cannot starve them.
  const urgent=Math.floor(budget/2);
  for(const key of this.urgent){if(out.length>=urgent)break;this.urgent.delete(key);this.dirty.delete(key);push(key);}
  for(const key of this.dirty){if(out.length>=urgent)break;if(!this.visible.has(key))continue;this.dirty.delete(key);push(key);if(out.length>=urgent)break;}
  for(const key of this.cleanup){if(out.length>=Math.max(0,budget-1))break;this.cleanup.delete(key);push(key);}
  for(let n=0;n<this.active.length&&out.length<budget;n++)push(this.active[this.cursor++%this.active.length]);
  return out;
 }
}
