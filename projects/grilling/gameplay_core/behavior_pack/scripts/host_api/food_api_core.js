/** Explicit cross-pack output metadata; the empty translated carrier is not display lore. */
export const FOOD_PAYLOAD_KEY='senluo.public.food.v1';
const ID=/^[a-z0-9_.-]+:[a-z0-9_./-]+$/;
export function normalizePublicFood(raw){
 if(!raw||raw.v!==1||!Number.isSafeInteger(raw.hotUntil)||raw.hotUntil<0||!Array.isArray(raw.seasoning)||raw.seasoning.length>8||raw.seasoning.some(x=>typeof x!=='string'||!ID.test(x)))return undefined;
 return {v:1,hotUntil:raw.hotUntil,seasoning:[...raw.seasoning]};
}
export function isFoodPayloadLine(row){return row&&typeof row==='object'&&row.translate===FOOD_PAYLOAD_KEY;}
export function readPublicFood(stack){
 let lines;try{lines=stack?.getRawLore().filter(isFoodPayloadLine)??[]}catch{return {present:true,valid:false}};
 if(!lines.length)return {present:false,valid:false};
 if(lines.length!==1||!Array.isArray(lines[0].with)||lines[0].with.length!==1||typeof lines[0].with[0]!=='string')return {present:true,valid:false};
 try{const state=normalizePublicFood(JSON.parse(lines[0].with[0]));return {present:true,valid:!!state,state}}catch{return {present:true,valid:false}}
}
export function writePublicFood(stack,raw){
 const state=normalizePublicFood(raw);if(!state)throw Error('public food schema');
 const rows=stack.getRawLore().filter(x=>!isFoodPayloadLine(x));if(rows.length>=20)throw Error('public food metadata has no space');
 rows.push({translate:FOOD_PAYLOAD_KEY,with:[JSON.stringify(state)]});stack.setLore(rows);
 const actual=readPublicFood(stack);if(!actual.valid||JSON.stringify(actual.state)!==JSON.stringify(state))throw Error('public food readback');return stack;
}
