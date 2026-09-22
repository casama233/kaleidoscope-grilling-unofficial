import {GRILL_ID} from './data.js';
import {readGrillState,occupiedGrillSlots} from './a2740_grill_state_adapter.js';
import {grillHudView} from './a2740_grill_hud_core.js';
import {registerCrosshairHudProvider} from './a2739_crosshair_hud_runtime.js';

registerCrosshairHudProvider({
 id:'kaleidoscope_grilling:grill',
 priority:90,
 probe(_player,block){
  if(block?.typeId!==GRILL_ID)return undefined;
  return grillHudView(readGrillState(block),occupiedGrillSlots(block));
 }
});
