/** Isolated Cookery QA import only; this file never ships in the Grilling runtime. */
import {system,world} from '@minecraft/server';
import {registerExtensionRecipe,getExtensionBoardRecipe,KC_EXTENSION_CAPABILITIES} from './api/extensionRegistry.js';
const check=(ok,label)=>{if(!ok)throw Error(label)};
system.runTimeout(()=>{try{
 check(KC_EXTENSION_CAPABILITIES.includes('chopping_board'),'board capability');
 const beef=registerExtensionRecipe({api:1,kind:'chopping_board',source:'qa_grilling',recipe:{id:'qa:beef',input:'minecraft:beef',result:'kaleidoscope_grilling:beef_chunks',count:2,cuts:4,priority:100,override:true}});
 const chicken=registerExtensionRecipe({api:1,kind:'chopping_board',source:'qa_grilling',recipe:{id:'qa:chicken',input:'minecraft:chicken',result:'kaleidoscope_cookery:raw_cut_small_meats',count:2,cuts:4,bonusOutputs:[{result:'kaleidoscope_grilling:chicken_skin',min:1,max:3}]}});
 check(beef.ok&&chicken.ok,'registration accepted');
 const b=getExtensionBoardRecipe('minecraft:beef'),c=getExtensionBoardRecipe('minecraft:chicken');
 check(b.priority===undefined&&b.override===undefined&&c.bonusOutputs===undefined,'unsupported schema fields discarded');
 const expected=[['kaleidoscope_grilling:sweet_potato_powder','kaleidoscope_grilling:raw_sweet_potato_sheet'],['minecraft:carrot','kaleidoscope_grilling:carrot_dice'],['minecraft:potato','kaleidoscope_grilling:potato_slice'],['kaleidoscope_cookery:mantou','kaleidoscope_grilling:raw_mantou_slice'],['kaleidoscope_grilling:houttuynia','kaleidoscope_grilling:minced_houttuynia']];
 for(const [input,result] of expected)check(getExtensionBoardRecipe(input)?.result===result,'actual Grilling recipe registered '+input);
 console.log('HOSTAPI_NATIVE_PASS '+JSON.stringify({host:'author 1.0.8',beefRegistrationAccepted:beef.ok,chickenRegistrationAccepted:chicken.ok,unsupportedPriorityDiscarded:true,unsupportedBonusDiscarded:true,otherBoardRecipesRegistered:5,actualBoardUse:false,naturalAcquisition:false,client:false,players:world.getAllPlayers().length}));
}catch(e){console.error('HOSTAPI_NATIVE_FAIL '+e+' '+e.stack)}},320);
