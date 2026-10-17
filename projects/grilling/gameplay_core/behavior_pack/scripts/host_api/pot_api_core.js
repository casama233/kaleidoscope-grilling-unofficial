/** Source-bounded Java pot matching and saved phase transitions. No native I/O. */
export const JAVA_POT_VERSION=1;
export const JAVA_POT_PREPARATION_TICKS=1200;
export const JAVA_POT_FINISHED_TICKS=800;
export const JAVA_POT_BURNT_TICKS=400;
export const JAVA_POT_SUSPICIOUS='kaleidoscope_cookery:suspicious_stir_fry';
export const JAVA_POT_DARK='kaleidoscope_cookery:dark_cuisine';
const ITEM=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
const copy=value=>JSON.parse(JSON.stringify(value));
const integer=(value,min,max)=>Number.isSafeInteger(value)&&value>=min&&value<=max;
export function paddedPotInputs(items){
 if(!Array.isArray(items)||items.length>9||items.some(id=>typeof id!=='string'||!ITEM.test(id)))return undefined;
 return [...items,...Array(9-items.length).fill('')];
}
export function potIngredientSlots(recipe){
 const raw=recipe?.ingredientSlots??recipe?.ingredients;
 if(!Array.isArray(raw)||!raw.length||raw.length>9)return undefined;
 const slots=raw.map(slot=>Array.isArray(slot)?[...slot]:[slot]);
 if(slots.some(slot=>slot.some(id=>typeof id!=='string'||!ITEM.test(id))))return undefined;
 return [...slots,...Array.from({length:9-slots.length},()=>[])];
}
/** Forge/NeoForge require a complete one-to-one assignment, including empties. */
export function matchesJavaPot(items,recipe,{flex=false}={}){
 if(!Array.isArray(items))return false;
 const values=flex?[...new Set(items)]:items,inputs=paddedPotInputs(values),slots=potIngredientSlots(recipe);
 if(!inputs||!slots)return false;
 const candidates=slots.map(slot=>inputs.map((id,i)=>(slot.length?slot.includes(id):id==='')?i:-1).filter(i=>i>=0));
 if(candidates.some(row=>!row.length))return false;
 candidates.sort((a,b)=>a.length-b.length);
 function visit(index,used){
  if(index===9)return true;
  for(const slot of candidates[index])if(!(used&(1<<slot))&&visit(index+1,used|(1<<slot)))return true;
  return false;
 }
 return visit(0,0);
}
export function selectJavaPotRecipe(items,exactRecipes,flexRecipes,hostRecipes=[]){
 if(!paddedPotInputs(items)||!items.length)return undefined;
 const hostExact=hostRecipes.find(recipe=>matchesJavaPot(items,recipe));
 if(hostExact){
  const own=exactRecipes.find(recipe=>recipe.id===hostExact.id&&recipe.result===hostExact.result&&matchesJavaPot(items,recipe));
  if(!own)return {kind:'legacy',recipe:copy(hostExact)};
  return {kind:'exact',recipe:copy(own)};
 }
 // The caller supplies only recipes acknowledged in the actual host registry.
 const flex=flexRecipes.find(recipe=>matchesJavaPot(items,recipe,{flex:true}));
 if(flex)return {kind:'flex',recipe:copy(flex)};
 return undefined;
}
export function newJavaPot(epoch){
 if(!integer(epoch,1,Number.MAX_SAFE_INTEGER))throw Error('Java pot epoch');
 return {version:JAVA_POT_VERSION,epoch,revision:0,phase:'preparing',ticksRemaining:JAVA_POT_PREPARATION_TICKS,stirsRemaining:0};
}
export function readJavaPot(data){
 const p=data?.grillingPot;if(p===undefined)return undefined;
 const limits={preparing:1200,cooking:200,finished:800,burnt:400,charcoal:0};
 if(!p||typeof p!=='object'||Array.isArray(p)||p.version!==JAVA_POT_VERSION
  ||!integer(p.epoch,1,Number.MAX_SAFE_INTEGER)||p.epoch!==data.grillingOutputEpoch
  ||!integer(p.revision,0,Number.MAX_SAFE_INTEGER)||!Object.hasOwn(limits,p.phase)
  ||!integer(p.ticksRemaining,0,limits[p.phase])||!integer(p.stirsRemaining,0,3)||!paddedPotInputs(data.items??[])
  ||data.oil!==true&&p.phase!=='charcoal')throw Error('Java pot saved state invalid');
 if(p.phase==='preparing'){
  if(p.stirsRemaining!==0||p.output!==undefined||p.quality!==undefined||data.result||data.burnt)throw Error('Java pot preparation conflict');
 }else{
  if(!data.items?.length||!['exact','flex','suspicious'].includes(p.recipeKind)||typeof p.recipeId!=='string'
   ||!p.output||typeof p.output.id!=='string'||!ITEM.test(p.output.id)||p.output.count!==1||p.output.carrier!=='minecraft:bowl')throw Error('Java pot result conflict');
  if(p.quality!==undefined&&(!integer(p.quality,0,3)||p.recipeKind!=='flex'||!['cooking','finished'].includes(p.phase)))throw Error('Java pot quality conflict');
  if(p.recipeKind==='flex'&&['cooking','finished'].includes(p.phase)&&p.quality===undefined)throw Error('Java pot quality missing');
  if(p.phase==='cooking'&&(data.result||data.burnt))throw Error('Java pot cooking output conflict');
  if(['finished','burnt'].includes(p.phase)&&JSON.stringify(data.result)!==JSON.stringify(p.output))throw Error('Java pot ready output conflict');
  if(p.phase==='charcoal'&&(data.result||data.burnt!==true||!integer(data.charcoalCount,1,3)))throw Error('Java pot charcoal conflict');
 }
 return p;
}
export function reviseJavaPot(data){
 const next=copy(data),p=readJavaPot(next);if(!p)throw Error('Java pot missing');
 if(p.revision===Number.MAX_SAFE_INTEGER)throw Error('Java pot revision exhausted');p.revision++;
 return next;
}
export function startJavaPot(data,selection,quality){
 const next=reviseJavaPot(data),p=next.grillingPot;if(p.phase!=='preparing'||!next.items?.length)throw Error('Java pot start phase');
 const recipe=selection?.recipe,kind=selection?.kind??'suspicious';
 if(!['exact','flex','suspicious'].includes(kind))throw Error('Java pot unknown recipe route');
 if(kind!=='suspicious'&&(!recipe||recipe.count!==1||recipe.carrier!=='minecraft:bowl'||recipe.time!==200||recipe.stirs!==3))throw Error('Java pot source recipe contract');
 if(kind==='flex'&&!integer(quality,0,3))throw Error('Java pot quality unavailable');
 p.phase='cooking';p.ticksRemaining=200;p.stirsRemaining=kind==='suspicious'?0:3;
 p.recipeKind=kind;p.recipeId=recipe?.javaId??recipe?.id??'kaleidoscope_cookery:unmatched_pot';
 p.output={id:recipe?.result??JAVA_POT_SUSPICIOUS,count:1,carrier:'minecraft:bowl'};
 if(kind==='flex')p.quality=quality;else delete p.quality;
 next.started=true;next.oilTicks=0;next.progress=0;next.stirs=0;
 return next;
}
export function stirJavaPot(data){
 const next=reviseJavaPot(data),p=next.grillingPot;
 if(p.phase==='preparing')return next;
 if(p.phase==='cooking'&&p.stirsRemaining>0)p.stirsRemaining--;
 next.stirs=p.recipeKind==='suspicious'?0:3-p.stirsRemaining;
 return next;
}
/** One loaded, heated block tick; no catch-up for unloaded or unheated time. */
export function advanceJavaPot(data){
 const next=reviseJavaPot(data),p=next.grillingPot;
 if(p.phase==='charcoal')return {data:next,action:'charcoal'};
 if(p.ticksRemaining>0)p.ticksRemaining--;
 if(p.phase==='preparing')next.oilTicks=p.ticksRemaining;
 if(p.ticksRemaining>0)return {data:next};
 if(p.phase==='preparing')return {data:next,action:next.items?.length?'start':'reset'};
 if(p.phase==='cooking'){
  if(p.stirsRemaining>0){p.output={id:JAVA_POT_SUSPICIOUS,count:1,carrier:'minecraft:bowl'};p.recipeKind='suspicious';delete p.quality;}
  p.phase='finished';p.ticksRemaining=JAVA_POT_FINISHED_TICKS;next.result=copy(p.output);next.started=false;
  return {data:next,action:'finished'};
 }
 if(p.phase==='finished'){
  p.phase='burnt';p.ticksRemaining=JAVA_POT_BURNT_TICKS;p.output={id:JAVA_POT_DARK,count:1,carrier:'minecraft:bowl'};delete p.quality;
  next.result=copy(p.output);return {data:next,action:'burnt'};
 }
 return {data:next,action:'burnout'};
}
