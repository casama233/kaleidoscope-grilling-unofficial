const ITEM_ID=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
export const SKEWER_COMPAT_REGISTER_EVENT='kaleidoscope_grilling:register_skewer_compat';
export const SKEWERABLE_TAG='kaleidoscope_grilling:skewerable_ingredients';
export const UNSKEWERABLE_TAG='kaleidoscope_grilling:unskewerable_ingredients';
export const RAW_SKEWER_TAG='kaleidoscope_grilling:raw_skewers';
export const GRILLED_SKEWER_TAG='kaleidoscope_grilling:grilled_skewers';

let ingredientRules=[];
const cooking=new Map();

function validId(value){return typeof value==='string'&&ITEM_ID.test(value)}
function tags(identity){return Array.isArray(identity?.tags)?identity.tags.filter(validId):[]}
function matches(rule,identity){
 if(rule.input)return identity?.id===rule.input;
 return tags(identity).includes(rule.tag);
}
export function registerSkewerIngredientRule(rule){
 if(!rule||typeof rule!=='object')return false;
 const input=validId(rule.input)?rule.input:'',tag=validId(rule.tag)?rule.tag:'',decision=String(rule.decision??'');
 if((!input&&!tag)||(input&&tag)||!['allow','deny'].includes(decision))return false;
 ingredientRules.push({input,tag,decision});return true;
}
export function registerSkewerCookingRule(rule,{replace=true}={}){
 if(!rule||!validId(rule.input)||!validId(rule.output))return false;
 if(!replace&&cooking.has(rule.input))return false;
 cooking.set(rule.input,rule.output);return true;
}
export function registerSkewerCompatBundle(payload){
 const result={ingredientRules:0,cooking:0};
 if(!payload||typeof payload!=='object')return result;
 for(const rule of Array.isArray(payload.ingredientRules)?payload.ingredientRules:[])
  if(registerSkewerIngredientRule(rule))result.ingredientRules++;
 for(const rule of Array.isArray(payload.cooking)?payload.cooking:[])
  if(registerSkewerCookingRule(rule))result.cooking++;
 return result;
}
export function skewerIngredientDecision(identity){
 const itemTags=tags(identity);
 // Java checks the UNSKEWERABLE tag before registered rules.
 if(itemTags.includes(UNSKEWERABLE_TAG))return 'deny';
 for(const rule of ingredientRules)if(matches(rule,identity))return rule.decision;
 if(itemTags.includes(SKEWERABLE_TAG))return 'allow';
 return 'pass';
}
export function customSkewerCookedId(identity){
 const id=typeof identity==='string'?identity:String(identity?.id??'');
 return cooking.get(id)??'';
}
export function isCompatRawSkewer(identity){
 const id=typeof identity==='string'?identity:String(identity?.id??'');
 return tags(typeof identity==='string'?{}:identity).includes(RAW_SKEWER_TAG)||cooking.has(id);
}
export function isCompatGrilledSkewer(identity){
 return tags(identity).includes(GRILLED_SKEWER_TAG);
}
export function resetSkewerCompatRegistry(){ingredientRules=[];cooking.clear()}
export function skewerCompatSnapshot(){return {ingredientRules:ingredientRules.map(x=>({...x})),cooking:Object.fromEntries(cooking)}}
