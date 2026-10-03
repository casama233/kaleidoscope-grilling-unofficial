/** Public, portable metadata. Producers call this on the actual output before handing it over. */
import {normalizePublicFood,readPublicFood,writePublicFood} from './host_api/food_api_core.js';
import {VANILLA_FOOD_NUTRITION} from './vanilla_food_nutrition.js';
export const PROJECTION_KEY='senluo.public.projection.v1';
export const ITEM_ID=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
export function utf8Bytes(text){let size=0;for(const char of text){const point=char.codePointAt(0);size+=point<128?1:point<2048?2:point<65536?3:4;}return size;}
export function publicStackFingerprint(stack){
 if(!stack)return undefined;
 return {id:stack.typeId,amount:stack.amount,name:stack.nameTag??'',lore:stack.getRawLore()};
}
export function stableJson(value){
 if(Array.isArray(value))return '['+value.map(stableJson).join(',')+']';
 if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stableJson(value[k])).join(',')+'}';
 return JSON.stringify(value);
}
export function samePublicStack(stack,expected){return stableJson(publicStackFingerprint(stack))===stableJson(expected);}
export function normalizeProjection(raw){
 if(!raw||raw.v!==1||!ITEM_ID.test(raw.provider??'')||!Number.isInteger(raw.data)||raw.data<0||raw.data>32767)return undefined;
 return {v:1,provider:raw.provider,data:raw.data};
}
export function readPublicProjection(stack){
 const rows=stack.getRawLore().filter(x=>x&&typeof x==='object'&&x.translate===PROJECTION_KEY);
 if(!rows.length)return {present:false,valid:false};
 if(rows.length!==1||rows[0].with?.length!==1||typeof rows[0].with[0]!=='string')return {present:true,valid:false};
 try{const state=normalizeProjection(JSON.parse(rows[0].with[0]));return {present:true,valid:!!state,state}}catch{return {present:true,valid:false}}
}
export function writePublicProjection(stack,raw){
 const state=normalizeProjection(raw);if(!state)throw Error('projection schema');
 const old=readPublicProjection(stack);if(old.present&&!old.valid)throw Error('projection unreadable');
 const rows=stack.getRawLore().filter(x=>!x||typeof x!=='object'||x.translate!==PROJECTION_KEY);
 if(rows.length>=20)throw Error('projection has no lore space');
 rows.push({translate:PROJECTION_KEY,with:[JSON.stringify(state)]});stack.setLore(rows);
 if(JSON.stringify(readPublicProjection(stack).state)!==JSON.stringify(state))throw Error('projection readback');return stack;
}
export function prepareProducedFood(stack,{kind='cuisine',hotTicks=0,seasoning=[],nativeVariant,projection}={},now,config={}){
 if(!Number.isSafeInteger(now)||now<0||!['cuisine','furnace','smoker'].includes(kind)||!Number.isInteger(hotTicks)||hotTicks<0||hotTicks>1728000)throw Error('production schema');
 if(!stack?.getComponent('minecraft:food')&&!VANILLA_FOOD_NUTRITION[stack?.typeId])throw Error('output is not edible');
 const old=readPublicFood(stack);if(old.present&&!old.valid)throw Error('food metadata unreadable');
 const duration=kind==='cuisine'?hotTicks:config.enableSmeltedFoodHeat===true?(config.smeltedFoodSeconds??30)*20:0;
 const meta=normalizePublicFood({v:1,hotUntil:duration?now+duration:old.state?.hotUntil??0,seasoning,nativeVariant:nativeVariant??old.state?.nativeVariant});
 if(!meta)throw Error('production metadata');
 const output=stack.clone();writePublicFood(output,meta);if(projection)writePublicProjection(output,projection);return output;
}
