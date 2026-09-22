import {COOKERY_EMPTY_ID,COOKERY_FILLED_ID} from './a2734_cookery_oil_pot_core.js';
import {EMPTY_SEASONING_ID,SEASONING_ID} from './data.js';
import {PENDING_SEASONING_ID} from './a2743_seasoning_contract_core.js';

export const ADVANCED_RACK_ID='kaleidoscope_grilling:advanced_rack';
export const RACK_COMPARTMENT_COUNT=9;
export const RACK_SEASONING_SLOTS=5;
export const RACK_TOOL_SLOTS=4;
export const COOKERY_KNIFE_TAG='kaleidoscope_cookery:kitchen_knife';
export const COOKERY_SHOVEL_TAG='kaleidoscope_cookery:kitchen_shovel';

const OIL_POTS=new Set([COOKERY_EMPTY_ID,COOKERY_FILLED_ID]);
const SEASONING_BOTTLES=new Set([EMPTY_SEASONING_ID,PENDING_SEASONING_ID,SEASONING_ID]);

export function normalizeRackDescriptor(row={}){
 const tags=Array.isArray(row?.tags)?[...new Set(row.tags.map(String).filter(Boolean))]:[];
 return {id:String(row?.id??''),tags,damageable:!!row?.damageable};
}

export function rackSlotKind(slot){
 const n=Math.floor(Number(slot));
 if(n<0||n>=RACK_COMPARTMENT_COUNT)return '';
 return n<RACK_SEASONING_SLOTS?'seasoning':'tool';
}

export function rackItemKind(row={}){
 const d=normalizeRackDescriptor(row);
 if(!d.id)return '';
 if(OIL_POTS.has(d.id))return 'oil_pot';
 if(SEASONING_BOTTLES.has(d.id))return 'seasoning_bottle';
 if(d.id==='minecraft:flint_and_steel'||d.tags.includes(COOKERY_KNIFE_TAG)||d.tags.includes(COOKERY_SHOVEL_TAG))return 'tool';
 return '';
}

export function rackCanPlace(slot,row={}){
 const kind=rackItemKind(row),target=rackSlotKind(slot);
 if(target==='seasoning')return kind==='oil_pot'||kind==='seasoning_bottle';
 if(target==='tool')return kind==='tool';
 return false;
}

export function rackFilterFor(row={}){
 const d=normalizeRackDescriptor(row),kind=rackItemKind(d);
 if(kind==='oil_pot')return {kind:'oil_pot',id:''};
 if(kind==='seasoning_bottle')return {kind:'seasoning_bottle',id:''};
 if(kind==='tool')return {kind:'tool',id:d.id};
 return null;
}

export function normalizeRackFilter(row){
 if(!row||typeof row!=='object')return null;
 const kind=['oil_pot','seasoning_bottle','tool'].includes(row.kind)?row.kind:'';
 if(!kind)return null;
 const id=kind==='tool'?String(row.id??''):'';
 if(kind==='tool'&&!id)return null;
 return {kind,id};
}

export function normalizeRackFilters(rows){
 const out=Array.from({length:RACK_COMPARTMENT_COUNT},()=>null);
 if(Array.isArray(rows))for(let i=0;i<Math.min(rows.length,RACK_COMPARTMENT_COUNT);i++)out[i]=normalizeRackFilter(rows[i]);
 return out;
}

export function rackFilterMatches(filter,row={}){
 const f=normalizeRackFilter(filter);if(!f)return true;
 const d=normalizeRackDescriptor(row),kind=rackItemKind(d);
 if(f.kind==='oil_pot')return kind==='oil_pot';
 if(f.kind==='seasoning_bottle')return kind==='seasoning_bottle';
 return kind==='tool'&&d.id===f.id;
}

export function rackCanPlaceWithFilter(slot,filter,row={}){
 return rackCanPlace(slot,row)&&rackFilterMatches(filter,row);
}

export function rackFiltersAfterInsert(filters,slot,row={}){
 const current=normalizeRackFilters(filters),n=Math.floor(Number(slot));
 if(n<0||n>=RACK_COMPARTMENT_COUNT||current[n])return current;
 const next=rackFilterFor(row);if(next)current[n]=next;
 return current;
}

export function rackCanClearFilter(filters,occupied,slot){
 const rows=normalizeRackFilters(filters),n=Math.floor(Number(slot));
 if(n<0||n>=RACK_COMPARTMENT_COUNT||!rows[n])return false;
 return !Boolean(Array.isArray(occupied)?occupied[n]:false);
}

export function rackSpiceLevel(occupied=[]){
 let count=0;
 for(let i=0;i<RACK_SEASONING_SLOTS;i++)if(Boolean(occupied?.[i]))count++;
 return Math.min(4,count);
}
