import {world,system} from '@minecraft/server';
import {readPublicOil,isOilPayloadLine} from './host_api/oil_api_core.js';
import {readCookeryOilPot,buildCookeryOilPot,COOKERY_FILLED_ID} from './a2734_cookery_oil_pot_adapter.js';
import {getHand,setHand,playerInventory} from './a2735_player_io.js';
const pending=new Map();let sequence=0;
const stable=s=>s?JSON.stringify({id:s.typeId,n:s.amount,name:s.nameTag,lore:s.getRawLore().filter(x=>!isOilPayloadLine(x))}):'';
export function publishLegacyGrillingPot(stack){
 const state=readCookeryOilPot(stack);if(state.source!=='legacy_grilling')return undefined;
 return buildCookeryOilPot(state.type,state.count,stack);
}
export function ensureOilHandPublished(player,hand,continueUse){
 const stack=getHand(player,hand),read=readCookeryOilPot(stack);
 if(read.valid){
  if(read.source==='legacy_grilling'){const next=publishLegacyGrillingPot(stack);if(!next)return false;setHand(player,hand,next);if(JSON.stringify(readCookeryOilPot(getHand(player,hand)))!==JSON.stringify(readCookeryOilPot(next)))return false;}
  return true;
 }
 if(read.reason!=='host_snapshot_required')return false;
 const id=player.id+':'+(++sequence),signature=stable(stack),slot=player.selectedSlotIndex;
 pending.set(id,{player,hand,slot,signature,continueUse});
 system.sendScriptEvent('senluo:oil_snapshot_request',JSON.stringify({api:1,id,playerId:player.id,hand,expectedId:stack.typeId,expectedLore:JSON.stringify(stack.getRawLore())}));
 system.runTimeout(()=>{const r=pending.get(id);if(!r)return;pending.delete(id);try{console.warn('[Grilling Oil API] host snapshot unavailable')}catch{}},60);return false;
}
system.afterEvents.scriptEventReceive.subscribe(ev=>{
 if(ev.id!=='senluo:oil_snapshot_response')return;
 try{const reply=JSON.parse(ev.message),r=pending.get(reply.id);if(!r||reply.api!==1)return;pending.delete(reply.id);
  if(!reply.ok){console.warn('[Grilling Oil API] host snapshot rejected');return}
  if(r.player.selectedSlotIndex!==r.slot||stable(getHand(r.player,r.hand))!==r.signature||!readCookeryOilPot(getHand(r.player,r.hand)).valid)return;
  system.run(()=>{if((r.hand==='off'||r.player.selectedSlotIndex===r.slot)&&stable(getHand(r.player,r.hand))===r.signature&&readCookeryOilPot(getHand(r.player,r.hand)).valid)r.continueUse?.();});
 }catch(e){console.warn('[Grilling Oil API] deferred use retained '+e)}
});
function migrate(p){
 const c=playerInventory(p);if(c)for(let i=0;i<c.size;i++){const s=c.getItem(i);if(s?.typeId!==COOKERY_FILLED_ID||readPublicOil(s).source==='public_api')continue;const next=publishLegacyGrillingPot(s);if(next)c.setItem(i,next)}
 const off=getHand(p,'off');if(off?.typeId===COOKERY_FILLED_ID){const next=publishLegacyGrillingPot(off);if(next)setHand(p,'off',next)}
}
world.afterEvents.playerSpawn.subscribe(e=>system.runTimeout(()=>{try{migrate(e.player)}catch(error){console.warn('[Grilling Oil API] legacy pot retained '+error)}},5));
system.runTimeout(()=>{for(const p of world.getAllPlayers())try{migrate(p)}catch{}},10);
