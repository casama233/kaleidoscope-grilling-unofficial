import {world,system} from '@minecraft/server';
import {getMainHand,getOffHand} from './a2735_player_io.js';
import {SECRET_VISUAL_SLOTS} from './secret_visual_catalog.js';
let reader;const signatures=new Map();
export function configureSecretHeldReader(read){reader=read;}
export function syncSecretHeld(player){
 if(!reader)return;
 const rows={};
 for(const [hand,stack] of [['main',getMainHand(player)],['off',getOffHand(player)]]){
  const ingredients=stack?.typeId==='kaleidoscope_grilling:secret_skewer'?reader(stack):[];
  for(let i=0;i<3;i++)rows['kaleidoscope_grilling:secret_'+hand+'_'+i]=SECRET_VISUAL_SLOTS[ingredients[i]?.id]??0;
 }
 const signature=JSON.stringify(rows);if(signatures.get(player.id)===signature)return;
 for(const [key,value] of Object.entries(rows))player.setProperty(key,value);
 signatures.set(player.id,signature);
}
world.afterEvents.playerInventoryItemChange.subscribe(e=>system.run(()=>{try{syncSecretHeld(e.player)}catch(error){console.warn('[Grilling held ingredients] '+error)}}));
world.afterEvents.playerHotbarSelectedSlotChange.subscribe(e=>system.run(()=>{try{syncSecretHeld(e.player)}catch(error){console.warn('[Grilling held ingredients] '+error)}}));
world.afterEvents.playerLeave.subscribe(e=>signatures.delete(e.playerId));
system.runInterval(()=>{for(const player of world.getAllPlayers())try{syncSecretHeld(player)}catch(error){console.warn('[Grilling held ingredients] '+error)}},20);
