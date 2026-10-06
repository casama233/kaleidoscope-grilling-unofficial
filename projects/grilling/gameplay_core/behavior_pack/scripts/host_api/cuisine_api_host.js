/** Author-owned output transactions; native food state travels with the actual output. */
import {world,system,ItemStack,EquipmentSlot} from '@minecraft/server';
import {writePublicFood,readPublicFood,normalizePublicFood,bucketHotUntil} from './food_api_core.js';
export const CUISINE_CAPABILITIES=Object.freeze(['cuisine_output_receipt_v2','secret_ingredient_consume_v1','cuisine_configuration_v1']);
const CONFIG_KEY='senluo:cuisine_heat_and_seasoning_v1';
const cuisineEnabled=()=>world.getDynamicProperty(CONFIG_KEY)!==false;
const META_PREFIX='senluo:cuisine_metadata:',RECEIPT_PREFIX='senluo:cuisine_output:';
const key=b=>b.dimension.id+':'+b.x+','+b.y+','+b.z;
const station=b=>({dimensionId:b.dimension.id,x:b.x,y:b.y,z:b.z});
const same=(a,b)=>a?.typeId===b?.typeId&&a?.amount===b?.amount&&a?.nameTag===b?.nameTag&&JSON.stringify(a?.getRawLore())===JSON.stringify(b?.getRawLore());
const carriers=new Map();
export function beginCuisineCarrier(player){const slot=player.getComponent('minecraft:equippable')?.getEquipmentSlot(EquipmentSlot.Mainhand);if(!slot)throw Error('carrier slot missing');carriers.set(player.id,{slot,before:slot.hasItem()?slot.getItem():undefined});}
function restoreCarrier(player){const r=carriers.get(player.id);if(r){r.slot.setItem(r.before);carriers.delete(player.id);}}
export function nextCuisineBatch(b){const k=RECEIPT_PREFIX+key(b)+'_batch',n=Number(world.getDynamicProperty(k)??0)+1;if(!Number.isSafeInteger(n))throw Error('batch sequence');world.setDynamicProperty(k,n);return n;}
export function readCuisineMetadata(b,data={},kind='pot'){
 if(!cuisineEnabled())return {v:1,hotUntil:0,seasoning:[]};
 let state={seasoning:[],oilType:data.grillingOilType??(data.oil?'default':'')};
 const raw=world.getDynamicProperty(META_PREFIX+key(b));if(raw!==undefined)state={...state,...JSON.parse(String(raw))};
 const oilType=data.grillingOilType||state.oilType;
 const heat=kind==='stockpot'?1200:oilType==='premium_chili'?24000:oilType==='secret_chili'?12000:1200;
 const result=normalizePublicFood({v:1,hotUntil:bucketHotUntil(Number(world.getAbsoluteTime())+heat),seasoning:[...(state.seasoning??[])]});if(!result)throw Error('cuisine metadata invalid');return result;
}
export function createNativeSuspiciousStew(b,variant=Math.floor(Math.random()*11)){
 if(!Number.isInteger(variant)||variant<0||variant>10)throw Error('stew variant');
 const stand=b.dimension.spawnEntity('kaleidoscope_grilling:equipment_visual',{x:b.x+.5,y:b.y+.5,z:b.z+.5});
 try{
  stand.runCommand('replaceitem entity @s slot.inventory 0 minecraft:suspicious_stew 1 '+variant);
  const stack=stand.getComponent('minecraft:inventory')?.container?.getItem(0);if(stack?.typeId!=='minecraft:suspicious_stew')throw Error('native stew variant missing');writePublicFood(stack,{v:1,hotUntil:0,seasoning:[],nativeVariant:variant});return stack.clone();
 }finally{stand.remove();}
}
const fingerprint=s=>({id:s.typeId,amount:s.amount,name:s.nameTag,lore:s.getRawLore()});
function matchesFingerprint(s,f){return !!s&&JSON.stringify(fingerprint(s))===JSON.stringify(f);}
function emit(receipt){try{system.sendScriptEvent('kaleidoscope_grilling:cookery_output_ready',JSON.stringify({version:2,receiptId:receipt.receiptId,station:receipt.station,target:receipt.target,metadata:receipt.metadata}));}catch(e){console.warn('[Cookery cuisine API] committed notification deferred '+receipt.receiptId+' '+e)}}
export function deliverCuisineOutput(b,data,id,count,kind,{container,playerId,targetBlock,dropLocation,nativeStack,operationId}={}){
 if(!Number.isInteger(count)||count<1||count>64)throw Error('output amount invalid');
 const op=operationId??'automatic:'+nextCuisineBatch(b),receiptId=key(b)+':'+op,receiptKey=RECEIPT_PREFIX+receiptId;
 const old=world.getDynamicProperty(receiptKey);
 if(old!==undefined){
  const prior=JSON.parse(String(old));
  if(prior.phase==='committed'){emit(prior);return {...prior,replayed:true};}
  if(prior.phase==='prepared'){
   const actual=prior.target?.kind==='item_entity'?world.getEntity(prior.target.entityId)?.getComponent('minecraft:item')?.itemStack:container?.getItem(prior.target?.slot);
   if(matchesFingerprint(actual,prior.output)){prior.phase='committed';world.setDynamicProperty(receiptKey,JSON.stringify(prior));emit(prior);return {...prior,replayed:true};}
   // Delivery may have been collected before a crash. Retain its receipt; never credit twice.
   throw Error('cuisine delivery outcome unresolved: '+receiptId);
  }
  if(prior.phase!=='rolled_back')throw Error('cuisine receipt quarantined: '+receiptId);
 }
 const meta=readCuisineMetadata(b,data,kind),base=nativeStack?.clone()??new ItemStack(id,count);if(base.typeId!==id||base.amount!==count)throw Error('native output identity');
 const outputMeta=readPublicFood(base);if(outputMeta.present&&!outputMeta.valid)throw Error('native output metadata unreadable');
 if(outputMeta.valid&&outputMeta.state.nativeVariant!==undefined)meta.nativeVariant=outputMeta.state.nativeVariant;
 const stack=writePublicFood(base,meta);if(meta.hotUntil>Number(world.getAbsoluteTime())&&stack.getRawLore().length<20)stack.setLore([...stack.getRawLore(),{rawtext:[{text:'§c🔥 '},{translate:'tooltip.kaleidoscope_grilling.smoky_warmth'},{text:' '+Math.ceil((meta.hotUntil-Number(world.getAbsoluteTime()))/20)+'s'}]}]);
 let slot=-1,target,entity;
 if(container)for(let i=0;i<container.size;i++)if(!container.getItem(i)){slot=i;break;}
 if(slot>=0){if(!playerId&&!targetBlock)throw Error('output block target missing');target=playerId?{kind:'player_slot',playerId,slot,expectedId:id,expectedAmount:count}:{kind:'block_slot',...station(targetBlock),slot,expectedId:id,expectedAmount:count};}
 else target={kind:'item_entity',entityId:'pending',expectedId:id,expectedAmount:count};
 const receipt={api:2,receiptId,station:station(b),metadata:meta,target,output:fingerprint(stack),phase:'prepared'};
 world.setDynamicProperty(receiptKey,JSON.stringify(receipt));
 try{
  if(slot>=0){container.setItem(slot,stack);if(!same(container.getItem(slot),stack))throw Error('output slot readback');}
  else{entity=b.dimension.spawnItem(stack,dropLocation??{x:b.x+.5,y:b.y+.45,z:b.z+.5});if(!entity||!same(entity.getComponent('minecraft:item')?.itemStack,stack))throw Error('output entity readback');target.entityId=entity.id;}
 }catch(error){
  let unknown=false;try{if(slot>=0)container.setItem(slot,undefined);else if(entity)entity.remove();else unknown=true}catch{unknown=true}
  receipt.phase=unknown?'quarantined':'rolled_back';receipt.reason=String(error);world.setDynamicProperty(receiptKey,JSON.stringify(receipt));throw error;
 }
 receipt.phase='committed';
 // Acknowledged delivery wins: do not throw after crediting and make the caller issue it again.
 try{world.setDynamicProperty(receiptKey,JSON.stringify(receipt))}catch(e){console.warn('[Cookery cuisine API] acknowledged output receipt retained '+receiptId+' '+e)}
 emit(receipt);return receipt;
}
function portionOperation(data,kind){return kind+':'+(data.grillingOutputEpoch??'legacy')+':'+Number(kind==='stockpot'?data.takeout??1:data.result?.count??1);}
export function giveCuisineOutput(b,p,data,id,count=1,kind='pot',{suspicious=false}={}){
 try{
  const receipt=deliverCuisineOutput(b,data,id,count,kind,{container:p.getComponent('minecraft:inventory')?.container,playerId:p.id,dropLocation:p.location,operationId:portionOperation(data,kind),nativeStack:suspicious?createNativeSuspiciousStew(b):undefined});
  if(receipt.replayed)restoreCarrier(p);else carriers.delete(p.id);return receipt;
 }catch(e){try{restoreCarrier(p);console.warn('[Cookery cuisine API] output retained '+e)}catch{};throw e;}
}
export function recoverCuisineOutput(b,data){
 if(!data.result?.id||data.burnt)return false;
 deliverCuisineOutput(b,data,data.result.id,Math.max(1,Number(data.result.count??1)),'pot',{operationId:'break:'+portionOperation(data,'pot')});return true;
}
system.afterEvents.scriptEventReceive.subscribe(e=>{
 if(e.id!=='kaleidoscope_cookery:cuisine_metadata')return;try{
  const r=JSON.parse(e.message),s=r.station;if(r.api!==1||!s||typeof s.dimensionId!=='string'||![s.x,s.y,s.z].every(Number.isInteger))return;
  const valid=normalizePublicFood({v:1,hotUntil:0,seasoning:r.state?.seasoning});if(!valid)return;
  const k=META_PREFIX+s.dimensionId+':'+s.x+','+s.y+','+s.z;
  world.setDynamicProperty(k,JSON.stringify({seasoning:valid.seasoning,oilType:String(r.state.oilType??'')}));
 }catch(error){console.warn('[Cookery cuisine API] metadata retained '+error)}
});

system.afterEvents.scriptEventReceive.subscribe(e=>{
 if(e.id!=='kaleidoscope_cookery:cuisine_config')return;
 try{const request=JSON.parse(e.message);if(request.api!==1||typeof request.enabled!=='boolean')throw Error('invalid cuisine configuration');
  world.setDynamicProperty(CONFIG_KEY,request.enabled);
  if(world.getDynamicProperty(CONFIG_KEY)!==request.enabled)throw Error('cuisine configuration readback');
 }catch(error){console.warn('[Cookery cuisine API] configuration retained '+error)}
});
system.run(()=>system.sendScriptEvent('kaleidoscope_grilling:cuisine_config_request','{"api":1}'));
