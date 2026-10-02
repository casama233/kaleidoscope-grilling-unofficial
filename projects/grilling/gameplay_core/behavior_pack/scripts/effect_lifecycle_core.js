/** Java 1.1.1 effects: milk preserves only uncurable heavy-metal poisoning; death clears all. */
export const FX_KEY='kaleidoscope_grilling:a21_fx';
export function activeEffects(value,t){
 const out={};if(!value||typeof value!=='object'||Array.isArray(value))return out;
 for(const [name,v] of Object.entries(value)){
  if(v&&Number.isFinite(Number(v.until))&&Number(v.until)>t)
   out[name]={until:Number(v.until),amp:Math.max(0,Math.floor(Number(v.amp)||0))};
 }
 return out;
}
export function milkEffects(value,t){
 const fx=activeEffects(value,t);
 return fx.heavy_metal_poisoning?{heavy_metal_poisoning:fx.heavy_metal_poisoning}:{};
}
export function effectPayload(value,t){const fx=activeEffects(value,t);return Object.keys(fx).length?JSON.stringify(fx):undefined;}
