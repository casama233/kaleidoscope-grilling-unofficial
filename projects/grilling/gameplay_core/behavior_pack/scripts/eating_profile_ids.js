import {PROFILE_BY_ITEM} from './data.js';
export const ALT_SUFFIX='_java_three_alt';
export const RANDOM_EATING_IDS=new Set([...Object.keys(PROFILE_BY_ITEM).filter(id=>PROFILE_BY_ITEM[id]==='THREE_RANDOM'),'kaleidoscope_grilling:secret_skewer']);
export function canonicalFoodId(id){const base=typeof id==='string'&&id.endsWith(ALT_SUFFIX)?id.slice(0,-ALT_SUFFIX.length):id;return RANDOM_EATING_IDS.has(base)?base:id;}
export function isAlternateEatingId(id){return canonicalFoodId(id)!==id;}
export function eatingItemId(id,alternate){const base=canonicalFoodId(id);return RANDOM_EATING_IDS.has(base)&&alternate?base+ALT_SUFFIX:base;}
// Keep canonical enumeration stable for guides and recipes. Internal native-use
// variants resolve to the same food, effects and cooking outputs at lookup sites.
export function foodLookup(table){return new Proxy({...table},{get:(target,key)=>Reflect.get(target,canonicalFoodId(key)),has:(target,key)=>Reflect.has(target,canonicalFoodId(key)),getOwnPropertyDescriptor:(target,key)=>(()=>{const d=Reflect.getOwnPropertyDescriptor(target,canonicalFoodId(key));return d?{...d,configurable:true}:undefined})()});}
