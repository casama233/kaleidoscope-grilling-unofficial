/** Cookery 1.6.0 quality. Java source pins and native-food adaptation are in
 * docs/evidence/cuisine-quality-native-food-20261009.md. No world/player writes. */
const RESOURCE_ID=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
const LONG_MIN=-(1n<<63n),LONG_MAX=(1n<<63n)-1n;
const RANDOM_MULTIPLIER=0x5deece66dn,RANDOM_MASK=(1n<<48n)-1n;
export const CUISINE_QUALITIES=Object.freeze([
 Object.freeze({id:0,name:'superb',score:.95,ratio:1.2}),
 Object.freeze({id:1,name:'excellent',score:.82,ratio:.9}),
 Object.freeze({id:2,name:'standard',score:.55,ratio:.6}),
 Object.freeze({id:3,name:'poor',score:0,ratio:.3})
]);
export function validCuisineQuality(value){return Number.isInteger(value)&&value>=0&&value<=3;}
export function javaStringHash(value){
 if(typeof value!=='string')throw Error('Java string hash input');
 let hash=0;for(let i=0;i<value.length;i++)hash=(Math.imul(hash,31)+value.charCodeAt(i))|0;
 return hash;
}
export function javaResourceLocationHash(id){
 if(typeof id!=='string'||!RESOURCE_ID.test(id))throw Error('Java resource location');
 const split=id.indexOf(':');return (Math.imul(javaStringHash(id.slice(0,split)),31)+javaStringHash(id.slice(split+1)))|0;
}
export function cuisineRecipeSeed(worldSeed,recipeId){
 // World.seed is a signed decimal string. Never round it through Number or
 // replace a failed read with another world's zero seed.
 if(typeof worldSeed!=='string'||!/^[-]?\d{1,19}$/.test(worldSeed))throw Error('Java world seed unreadable');
 const seed=BigInt(worldSeed);if(seed<LONG_MIN||seed>LONG_MAX)throw Error('Java world seed range');
 return BigInt.asIntN(64,seed*31n+BigInt(javaResourceLocationHash(recipeId)));
}
export function javaRandom(seed){
 if(typeof seed!=='bigint')throw Error('Java random seed');
 let state=(BigInt.asIntN(64,seed)^RANDOM_MULTIPLIER)&RANDOM_MASK;
 const next31=()=>{state=(state*RANDOM_MULTIPLIER+11n)&RANDOM_MASK;return Number(state>>17n);};
 return Object.freeze({nextInt(bound){
  if(!Number.isInteger(bound)||bound<1||bound>2147483647)throw Error('Java random bound');
  if((bound&-bound)===bound)return Number((BigInt(bound)*BigInt(next31()))>>31n);
  // Java's signed int overflow rejects the incomplete high interval.
  let bits,value;do{bits=next31();value=bits%bound;}while(bits-value+bound-1>2147483647);
  return value;
 }});
}
export function cuisineRecipeRatios(worldSeed,recipeId,size){
 if(!Number.isInteger(size)||size<2||size>9)throw Error('Cuisine ingredient count');
 const random=javaRandom(cuisineRecipeSeed(worldSeed,recipeId)),values=[];
 if(size===2)values.push(2+random.nextInt(3),1+random.nextInt(2));
 else if(size===3)values.push(2+random.nextInt(3),1+random.nextInt(3),1+random.nextInt(2));
 else for(let i=0;i<size;i++)values.push(1+random.nextInt(2));
 // Collections.shuffle uses the same RNG after all ratio draws.
 for(let sizeLeft=values.length;sizeLeft>1;sizeLeft--){const selected=random.nextInt(sizeLeft),last=sizeLeft-1;[values[last],values[selected]]=[values[selected],values[last]];}
 return values;
}
export function evaluateCuisineQuality({worldSeed,recipeId,ingredients,inputs}={}){
 try{
  if(!Array.isArray(inputs)||inputs.length!==9||inputs.some(id=>typeof id!=='string'||id!==''&&!RESOURCE_ID.test(id)))return undefined;
  if(!Array.isArray(ingredients)||ingredients.length>9||ingredients.some(slot=>!Array.isArray(slot)||slot.length>256||slot.some(id=>typeof id!=='string'||!RESOURCE_ID.test(id))))return undefined;
  const seed=cuisineRecipeSeed(worldSeed,recipeId),nonEmpty=ingredients.filter(slot=>slot.length);
  if(!nonEmpty.length)return 3;
  if(nonEmpty.length===1){
   const random=javaRandom(seed),count=inputs.length;
   if(count<=1)return 3;
   if(count<=1+random.nextInt(2))return 2;
   if(count<=2+random.nextInt(2))return 1;
   return 0;
  }
  const ratios=cuisineRecipeRatios(worldSeed,recipeId,nonEmpty.length);
  let dot=0,normInput=0,normRecipe=0;
  for(let i=0;i<nonEmpty.length;i++){
   const count=inputs.reduce((sum,id)=>sum+(nonEmpty[i].includes(id)?1:0),0),ratio=ratios[i];
   dot+=count*ratio;normInput+=count*count;normRecipe+=ratio*ratio;
  }
  const cosine=dot/(Math.sqrt(normInput)*Math.sqrt(normRecipe));
  // The native pot passes a nine-slot list INCLUDING empty slots. Its quantity
  // factor is 1, even for only two or three occupied slots.
  const score=Math.max(0,Math.min(1,Math.pow(cosine,4)*(0.8+0.2*(inputs.length/9))));
  return CUISINE_QUALITIES.find(quality=>score>=quality.score)?.id??2;
 }catch{return undefined;}
}

// Only these three authored flex dishes acquire quality. Exact recipes retain
// their existing item IDs and base food components, without implicit STANDARD.
const BASE_FOODS=Object.freeze({
 'kaleidoscope_grilling:houttuynia_stir_fried_pork':Object.freeze({nutrition:9,saturation:.7}),
 'kaleidoscope_grilling:green_pepper_squid_tentacles':Object.freeze({nutrition:8,saturation:.6}),
 'kaleidoscope_grilling:braised_chicken_wings':Object.freeze({nutrition:10,saturation:.8})
});
export const CUISINE_QUALITY_BASE_IDS=Object.freeze(Object.keys(BASE_FOODS));
const VARIANTS=new Map(CUISINE_QUALITY_BASE_IDS.flatMap(base=>CUISINE_QUALITIES.map(({id})=>[base+'_cuisine_q'+id,{base,quality:id}])));
export function canonicalCuisineFoodId(id){return VARIANTS.get(id)?.base??id;}
export function cuisineQualityOfItem(id){return VARIANTS.get(id)?.quality;}
export function isQualityCuisineFood(id){return Object.hasOwn(BASE_FOODS,canonicalCuisineFoodId(id));}
export function cuisineQualityItemId(id,quality){
 const base=canonicalCuisineFoodId(id);
 if(!Object.hasOwn(BASE_FOODS,base)||quality!==undefined&&!validCuisineQuality(quality))return undefined;
 return quality===undefined?base:base+'_cuisine_q'+quality;
}
export function cuisineQualityPayloadMatches(id,portable){
 if(!isQualityCuisineFood(id))return true;
 if(portable?.present&&!portable.valid)return false;
 const quality=cuisineQualityOfItem(id);
 return quality===undefined?portable?.state?.quality===undefined:portable?.valid===true&&portable.state.quality===quality;
}
export function cuisineQualityFoodSpec(id,quality=cuisineQualityOfItem(id)){
 const raw=BASE_FOODS[canonicalCuisineFoodId(id)];if(!raw||!validCuisineQuality(quality))return undefined;
 const ratio=CUISINE_QUALITIES[quality].ratio,nutrition=Math.round(ratio*raw.nutrition);
 // NeoForge 1.21.1 scales FoodProperties.saturation() itself. Recomputing from
 // the new nutrition and a scaled Forge modifier would multiply twice.
 const baseGain=Math.fround(Math.fround(raw.nutrition*Math.fround(raw.saturation))*2);
 const saturationGain=Math.fround(Math.fround(ratio)*baseGain);
 return {nutrition,saturation:Math.fround(saturationGain/(2*nutrition)),saturationGain,quality};
}
