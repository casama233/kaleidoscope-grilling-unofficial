import {PLATE_BLOCK_ID} from './a25_plate_recipe_core.js';
import {a25ReadPlateBlock} from './a25_plate_recipe_runtime.js';
import {skewerPlateHudView} from './a2744_skewer_plate_hud_core.js';
import {registerCrosshairHudProvider} from './a2739_crosshair_hud_runtime.js';

registerCrosshairHudProvider({
 id:'kaleidoscope_grilling:skewer_plate',
 priority:60,
 probe(_player,block){
  if(block?.typeId!==PLATE_BLOCK_ID)return undefined;
  return skewerPlateHudView(a25ReadPlateBlock(block));
 }
});
