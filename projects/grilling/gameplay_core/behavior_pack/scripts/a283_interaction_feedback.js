import {world,system} from '@minecraft/server';

// Only failed/requested interactions call this. No crosshair or tick HUD.
// Holding the use button must not refresh a message every tick.
const LAST=new Map();
export function interactionFeedback(player,text){
 if(!player||!text)return;
 const previous=LAST.get(player.id),now=system.currentTick;
 if(previous&&now-previous.tick<60)return;
 try{player.onScreenDisplay.setActionBar(text);LAST.set(player.id,{tick:now})}catch{}
}
world.afterEvents.playerLeave.subscribe(e=>LAST.delete(e.playerId));
