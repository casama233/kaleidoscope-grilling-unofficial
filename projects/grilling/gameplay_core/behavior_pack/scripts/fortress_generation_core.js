/** Exact Java 1.1.1 coordinate hash; only an authoritative fresh-generation host supplies positions. */
// Four unsigned 16-bit words avoid the BDS BigInt discrepancy observed at (2,64,0).
// Every intermediate stays below 2^35, where ordinary JS integers remain exact.
function words(value){const low=value>>>0,high=Math.floor(value/4294967296)>>>0;return [low&65535,low>>>16,high&65535,high>>>16];}
function multiply(a,b){
 const out=[];let carry=0;for(let k=0;k<4;k++){
  let sum=carry;for(let i=0;i<=k;i++)sum+=a[i]*b[k-i];
  out[k]=sum%65536;carry=Math.floor(sum/65536);
 }return out;
}
function mixShift(v){const high=v[2]+v[3]*65536;v[0]^=(high>>>1)&65535;v[1]^=high>>>17;return v;}
const X_HASH=words(341873128712),Z_HASH=words(132897987541),Y_HASH=words(42317861),MIX_HASH=[0x8ccd,0xed55,0xafd7,0xff51];
export function fortressHashModulo({x,y,z}){
 const a=multiply(words(x),X_HASH),b=multiply(words(z),Z_HASH),c=multiply(words(y),Y_HASH);
 let v=a.map((word,i)=>word^b[i]^c[i]);v=mixShift(multiply(mixShift(v),MIX_HASH));
 let mod=0;for(let i=3;i>=0;i--)mod=(mod*65536+v[i])%100;
 // A negative Java long is the unsigned words minus 2^64; 2^64 modulo 100 is 16.
 return (mod-(v[3]>=32768?16:0)+100)%100;
}
export const fortressReplacementAt=position=>fortressHashModulo(position)<25;
export function normalizeFreshFortress(raw,now){
 const {chunk,bounds,positions}=raw??{};
 if(raw?.dimensionId!=='minecraft:nether'||raw.structureId!=='minecraft:fortress'||raw.isNewChunk!==true||!Number.isSafeInteger(raw.generatedAt)||raw.generatedAt>now||now-raw.generatedAt>20||!chunk||![chunk.x,chunk.z].every(Number.isSafeInteger)||!bounds||!['min','max'].every(k=>bounds[k]&&['x','y','z'].every(a=>Number.isSafeInteger(bounds[k][a])))||!Array.isArray(positions)||!positions.length||positions.length>128)throw Error('fresh fortress evidence required');
 if(bounds.min.y<0||bounds.max.y>127||['x','y','z'].some(a=>bounds.min[a]>bounds.max[a])||Math.floor(bounds.min.x/16)!==chunk.x||Math.floor(bounds.max.x/16)!==chunk.x||Math.floor(bounds.min.z/16)!==chunk.z||Math.floor(bounds.max.z/16)!==chunk.z)throw Error('fortress bounds must be clipped to the new chunk');
 const seen=new Set();for(const p of positions){if(!p||['x','y','z'].some(a=>!Number.isSafeInteger(p[a])||p[a]<bounds.min[a]||p[a]>bounds.max[a]))throw Error('position outside generated bounds');const k=[p.x,p.y,p.z].join(',');if(seen.has(k))throw Error('duplicate generated position');seen.add(k);}
 return {dimensionId:raw.dimensionId,structureId:raw.structureId,isNewChunk:true,generatedAt:raw.generatedAt,chunk:{...chunk},bounds:structuredBounds(bounds),positions:positions.map(p=>({x:p.x,y:p.y,z:p.z}))};
}
function structuredBounds(b){return {min:{x:b.min.x,y:b.min.y,z:b.min.z},max:{x:b.max.x,y:b.max.y,z:b.max.z}};}
