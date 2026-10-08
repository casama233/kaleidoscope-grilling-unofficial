import {getMainHand,getOffHand} from './a2735_player_io.js';
import {getItemProperty} from './itemData.js';
import {PLATE_ID,PLATE_SKEWERS_KEY} from './a25_plate_recipe_core.js';
import {decodePlateStorage} from './plate_transaction_core.js';
import {plateHeldVisualPlan} from './plate_held_visual_core.js';
import {writeHeldVisual,invalidateHeldVisual} from './held_visual_transport.js';
import {registerHeldVisualProvider,reportHeldVisualError} from './held_visual_dispatch_runtime.js';

// Read the saved envelope directly. Reconstructing temporary ItemStacks here
// would unnecessarily touch content-addressed item metadata on every refresh.
export function syncPlateHeld(player){
 for(const [hand,read] of [['main',getMainHand],['off',getOffHand]]){
  try{
   const stack=read(player);if(stack?.typeId!==PLATE_ID)continue;
   const rows=decodePlateStorage(getItemProperty(stack,PLATE_SKEWERS_KEY));
   writeHeldVisual(player,hand,'plate',plateHeldVisualPlan(rows));
  }catch(error){
   try{invalidateHeldVisual(player,hand)}catch{}
   reportHeldVisualError('plate '+hand,player,error);
  }
 }
}
registerHeldVisualProvider('plate contents',syncPlateHeld);
