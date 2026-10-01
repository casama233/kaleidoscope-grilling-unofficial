// Test-only file injected into the PUBLIC Cookery pack in an isolated candidate world.
// Observe the real cross-pack recipe registration, not a mocked script-event bus.
import {world,system,ItemTypes} from '@minecraft/server';
import {getExtensionMillstoneRecipe,getExtensionBoardRecipe} from './api/extensionRegistry.js';
const expected=[
 ['kaleidoscope_cookery:green_chili','kaleidoscope_grilling:green_chili_powder'],
 ['kaleidoscope_grilling:houttuynia','kaleidoscope_grilling:houttuynia_powder'],
 ['minecraft:totem_of_undying','kaleidoscope_grilling:totem_powder'],
 ['kaleidoscope_grilling:canola_seeds','kaleidoscope_grilling:canola_powder'],
 ['kaleidoscope_grilling:onion','kaleidoscope_grilling:onion_powder'],
 ['kaleidoscope_cookery:red_chili','kaleidoscope_grilling:red_chili_powder'],
 ['kaleidoscope_grilling:sweet_potato','kaleidoscope_grilling:sweet_potato_powder']
];
const wait=n=>new Promise(resolve=>system.runTimeout(resolve,n));
world.afterEvents.worldLoad.subscribe(()=>system.run(async()=>{try{
 for(let attempt=0;attempt<40;attempt++){
  if(expected.every(([id])=>getExtensionMillstoneRecipe(id)))break;
  await wait(10);
 }
 for(const [input,output] of expected){
  const row=getExtensionMillstoneRecipe(input);
  if(row?.outputs?.length!==1||row.outputs[0].id!==output||row.outputs[0].count!==1||row.outputs[0].chance!==1)throw Error('Native registered recipe differs: '+input);
  if(!ItemTypes.get(input)||!ItemTypes.get(output))throw Error('Native recipe item missing: '+input);
 }
 if(getExtensionBoardRecipe('minecraft:carrot')?.result!=='kaleidoscope_grilling:carrot_dice')throw Error('Existing chopping recipe regressed');
 const ids=['minecraft:wooden_button',...['spruce','birch','jungle','acacia','dark_oak','mangrove','cherry','bamboo','crimson','warped'].map(x=>'minecraft:'+x+'_button'),'minecraft:brick','minecraft:glass','minecraft:coal','minecraft:lava_bucket','kaleidoscope_grilling:grill','kaleidoscope_grilling:empty_seasoning_bottle','kaleidoscope_grilling:premium_chili_oil_bucket','kaleidoscope_grilling:dragon_egg_powder'];
 for(const id of ids)if(!ItemTypes.get(id))throw Error('Crafting/native item missing: '+id);
 console.warn('GRILL_SURVIVAL_NATIVE_PASS '+JSON.stringify({millstoneRecipes:7,choppingPreserved:true,verifiedItemTypes:ids.length,clientCrafting:false}));
 }catch(e){console.error('GRILL_SURVIVAL_NATIVE_FAIL '+e+' '+e.stack)}}));
