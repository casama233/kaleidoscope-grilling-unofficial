// Transactions publish only coordinates after committing. Rendering reads the
// authoritative data later; the queue never owns an ItemStack or storage row.
const pending=new Map();
export function queueStationContentsVisual(block){
 if(!block)return;
 const dimensionId=block.dimension.id,location={...block.location};
 if(typeof dimensionId!=='string'||![location.x,location.y,location.z].every(Number.isSafeInteger))return;
 pending.set([dimensionId,location.x,location.y,location.z].join('|'),{dimensionId,location});
}
export function takeStationContentsVisualDirty(limit){
 const rows=[];
 for(const [key,row] of pending){if(rows.length>=limit)break;pending.delete(key);rows.push(row);}
 return rows;
}
