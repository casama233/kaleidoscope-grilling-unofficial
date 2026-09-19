/** Presentation-only rehearsal. Never grants food, consumes items or changes world blocks. */
export const TICKS = Object.freeze({brush:20, flip:14, season:10, eat:90});
export const BITE_SECONDS = Object.freeze([0.95833, 2.33333, 3.45833, 4.08333]);
export const PHASES = Object.freeze(['cold','heated','loaded','turning','seasonable','ready','taken','finished']);
const copy = x => JSON.parse(JSON.stringify(x));
function integer(n) { return Number.isSafeInteger(n) && n>=0; }
export function initial() { return {schema:1,phase:'cold',flips:0,seq:0,action:null,lastCue:-1}; }
export function valid(s) {
  return s && s.schema===1 && PHASES.includes(s.phase) && Number.isInteger(s.flips) && s.flips>=0 && s.flips<=4 && integer(s.seq)
    && (s.action===null || (Object.hasOwn(TICKS,s.action.kind) && integer(s.action.started) && integer(s.action.ends) && s.action.ends-s.action.started===TICKS[s.action.kind]));
}
export function restore(raw) {
  if(raw===undefined) return initial();
  const s=JSON.parse(raw); if(!valid(s)) throw new Error('Unknown or invalid lab state; retained without overwriting');
  // An unfinished cosmetic action is cancelled/settled on load, not replayed to new viewers.
  if(s.action?.kind==='eat') s.phase='taken';
  s.action=null;s.lastCue=-1;return s;
}
export function nextAction(s) {
  if(s.action) return 'busy';
  return ({cold:'ignite',heated:'insert',loaded:'brush',turning:'flip',seasonable:'season',ready:'take',taken:'eat',finished:'reset'})[s.phase];
}
export function apply(state,kind,tick) {
  if(!valid(state)||!integer(tick)) throw new Error('Invalid state or clock');
  if(state.action || kind!==nextAction(state)) return {accepted:false,state,events:[]};
  const s=copy(state),events=[];s.seq++;s.lastCue=-1;
  if(kind==='reset') return {accepted:true,state:{...initial(),seq:s.seq},events:[{kind:'stop_audio'}]};
  if(kind==='ignite') {s.phase='heated';events.push({kind:'ignite'});}
  if(kind==='insert') {s.phase='loaded';events.push({kind:'insert'});}
  if(kind==='brush') {s.phase='turning';events.push({kind:'brush'});}
  if(kind==='flip') {s.flips++;if(s.flips===4)s.phase='seasonable';events.push({kind:'flip',number:s.flips});}
  if(kind==='season') {s.phase='ready';events.push({kind:'season'});}
  if(kind==='take') {s.phase='taken';events.push({kind:'take'},{kind:'stop_audio'});}
  if(kind==='eat') events.push({kind:'eat_start'});
  if(Object.hasOwn(TICKS,kind))s.action={kind,started:tick,ends:tick+TICKS[kind]};
  return {accepted:true,state:s,events};
}
export function advance(state,tick) {
  if(!valid(state)||!integer(tick))throw new Error('Invalid state or clock');
  if(!state.action)return {state,events:[]};
  const s=copy(state),events=[];const a=s.action,seconds=Math.max(0,(tick-a.started)/20);
  if(a.kind==='eat') {
    let index=-1;for(let i=0;i<BITE_SECONDS.length;i++)if(seconds>=BITE_SECONDS[i])index=i;
    // Late ticks update the final visual stage; no burst of stale bite sounds.
    if(index>s.lastCue){events.push({kind:'bite',index,coalesced:index-s.lastCue>1});s.lastCue=index;}
  }
  if(tick>=a.ends){s.action=null;if(a.kind==='eat')s.phase='finished';events.push({kind:'action_end',action:a.kind});}
  return {state:s,events};
}
export function cancel(state) {
  if(!valid(state))throw new Error('Invalid state');
  const s=copy(state);if(s.action?.kind==='eat')s.phase='taken';s.action=null;s.lastCue=-1;
  return {state:s,events:[{kind:'stop_audio'}]};
}
export function view(s,tick) {
  if(!valid(s))throw new Error('Invalid state');
  const loaded=['loaded','turning','seasonable','ready'].includes(s.phase);
  const action=s.action?.kind??'idle';const t=s.action?Math.max(0,Math.min((tick-s.action.started)/20,TICKS[action]/20)):0;
  const stage=s.phase==='loaded'?0:Math.min(4,1+s.flips);
  const bites=action==='eat'?BITE_SECONDS.filter(b=>t>=b).length:s.phase==='finished'?4:0;
  return {lit:s.phase!=='cold',loaded,loop:loaded&&s.phase!=='cold',stage,flips:s.flips,action,seconds:t,bites,held:['taken','finished'].includes(s.phase)};
}
export function flipSample(t,height,flips) {
  if(!Number.isFinite(height)||height<0.28||height>0.38||!Number.isInteger(flips)||flips<1||flips>4)throw new Error('Invalid flip');
  const p=Math.max(0,Math.min(1,t/0.7));return {lift:height*Math.sin(Math.PI*p),degrees:(flips-1+p)*180};
}
export function brushSample(t,side=1) {
  if(![1,-1].includes(side))throw new Error('side');const p=Math.max(0,Math.min(1,t));const w=Math.sin(2*Math.PI*p);
  return {position:[side*.52+w*.25,-.48,-.78],rotationXYZ:[-24,180,side*(32+w*34)],swing:w};
}
export function seasonSample(t,side=1) {
  if(![1,-1].includes(side))throw new Error('side');const p=Math.max(0,Math.min(1,t/.5)),w=Math.sin(4*Math.PI*p),a=Math.sin(Math.PI*p);
  return {position:[side*(.50+w*.08),-.41+a*.10,-.82],rotationXYZ:[-28+a*42,180+side*w*18,side*(22+w*25)+180],wave:w,arc:a};
}
