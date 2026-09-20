export const FINISHED_TICKS=800;
export const BURNT_TICKS=400;
export const FLIP_COOLDOWN=20;

export function initialState(){
  return {phase:0,phaseTicks:0,flips:0,flipCooldown:0,seasoned:false,failed:false,heatTicks:0,lit:false};
}
export function validState(s){
  return s&&Number.isInteger(s.phase)&&s.phase>=0&&s.phase<=3&&Number.isInteger(s.phaseTicks)&&s.phaseTicks>=0&&Number.isInteger(s.flips)&&s.flips>=0&&s.flips<=4&&Number.isInteger(s.flipCooldown)&&s.flipCooldown>=0&&typeof s.seasoned==='boolean'&&typeof s.failed==='boolean'&&Number.isInteger(s.heatTicks)&&s.heatTicks>=0&&typeof s.lit==='boolean';
}
export function tickState(state,occupied,delta=1){
  if(!validState(state)||!Number.isInteger(occupied)||occupied<0||occupied>3||!Number.isInteger(delta)||delta<0)throw new Error('invalid tick');
  const s={...state},events=[];
  s.flipCooldown=Math.max(0,s.flipCooldown-delta);
  if(!s.lit||occupied===0||delta===0)return {state:s,events};
  s.phaseTicks+=delta;
  if(s.phase<=2&&s.phaseTicks>=FINISHED_TICKS){
    s.phase=3;s.phaseTicks=0;events.push({kind:'overcooked'});
  }else if(s.phase===3&&s.phaseTicks>=BURNT_TICKS){
    events.push({kind:'burn_to_charcoal'});return {state:initialState(),events};
  }
  return {state:s,events};
}
export function light(state,on=true){
  if(!validState(state))throw new Error('state');
  return {...state,lit:!!on};
}
export function brush(state,occupied,heatTicks){
  if(!validState(state)||state.phase!==0||occupied<1||!state.lit||!Number.isInteger(heatTicks)||heatTicks<1)return {ok:false,state};
  return {ok:true,state:{...state,phase:1,phaseTicks:0,heatTicks}};
}
export function flip(state){
  if(!validState(state)||state.phase!==1||state.flipCooldown!==0)return {ok:false,state};
  const flips=state.flips+1;
  return {ok:true,state:{...state,flips,phaseTicks:0,flipCooldown:FLIP_COOLDOWN,phase:flips>=4?2:1,failed:false}};
}
export function season(state,occupied){
  if(!validState(state)||state.phase!==2||state.seasoned||occupied<1)return {ok:false,state};
  return {ok:true,state:{...state,seasoned:true}};
}
export function canInsert(state,occupied){return validState(state)&&state.lit&&state.phase===0&&occupied<3;}
export function canExtract(state){return validState(state)&&((state.phase===2&&state.seasoned)||state.phase===3);}
export function breakDisposition(state){
  if(!validState(state))throw new Error('state');
  if(state.phase===0)return 'raw';
  if(state.phase===2&&state.seasoned&&!state.failed)return 'cooked';
  if(state.phase===3)return 'dark';
  return 'mysterious';
}
export function outputKind(state){if(!canExtract(state))return null;return state.phase===3?'dark':state.failed?'mysterious':'cooked';}
