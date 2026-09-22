import {OIL_PRESS_ID} from './a26_oil_machine_core.js';
import {a26ReadPress,a26ReadVat,a26ProbePressContainer} from './a26_oil_machine_runtime.js';
import {oilPressHudView} from './a2741_oil_press_hud_core.js';
import {registerCrosshairHudProvider} from './a2739_crosshair_hud_runtime.js';

registerCrosshairHudProvider({
 id:'kaleidoscope_grilling:oil_press',
 priority:80,
 probe(_player,block){
  if(block?.typeId!==OIL_PRESS_ID)return undefined;
  const found=a26ProbePressContainer(block);
  return oilPressHudView(a26ReadPress(block),{
   status:found?.status,
   vat:found?.block?a26ReadVat(found.block):undefined
  });
 }
});
