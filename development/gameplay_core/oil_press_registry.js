/** Persistent per-press registry; no lossy 256-row array or unloaded-chunk purge.
 * One bounded coordinate record per DP avoids the single-string size limit.
 */
export function createOilPressRegistry(world,legacyKey){
 const prefix=legacyKey+'_entry_',cache=new Map();let loaded=false;
 function normalize(row){
  if(!row||typeof row.d!=='string'||!row.d||!['x','y','z'].every(k=>Number.isSafeInteger(row[k])))throw Error('Invalid oil press registry record');
  return {k:row.d+'|'+row.x+'|'+row.y+'|'+row.z,d:row.d,x:row.x,y:row.y,z:row.z};
 }
 const property=row=>prefix+encodeURIComponent(row.k);
 function load(){
  if(loaded)return;
  const found=new Map(),raw=world.getDynamicProperty(legacyKey);
  const old=raw===undefined?[]:JSON.parse(String(raw));if(!Array.isArray(old))throw Error('Invalid legacy oil press registry');
  for(const value of old){const row=normalize(value);found.set(row.k,row);}
  for(const id of world.getDynamicPropertyIds())if(id.startsWith(prefix)){
   const row=normalize(JSON.parse(String(world.getDynamicProperty(id))));
   if(property(row)!==id)throw Error('Oil press registry identity mismatch');
   found.set(row.k,row);
  }
  // Migration is restartable: retain the old array until all entries persist.
  for(const value of old){const row=normalize(value);world.setDynamicProperty(property(row),JSON.stringify(row));}
  if(raw!==undefined)world.setDynamicProperty(legacyKey,undefined);
  cache.clear();for(const [k,row] of found)cache.set(k,row);loaded=true;
 }
 return {
  rows(){load();return [...cache.values()];},
  add(value){load();const row=normalize(value);if(cache.has(row.k))return;
   world.setDynamicProperty(property(row),JSON.stringify(row));cache.set(row.k,row);
  },
  remove(value){load();const row=normalize(value);if(!cache.has(row.k))return;
   world.setDynamicProperty(property(row),undefined);cache.delete(row.k);}
 };
}
