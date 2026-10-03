/** Exact Java 1.1.1 coordinate hash; only an authoritative fresh-generation host supplies positions. */
export function fortressReplacementAt({x,y,z}){
 let v=BigInt.asUintN(64,BigInt(x)*341873128712n^BigInt(z)*132897987541n^BigInt(y)*42317861n);
 v^=v>>33n;v=BigInt.asUintN(64,v*0xff51afd7ed558ccdn);v^=v>>33n;
 return Number((BigInt.asIntN(64,v)%100n+100n)%100n)<25;
}
export function normalizeFreshFortress(raw,now){
 const {chunk,bounds,positions}=raw??{};
 if(raw?.dimensionId!=='minecraft:nether'||raw.structureId!=='minecraft:fortress'||raw.isNewChunk!==true||!Number.isSafeInteger(raw.generatedAt)||raw.generatedAt>now||now-raw.generatedAt>20||!chunk||![chunk.x,chunk.z].every(Number.isSafeInteger)||!bounds||!['min','max'].every(k=>bounds[k]&&['x','y','z'].every(a=>Number.isSafeInteger(bounds[k][a])))||!Array.isArray(positions)||!positions.length||positions.length>128)throw Error('fresh fortress evidence required');
 if(bounds.min.y<0||bounds.max.y>127||['x','y','z'].some(a=>bounds.min[a]>bounds.max[a])||Math.floor(bounds.min.x/16)!==chunk.x||Math.floor(bounds.max.x/16)!==chunk.x||Math.floor(bounds.min.z/16)!==chunk.z||Math.floor(bounds.max.z/16)!==chunk.z)throw Error('fortress bounds must be clipped to the new chunk');
 const seen=new Set();for(const p of positions){if(!p||['x','y','z'].some(a=>!Number.isSafeInteger(p[a])||p[a]<bounds.min[a]||p[a]>bounds.max[a]))throw Error('position outside generated bounds');const k=[p.x,p.y,p.z].join(',');if(seen.has(k))throw Error('duplicate generated position');seen.add(k);}
 return {dimensionId:raw.dimensionId,structureId:raw.structureId,isNewChunk:true,generatedAt:raw.generatedAt,chunk:{...chunk},bounds:structuredBounds(bounds),positions:positions.map(p=>({x:p.x,y:p.y,z:p.z}))};
}
function structuredBounds(b){return {min:{x:b.min.x,y:b.min.y,z:b.min.z},max:{x:b.max.x,y:b.max.y,z:b.max.z}};}
