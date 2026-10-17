// Java GrillingDataManager seeds defaults, then applies ordered data roots.
// Stored foods retain ingredient IDs; consumers resolve their current mapping.
export const DEFAULT_SEASONING_EFFECTS=Object.freeze({
 'minecraft:redstone':'speed',
 'minecraft:gunpowder':'strength',
 'kaleidoscope_grilling:houttuynia_powder':'duration',
 'kaleidoscope_grilling:totem_powder':'totem',
 'kaleidoscope_grilling:dragon_egg_powder':'vitality',
 'kaleidoscope_grilling:sichuan_pepper':'numbness'
});
const ITEM_ID=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
let overrides=new Map(),effective=new Map(Object.entries(DEFAULT_SEASONING_EFFECTS));
export const seasoningKind=id=>effective.get(id);
export const hasSeasoningMapping=id=>effective.has(id);
export function seasoningDataSnapshot(){return [...overrides].map(([ingredient,kind])=>({ingredient,kind}));}
export function replaceSeasoningData(roots){
 if(!Array.isArray(roots))throw Error('seasoning roots must be an ordered array');
 const next=new Map();
 for(const root of roots){
  if(!root||typeof root!=='object'||Array.isArray(root))throw Error('seasoning root schema');
  if(!Object.hasOwn(root,'seasoning_effects'))continue;
  if(!Array.isArray(root.seasoning_effects))throw Error('seasoning effects schema');
  for(const row of root.seasoning_effects){
   if(typeof row?.ingredient!=='string'||!ITEM_ID.test(row.ingredient)||typeof row.kind!=='string')throw Error('seasoning entry schema');
   // Unknown and empty kinds are valid ingredients in Java. They grant no
   // built-in effect unless a consumer recognizes that exact kind.
   next.set(row.ingredient,row.kind);
  }
 }
 const merged=new Map([...Object.entries(DEFAULT_SEASONING_EFFECTS),...next]);
 overrides=next;effective=merged;
 return {ingredients:effective.size,overrides:overrides.size};
}
