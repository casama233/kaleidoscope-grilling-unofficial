from __future__ import annotations
import base64, json, re, shutil, struct, zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'projects/grilling'
P=SRC/'gameplay_core'; BP=P/'behavior_pack'; RP=P/'resource_pack'
VERSION=[2,2,0]
FORMAL_BASES=['beef','pork_belly','chicken_skin','mid_wing','squid_tentacle','fish','sweet_potato_sheet','potato_slice','caterpillar','mushroom','bun_slice','ender_pearl','meatball','slime','meat_and_bone','fried_egg','gluten','lamb','golden']
PROFILE_TIMES={
 'ONE':[1.16667,3.08333],
 'TWO':[0.95833,4.0],
 'THREE':[0.95833,2.33333,3.54167],
 'THREE_ALT':[0.95833,2.16667,3.5],
 'FOUR':[0.95833,2.33333,3.45833,4.08333],
}
THREE_RANDOM_VIS=[0.95833,(2.33333+2.16667)/2,(3.54167+3.5)/2]
BOTTLE_COLLISIONS={
 1:{'origin':[-3,0,-3],'size':[6,12.25,6]},
 2:{'origin':[-6,0,-4],'size':[13,12.25,10]},
 3:{'origin':[-6,0,-6.75],'size':[13,12.25,13.75]},
 4:{'origin':[-7.25,0,-6.25],'size':[14.25,12.25,14.25]},
}

def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(data,(dict,list)): p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else: p.write_text(data,encoding='utf-8')

def replace_once(text,old,new,label):
    if old not in text: raise RuntimeError('A2.2 patch anchor missing: '+label)
    return text.replace(old,new,1)

def profile_for(item):
    name=item.replace('raw_','').replace('grilled_','')
    if name in ('fish_skewer','caterpillar_skewer'): return 'ONE'
    if name in ('bun_slice_skewer','fried_egg_skewer','slime_skewer','sweet_potato_sheet_skewer'): return 'TWO'
    if name in ('beef_skewer','chicken_skin_skewer','pork_belly_skewer'): return 'FOUR'
    if name=='ender_pearl_skewer': return 'THREE'
    return 'THREE_RANDOM'

def base_candidate(item):
    if item=='ordinary_skewer': return 'ordinary_full'
    cooked=item.startswith('grilled_')
    base=item.replace('raw_','').replace('grilled_','').removesuffix('_skewer')
    if base=='slime': return 'slime_frame_4' if cooked else 'slime_frame_0'
    return base+('_cooked' if cooked else '_raw')

def bite_candidates(item,names):
    if item=='ordinary_skewer':
        return [f'ordinary_bite_{i}' for i in range(1,4)]
    cooked=item.startswith('grilled_')
    base=item.replace('raw_','').replace('grilled_','').removesuffix('_skewer')
    if base=='slime':
        prefix='slime_bite_' if cooked else 'slime_raw_bite_'
    else:
        prefix=base+('_cooked_bite_' if cooked else '_raw_bite_')
    out=[];i=1
    while prefix+str(i) in names:
        out.append(prefix+str(i)); i+=1
    return out

def stage_expression(times):
    expr='0'
    for i,t in reversed(list(enumerate(times,1))):
        expr=f'(q.item_in_use_duration >= {t:.5f} ? {i} : {expr})'
    return f'v.kg_bite_stage = q.is_using_item ? {expr} : 0;'

def png_rgba(path,w,h,pixels):
    raw=b''.join(b'\x00'+bytes(pixels[y*w*4:(y+1)*w*4]) for y in range(h))
    def chunk(t,d):
        return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    data=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)

def add_stage_file(item,stage,candidate,specs):
    spec=specs[candidate]; geo_src=SRC/f'resource_pack/models/entity/kg_a1/{candidate}.geo.json'
    tex_src=SRC/f"resource_pack/textures/kg_a1/{spec['atlas_name']}.png"
    if not geo_src.is_file() or not tex_src.is_file(): raise RuntimeError(f'missing bite source {candidate}')
    geo=load(geo_src); ident=f'geometry.kg_a22.{item}.stage{stage}'
    for g in geo['minecraft:geometry']:
        g['description']['identifier']=ident
        for b in g.get('bones',[]):
            if not b.get('parent'): b['binding']='q.item_slot_to_bone_name(context.item_slot)'
    write(RP/f'models/entity/a22_bites/{item}_stage{stage}.geo.json',geo)
    td=RP/f'textures/a22_bites/{item}_stage{stage}.png';td.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(tex_src,td)
    return ident, f'textures/a22_bites/{item}_stage{stage}'

def patch_runtime():
    path=BP/'scripts/main.js'; s=path.read_text()
    s=replace_once(s,
      "const PENDING_SEASONING='kaleidoscope_grilling:pending_seasoning',SEASONING_BLOCK='kaleidoscope_grilling:seasoning_bottle';",
      "const PENDING_SEASONING='kaleidoscope_grilling:pending_seasoning',SEASONING_BLOCK='kaleidoscope_grilling:seasoning_bottle_1';\\nconst SEASONING_BLOCKS=new Set(['kaleidoscope_grilling:seasoning_bottle','kaleidoscope_grilling:seasoning_bottle_1','kaleidoscope_grilling:seasoning_bottle_2','kaleidoscope_grilling:seasoning_bottle_3','kaleidoscope_grilling:seasoning_bottle_4']);",
      'seasoning block constants')
    s=replace_once(s,
      "const DANGEROUS_FOODS=new Set(['minecraft:rotten_flesh','minecraft:chicken','minecraft:poisonous_potato','minecraft:pufferfish','minecraft:spider_eye']);",
      """const DANGEROUS_FOODS=new Set(['minecraft:rotten_flesh','minecraft:chicken','minecraft:poisonous_potato','minecraft:pufferfish','minecraft:spider_eye']);
const BITE_TIMES=Object.freeze({
 ONE:[1.16667,3.08333],TWO:[0.95833,4.0],THREE:[0.95833,2.33333,3.54167],THREE_ALT:[0.95833,2.16667,3.5],FOUR:[0.95833,2.33333,3.45833,4.08333]
});
const NUMB_VISUAL=new Set();
const OIL_TYPES=Object.freeze({canola:{heatTicks:1200},secret_chili:{heatTicks:12000},premium_chili:{heatTicks:24000}});
function isSeasoningBlock(id){return SEASONING_BLOCKS.has(id)}
function soundFor(profile){return profile==='ONE'?'one_skewer_eat':profile==='TWO'?'two_skewer_eat':profile==='FOUR'?'four_skewer_eat':'three_skewer_eat'}
function stopEatSound(player,profile){try{player.runCommand('stopsound @s kg_imm.'+soundFor(profile))}catch{}}
function spawnBiteCrumbs(player){
 try{
  const h=player.getHeadLocation(),v=player.getViewDirection();
  for(let i=0;i<5;i++)player.dimension.spawnParticle('kaleidoscope_grilling:skewer_crumb',{x:h.x+v.x*.32+(Math.random()-.5)*.14,y:h.y-.08+(Math.random()-.5)*.12,z:h.z+v.z*.32+(Math.random()-.5)*.14});
 }catch{}
}
function advanceBites(player,a){
 const elapsed=(system.currentTick-a.start)/20,times=a.biteTimes??[];
 while((a.nextBite??0)<times.length&&elapsed+1e-6>=times[a.nextBite]){spawnBiteCrumbs(player);a.nextBite++;try{player.playSound('random.eat',{volume:.35,pitch:1.0})}catch{}}
}
""",
      'A2.2 constants')
    s=replace_once(s,
      "function cookeryOilType(stack){try{return String(stack?.getDynamicProperty('kaleidoscope_grilling:oil_type')??'canola')}catch{return 'canola'}}\\nfunction heatForOil(type){return type==='premium_chili'?24000:type==='secret_chili'?12000:1200}",
      "function cookeryOilType(stack){try{const type=String(stack?.getDynamicProperty('kaleidoscope_grilling:oil_type')??'canola');return Object.hasOwn(OIL_TYPES,type)?type:'canola'}catch{return 'canola'}}\\nfunction heatForOil(type){return OIL_TYPES[type]?.heatTicks??OIL_TYPES.canola.heatTicks}",
      'oil types')
    start=s.index("function readBottleBlock(block)")
    end=s.index("function readFx(entity)")
    if start<0 or end<0 or end<=start: raise RuntimeError('A2.2 bottle function range missing')
    bottle=r"""function readBottleStack(block){
 try{
  const raw=world.getDynamicProperty(seasoningBlockKey(block));if(raw===undefined)return [];
  const v=JSON.parse(raw);if(!Array.isArray(v))return [];
  if(v.length&&typeof v[0]==='string'){const list=v.filter(x=>typeof x==='string').slice(0,8);return [{kind:hasSeasoningBase(list)?'pending':'empty',ingredients:list,uses:0,variant:0}]}
  return v.slice(0,4).map(x=>({kind:['empty','pending','special'].includes(x?.kind)?x.kind:'empty',ingredients:Array.isArray(x?.ingredients)?x.ingredients.filter(y=>typeof y==='string').slice(0,8):[],uses:Math.max(0,Math.min(16,Number(x?.uses)||0)),variant:Math.max(0,Math.min(7,Number(x?.variant)||0))}));
 }catch{return []}
}
function writeBottleStack(block,stack){world.setDynamicProperty(seasoningBlockKey(block),stack.length?JSON.stringify(stack.slice(0,4)):undefined)}
function bottleDataFromItem(stack){
 const kind=stack?.typeId===SEASONING_ID?'special':stack?.typeId===PENDING_SEASONING?'pending':'empty';
 return {kind,ingredients:readSeasonings(stack),uses:kind==='special'?getUses(stack):0,variant:kind==='special'?Math.max(0,Math.min(7,Number(stack.getDynamicProperty(SEASON_VARIANT_KEY)??0)|0)):0};
}
function bottleItem(data){
 const id=data.kind==='special'?SEASONING_ID:data.kind==='pending'?PENDING_SEASONING:EMPTY_SEASONING_ID,stack=new ItemStack(id,1);setSeasonings(stack,data.ingredients??[]);
 if(data.kind==='special'){setUses(stack,data.uses??0);try{stack.setDynamicProperty(SEASON_VARIANT_KEY,data.variant??0);stack.setLore(['§7Uses: '+(16-(data.uses??0))+'/16','§7Ingredients: '+(data.ingredients?.length??0)+'/8'])}catch{}}
 else try{if(data.ingredients?.length)stack.setLore(['§7Ingredients: '+data.ingredients.length+'/8',data.kind==='pending'?'§eReady to shake':'§7Missing base seasoning'])}catch{}
 return stack;
}
function setBottleVisual(block,count){
 const target=count>0?'kaleidoscope_grilling:seasoning_bottle_'+Math.max(1,Math.min(4,count)):'minecraft:air';
 if(block.typeId!==target)block.setType(target);
}
function pushBottle(block,player,held){
 const stack=readBottleStack(block);if(stack.length>=4){message(player,'§c最多只能堆4瓶');return false}
 stack.push(bottleDataFromItem(held));if(!decrementMain(player))return false;writeBottleStack(block,stack);setBottleVisual(block,stack.length);message(player,'§a調料瓶堆疊 '+stack.length+'/4');return true;
}
function handleSeasoningBlock(block,player){
 let stack=readBottleStack(block);if(!stack.length)stack=[{kind:'empty',ingredients:[],uses:0,variant:0}];
 const held=heldMain(player),id=held?.typeId;
 if(id===EMPTY_SEASONING_ID||id===PENDING_SEASONING||id===SEASONING_ID){pushBottle(block,player,held);return}
 const top=stack[stack.length-1];
 if(id&&Object.hasOwn(SEASONING_KINDS,id)){
  if(top.kind==='special'){message(player,'§7最上層是完成調料，不能再加料');return}
  if(top.ingredients.length>=8){message(player,'§c最上層調料瓶已滿 8/8');return}
  top.ingredients.push(id);top.kind=hasSeasoningBase(top.ingredients)?'pending':'empty';if(!decrementMain(player))return;writeBottleStack(block,stack);
  try{block.dimension.spawnParticle('minecraft:endrod',{x:block.x+.5,y:block.y+.7,z:block.z+.5})}catch{}
  message(player,hasSeasoningBase(top.ingredients)?'§a已加入 '+top.ingredients.length+'/8；基礎三料齊全':'§e已加入 '+top.ingredients.length+'/8');return;
 }
 if(!id){
  const out=stack.pop();setMain(player,bottleItem(out));writeBottleStack(block,stack);setBottleVisual(block,stack.length);message(player,'§a取回最上層調料瓶，剩 '+stack.length+'/4');return;
 }
 message(player,'§7這不是可加入的調料或調料瓶');
}
function placeSeasoningState(block,player){
 const cached=SEASON_PLACE_CACHE.get(player.id);SEASON_PLACE_CACHE.delete(player.id);
 const data=cached&&system.currentTick-cached.tick<=8?cached.data:{kind:'empty',ingredients:[],uses:0,variant:0};writeBottleStack(block,[data]);setBottleVisual(block,1);
}
"""
    s=s[:start]+bottle+s[end:]
    old=r"""world.afterEvents.itemStartUse.subscribe(e=>{
 const id=e.itemStack?.typeId;
 if(id===PENDING_SEASONING){const hand=handFor(e.source,id)?.name??'main';try{e.source.playAnimation('animation.kg_a21.player.shake.'+hand,{blendOutTime:.08})}catch{}return}
 if(!FOOD_DATA[id])return;const hand=handFor(e.source,id)?.name??'main',profile=resolvedProfile(PROFILE_BY_ITEM[id]??'THREE'),meta=stackMeta(e.itemStack),sat=e.source.getComponent('minecraft:player.saturation');
 ACTIVE_EATS.set(e.source.id,{id,start:system.currentTick,profile,hand,meta,nativeBefore:meta.hot?nativeSnapshot(e.source):{},fxBefore:meta.hot?fxSnapshot(e.source):{},saturationBefore:meta.hot?sat?.currentValue:undefined});
 try{e.source.playAnimation('animation.kg_imm.player.eat_'+profile.toLowerCase()+'.'+hand,{blendOutTime:.12})}catch{}
});"""
    new=r"""world.afterEvents.itemStartUse.subscribe(e=>{
 const id=e.itemStack?.typeId;
 if(id===PENDING_SEASONING){const hand=handFor(e.source,id)?.name??'main';try{e.source.playAnimation('animation.kg_a21.player.shake.'+hand,{blendOutTime:.08})}catch{}return}
 if(!FOOD_DATA[id])return;
 const requested=PROFILE_BY_ITEM[id]??'THREE',hand=handFor(e.source,id)?.name??'main',profile=resolvedProfile(requested),meta=stackMeta(e.itemStack),sat=e.source.getComponent('minecraft:player.saturation');
 const a={id,start:system.currentTick,requested,profile,hand,meta,biteTimes:BITE_TIMES[profile]??BITE_TIMES.THREE,nextBite:0,nativeBefore:meta.hot?nativeSnapshot(e.source):{},fxBefore:meta.hot?fxSnapshot(e.source):{},saturationBefore:meta.hot?sat?.currentValue:undefined};
 ACTIVE_EATS.set(e.source.id,a);
 try{e.source.playAnimation('animation.kg_imm.player.eat_'+profile.toLowerCase()+'.'+hand,{blendOutTime:.12});e.source.playSound('kg_imm.'+soundFor(profile))}catch{}
});"""
    s=replace_once(s,old,new,'itemStartUse')
    old=r"""world.afterEvents.itemCompleteUse.subscribe(e=>{
 const id=e.itemStack?.typeId;if(id===PENDING_SEASONING){completePending(e.source,e.itemStack);return}
 dangerousPreservation(e.source,id);if(!FOOD_DATA[id])return;
 const a=ACTIVE_EATS.get(e.source.id)??{id,meta:stackMeta(e.itemStack),nativeBefore:{},fxBefore:{},saturationBefore:undefined};SETTLED.set(e.source.id,system.currentTick);ACTIVE_EATS.delete(e.source.id);
 if(RAW_NAUSEA[id])try{e.source.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{e.source.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{e.source.addEffect('blindness',200,{showParticles:true})}catch{}
 afterCommitted(e.source,id,a.meta,a,true);
});"""
    new=r"""world.afterEvents.itemCompleteUse.subscribe(e=>{
 const id=e.itemStack?.typeId;if(id===PENDING_SEASONING){completePending(e.source,e.itemStack);return}
 dangerousPreservation(e.source,id);if(!FOOD_DATA[id])return;
 const a=ACTIVE_EATS.get(e.source.id)??{id,profile:PROFILE_BY_ITEM[id]??'THREE',meta:stackMeta(e.itemStack),nativeBefore:{},fxBefore:{},saturationBefore:undefined};stopEatSound(e.source,a.profile);SETTLED.set(e.source.id,system.currentTick);ACTIVE_EATS.delete(e.source.id);
 if(RAW_NAUSEA[id])try{e.source.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{e.source.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{e.source.addEffect('blindness',200,{showParticles:true})}catch{}
 afterCommitted(e.source,id,a.meta,a,true);
});"""
    s=replace_once(s,old,new,'itemCompleteUse')
    old="world.afterEvents.itemStopUse.subscribe(e=>{const a=ACTIVE_EATS.get(e.source.id);if(!a)return;ACTIVE_EATS.delete(e.source.id);if(SETTLED.get(e.source.id)===system.currentTick)return;const used=system.currentTick-a.start;if(used>=25&&used<profileDuration(a.profile)){if(hungerSettle(e.source,a.id,a))message(e.source,'§a在1.25秒檢查點完成進食')}try{e.source.playAnimation('animation.kg_core.player.reset',{blendOutTime:.12})}catch{}});"
    new="world.afterEvents.itemStopUse.subscribe(e=>{const a=ACTIVE_EATS.get(e.source.id);if(!a)return;ACTIVE_EATS.delete(e.source.id);stopEatSound(e.source,a.profile);if(SETTLED.get(e.source.id)===system.currentTick)return;const used=system.currentTick-a.start;if(used>=25&&used<profileDuration(a.profile)){if(hungerSettle(e.source,a.id,a))message(e.source,'§a在1.25秒檢查點完成進食')}try{e.source.playAnimation('animation.kg_core.player.reset',{blendOutTime:.12})}catch{}});"
    s=replace_once(s,old,new,'itemStopUse')
    old="world.beforeEvents.playerPlaceBlock.subscribe(e=>{try{if(e.permutationToPlace?.type?.id!==SEASONING_BLOCK)return;const held=heldMain(e.player);if(held?.typeId!==EMPTY_SEASONING_ID)return;SEASON_PLACE_CACHE.set(e.player.id,{tick:system.currentTick,list:readSeasonings(held)})}catch{}});"
    new="world.beforeEvents.playerPlaceBlock.subscribe(e=>{try{if(e.permutationToPlace?.type?.id!==SEASONING_BLOCK)return;const held=heldMain(e.player);if(!held||![EMPTY_SEASONING_ID,PENDING_SEASONING,SEASONING_ID].includes(held.typeId))return;SEASON_PLACE_CACHE.set(e.player.id,{tick:system.currentTick,data:bottleDataFromItem(held)})}catch{}});"
    s=replace_once(s,old,new,'place cache')
    old="world.beforeEvents.playerInteractWithBlock.subscribe(e=>{if(e.block.typeId!==GRILL_ID&&e.block.typeId!==SEASONING_BLOCK)return;e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const block=dim.getBlock(loc);if(block?.typeId===GRILL_ID)handleGrill(block,p);else if(block?.typeId===SEASONING_BLOCK)handleSeasoningBlock(block,p)})});"
    new="world.beforeEvents.playerInteractWithBlock.subscribe(e=>{if(e.block.typeId!==GRILL_ID&&!isSeasoningBlock(e.block.typeId))return;e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const block=dim.getBlock(loc);if(block?.typeId===GRILL_ID)handleGrill(block,p);else if(block&&isSeasoningBlock(block.typeId))handleSeasoningBlock(block,p)})});"
    s=replace_once(s,old,new,'interact bottles')
    old="world.afterEvents.playerPlaceBlock.subscribe(e=>{if(e.block.typeId===GRILL_ID){register(e.block);resetBlock(e.block,false)}else if(e.block.typeId===SEASONING_BLOCK)placeSeasoningState(e.block,e.player)});"
    new="world.afterEvents.playerPlaceBlock.subscribe(e=>{if(e.block.typeId===GRILL_ID){register(e.block);resetBlock(e.block,false)}else if(isSeasoningBlock(e.block.typeId))placeSeasoningState(e.block,e.player)});"
    s=replace_once(s,old,new,'after place bottles')
    old=r""" if(e.block.typeId===SEASONING_BLOCK){e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const b=dim.getBlock(loc);if(!b||b.typeId!==SEASONING_BLOCK)return;const list=readBottleBlock(b);writeBottleBlock(b,[]);b.setType('minecraft:air');if(!creative(p))b.dimension.spawnItem(seasoningBottleItem(list),{x:loc.x+.5,y:loc.y+.4,z:loc.z+.5})})}"""
    new=r""" if(isSeasoningBlock(e.block.typeId)){e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const b=dim.getBlock(loc);if(!b||!isSeasoningBlock(b.typeId))return;const bottles=readBottleStack(b);writeBottleStack(b,[]);b.setType('minecraft:air');if(!creative(p))for(const data of bottles)b.dimension.spawnItem(bottleItem(data),{x:loc.x+.5,y:loc.y+.4,z:loc.z+.5})})}"""
    s=replace_once(s,old,new,'break bottle stack')
    old=" for(const p of world.getAllPlayers()){try{\\n  writeFx(p,readFx(p));const hunger=p.getComponent('minecraft:player.hunger'),sat=p.getComponent('minecraft:player.saturation');"
    new=""" for(const p of world.getAllPlayers()){try{
  const active=ACTIVE_EATS.get(p.id);
  if(active){advanceBites(p,active);if(active.requested==='THREE_RANDOM'&&active.profile==='THREE_ALT'&&system.currentTick-active.start>=90){ACTIVE_EATS.delete(p.id);SETTLED.set(p.id,system.currentTick);stopEatSound(p,active.profile);if(hungerSettle(p,active.id,active))try{p.playAnimation('animation.kg_core.player.reset',{blendOutTime:.12})}catch{}}}
  writeFx(p,readFx(p));const hunger=p.getComponent('minecraft:player.hunger'),sat=p.getComponent('minecraft:player.saturation');"""
    s=replace_once(s,old,new,'active eat tick')
    old="  if(system.currentTick%20===0){const db=fxGet(p,'dragon_blood');if(db)try{p.addEffect('health_boost',25,{amplifier:db.amp>0?1:0,showParticles:false})}catch{}}"
    new="""  if(system.currentTick%20===0){const db=fxGet(p,'dragon_blood');if(db)try{p.addEffect('health_boost',25,{amplifier:db.amp>0?1:0,showParticles:false})}catch{}}
  const numb=fxGet(p,'numb');if(numb&&!ACTIVE_EATS.has(p.id)){if(system.currentTick%12===0)try{p.playAnimation('animation.kg_a22.player.numb',{blendOutTime:.08})}catch{};NUMB_VISUAL.add(p.id)}else if(!numb&&NUMB_VISUAL.delete(p.id)){try{p.playAnimation('animation.kg_core.player.reset',{blendOutTime:.12})}catch{}}"""
    s=replace_once(s,old,new,'numb visual')
    path.write_text(s,encoding='utf-8')

def main():
    report=load(P/'reports/build.json')
    if report.get('version')!='A2.1.0': raise RuntimeError('expected A2.1 baseline before A2.2 augmentation')
    # Version bump and names.
    bm=load(BP/'manifest.json');rm=load(RP/'manifest.json')
    bm['header']['version']=VERSION;rm['header']['version']=VERSION
    bm['header']['name']='Kaleidoscope Grilling A2.2 Gameplay BP';rm['header']['name']='Kaleidoscope Grilling A2.2 Gameplay RP'
    bm['header']['description']='逐口3D、四瓶調料堆疊與Numb動作；需要 Cookery 1.0.6';rm['header']['description']='逐口3D與四瓶調料外觀；需要 Cookery 1.0.6'
    for m in bm['modules']:m['version']=VERSION
    for m in rm['modules']:m['version']=VERSION
    for d in bm['dependencies']:
        if d.get('uuid')==rm['header']['uuid']:d['version']=VERSION
    write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
    cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.2 Gameplay';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_2';write(P/'config.json',cfg)
    # THREE_RANDOM must expose a 5s native window; script settles THREE_ALT at 90 ticks.
    for p in (BP/'items').glob('*.json'):
        doc=load(p);item=p.stem
        if item in ('mysterious_skewer','dark_grilling') or item.startswith('raw_') or item.startswith('grilled_') or item=='ordinary_skewer':
            if profile_for(item)=='THREE_RANDOM':
                comp=doc['minecraft:item']['components']
                if 'minecraft:use_modifiers' in comp:comp['minecraft:use_modifiers']['use_duration']=5.0
                write(p,doc)
    # Bite-stage attachables, exact source candidate states.
    specs_doc=load(SRC/'config/asset_specs.json');specs={x['name']:x for x in specs_doc['candidates']};names=set(specs)
    formal=[]
    for base in FORMAL_BASES:
        formal.extend(['raw_'+base+'_skewer','grilled_'+base+'_skewer'])
    formal.append('ordinary_skewer')
    stage_count=0;source_map={}
    for item in formal:
        profile=profile_for(item);times=THREE_RANDOM_VIS if profile=='THREE_RANDOM' else PROFILE_TIMES[profile]
        candidates=[base_candidate(item)]+bite_candidates(item,names)
        if len(candidates)!=len(times)+1:raise RuntimeError(f'{item}: {len(candidates)-1} bite models but {len(times)} bite times')
        geos=[];texs=[];source_map[item]={'profile':profile,'visual_bites':times,'candidates':candidates}
        for idx,cand in enumerate(candidates):
            g,t=add_stage_file(item,idx,cand,specs);geos.append(g);texs.append(t);stage_count+=1
        while len(geos)<5:geos.append(geos[-1]);texs.append(texs[-1])
        attach={'format_version':'1.26.0','minecraft:attachable':{'description':{
          'identifier':'kaleidoscope_grilling:'+item,'materials':{'default':'entity_alphablend'},
          'textures':{f'stage{i}':texs[i] for i in range(5)},
          'geometry':{f'stage{i}':geos[i] for i in range(5)},
          'scripts':{'pre_animation':[stage_expression(times)]},
          'render_controllers':['controller.render.kg_a22.bite']
        }}}
        write(RP/f'attachables/{item}.attachable.json',attach)
    write(RP/'render_controllers/a22_bites.render_controllers.json',{'format_version':'1.8.0','render_controllers':{
      'controller.render.kg_a22.bite':{
        'arrays':{
          'geometries':{'Array.kg_bite_geo':['Geometry.stage0','Geometry.stage1','Geometry.stage2','Geometry.stage3','Geometry.stage4']},
          'textures':{'Array.kg_bite_tex':['Texture.stage0','Texture.stage1','Texture.stage2','Texture.stage3','Texture.stage4']}
        },
        'geometry':'Array.kg_bite_geo[v.kg_bite_stage]','materials':[{'*':'Material.default'}],'textures':['Array.kg_bite_tex[v.kg_bite_stage]']
      }
    }})
    # Bite crumb particle with a tiny authored texture.
    pix=[]
    for y in range(8):
        for x in range(8):
            alpha=0 if (x in (0,7) and y in (0,7)) else 255
            pix += [156+(x%2)*18,96+(y%2)*12,52,alpha]
    png_rgba(RP/'textures/particle/kg_skewer_crumb.png',8,8,pix)
    write(RP/'particles/skewer_crumb.json',{'format_version':'1.26.10','particle_effect':{
      'description':{'identifier':'kaleidoscope_grilling:skewer_crumb','basic_render_parameters':{'material':'particles_alpha','texture':'textures/particle/kg_skewer_crumb'}},
      'components':{
        'minecraft:emitter_lifetime_expression':{},'minecraft:emitter_rate_manual':{'max_particles':1},
        'minecraft:emitter_shape_point':{'offset':[0,0,0],'direction':['math.random(-.12,.12)','math.random(.06,.18)','math.random(-.12,.12)']},
        'minecraft:particle_appearance_billboard':{'size':['math.random(.025,.045)','math.random(.025,.045)'],'facing_camera_mode':'lookat_xyz','uv':{'uv':[0,0],'uv_size':[1,1]}},
        'minecraft:particle_appearance_lighting':{},'minecraft:particle_initial_speed':1.2,'minecraft:particle_lifetime_expression':{'max_lifetime':'math.random(.25,.5)'},
        'minecraft:particle_motion_dynamic':{'linear_acceleration':[0,-4,0],'linear_drag_coefficient':1.5}
      }
    }})
    # Numb limb animation: one-second windows refreshed while effect is active, so expiry cannot leave a permanent pose.
    move="math.min(q.modified_move_speed * 1.8, 1.0)"
    phase="q.life_time * 18.334"
    write(RP/'animations/a22_numb.animation.json',{'format_version':'1.8.0','animations':{
      'animation.kg_a22.player.numb':{'animation_length':1.0,'override_previous_animation':False,'bones':{
        'rightarm':{'rotation':[f'math.cos({phase}) * 177.62 * {move}',0,f'math.sin({phase}) * 42.97 * {move}']},
        'leftarm':{'rotation':[f'-math.cos({phase}) * 177.62 * {move}',0,f'-math.sin({phase}) * 42.97 * {move}']},
        'rightleg':{'rotation':[f'-math.cos({phase}) * 94.54 * {move}',0,0]},
        'leftleg':{'rotation':[f'math.cos({phase}) * 94.54 * {move}',0,0]}
      }}
    }})
    # Four physical bottle stack block variants; no custom block states, so retail remains experiment-free.
    terrain=load(RP/'textures/terrain_texture.json')
    for n in range(1,5):
        src=SRC/f'resource_pack/models/entity/kg_a1/seasoning_bottles_{n}.geo.json';geo=load(src)
        ident=f'geometry.kg_a22.seasoning_bottles_{n}';geo['minecraft:geometry'][0]['description']['identifier']=ident
        write(RP/f'models/blocks/seasoning_bottles_{n}.geo.json',geo)
        terrain['texture_data'][f'kg_a22_seasoning_bottles_{n}']={'textures':'textures/blocks/seasoning_bottle'}
        box=BOTTLE_COLLISIONS[n]
        write(BP/f'blocks/seasoning_bottle_{n}.json',{'format_version':'1.26.50','minecraft:block':{
          'description':{'identifier':f'kaleidoscope_grilling:seasoning_bottle_{n}'},
          'components':{
            'minecraft:display_name':'tile.kaleidoscope_grilling:seasoning_bottle.name','minecraft:geometry':ident,
            'minecraft:material_instances':{'*':{'texture':f'kg_a22_seasoning_bottles_{n}','render_method':'blend'}},
            'minecraft:collision_box':box,'minecraft:selection_box':box,'minecraft:destructible_by_mining':{'seconds_to_destroy':.3}
          }
        }})
    write(RP/'textures/terrain_texture.json',terrain)
    # Empty/pending/special can all be physically placed as a bottle.
    for item in ('empty_seasoning_bottle','pending_seasoning','special_seasoning'):
        p=BP/f'items/{item}.json';doc=load(p);doc['minecraft:item']['components']['minecraft:block_placer']={'block':'kaleidoscope_grilling:seasoning_bottle_1','replace_block_item':True};write(p,doc)
    # Stable oil type contract only; Bedrock 26.51 has no public custom fluid registration.
    write(BP/'scripts/oil_types.js',"""export const OIL_TYPE_PROPERTY='kaleidoscope_grilling:oil_type';
export const OIL_TYPES=Object.freeze({
 canola:{heatTicks:1200,display:'canola'},
 secret_chili:{heatTicks:12000,display:'secret_chili'},
 premium_chili:{heatTicks:24000,display:'premium_chili'}
});
""")
    patch_runtime()
    report.update({
      'version':'A2.2.0','bite_stage_attachables':39,'bite_stage_geometry_files':stage_count,'bite_stage_source_map':'reports/a22-bite-stages.json',
      'bite_timing_source':'A1.16 binding plan / Java MultiBiteSkewerItem','three_random_visual_midpoint_max_drift_ticks':1.6666,
      'bite_particles':'kaleidoscope_grilling:skewer_crumb','profile_eating_sound_sync':True,'three_random_native_duration_fixed':True,
      'numb_limb_animation':True,'numb_crosshair_offset':False,
      'seasoning_physical_stack_max':4,'seasoning_independent_bottle_payload':True,'seasoning_stack_uses_custom_block_states':False,
      'oil_types':['canola','secret_chili','premium_chili'],'true_custom_fluids':False,
      'true_custom_fluids_reason':'Bedrock 26.51 stable exposes built-in LiquidType values only and liquid_detection supports water; no public custom fluid registration API',
      'a22_known_gaps':[
        'Minecraft/BDS runtime not yet tested',
        'THREE_RANDOM attachable geometry cannot read the server-selected branch; midpoint bite times keep maximum model-stage drift to about 1.67 ticks while logic/sound/particles use the exact branch',
        'Numb limb motion is reproduced through player animation; Java crosshair orbit has no stable Bedrock HUD offset API and remains unresolved',
        'No true custom oil fluid blocks: A2.2 formalizes typed container data only',
        'four-bottle stack uses four block identifiers rather than experimental custom block states to keep the 26.51 retail/no-experiments boundary'
      ]
    })
    write(P/'reports/build.json',report);write(P/'reports/a22-bite-stages.json',source_map)
    write(P/'reports/a22-build.json',{k:report[k] for k in ['version','bite_stage_attachables','bite_stage_geometry_files','three_random_visual_midpoint_max_drift_ticks','profile_eating_sound_sync','numb_limb_animation','numb_crosshair_offset','seasoning_physical_stack_max','seasoning_independent_bottle_payload','oil_types','true_custom_fluids','true_custom_fluids_reason','a22_known_gaps']})
    write(P/'README.zh-TW.md','# A2.2 Gameplay Core\n\nA2.2 在 A2.1 上加入正式逐口3D串、原作咬點粒子/聲音同步、THREE_RANDOM 4.5/5秒修正、Numb四肢動作、最多4瓶的獨立調料瓶實體堆疊，以及三種油型資料契約。真自訂流體在 Bedrock 26.51 沒有公開穩定註冊API，因此未冒充完成。\n')
    print(json.dumps(load(P/'reports/a22-build.json'),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
