import {RECIPE_BLOCK_ID} from './a25_plate_recipe_core.js';
import {a25ReadRecipeBlockSnapshot} from './a25_plate_recipe_runtime.js';
import {skewerRecipeHudView} from './a2745_skewer_recipe_hud_core.js';
import {registerCrosshairHudProvider} from './a2739_crosshair_hud_runtime.js';

registerCrosshairHudProvider({
 id:'kaleidoscope_grilling:skewer_recipe',
 priority:50,
 probe(_player,block){
  if(block?.typeId!==RECIPE_BLOCK_ID)return undefined;
  return skewerRecipeHudView(a25ReadRecipeBlockSnapshot(block));
 }
});
