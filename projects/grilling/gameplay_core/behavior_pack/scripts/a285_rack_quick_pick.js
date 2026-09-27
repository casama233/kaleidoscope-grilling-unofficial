// Inverse of the rack's cardinal transformation. Top row: five seasoning slots;
// bottom row: four tools. Hit positions are relative to the block's NW bottom.
export function rackSlotAtHit(direction,hit){
 if(!hit||!Number.isFinite(hit.x)||!Number.isFinite(hit.y)||!Number.isFinite(hit.z))return -1;
 const x=hit.x-.5,z=hit.z-.5;
 const localX=direction==='south'?-x:direction==='west'?z:direction==='east'?-z:x;
 const u=Math.max(0,Math.min(.999999,(localX+7/16)/(14/16)));
 return hit.y>=10/16?Math.floor(u*5):5+Math.floor(u*4);
}
