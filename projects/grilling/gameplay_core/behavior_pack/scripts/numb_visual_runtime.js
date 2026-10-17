// Java HumanoidAnvilPressMixin uses entity age, not an animation-local clock.
// RP phase: 20 ticks/s * 0.32 rad/tick * 180/pi = 366.6929889 degrees/s.
// A namespaced controller leaves eating, seasoning and the host's pose alone.
const active=new Map(),suppressedUntil=new Map(),CONTROLLER='kg_numb',REFRESH_TICKS=12;
function stopNumbVisual(player){
 if(!active.has(player.id))return;
 try{
  player.playAnimation('animation.kg_a22.player.numb_stop',{controller:CONTROLLER,blendOutTime:0});
  active.delete(player.id);
 }catch{} // Retry an unacknowledged stop without resetting another controller.
}
/** Call after another pose starts successfully; include its native blend-out. */
export function suppressNumbVisual(player,tick,durationTicks){
 if(!Number.isFinite(tick)||!Number.isFinite(durationTicks)||durationTicks<=0)return;
 const until=tick+Math.ceil(durationTicks);if(!Number.isFinite(until))return;
 suppressedUntil.set(player.id,Math.max(suppressedUntil.get(player.id)??until,until));
 stopNumbVisual(player);
}
export function updateNumbVisual(player,enabled,tick){
 const until=suppressedUntil.get(player.id);
 if(until!==undefined&&tick>=until)suppressedUntil.delete(player.id);
 if(!enabled||(until!==undefined&&tick<until)){stopNumbVisual(player);return}
 const row=active.get(player.id);
 if(row&&tick<row.refreshAt)return;
 active.set(player.id,{refreshAt:tick+REFRESH_TICKS});
 try{
  // Keep a bounded resync for clients which begin tracking this entity later.
  // The looping asset samples life_time and has no restart fade or keyframes.
  player.playAnimation('animation.kg_a22.player.numb',{controller:CONTROLLER,blendOutTime:0,stopExpression:'0'});
 }catch{}
}
export function forgetNumbVisual(playerId){active.delete(playerId);suppressedUntil.delete(playerId)}
