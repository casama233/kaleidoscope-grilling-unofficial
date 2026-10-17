// Cross-addon compatibility registry for Java SecretSkewerItem parity.
// Bedrock stable cannot query another pack's recipe manager at runtime, so the
// port keeps the Java 1.1.1 built-ins here and exposes item/tag registrations.
import {canonicalFoodId} from './eating_profile_ids.js';
const ITEM_ID=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
const EFFECT_ID=/^[a-z0-9_.:/-]+$/;

export const DEFAULT_SECRET_SMOKING_ITEMS=Object.freeze({
 'minecraft:beef':'minecraft:cooked_beef',
 'minecraft:porkchop':'minecraft:cooked_porkchop',
 'minecraft:chicken':'minecraft:cooked_chicken',
 'minecraft:mutton':'minecraft:cooked_mutton',
 'minecraft:rabbit':'minecraft:cooked_rabbit',
 'minecraft:cod':'minecraft:cooked_cod',
 'minecraft:salmon':'minecraft:cooked_salmon',
 'minecraft:potato':'minecraft:baked_potato',
 'minecraft:kelp':'minecraft:dried_kelp',
 'kaleidoscope_grilling:chicken_wing':'kaleidoscope_grilling:roasted_chicken_wing',
 'kaleidoscope_grilling:sweet_potato':'kaleidoscope_grilling:roasted_sweet_potato'
});
export const DEFAULT_SECRET_SMOKING_TAGS=Object.freeze({
 'kaleidoscope_grilling:ingredients/chicken_wings':'kaleidoscope_grilling:roasted_chicken_wing',
 'kaleidoscope_grilling:ingredients/sweet_potatoes':'kaleidoscope_grilling:roasted_sweet_potato'
});

const smokingItems=new Map();
const smokingTags=new Map();
const behaviorItems=new Map();
const behaviorTags=new Map();

function validId(value){return typeof value==='string'&&ITEM_ID.test(value)}
function primitiveProps(value){
 const out={};if(!value||typeof value!=='object'||Array.isArray(value))return out;
 for(const [key,v] of Object.entries(value)){
  if(typeof key!=='string'||!key||key.length>128)continue;
  if(typeof v==='string'||typeof v==='number'||typeof v==='boolean')out[key]=v;
  else if(v&&typeof v==='object'&&!Array.isArray(v)&&Number.isFinite(v.x)&&Number.isFinite(v.y)&&Number.isFinite(v.z))
   out[key]={x:Number(v.x),y:Number(v.y),z:Number(v.z)};
 }
 return out;
}
function cleanEffect(raw){
 if(!raw||typeof raw!=='object')return null;
 const effect=String(raw.effect??'');
 if(!effect||!EFFECT_ID.test(effect))return null;
 const requestedTicks=Math.trunc(Number(raw.ticks)||0);if(requestedTicks<=0)return null;
 const ticks=Math.min(1728000,requestedTicks);
 return {
  kind:raw.kind==='persistent_fx'?'persistent_fx':'native',
  effect,ticks,
  amplifier:Math.max(0,Math.min(255,Math.trunc(Number(raw.amplifier)||0))),
  chance:Math.max(0,Math.min(1,Number.isFinite(Number(raw.chance))?Number(raw.chance):1)),
  ...(raw.options&&typeof raw.options==='object'&&!Array.isArray(raw.options)?{options:{...raw.options}}:{})
 };
}
function cleanRemainder(raw,convertTo=''){
 const value=raw??(validId(convertTo)?{id:convertTo,count:1}:null);
 if(typeof value==='string')return validId(value)?{id:value,count:1}:null;
 if(!value||typeof value!=='object'||!validId(value.id))return null;
 const count=Math.max(1,Math.min(64,Math.trunc(Number(value.count)||1)));
 const lore=Array.isArray(value.lore)?value.lore.filter(x=>typeof x==='string').slice(0,32):[];
 const name=typeof value.name==='string'?value.name.slice(0,256):'';
 const props=primitiveProps(value.props);
 return {id:value.id,count,...(name?{name}:{}),...(lore.length?{lore}:{}),...(Object.keys(props).length?{props}:{})};
}
function cleanBehavior(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw))return null;
 const effects=(Array.isArray(raw.effects)?raw.effects:[]).map(cleanEffect).filter(Boolean).slice(0,32);
 const convertTo=validId(raw.convertTo)?raw.convertTo:'';
 const remainder=cleanRemainder(raw.remainder,convertTo);
 return {
  mode:raw.mode==='replace'?'replace':'merge',
  effects,convertTo,remainder,
  remainders:(Array.isArray(raw.remainders)?raw.remainders:[]).map(x=>cleanRemainder(x)).filter(Boolean).slice(0,8),
  damage:Number.isFinite(raw.damage)?Math.max(0,Math.min(20,raw.damage)):0,
  clearPoison:!!raw.clearPoison,
  teleport:!!raw.teleport,
  ordinary:!!raw.ordinary
 };
}
function rowId(row){return typeof row==='string'?row:String(row?.id??'')}
function rowTags(row){return Array.isArray(row?.tags)?row.tags.filter(validId).slice(0,64):[]}
function extensionFor(row){
 const id=rowId(row);
 if(behaviorItems.has(id))return behaviorItems.get(id);
 const canonical=canonicalFoodId(id);
 if(canonical!==id&&behaviorItems.has(canonical))return behaviorItems.get(canonical);
 for(const tag of rowTags(row))if(behaviorTags.has(tag))return behaviorTags.get(tag);
 return null;
}
function resetBuiltins(){
 smokingItems.clear();smokingTags.clear();behaviorItems.clear();behaviorTags.clear();
 for(const [input,output] of Object.entries(DEFAULT_SECRET_SMOKING_ITEMS))smokingItems.set(input,output);
 for(const [tag,output] of Object.entries(DEFAULT_SECRET_SMOKING_TAGS))smokingTags.set(tag,output);
}
resetBuiltins();

export function registerSecretSmoking(rule,{replace=true}={}){
 if(!rule||typeof rule!=='object'||!validId(rule.output))return false;
 const input=validId(rule.input)?rule.input:'',tag=validId(rule.tag)?rule.tag:'';
 if(!input&&!tag||input&&tag)return false;
 const map=input?smokingItems:smokingTags,key=input||tag;
 if(!replace&&map.has(key))return false;
 map.set(key,rule.output);return true;
}
export function resolveSecretSmokedId(row){
 const id=rowId(row);
 if(smokingItems.has(id))return smokingItems.get(id);
 for(const tag of rowTags(row))if(smokingTags.has(tag))return smokingTags.get(tag);
 return '';
}
export function registerSecretIngredientBehavior(rule,{replace=true}={}){
 if(!rule||typeof rule!=='object')return false;
 const input=validId(rule.input)?rule.input:'',tag=validId(rule.tag)?rule.tag:'';
 if(!input&&!tag||input&&tag)return false;
 const behavior=cleanBehavior(rule.behavior??rule);if(!behavior)return false;
 const map=input?behaviorItems:behaviorTags,key=input||tag;
 if(!replace&&map.has(key))return false;
 map.set(key,behavior);return true;
}
export function applySecretBehaviorExtension(base,row){
 const ext=extensionFor(row);if(!ext)return base;
 const seed=ext.mode==='replace'?{effects:[],convertTo:'',remainder:null,clearPoison:false,teleport:false,ordinary:false}:base;
 const convertTo=ext.convertTo||seed.convertTo||'';
 const remainder=ext.remainder??seed.remainder??(convertTo?{id:convertTo,count:1}:null);
 return {
  ...seed,
  effects:ext.mode==='replace'?[...ext.effects]:[...(seed.effects??[]),...ext.effects],
  remainders:ext.mode==='replace'?[...ext.remainders]:[...(seed.remainders??[]),...ext.remainders],
  damage:ext.mode==='replace'?ext.damage:Math.max(seed.damage??0,ext.damage),
  convertTo,remainder,
  clearPoison:ext.mode==='replace'?ext.clearPoison:!!seed.clearPoison||ext.clearPoison,
  teleport:ext.mode==='replace'?ext.teleport:!!seed.teleport||ext.teleport,
  ordinary:ext.mode==='replace'?ext.ordinary:!!seed.ordinary||ext.ordinary
 };
}
export function registerSecretCompatBundle(payload){
 const result={smoking:0,behaviors:0};
 if(!payload||typeof payload!=='object')return result;
 for(const rule of Array.isArray(payload.smoking)?payload.smoking:[])if(registerSecretSmoking(rule))result.smoking++;
 for(const rule of Array.isArray(payload.behaviors)?payload.behaviors:[])if(registerSecretIngredientBehavior(rule))result.behaviors++;
 return result;
}
export function secretCompatSnapshot(){
 return {
  smokingItems:Object.fromEntries(smokingItems),
  smokingTags:Object.fromEntries(smokingTags),
  behaviorItems:[...behaviorItems.keys()],
  behaviorTags:[...behaviorTags.keys()]
 };
}
export function resetSecretCompatRegistry(){resetBuiltins()}

export function secretIngredientRegistration(row){const value=extensionFor(row);return value?JSON.parse(JSON.stringify(value)):undefined;}
