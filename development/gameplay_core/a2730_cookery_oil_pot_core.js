export const COOKERY_EMPTY_ID='kaleidoscope_cookery:oil_pot';
export const COOKERY_FILLED_ID='kaleidoscope_cookery:oil_pot_filled';
export const HOST_COUNT_KEY='kc_oil_count';
export const GRILLING_TYPE_KEY='kaleidoscope_grilling:oil_type';
export const HOST_FAT_CAPACITY=256;
export const GRILLING_FLUID_CAPACITY=64;

export const GRILLING_OIL_TYPES=Object.freeze([
 'canola','secret_chili','premium_chili'
]);

const GRILLING_TYPES=new Set(GRILLING_OIL_TYPES);

export function normalizeOilType(value){
 const type=String(value??'');
 return GRILLING_TYPES.has(type)?type:'';
}

export function oilCapacity(type){
 return normalizeOilType(type)?GRILLING_FLUID_CAPACITY:HOST_FAT_CAPACITY;
}

export function normalizeOilCount({filled=false,type='',raw=undefined,hasRaw=false}={}){
 if(!filled)return 0;
 const cap=oilCapacity(type);
 if(!hasRaw)return cap;
 const n=Number(raw);
 return Math.max(0,Math.min(cap,Number.isFinite(n)?Math.floor(n):0));
}

export function planOilConsumption(state={},needed=1,requiredType=''){
 if(!state.filled)return {ok:false,reason:'not_pot',count:0};
 const type=normalizeOilType(state.type);
 const count=normalizeOilCount({filled:true,type,raw:state.count,hasRaw:true});
 const required=normalizeOilType(requiredType);
 if(required&&type!==required)return {ok:false,reason:'wrong_oil',type,count};
 const use=Math.max(0,Math.floor(Number(needed)||0));
 if(use<=0)return {ok:false,reason:'invalid_amount',type,count};
 if(count<use)return {ok:false,reason:'insufficient',type,count};
 return {ok:true,type,count,used:use,remaining:count-use,capacity:oilCapacity(type)};
}
