/** Test overlay only: real ItemStacks/container/restart, never simulated players. */
import {world,system,ItemStack,EnchantmentType} from '@minecraft/server';
import {a25PlateRows} from './a25_plate_recipe_runtime.js';
import {plateHighestNutritionIndex,bookIngredientSlots,planInventoryConsumption} from './a25_plate_recipe_core.js';
import {VANILLA_FOOD_NUTRITION} from './vanilla_food_nutrition.js';
import {DEFAULT_SECRET_SMOKING_ITEMS,registerSecretSmoking} from './secret_compat_core.js';
import {captureSkewerMetadata,restoreSkewerMetadata,metadataSignature} from './skewer_item_snapshot.js';
import {setItemProperty,getItemProperty,setItemLore} from './itemData.js';
import {ingredientSnapshot,cookedIngredientRows,restoreIngredient} from './main.js';
const check=(ok,label)=>{if(!ok)throw Error(label)},key='kaleidoscope_grilling:qa_parity28',wait=t=>new Promise(r=>system.runTimeout(r,t));
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');try{d.runCommand('tickingarea add circle 0 80 64 2 parity_qa true')}catch{}
 let block;for(let i=0;i<60;i++){await wait(10);try{block=d.getBlock({x:3,y:80,z:64})}catch{}if(block)break}check(block,'chunk unavailable');
 const canonicalFoods=["minecraft:apple", "minecraft:enchanted_golden_apple", "minecraft:baked_potato", "minecraft:beef", "minecraft:beetroot_soup", "minecraft:beetroot", "minecraft:bread", "minecraft:carrot", "minecraft:chicken", "minecraft:chorus_fruit", "minecraft:tropical_fish", "minecraft:cooked_beef", "minecraft:cooked_chicken", "minecraft:cooked_cod", "minecraft:cooked_porkchop", "minecraft:cooked_rabbit", "minecraft:cooked_salmon", "minecraft:cookie", "minecraft:dried_kelp", "minecraft:cod", "minecraft:glow_berries", "minecraft:golden_apple", "minecraft:golden_carrot", "minecraft:honey_bottle", "minecraft:melon_slice", "minecraft:mushroom_stew", "minecraft:cooked_mutton", "minecraft:mutton", "minecraft:poisonous_potato", "minecraft:porkchop", "minecraft:potato", "minecraft:pufferfish", "minecraft:pumpkin_pie", "minecraft:rabbit_stew", "minecraft:rabbit", "minecraft:rotten_flesh", "minecraft:salmon", "minecraft:spider_eye", "minecraft:suspicious_stew", "minecraft:sweet_berries"];
 for(const id of canonicalFoods){const row=ingredientSnapshot(new ItemStack(id),true),expected=VANILLA_FOOD_NUTRITION[id];check(row.edible&&row.nutrition===expected.nutrition&&Math.abs(row.saturation-expected.saturation)<0.000001,'native vanilla food '+id);}
 for(const [input,output] of Object.entries(DEFAULT_SECRET_SMOKING_ITEMS)){const row=cookedIngredientRows([ingredientSnapshot(new ItemStack(input),true)])[0];check(row.id===output&&row.edible,'native smoker '+input);}
 const carrot=ingredientSnapshot(new ItemStack('minecraft:carrot'),true);registerSecretSmoking({input:carrot.id,output:'minecraft:stone'});check(cookedIngredientRows([carrot])[0]===carrot,'nonfood smoker preserves original');
 const tagged=new ItemStack('senra_qa:tagged_wing',2),chili=new ItemStack('kaleidoscope_cookery:red_chili');
 const fixedSlots=bookIngredientSlots({resultId:'kaleidoscope_grilling:raw_mid_wing_skewer'});
 const tagPlan=planInventoryConsumption([tagged,chili].map(s=>({id:s.typeId,count:s.amount,tags:s.getTags()})),fixedSlots);
 check(tagPlan.ok&&tagPlan.plan[0].count===2&&tagPlan.plan[1].count===1,'native tagged substitute fixed book');
 const secretSlots=bookIngredientSlots({resultId:'kaleidoscope_grilling:secret_skewer',customIngredients:['kaleidoscope_grilling:chicken_wing','kaleidoscope_cookery:red_chili','kaleidoscope_grilling:chicken_wing']});
 check(!planInventoryConsumption([tagged,chili].map(s=>({id:s.typeId,count:s.amount,tags:s.getTags()})),secretSlots).ok,'secret book remains exact ID');
 const previous=world.getDynamicProperty(key);
 if(previous===undefined){
  block.setType('minecraft:chest');const c=block.getComponent('minecraft:inventory').container;
  const sword=new ItemStack('minecraft:diamond_sword');sword.nameTag='Parity native';sword.keepOnDeath=true;
  sword.setCanDestroy(['minecraft:stone']);sword.setCanPlaceOn(['minecraft:dirt']);sword.getComponent('minecraft:durability').damage=37;
  sword.getComponent('minecraft:enchantable').addEnchantments([{type:new EnchantmentType('unbreaking'),level:3}]);
  setItemLore(sword,[{translate:'item.apple.name'},{rawtext:[{text:'Native '},{translate:'item.diamond.name'}]}]);setItemProperty(sword,'qa:vector',{x:1,y:2,z:3});
  const rows=[ingredientSnapshot(sword,true),ingredientSnapshot(new ItemStack('minecraft:potato'),true),ingredientSnapshot(new ItemStack('minecraft:beef'),true)];
  for(const row of rows)check(metadataSignature(captureSkewerMetadata(restoreIngredient(row)))===metadataSignature(row.native),'roundtrip before save');
  const skewer=new ItemStack('kaleidoscope_grilling:secret_skewer');setItemProperty(skewer,'kaleidoscope_grilling:skewer_ingredients',JSON.stringify(rows));c.setItem(0,skewer);
  const book=new ItemStack('kaleidoscope_grilling:skewer_recipe_book');setItemProperty(book,'kaleidoscope_grilling:recipe_record',JSON.stringify({resultId:skewer.typeId,customIngredients:rows.map(r=>r.id),recordedStack:{id:skewer.typeId,native:captureSkewerMetadata(skewer)}}));c.setItem(1,book);
  c.setItem(2,new ItemStack('kaleidoscope_grilling:unfinished_skewer'));
  const legacyRaw=['minecraft:apple','minecraft:carrot','minecraft:beef'].map(id=>({id,edible:false,nutrition:0,saturation:0}));
  const props={'kaleidoscope_grilling:skewer_ingredients':JSON.stringify(legacyRaw),'kaleidoscope_grilling:secret_cooked':true,'kaleidoscope_grilling:secret_cooked_ingredients':JSON.stringify(legacyRaw.map((r,i)=>({...r,id:i===2?'minecraft:cooked_beef':r.id})))};
  const oldPlate=new ItemStack('kaleidoscope_grilling:skewer_plate');setItemProperty(oldPlate,'kaleidoscope_grilling:plate_skewers',JSON.stringify([{id:'kaleidoscope_grilling:secret_skewer',nutrition:1,saturation:0,props},{id:'kaleidoscope_grilling:grilled_fish_skewer',nutrition:6,saturation:.6}]));c.setItem(3,oldPlate);
  world.setDynamicProperty(key,JSON.stringify(rows));console.log('PARITY_NATIVE_PASS '+JSON.stringify({stage:'saved',taggedBookPlanning:true,secretBookExactId:true,vanillaFoods:40,smokerMappings:11,nonfoodOutputRejected:true,fullStableMetadata:true,rawTranslatedLore:true,recipeBookSaved:true,simulatedPlayers:false}));
 }else{
  const c=block.getComponent('minecraft:inventory').container,rows=JSON.parse(getItemProperty(c.getItem(0),'kaleidoscope_grilling:skewer_ingredients'));
  check(JSON.stringify(rows)===previous,'ingredient rows survived restart');
  for(const row of rows)check(metadataSignature(captureSkewerMetadata(restoreIngredient(row)))===metadataSignature(row.native),'restore after restart');
  const cooked=cookedIngredientRows(rows);check(cooked[0]===rows[0],'unmapped tool unchanged');check(cooked[1].id==='minecraft:baked_potato'&&cooked[1].edible,'potato smoker');check(cooked[2].id==='minecraft:cooked_beef'&&cooked[2].edible,'beef smoker');
  const record=JSON.parse(getItemProperty(c.getItem(1),'kaleidoscope_grilling:recipe_record'));
  const restored=restoreSkewerMetadata(record.recordedStack.native,(id,n)=>new ItemStack(id,n),id=>new EnchantmentType(id));check(getItemProperty(restored,'kaleidoscope_grilling:skewer_ingredients')===previous,'recipe native snapshot survived restart');
  check(c.getItem(2).typeId==='kaleidoscope_grilling:unfinished_skewer','starter retained');
  const migrated=a25PlateRows(c.getItem(3));check(migrated[0].nutrition===9&&plateHighestNutritionIndex(migrated)===0,'legacy plate cache ranking after restart');
  console.log('PARITY_NATIVE_PASS '+JSON.stringify({stage:'restored',taggedBookPlanning:true,secretBookExactId:true,vanillaFoods:40,smokerMappings:11,nonfoodOutputRejected:true,fullStableMetadata:true,smokerOutputs:true,recipeBookRestored:true,legacyPlateRanking:true,restartPreserved:true,simulatedPlayers:false}));
 }
}catch(e){console.error('PARITY_NATIVE_FAIL '+e+' '+e.stack)}},120);
