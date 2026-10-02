// Verified author source, storage-operation doubles only; no Minecraft players.
import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import path from 'node:path';import {pathToFileURL} from 'node:url';
import {recipeTable} from '../../projects/grilling/gameplay_core/behavior_pack/scripts/a2727_cookery_host_recipes_core.js';
if(process.argv.length<4)throw Error('Usage: node reproduce_cookery_acquisition.mjs <verified-author-BP-directory> <report.json>');
const root=pathToFileURL(path.resolve(process.argv[2],'scripts')+path.sep);
const read=p=>fs.readFileSync(new URL(p,root),'utf8');
const registry=read('api/extensionRegistry.js'),station=read('custom_components/blocks/directStation.js'),data=read('data/stationRecipes.js');
const expectedHashes={registry:'9fd1c604a69825e684d8d0b0e68f584fba947073d70b3e22084f451c94351646',station:'be855cfe437b036f8a6b706f58607385f4b1ca6e53cfdad5a2c3a28bbc5cff06',recipes:'2def68bd907c9600567896973e4b4682dfeef46aed6d1c11d702f1daf9fca89d'};
const sourceHashes=Object.fromEntries([['registry',registry],['station',station],['recipes',data]].map(([k,v])=>[k,crypto.createHash('sha256').update(v).digest('hex')]));
assert.deepEqual(sourceHashes,expectedHashes,'Only verified author 1.0.8 sources may certify this reproduction');
function fn(source,name){const start=source.indexOf('function '+name+'(');assert.ok(start>=0,name);let end=source.indexOf('{',start)+1,depth=1;while(depth){const c=source[end++];if(c==='{')depth++;if(c==='}')depth--}return source.slice(start,end)}
const context=vm.createContext({console,system:{currentTick:0,afterEvents:{scriptEventReceive:{subscribe(){}}},run(){},runTimeout(){},runInterval(){},clearRun(){},sendScriptEvent(){}}});
vm.runInContext(data.replace(/\bexport /g,''),context);
vm.runInContext(read('data/stockpotJavaRecipes.js').replace(/\bexport /g,''),context);
vm.runInContext(registry.replace(/^import\b[\s\S]*?;\s*/gm,'').replace(/\bexport /g,''),context);
const register=vm.runInContext('registerExtensionRecipe',context);
const beef=register({api:1,kind:'chopping_board',source:'qa_grilling',recipe:{id:'qa:beef',input:'minecraft:beef',result:'kaleidoscope_grilling:beef_chunks',count:2,cuts:4,priority:100,override:true}});assert.equal(beef.ok,true);
const chicken=register({api:1,kind:'chopping_board',source:'qa_grilling',recipe:{id:'qa:chicken',input:'minecraft:chicken',result:'kaleidoscope_cookery:raw_cut_small_meats',count:2,cuts:4,bonusOutputs:[{result:'kaleidoscope_grilling:chicken_skin',min:1,max:3}]}});assert.equal(chicken.ok,true);
let state={},held,damage=0,payout=[],debits=0,failDrop=false;
Object.assign(context,{held:()=>held,load:()=>structuredClone(state),save:(_b,s)=>state=structuredClone(s),consume:()=>debits++,give:(_p,id,count)=>payout.push({id,count}),pop:(_b,id,count)=>{if(!failDrop)payout.push({id,count})},dmgTool:()=>damage++,emitBoardCutParticles(){},playSoundAccessible(){},isKitchenKnife:s=>s?.typeId==='qa:knife',msg(){},hint:()=>'',Math});
vm.runInContext(fn(station,'boardInteract')+';this.interact=boardInteract',context);
function processBoard(input,fail=false){state={};damage=0;payout=[];debits=0;failDrop=fail;held={typeId:input};context.interact({},{});const selected=structuredClone(state);held={typeId:'qa:knife'};for(let n=0;n<4;n++)context.interact({},{});assert.equal(payout.length,0);context.interact({},{});return {selected,payout:structuredClone(payout),knifeDamage:damage,debits,stationEmpty:Object.keys(state).length===0}}
const beefResult=processBoard('minecraft:beef'),chickenResult=processBoard('minecraft:chicken'),failedChicken=processBoard('minecraft:chicken',true);
assert.equal(beefResult.selected.result.id,'kaleidoscope_cookery:raw_cow_offal');assert.equal(beefResult.payout[0].id,'kaleidoscope_cookery:raw_cow_offal');assert.deepEqual(chickenResult.payout,[{id:'kaleidoscope_cookery:raw_cut_small_meats',count:2}]);assert.equal(failedChicken.stationEmpty,true);assert.equal(failedChicken.payout.length,0);
const get=context.getExtensionBoardRecipe??vm.runInContext('getExtensionBoardRecipe',context);const normalizedBeef=get('minecraft:beef'),normalizedChicken=get('minecraft:chicken');assert.equal(normalizedBeef.priority,undefined);assert.equal(normalizedChicken.bonusOutputs,undefined);
const registeredBoardCases=[];
for(const {payload} of recipeTable().filter(r=>r.capability==='chopping_board')){assert.equal(register(payload).ok,true);const result=processBoard(payload.recipe.input);assert.equal(result.payout[0].id,payload.recipe.result);assert.equal(result.payout[0].count,payload.recipe.count);registeredBoardCases.push({input:payload.recipe.input,expected:payload.recipe.result,count:payload.recipe.count,matched:true});}
const toolAlternatives=[];
for(const [input,result] of [['minecraft:beef','kaleidoscope_grilling:beef_chunks'],['minecraft:chicken','kaleidoscope_grilling:chicken_skin']]){assert.equal(register({api:1,kind:'chopping_board_tool',source:'qa_grilling',recipe:{id:'qa:tool_'+input.split(':')[1],input,tool:'minecraft:shears',result,count:2,popOutput:true}}).ok,true);state={};damage=0;payout=[];debits=0;failDrop=false;held={typeId:input};context.interact({},{});held={typeId:'minecraft:shears'};context.interact({},{});assert.deepEqual(payout,[{id:result,count:2}]);toolAlternatives.push({input,payout:structuredClone(payout),toolActions:1,toolDamage:damage,faithfulToJava:false});}
const report={schema:1,host:'author Cookery 1.0.8',archiveSha256:'9e5b617cc4c7a08ecd429fb9e42ec10e8d40a1ed5fc1f6f6687c3aff8a45a5d5',sourceHashes,beefRegistrationAccepted:beef.ok,chickenRegistrationAccepted:chicken.ok,unsupportedFieldsRemoved:{priority:normalizedBeef.priority===undefined,bonusOutputs:normalizedChicken.bonusOutputs===undefined},beefResult,chickenResult,failedChicken,registeredBoardCases,toolAlternatives,boundary:'Actual unmodified host function bodies with storage-operation doubles. Not native/client acceptance; no Minecraft players.'};
fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
