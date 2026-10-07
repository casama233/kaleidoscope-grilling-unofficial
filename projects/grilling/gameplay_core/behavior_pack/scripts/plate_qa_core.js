/** Default-off, bounded, sanitized native plate diagnostics. Never owns gameplay. */
const TYPES=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
const PHASES=new Set(['plate_before','plate_before_empty','plate_before_allowed','plate_before_error','guard_before','guard_result','start_received','start_empty','start_selected','start_registered','complete_received','complete_gate','settlement','stop_received','stop_cleared','reward_detail']);
const STAGES=new Set(['received','already_cancelled','empty_event_rows','allowed','unreadable','cancelled','missing_session','identity_rejected','accepted','selected','registered','reconstruct_begin','reconstruct_ok','reconstruct_failed','commit_begin','debit_begin','debit_ok','reward_begin','reward_ok','commit_failed','commit_threw','commit_ok','finish_ok','stop_scheduled','stop_cleared','reward_facts_begin','reward_facts_ok','reward_components','reward_hunger_before','reward_hunger_after','reward_saturation_before','reward_saturation_after','reward_failed']);
const NUMERIC=['nutrition','saturationModifier','hungerCurrent','hungerMax','hungerTarget','hungerAfter','saturationCurrent','saturationMax','saturationTarget','saturationAfter','gain'];
const OPERATIONS=new Set(['facts','components','hunger_target','hunger_write','saturation_target','saturation_write']);
const ERRORS=new Set(['Error','TypeError','RangeError','ArgumentOutOfBoundsError','InvalidEntityError','UnsupportedFunctionalityError','EngineError','RestrictedExecutionError','InvalidArgumentError']);
function type(value){return typeof value==='string'&&value.length<=128&&TYPES.test(value)?value:'none';}
function rows(value){return Number.isInteger(value)&&value>=0&&value<=5?value:value==='unreadable'?'unreadable':'not_plate';}
export function createPlateQaLogger({enabled,key,tick,snapshot,write,windowTicks=1200,perPlayerLimit=96,globalLimit=192,maxPlayers=16}){
 let window=-1,total=0;const counts=new Map();
 return (player,phase,eventStack,detail={})=>{
  try{
   // Do not read either hand or any item metadata unless the native opt-in tag is set.
   if(!PHASES.has(phase)||!enabled(player))return false;
   const time=tick();if(!Number.isFinite(time)||time<0)return false;
   const current=Math.floor(time/windowTicks);if(current!==window){window=current;total=0;counts.clear();}
   const id=key(player),count=counts.get(id)??0;
   if(total>=globalLimit||count>=perPlayerLimit||(!counts.has(id)&&counts.size>=maxPlayers))return false;
   counts.set(id,count+1);total++;
   const state=snapshot(player,eventStack)??{};
   if(typeof detail==='function')detail=detail();
   const out={phase,eventType:type(state.eventType),mainType:type(state.mainType),offType:type(state.offType),eventRows:rows(state.eventRows),mainRows:rows(state.mainRows),offRows:rows(state.offRows)};
   for(const name of ['cancelled','session','identityMatch'])if(typeof detail[name]==='boolean')out[name]=detail[name];
   if(STAGES.has(detail.stage))out.stage=detail.stage;
   for(const name of NUMERIC)if(typeof detail[name]==='number')out[name]=Number.isFinite(detail[name])&&Math.abs(detail[name])<=1000000?detail[name]:'non_finite_or_out_of_bounds';
   if(OPERATIONS.has(detail.operation))out.operation=detail.operation;
   if(typeof detail.errorName==='string'){
    const name=detail.errorName.split('.').pop();out.errorName=ERRORS.has(name)?name:'OtherError';
    out.errorCategory=({ArgumentOutOfBoundsError:'native_bounds',InvalidArgumentError:'native_argument',InvalidEntityError:'native_entity',UnsupportedFunctionalityError:'native_unsupported',RestrictedExecutionError:'restricted',TypeError:'js_type',RangeError:'js_range',EngineError:'engine'})[out.errorName]??'unknown';
   }
   write('[Grilling plate QA] '+JSON.stringify(out));return true;
  }catch{return false;} // Diagnostic failure must never alter the original interaction.
 };
}
