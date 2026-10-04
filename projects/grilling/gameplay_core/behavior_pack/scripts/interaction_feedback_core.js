// No Minecraft UI dependency: only explicit failure calls enter this gate.
export const JAVA_INTERACTION_KEYS=Object.freeze([
 'oiled','no_brushable_skewers','not_enough_oil','no_seasonable_skewers',
 'not_enough_seasoning','grill_need_heat','grill_need_oil','grill_wait_flip',
 'grill_need_seasoning','grill_ready_to_take','bottle_full','invalid_seasoning',
 'missing_base_seasoning','oil_type_mismatch','big_vat_status','big_vat_reject',
 'press_full','press_need_full_batch','press_status','press_vat_full',
 'press_wrong_vat','press_no_vat','skewer_book_missing','cookery_integration_disabled'
]);
export function javaInteractionMessage(key,args=[],red=false){
 if(!JAVA_INTERACTION_KEYS.includes(key))return undefined;
 const withArgs=args.some(x=>x&&typeof x==='object')?{rawtext:args.map(x=>x&&typeof x==='object'?x:{text:String(x)})}:args.map(String);
 const translated={translate:'message.kaleidoscope_grilling.'+key,with:withArgs};
 return {rawtext:red?[{text:'§c'},translated,{text:'§r'}]:[translated]};
}
export function createFailureFeedbackGate(quietTicks=100){
 const attempts=new Map();
 return {
  allow(id,tick){
   const previous=attempts.get(id);
   attempts.set(id,tick);
   return previous===undefined||tick-previous>=quietTicks;
  },
  forget(id){attempts.delete(id)}
 };
}
