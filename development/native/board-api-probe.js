/** Actor-neutral native storage probe. No players or player-use events are created. */
import {system,world,ItemStack} from '@minecraft/server';
import {BOARD_CAPABILITIES,createBoardHostIO,getBoardV2Recipe} from './api/board_api_runtime.js';
import {executeBoardOperation,normalizeBoardV2Recipe} from './api/board_api_core.js';
import {boardApiHost} from './custom_components/blocks/directStation.js';
import {KC_EXTENSION_CAPABILITIES,registerExtensionRecipe} from './api/extensionRegistry.js';
const check=(ok,label)=>{if(!ok)throw Error(label)},wait=t=>new Promise(r=>system.runTimeout(r,t));
const recipes=[{api:1,kind:'chopping_board_v2',source:'kaleidoscope_grilling:board_api',recipe:{id:'kaleidoscope_grilling:chopping_board/beef_chunks',input:'minecraft:beef',builtin:{result:'kaleidoscope_cookery:raw_cow_offal',count:2,cuts:4},mode:'replace',result:'kaleidoscope_grilling:beef_chunks',count:2}},{api:1,kind:'chopping_board_v2',source:'kaleidoscope_grilling:board_api',recipe:{id:'kaleidoscope_grilling:chopping_board/chicken_skin',input:'minecraft:chicken',builtin:{result:'kaleidoscope_cookery:raw_cut_small_meats',count:2,cuts:4},mode:'supplement',bonusOutputs:[{id:'kaleidoscope_grilling:chicken_skin',min:1,max:3}]}}];
const key='kaleidoscope_cookery:qa_board_api_010';
system.runTimeout(async()=>{try{
 for(const c of BOARD_CAPABILITIES)check(KC_EXTENSION_CAPABILITIES.includes(c),'public handshake '+c);
 for(const r of recipes){check(getBoardV2Recipe(r.recipe.input,r.recipe.builtin)?.id===r.recipe.id,'actual Grilling registration');check(registerExtensionRecipe(r).ok,'registry idempotent')}
 const d=world.getDimension('overworld');try{d.runCommand('tickingarea add circle 24 80 64 2 board_api_qa true')}catch{}
 let b;for(let i=0;i<60;i++){await wait(10);try{b=d.getBlock({x:24,y:80,z:64})}catch{}if(b)break}check(b,'chunk');
 const chest=d.getBlock({x:26,y:80,z:64}),host=boardApiHost();
 const io=()=>{const out=createBoardHostIO(b,undefined,host),slot=chest.getComponent('minecraft:inventory').container.getSlot(0);out.readHeld=()=>slot.hasItem()?slot.getItem():undefined;out.writeHeld=s=>{slot.setItem(s);check(slot.getItem()?.typeId===s?.typeId,'native hand storage')};return out};
 const previous=world.getDynamicProperty(key);
 if(previous){
  const x=io(),state=x.readState();check(state.cuts===2&&state.boardV2.phase==='cutting','half-cut saved');const knife=x.readHeld();check(knife.getComponent('minecraft:durability').damage===2,'knife damage saved');
  for(let i=0;i<3;i++)executeBoardOperation(x,undefined,{random:()=>.999});check(x.readReceipt().phase==='committed','restored release receipt');check(!x.readState().input,'restored board clear');
  console.log('BOARD_NATIVE_PASS '+JSON.stringify({stage:'restored',halfCutResumed:true,cuts:4,release:1,skin:3,originalChickenOutput:2,nativeItemStacks:true,nativeDrops:true,authorStateAndVisuals:true,players:world.getAllPlayers().length,playerUseEvents:false}));return;
 }
 b.below().setType('minecraft:stone');b.setType('kaleidoscope_cookery:chopping_board');chest.setType('minecraft:chest');const bag=chest.getComponent('minecraft:inventory').container;
 const results=[];
 for(const p of recipes){
  const x=io(),r=normalizeBoardV2Recipe(p),raw=new ItemStack(r.input,2);raw.nameTag='QA original';raw.setLore(['foreign lore']);bag.setItem(0,raw);executeBoardOperation(x,r);check(bag.getItem(0).amount===1,'input debit');
  bag.setItem(0,new ItemStack('kaleidoscope_cookery:iron_kitchen_knife'));for(let i=0;i<4;i++)executeBoardOperation(x,r,{random:()=>0});check(x.readState().cuts===4,'four cuts');const cutKnife=bag.getItem(0);check(cutKnife.getComponent('minecraft:durability').damage===4,'four damage');executeBoardOperation(x,r,{random:()=>.999});
  const receipt=x.readReceipt();check(receipt.phase==='committed','durable native delivery');check(!x.readState().input,'clear author state');results.push(receipt.outputs);
 }
 check(results[0][0].id==='kaleidoscope_grilling:beef_chunks'&&results[0][0].count===2,'beef replacement');check(results[1][0].id==='kaleidoscope_cookery:raw_cut_small_meats'&&results[1][1].count===3,'chicken supplement');
 const x=io(),r=normalizeBoardV2Recipe(recipes[1]);bag.setItem(0,new ItemStack(r.input));executeBoardOperation(x,r);bag.setItem(0,new ItemStack('kaleidoscope_cookery:iron_kitchen_knife'));for(let i=0;i<2;i++)executeBoardOperation(x,r,{random:()=>0});world.setDynamicProperty(key,JSON.stringify({results}));
 console.log('BOARD_NATIVE_PASS '+JSON.stringify({stage:'saved',outputs:results,halfCutSaved:true,nativeItemStacks:true,nativeDrops:true,authorStateAndVisuals:true,players:world.getAllPlayers().length,playerUseEvents:false}));
}catch(e){console.error('BOARD_NATIVE_FAIL '+e+' '+e.stack)}},340);
