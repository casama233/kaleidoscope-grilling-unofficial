import {SECRET_ID,recipeTable} from './a24_skewering_core.js';

export const PLATE_ITEM_ID='kaleidoscope_grilling:skewer_plate';
export const PLATE_BLOCK_ID='kaleidoscope_grilling:skewer_plate_block';
export const RECIPE_BOOK_ID='kaleidoscope_grilling:skewer_recipe_book';
export const RECIPE_BLOCK_ID='kaleidoscope_grilling:skewer_recipe';
export const COOKERY_RECIPE_ITEM_ID='kaleidoscope_cookery:recipe_item';
export const PLATE_CAPACITY=5;
export const PLATE_CONTENTS_KEY='kaleidoscope_grilling:plate_skewers';
export const BOOK_RESULT_KEY='kaleidoscope_grilling:recipe_result';
export const BOOK_STACK_KEY='kaleidoscope_grilling:recipe_stack';

const RECIPES=recipeTable();
const RAW_IDS=new Set(RECIPES.map(x=>x.id));
const COOKED_IDS=new Set(RECIPES.map(x=>x.cooked).filter(Boolean));
const EXTRA_PLATE_IDS=new Set([
  SECRET_ID,
  'kaleidoscope_grilling:mysterious_skewer',
  'kaleidoscope_grilling:dark_grilling'
]);

export function isPlateSkewerId(id){
  return RAW_IDS.has(id)||COOKED_IDS.has(id)||EXTRA_PLATE_IDS.has(id);
}
export function isRecordableSkewer(id,ingredientRows=[]){
  if(id===SECRET_ID)return Array.isArray(ingredientRows)&&ingredientRows.length===3;
  return RAW_IDS.has(id);
}
export function addToPlate(rows,stack){
  const list=Array.isArray(rows)?rows.slice(0,PLATE_CAPACITY):[];
  if(list.length>=PLATE_CAPACITY||!stack||!isPlateSkewerId(stack.id))return {ok:false,rows:list};
  return {ok:true,rows:[...list,stack]};
}
export function removeLastFromPlate(rows){
  const list=Array.isArray(rows)?rows.slice(0,PLATE_CAPACITY):[];
  if(!list.length)return {ok:false,rows:list,stack:null};
  return {ok:true,rows:list.slice(0,-1),stack:list[list.length-1]};
}
export function plateCount(rows){return Math.min(PLATE_CAPACITY,Array.isArray(rows)?rows.length:0)}
export function highestNutritionIndex(rows,nutrition){
  let selected=-1,best=-Infinity;
  for(let i=0;i<(rows?.length??0);i++){
    const value=Number(nutrition(rows[i],i));
    if(Number.isFinite(value)&&value>best){best=value;selected=i}
  }
  return selected;
}
export function takeHighestNutrition(rows,nutrition){
  const list=Array.isArray(rows)?rows.slice(0,PLATE_CAPACITY):[],index=highestNutritionIndex(list,nutrition);
  if(index<0)return {ok:false,rows:list,stack:null,index:-1};
  const stack=list[index],next=[...list.slice(0,index),...list.slice(index+1)];
  return {ok:true,rows:next,stack,index};
}
export function recordBook(stack){
  if(!stack||!isRecordableSkewer(stack.id,stack.ingredients))return null;
  return {
    resultId:stack.id,
    stack:stack.id===SECRET_ID?JSON.parse(JSON.stringify(stack)):null
  };
}
export function clearBook(){return {resultId:'',stack:null}}
export function bookIngredients(book){
  if(!book||typeof book.resultId!=='string'||!book.resultId)return null;
  if(book.resultId===SECRET_ID){
    const rows=book.stack?.ingredients;
    return Array.isArray(rows)&&rows.length===3?rows.map(x=>[x.id]):null;
  }
  const recipe=RECIPES.find(x=>x.id===book.resultId);
  return recipe?recipe.slots.map(x=>[...x]):null;
}
export function planBookCraft(book,inventory){
  const ingredients=bookIngredients(book);
  if(!ingredients)return {ok:false,reason:'invalid_recipe',consumption:[],missing:[]};
  const rows=(inventory??[]).map(x=>({
    slot:Number(x.slot),id:String(x.id??''),count:Math.max(0,Number(x.count)||0),skip:!!x.skip
  }));
  const reserved=new Map();
  for(const acceptable of ingredients){
    let found=null;
    for(const row of rows){
      if(row.skip||!acceptable.includes(row.id))continue;
      const used=reserved.get(row.slot)??0;
      if(row.count>used){found=row;reserved.set(row.slot,used+1);break}
    }
    if(!found)return {ok:false,reason:'missing',consumption:[...reserved].map(([slot,count])=>({slot,count})),missing:acceptable};
  }
  return {ok:true,reason:'ok',consumption:[...reserved].map(([slot,count])=>({slot,count})),missing:[]};
}
export function plateLore(rows,label=x=>x.id){
  const list=Array.isArray(rows)?rows.slice(0,PLATE_CAPACITY):[];
  return [
    '§7烤串盤 '+list.length+'/'+PLATE_CAPACITY,
    ...list.map(x=>'§8- '+label(x))
  ];
}
export function bookLore(book,label=x=>x){
  if(!book?.resultId)return ['§8空白烤串配方'];
  const ingredients=bookIngredients(book)??[];
  return [
    '§7已記錄: '+label(book.resultId),
    ...ingredients.map(x=>'§8- '+x.map(label).join(' / '))
  ];
}
