// Sound lifecycle only. Callbacks are native sound handles, never inventory writes.
export const GRILL_LOOP_TICKS=569; // Released OGG: 28.416 s; do not overlap tails.
export const GRILL_AUDIO_STALE_TICKS=8;
export function stopSoundHandle(handle){
 if(!handle)return;
 try{handle.stop()}catch{} // A completed/unloaded native instance may already be gone.
}
export function createGrillAudioController({play,stop=stopSoundHandle,repeatTicks=GRILL_LOOP_TICKS,staleTicks=GRILL_AUDIO_STALE_TICKS}){
 const active=new Map();
 return {
  update(key,station,isActive,tick){
   let row=active.get(key);
   if(!isActive){if(row){stop(row.handle);active.delete(key)}return false}
   if(!row){row={handle:undefined,next:tick,seen:tick};active.set(key,row)}
   row.seen=tick;
   if(tick<row.next)return false;
   // Retire only this station's sound, never all sounds of the same type.
   stop(row.handle);row.handle=undefined;row.next=tick+20;
   try{row.handle=play(station);row.next=tick+repeatTicks;return true}
   catch{return false} // Bounded retry; audio cannot abort a gameplay transaction.
  },
  sweep(tick){
   for(const [key,row] of active)if(tick-row.seen>staleTicks){stop(row.handle);active.delete(key)}
  },
  remove(key){const row=active.get(key);if(row){stop(row.handle);active.delete(key)}},
  get size(){return active.size}
 };
}
