import {VANILLA_FOOD_BEHAVIOR} from './a285_vanilla_food_data.js';
import {effectsForStandaloneFood} from './a2732_standalone_food_effect_core.js';
import {COOKED_EFFECTS,RAW_NAUSEA} from './data.js';
import {ingredientFinishBehavior} from './a288_parity_contract.js';

// Explicit compatibility data, never a forged itemCompleteUse event. Only edible
// ingredients inherit finish-use effects, matching Java SecretSkewerItem.
export function ingredientBehavior(row){
 if(!row||!(row.edible??(Number(row.nutrition)>0)))return {effects:[],convertTo:''};
 const vanilla=VANILLA_FOOD_BEHAVIOR[row.id],registered=ingredientFinishBehavior(row.id);
 const effects=registered?.replaceEffects?[]:(vanilla?.effects??[]).map(e=>({...e,kind:'native'}));
 if(!registered?.replaceEffects){
  effects.push(...effectsForStandaloneFood(row.id));
  const fixed=COOKED_EFFECTS[row.id];
  if(fixed?.effect)effects.push({kind:fixed.effect.startsWith('minecraft:')?'native':'persistent_fx',
   effect:fixed.effect.split(':')[1],ticks:fixed.seconds*20,amplifier:0});
  if(RAW_NAUSEA[row.id]||row.id==='kaleidoscope_grilling:mysterious_skewer')
   effects.push({kind:'native',effect:'nausea',ticks:row.id.endsWith('mysterious_skewer')?100:60});
  if(row.id==='kaleidoscope_grilling:dark_grilling')effects.push({kind:'native',effect:'blindness',ticks:200});
  if(row.id==='kaleidoscope_grilling:sichuan_pepper')effects.push({kind:'persistent_fx',effect:'numb',ticks:200});
 }
 if(registered)effects.push(...registered.effects);
 return {effects,convertTo:registered?.convertTo||row.convertTo||vanilla?.convertTo||'',
  clearPoison:registered?.clearPoison??(row.id==='minecraft:honey_bottle'),
  teleport:registered?.teleport??(row.id==='minecraft:chorus_fruit'),
  ordinary:registered?.ordinary??(row.id==='kaleidoscope_grilling:ordinary_skewer')};
}

export function rolledIngredientEffects(row,random=Math.random){
 const behavior=ingredientBehavior(row);
 return {...behavior,effects:behavior.effects.filter(e=>(e.chance??1)>=1||random()<(e.chance??1))};
}
