import {world,system,ItemStack} from '@minecraft/server';
import {writeEffects,readEffects,clearEffects} from './effect_state_runtime.js';
import {setHotFood,hotUntil} from './a2750_food_state_adapter.js';
import {trackHotContainer} from './hot_lore_runtime.js';
import {renderItemType} from './station_contents_visual_runtime.js';
import {isHeatLore} from './localized_lore_core.js';
import {writePublicFood} from './host_api/food_api_core.js';
import {grillingConfig,setGrillingConfig} from './server_config_runtime.js';
const need=(v,message)=>{if(!v)throw Error(message)};
function run(){
 try{
  need(world.getAllPlayers().length===0,'unexpected player');const d=world.getDimension('overworld');
  const pig=d.spawnEntity('minecraft:pig',{x:0,y:81,z:64});
  const until=world.getAbsoluteTime()+400;
  writeEffects(pig,{vigor:{until,amp:0},dragon_blood:{until,amp:1},heavy_metal_poisoning:{until,amp:0}});
  pig.setDynamicProperty('kaleidoscope_grilling:dragon_pool',2);clearEffects(pig,{milk:true});
  need(Object.keys(readEffects(pig)).join()==='heavy_metal_poisoning','native custom cure mismatch');
  need(pig.getDynamicProperty('kaleidoscope_grilling:dragon_pool')===undefined,'dragon pool retained');clearEffects(pig);need(Object.keys(readEffects(pig)).length===0,'native clear mismatch');pig.remove();
  const original=grillingConfig().contentsHelpers;setGrillingConfig('contentsHelpers',4096);need(grillingConfig().contentsHelpers===4096,'config save');setGrillingConfig('contentsHelpers',original);
  const b=d.getBlock({x:2,y:80,z:64});b.setType('minecraft:chest');const c=b.getComponent('minecraft:inventory').container;
  const s=new ItemStack('minecraft:cooked_beef');s.nameTag='Preserved native food';s.setLore([{text:'foreign lore retained'}]);
  const t=world.getAbsoluteTime();setHotFood(s,1197);need(hotUntil(s)===t+1197,'deadline rounded');setHotFood(s,47);c.setItem(5,s);trackHotContainer(b);
  const e=d.spawnEntity('kaleidoscope_grilling:equipment_visual',{x:4,y:81,z:64}),stew=new ItemStack('minecraft:suspicious_stew');writePublicFood(stew,{v:1,hotUntil:0,seasoning:[],nativeVariant:7});
  const projection=renderItemType(e,stew);need(projection.data===7&&projection.commandVerified,'native aux projection');e.remove();
  system.runTimeout(()=>{try{
   const food=c.getItem(5);need(hotUntil(food)===0,'container heat not expired');need(food.nameTag==='Preserved native food','container custom name changed');need(food.getRawLore().some(x=>x.text==='foreign lore retained'),'foreign lore dropped');
   need(!food.getRawLore().some(isHeatLore),'stale heat line');
   console.warn('PARITY_NATIVE_PASS '+JSON.stringify({players:0,simulated_players:false,client:false,native_effect_storage:true,native_clear_function:true,milk_player_event:false,respawn_player_event:false,exact_deadline:true,opened_container_expiry:true,foreign_lore_preserved:true,native_aux:7,configuration_storage:true}));
  }catch(error){console.warn('PARITY_NATIVE_FAIL '+error)}},85);
 }catch(error){console.warn('PARITY_NATIVE_FAIL '+error)}
}
system.runTimeout(run,100);
