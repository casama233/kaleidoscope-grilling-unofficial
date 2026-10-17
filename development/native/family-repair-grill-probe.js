/** Test-only native visual and plate delivery checks; no players. */
import {world,system,ItemStack} from '@minecraft/server';
import {renderItemType} from './station_contents_visual_runtime.js';
import {a25NativeBreakPlate,a25RetryPlateDelivery,a25StackRow,a25ReadPlateBlock} from './a25_plate_recipe_runtime.js';
const wait=t=>new Promise(r=>system.runTimeout(r,t));const check=(v,label)=>{if(!v)throw Error(label)};
system.runTimeout(async()=>{try{
 const d=world.getDimension('overworld');d.runCommand('tickingarea add circle 54 80 64 2 repair_plate true');let b;for(let i=0;i<60;i++){await wait(10);try{b=d.getBlock({x:54,y:80,z:64})}catch{}if(b)break}check(b,'chunk');
 const helper=d.spawnEntity('kaleidoscope_grilling:equipment_visual',{x:54,y:80,z:64});const visual=renderItemType(helper,new ItemStack('kaleidoscope_cookery:iron_kitchen_knife'));helper.remove();check(visual.commandVerified,'native equipment command');
 const key='kaleidoscope_grilling:a25_plate_minecraft_overworld_p54_p80_p64';
 if(!world.getDynamicProperty('qa:plate_delivery')){
  b.below().setType('minecraft:stone');b.setType('kaleidoscope_grilling:skewer_plate_block');const item=new ItemStack('kaleidoscope_grilling:grilled_beef_skewer');item.nameTag='Native plate delivery';world.setDynamicProperty(key,JSON.stringify([a25StackRow(item)]));
  check(a25ReadPlateBlock(b).length===1,'native plate load');check(a25NativeBreakPlate(b),'native break');
  check(b.typeId==='minecraft:air'&&world.getDynamicProperty(key)===undefined,'native plate cleanup');
  const outputs=d.getEntities({type:'minecraft:item',location:{x:54.5,y:80,z:64.5},maxDistance:2}).filter(e=>e.getComponent('minecraft:item')?.itemStack.typeId==='kaleidoscope_grilling:skewer_plate');check(outputs.length===1,'one native packed plate');outputs[0].remove();world.setDynamicProperty('qa:plate_delivery',true);
 }
 check(!a25RetryPlateDelivery(b),'delivery replay refused');
 console.log('CONTENTS_NATIVE_PASS '+JSON.stringify({nativeEquipmentVerified:true,plateDeliveryReceipt:JSON.parse(world.getDynamicProperty(key+'_delivery')).phase,replayNoCredit:true,players:world.getAllPlayers().length,client:false}));
}catch(e){console.error('CONTENTS_NATIVE_FAIL '+e+' '+e.stack)}},260);
