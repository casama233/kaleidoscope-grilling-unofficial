import {ItemStack} from '@minecraft/server';

export const UNFINISHED_ID='kaleidoscope_grilling:unfinished_skewer';
export const SECRET_ID='kaleidoscope_grilling:secret_skewer';
export const INGREDIENTS_KEY='kaleidoscope_grilling:skewer_ingredients';
export const VARIANTS_KEY='kaleidoscope_grilling:model_variants';
export const CREATOR_NAME_KEY='kaleidoscope_grilling:creator_name';
export const CREATOR_UUID_KEY='kaleidoscope_grilling:creator_uuid';
export const SECRET_COOKED_KEY='kaleidoscope_grilling:secret_cooked';

export const SKEWER_RECIPES=Object.freeze([
 {result:'kaleidoscope_grilling:raw_beef_skewer',slots:[['kaleidoscope_grilling:beef_chunks'],['kaleidoscope_cookery:red_chili'],['kaleidoscope_grilling:beef_chunks']]},
 {result:'kaleidoscope_grilling:raw_pork_belly_skewer',slots:[['kaleidoscope_cookery:raw_pork_belly'],['kaleidoscope_cookery:green_chili'],['kaleidoscope_cookery:raw_pork_belly']]},
 {result:'kaleidoscope_grilling:raw_chicken_skin_skewer',slots:[['kaleidoscope_grilling:chicken_skin'],['kaleidoscope_grilling:chicken_skin']]},
 {result:'kaleidoscope_grilling:raw_mid_wing_skewer',slots:[['kaleidoscope_grilling:chicken_wing'],['kaleidoscope_cookery:red_chili'],['kaleidoscope_grilling:chicken_wing']]},
 {result:'kaleidoscope_grilling:raw_squid_tentacle_skewer',slots:[['kaleidoscope_grilling:squid_tentacle'],['kaleidoscope_grilling:squid_tentacle'],['kaleidoscope_grilling:squid_tentacle']]},
 {result:'kaleidoscope_grilling:raw_fish_skewer',slots:[['minecraft:cod','minecraft:salmon','minecraft:tropical_fish','minecraft:pufferfish']]},
 {result:'kaleidoscope_grilling:raw_sweet_potato_sheet_skewer',slots:[['kaleidoscope_grilling:raw_sweet_potato_sheet'],['kaleidoscope_grilling:minced_houttuynia'],['kaleidoscope_grilling:minced_houttuynia']]},
 {result:'kaleidoscope_grilling:raw_potato_slice_skewer',slots:[['kaleidoscope_grilling:potato_slice'],['kaleidoscope_grilling:potato_slice'],['kaleidoscope_grilling:potato_slice']]},
 {result:'kaleidoscope_grilling:raw_caterpillar_skewer',slots:[['kaleidoscope_cookery:caterpillar']]},
 {result:'kaleidoscope_grilling:raw_mushroom_skewer',slots:[['minecraft:brown_mushroom','minecraft:red_mushroom'],['kaleidoscope_grilling:carrot_dice'],['minecraft:brown_mushroom','minecraft:red_mushroom']]},
 {result:'kaleidoscope_grilling:raw_bun_slice_skewer',slots:[['kaleidoscope_grilling:raw_mantou_slice'],['kaleidoscope_grilling:raw_mantou_slice'],['kaleidoscope_grilling:raw_mantou_slice']]},
 {result:'kaleidoscope_grilling:raw_ender_pearl_skewer',slots:[['minecraft:ender_pearl'],['minecraft:beetroot'],['minecraft:ender_pearl']]},
 {result:'kaleidoscope_grilling:raw_meatball_skewer',slots:[['kaleidoscope_cookery:raw_meatball'],['kaleidoscope_cookery:raw_meatball'],['kaleidoscope_cookery:raw_meatball']]},
 {result:'kaleidoscope_grilling:raw_slime_skewer',slots:[['minecraft:slime_ball'],['kaleidoscope_grilling:houttuynia'],['minecraft:slime_ball']]},
 {result:'kaleidoscope_grilling:raw_meat_and_bone_skewer',slots:[['kaleidoscope_cookery:raw_cut_small_meats'],['minecraft:bone'],['kaleidoscope_cookery:raw_cut_small_meats']]},
 {result:'kaleidoscope_grilling:raw_fried_egg_skewer',slots:[['kaleidoscope_cookery:fried_egg'],['kaleidoscope_cookery:fried_egg']]},
 {result:'kaleidoscope_grilling:raw_gluten_skewer',slots:[['kaleidoscope_cookery:raw_dough'],['kaleidoscope_cookery:raw_dough']]},
 {result:'kaleidoscope_grilling:raw_lamb_skewer',slots:[['kaleidoscope_cookery:raw_lamb_chops'],['kaleidoscope_cookery:oil'],['kaleidoscope_cookery:raw_lamb_chops']]},
 {result:'kaleidoscope_grilling:raw_golden_skewer',slots:[['minecraft:golden_apple'],['minecraft:totem_of_undying'],['minecraft:golden_carrot']]},
 {result:'kaleidoscope_grilling:ordinary_skewer',slots:[['minecraft:poisonous_potato'],['minecraft:spider_eye'],['minecraft:pufferfish']]}
]);

const CONFIGURED=new Set(SKEWER_RECIPES.flatMap(r=>r.slots.flat()));
const RAW_FIXED=new Set(SKEWER_RECIPES.map(r=>r.result).filter(x=>x!=='kaleidoscope_grilling:ordinary_skewer'));
const COOKED_FALLBACK=Object.freeze({
 'minecraft:beef':'minecraft:cooked_beef','minecraft:chicken':'minecraft:cooked_chicken',
 'minecraft:porkchop':'minecraft:cooked_porkchop','minecraft:mutton':'minecraft:cooked_mutton',
 'minecraft:rabbit':'minecraft:cooked_rabbit','minecraft:cod':'minecraft:cooked_cod',
 'minecraft:salmon':'minecraft:cooked_salmon','minecraft:potato':'minecraft:baked_potato',
 'minecraft:kelp':'minecraft:dried_kelp','kaleidoscope_grilling:chicken_wing':'kaleidoscope_grilling:roasted_chicken_wing'
});

function parse(raw){if(typeof raw!=='string')return [];try{const v=JSON.parse(raw);return Array.isArray(v)?v.filter(x=>typeof x==='string').slice(0,3):[]}catch{return []}}
function readJson(stack,key){try{return parse(stack?.getDynamicProperty(key))}catch{return []}}
function writeJson(stack,key,value){try{stack.setDynamicProperty(key,JSON.stringify(value))}catch{}}
function prefix(recipe,ids){return ids.length<=recipe.slots.length&&ids.every((id,i)=>recipe.slots[i]?.includes(id))}
function pretty(id){return id.split(':').pop().replaceAll('_',' ')}
function variantList(stack){return readJson(stack,VARIANTS_KEY).map(Number).filter(Number.isFinite).slice(0,3)}
function hasDuplicate(ids){return ids.some((id,i)=>ids.indexOf(id)!==i)}
function setLore(stack,ids,cooked=false){
 try{
  const lore=ids.map((id,i)=>'§7'+(i+1)+'. '+pretty(id));
  if(stack.typeId===UNFINISHED_ID)lore.unshift('§e穿串進度 '+ids.length+'/'+expectedSize(ids));
  if(stack.typeId===SECRET_ID){
   const creator=creatorName(stack);lore.unshift(cooked?'§6秘制烤串 · 已烤熟':'§8秘制烤串 · 生');
   if(creator)lore.push('§8作者：'+creator);
   if(hasDuplicate(ids))lore.push('§8重複食材：營養係數 ×0.8');
  }
  stack.setLore(lore);
 }catch{}
 return stack;
}
export function readIngredients(stack){return readJson(stack,INGREDIENTS_KEY)}
export function creatorName(stack){try{return String(stack?.getDynamicProperty(CREATOR_NAME_KEY)??'')}catch{return ''}}
export function isSecretCooked(stack){try{return stack?.typeId===SECRET_ID&&stack.getDynamicProperty(SECRET_COOKED_KEY)===true}catch{return false}}
export function setSecretCooked(stack,value){
 if(stack?.typeId!==SECRET_ID)return stack;
 try{stack.setDynamicProperty(SECRET_COOKED_KEY,value?true:undefined)}catch{}
 return setLore(stack,readIngredients(stack),!!value);
}
export function isRawFixed(stack){return !!stack&&RAW_FIXED.has(stack.typeId)}
export function canDisassemble(stack){return !!stack&&(stack.typeId===UNFINISHED_ID||isRawFixed(stack)||(stack.typeId===SECRET_ID&&!isSecretCooked(stack)))&&readIngredients(stack).length>0}
export function expectedSize(ids){
 const sizes=SKEWER_RECIPES.filter(r=>prefix(r,ids)).map(r=>r.slots.length);
 return sizes.length?Math.max(...sizes):3;
}
export function fixedResult(ids){
 const r=SKEWER_RECIPES.find(x=>x.slots.length===ids.length&&prefix(x,ids));
 return r?.result??null;
}
export function canAppend(ids,nextId,isEdible=false){
 if(ids.length>=3)return false;
 if(SKEWER_RECIPES.some(r=>prefix(r,ids)&&r.slots.length>ids.length&&r.slots[ids.length].includes(nextId)))return true;
 return CONFIGURED.has(nextId)||!!isEdible;
}
export function createThreaded(target,next,creator='',creatorUuid=''){
 const ids=target?.typeId==='minecraft:stick'?[]:readIngredients(target);
 let edible=false;try{edible=!!next?.getComponent('minecraft:food')}catch{}
 if(!next||!canAppend(ids,next.typeId,edible))return null;
 const outIds=[...ids,next.typeId],fixed=fixedResult(outIds);
 const outId=fixed??(outIds.length>=3?SECRET_ID:UNFINISHED_ID);
 const out=new ItemStack(outId,1);
 writeJson(out,INGREDIENTS_KEY,outIds);
 const variants=target?.typeId==='minecraft:stick'?[]:variantList(target);
 variants.push(4+Math.floor(Math.random()*6));writeJson(out,VARIANTS_KEY,variants);
 if(outId===SECRET_ID){try{if(creator)out.setDynamicProperty(CREATOR_NAME_KEY,creator);if(creatorUuid)out.setDynamicProperty(CREATOR_UUID_KEY,creatorUuid)}catch{}}
 setLore(out,outIds,false);
 return {stack:out,completed:!!fixed||outIds.length>=3,fixed:!!fixed,ingredients:outIds};
}
export function cookSecret(raw){
 if(raw?.typeId!==SECRET_ID)return null;
 const out=raw.clone();out.amount=1;return setSecretCooked(out,true);
}
export function copySkewerProperties(from,to){
 if(!from||!to)return to;
 try{for(const id of from.getDynamicPropertyIds())to.setDynamicProperty(id,from.getDynamicProperty(id))}catch{}
 try{if(from.nameTag)to.nameTag=from.nameTag}catch{}
 try{to.setLore(from.getLore())}catch{}
 return to;
}
export function disassemblyItems(stack){
 const ids=readIngredients(stack);if(!ids.length)return [];
 const out=[];
 for(const id of ids){try{out.push(new ItemStack(id,1))}catch{}}
 out.push(new ItemStack('minecraft:stick',1));return out;
}
function foodComponent(id){
 try{
  const s=new ItemStack(id,1),c=s.getComponent('minecraft:food');if(!c)return null;
  const nutrition=Number(c.nutrition),saturation=Number(c.saturationModifier);
  if(!Number.isFinite(nutrition)||nutrition<=0)return null;
  return {nutrition,saturation:Number.isFinite(saturation)?Math.max(0,saturation):0};
 }catch{return null}
}
function cookedId(id){const mapped=COOKED_FALLBACK[id];if(!mapped)return id;try{new ItemStack(mapped,1);return mapped}catch{return id}}
export function secretFoodStats(stack){
 const raw=readIngredients(stack),cooked=isSecretCooked(stack);
 if(raw.length!==3)return null;
 const rows=raw.map(id=>foodComponent(cooked?cookedId(id):id)).filter(Boolean);
 if(!rows.length)return {nutrition:1,saturation:0};
 const total=rows.reduce((s,x)=>s+x.nutrition,0);
 if(total<=0)return {nutrition:1,saturation:0};
 const weighted=rows.reduce((s,x)=>s+x.nutrition*x.saturation,0);
 const coefficient=.6*(hasDuplicate(raw)?.8:1);
 let nutrition=Math.max(1,Math.floor(total*coefficient)),saturation=Math.max(0,weighted/total);
 if(!cooked){nutrition=Math.max(1,Math.floor(nutrition*.5));saturation*=.5}
 return {nutrition,saturation};
}
export function isThreadTarget(stack){return !!stack&&(stack.typeId==='minecraft:stick'||stack.typeId===UNFINISHED_ID||(stack.typeId===SECRET_ID&&!isSecretCooked(stack)))}
