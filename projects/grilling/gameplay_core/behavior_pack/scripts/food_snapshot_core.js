import {VANILLA_FOOD_NUTRITION} from './vanilla_food_nutrition.js';
// ItemFoodComponent is only exposed for data-driven foods. Native vanilla foods
// use the pinned Mojang definition fallback, never an invented tag-derived value.
export function foodFacts(stack){
 const food=stack?.getComponent('minecraft:food');
 if(food)return {edible:true,nutrition:Number(food.nutrition)||0,saturation:Number(food.saturationModifier)||0,convertTo:String(food.usingConvertsTo??'')};
 const known=VANILLA_FOOD_NUTRITION[stack?.typeId];
 return known?{...known,edible:true}:{edible:false,nutrition:0,saturation:0,convertTo:''};
}
export function ingredientFoodFacts(row){
 // Repair old snapshots captured before vanilla foods were queryable. Explicit
 // data-driven food snapshots remain authoritative, including zero-nutrition food.
 const known=!row?.edible&&row?.nutrition===0?VANILLA_FOOD_NUTRITION[row?.id]:undefined;
 return known?{...row,...known,edible:true}:row??{};
}
