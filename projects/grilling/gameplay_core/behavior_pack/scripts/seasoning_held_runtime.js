import {system,world} from '@minecraft/server';
import {getMainHand,getOffHand} from './a2735_player_io.js';
import {readFoodSeasonings} from './a2750_food_state_adapter.js';
import {INGREDIENT_COLORS,PLACED_TINT_INDEX} from './a2770_placed_visual_data.js';
import {eatingIdentity} from './a285_eating_transaction.js';
const NS='kaleidoscope_grilling:',COUNT=Object.keys(PLACED_TINT_INDEX).length;
const signatures=new Map(),motions=new Map();
function held(player,hand){return hand==='off'?getOffHand(player):getMainHand(player)}
export function beginSeasoningMotion(player,hand){
 const stack=held(player,hand);if(!stack)return;
 motions.set(player.id,{hand,identity:eatingIdentity(stack),slot:player.selectedSlotIndex,start:system.currentTick});
 player.setProperty(NS+'season_hand',hand==='off'?2:1);player.setProperty(NS+'season_phase',1);
}
export function syncSeasoningHeld(player,pending){
 const values={};
 for(const hand of ['main','off']){
  const stack=held(player,hand),layered=[NS+'empty_seasoning_bottle',NS+'pending_seasoning'].includes(stack?.typeId);
  const list=layered?readFoodSeasonings(stack):[];
  values[NS+'bottle_'+hand+'_fill']=Math.min(8,list.length);
  for(let i=0;i<8;i++){
   const pair=INGREDIENT_COLORS[list[i]]??[0xB86B45,0xE0A56A];
   values[NS+'bottle_'+hand+'_'+i]=PLACED_TINT_INDEX[pair[0]]*COUNT+PLACED_TINT_INDEX[pair[1]];
  }
 }
 // The actual use event chooses the hand. Two pending bottles must not both shake.
 const using=pending&&held(player,pending.hand)?.typeId===NS+'pending_seasoning'&&
  eatingIdentity(held(player,pending.hand))===pending.use.identity&&
  (pending.hand==='off'||pending.use.slot===player.selectedSlotIndex);
 values[NS+'pending_hand']=using?(pending.hand==='off'?2:1):0;
 const signature=JSON.stringify(values);
 if(signatures.get(player.id)!==signature){
  for(const [key,value] of Object.entries(values))player.setProperty(key,value);
  signatures.set(player.id,signature);
 }
 const motion=motions.get(player.id),elapsed=motion?system.currentTick-motion.start:11;
 const current=motion&&elapsed<10&&eatingIdentity(held(player,motion.hand))===motion.identity&&
  (motion.hand==='off'||motion.slot===player.selectedSlotIndex);
 if(motion){
  player.setProperty(NS+'season_phase',current?elapsed+1:0);
  if(!current){motions.delete(player.id);player.setProperty(NS+'season_hand',0)}
 }
}
export function forgetSeasoningHeld(id){signatures.delete(id);motions.delete(id)}
world.afterEvents.playerLeave.subscribe(e=>forgetSeasoningHeld(e.playerId));
world.afterEvents.playerSpawn.subscribe(e=>{
 forgetSeasoningHeld(e.player.id);
 for(const key of ['season_hand','season_phase','pending_hand'])e.player.setProperty(NS+key,0);
});
