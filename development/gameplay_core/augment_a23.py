from __future__ import annotations
import hashlib,json,struct,shutil,urllib.request,zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'projects/grilling';P=SRC/'gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
VERSION=[2,3,0]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
BUCKETS={
 'canola_oil_bucket':('6a41780c98bb4eacfd7085f48639e23bf4a6fee5','菜籽油桶','Canola Oil Bucket'),
 'secret_chili_oil_bucket':('85abec19db960fc7e64ac3ee6f63b039d4819fcb','辣椒油桶','Chili Oil Bucket'),
 'premium_chili_oil_bucket':('ffbd8b5d0bc3fb6f4a4d9de0a6811e618a0bc0b0','熔岩辣椒油桶','Lava Chili Oil Bucket')
}
OILS={
 'canola':{'tint':(192,138,36,190),'light':0,'label':'菜籽油','en':'Canola Oil'},
 'secret_chili':{'tint':(224,75,42,195),'light':0,'label':'辣椒油','en':'Chili Oil'},
 'premium_chili':{'tint':(158,27,22,225),'light':15,'label':'熔岩辣椒油','en':'Lava Chili Oil'}
}

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+b'\0'+v).hexdigest()
def fetch(path,sha):
 req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.3/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 if blob(v)!=sha:raise RuntimeError('pinned bucket mismatch '+path)
 return v
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(data,(dict,list)):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else:p.write_text(data,encoding='utf-8')
def replace_once(text,old,new,label):
 if old not in text:raise RuntimeError('A2.3 patch anchor missing: '+label)
 return text.replace(old,new,1)
def png(path,rgba):
 w=h=16;raw=[]
 for y in range(h):
  raw.append(b'\x00')
  row=bytearray()
  for x in range(w):
   d=((x*13+y*7)%5-2)*4
   row.extend((max(0,min(255,rgba[0]+d)),max(0,min(255,rgba[1]+d)),max(0,min(255,rgba[2]+d)),rgba[3]))
  raw.append(bytes(row))
 def ch(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 data=b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(raw),9))+ch(b'IEND',b'')
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)

def patch_runtime():
 path=BP/'scripts/main.js';s=path.read_text()
 s=replace_once(s,
  "import {initialState,normalizeState,tickState,light,brush,flip,season,canInsert,canExtract,breakDisposition,outputKind} from './core_logic.js';",
  "import {initialState,normalizeState,tickState,light,brush,flip,season,canInsert,canExtract,breakDisposition,outputKind} from './core_logic.js';\nimport {mergeIntoContainer,compactSkewerContainer} from './a23_hot_runtime.js';\nimport './a23_oil_world.js';",
  'imports')
 s=replace_once(s,
  "const NUMB_VISUAL=new Set();",
  "const NUMB_VISUAL=new Set(),DRAGON_REPLAY=new Set();\nconst STORAGE_SORT_BLOCKS=new Set(['minecraft:chest','minecraft:trapped_chest','minecraft:barrel']);\nconst DRAGON_POOL_KEY='kaleidoscope_grilling:dragon_pool';",
  'constants')
 s=replace_once(s,
  "function writeState(block,s){world.setDynamicProperty(stateKey(block),JSON.stringify(normalizeState(s)))}",
  """function syncGrillPermutation(block,state){
 try{
  let perm=block.permutation,below=block.below(),legged=!(below?.isSolid??false),lit=!!state.lit;
  if(perm.getState('kaleidoscope_grilling:legged')!==legged)perm=perm.withState('kaleidoscope_grilling:legged',legged);
  if(perm.getState('kaleidoscope_grilling:lit')!==lit)perm=perm.withState('kaleidoscope_grilling:lit',lit);
  block.setPermutation(perm);
 }catch{}
}
function writeState(block,s){const state=normalizeState(s);world.setDynamicProperty(stateKey(block),JSON.stringify(state));syncGrillPermutation(block,state)}""",
  'grill permutation sync')
 s=replace_once(s,
  "function give(player,stack){const c=mainContainer(player);if(!c)return;const rem=c.addItem(stack);if(rem)player.dimension.spawnItem(rem,player.location)}",
  "function give(player,stack){const c=mainContainer(player);if(!c)return;const rem=mergeIntoContainer(c,stack);if(rem)player.dimension.spawnItem(rem,player.location)}",
  'manual give merge')
 # Dragon Blood exact effective total = native +4/+8 plus virtual +2.
 marker="function counts(list){const out={};for(const id of list){const kind=SEASONING_KINDS[id];if(kind)out[kind]=(out[kind]??0)+1}return out}"
 dragon=marker+"""
function dragonPool(entity){try{return Math.max(0,Math.min(2,Number(entity.getDynamicProperty(DRAGON_POOL_KEY)??0)))}catch{return 0}}
function setDragonPool(entity,value){try{entity.setDynamicProperty(DRAGON_POOL_KEY,value>0?Math.max(0,Math.min(2,value)):undefined)}catch{}}
function applyDragonBlood(player,ticks,amp){
 const old=fxGet(player,'dragon_blood'),oldNative=old?(old.amp>0?8:4):0,newNative=amp>0?8:4;
 fxSet(player,'dragon_blood',ticks,amp);
 if(!old)setDragonPool(player,2);
 try{player.addEffect('health_boost',Math.max(25,ticks),{amplifier:amp>0?1:0,showParticles:false})}catch{}
 const gain=Math.max(0,newNative-oldNative);
 if(gain>0)system.run(()=>{try{const hp=player.getComponent('minecraft:health');if(hp)hp.setCurrentValue(Math.min(hp.effectiveMax,hp.currentValue+gain))}catch{}});
}
"""
 s=replace_once(s,marker,dragon,'dragon helpers')
 s=replace_once(s,
  " if((c.vitality??0)>0)fxSet(player,'dragon_blood',duration,c.vitality>=4?1:0);",
  " if((c.vitality??0)>0)applyDragonBlood(player,duration,c.vitality>=4?1:0);",
  'dragon apply')
 # Damage pool before heavy metal; replay residual keeps later death protection semantics.
 old=" const hm=fxGet(target,'heavy_metal'),hp=target.getComponent?.('minecraft:health');if(hm&&!fxGet(target,'heavy_metal_poisoning')&&hp&&e.damage>=hp.currentValue){e.cancel=true;system.run(()=>{fxClear(target,'heavy_metal');fxSet(target,'heavy_metal_poisoning',12000);try{hp.setCurrentValue(1);target.dimension.playSound('random.totem',target.location)}catch{}})}"
 new=""" const replay=DRAGON_REPLAY.delete(target.id);
 if(!replay){
  const db=fxGet(target,'dragon_blood'),pool=dragonPool(target);
  if(db&&pool>0&&e.damage>0){
   const absorb=Math.min(pool,e.damage),remain=e.damage-absorb;setDragonPool(target,pool-absorb);e.cancel=true;
   if(remain>0)system.run(()=>{try{DRAGON_REPLAY.add(target.id);const opt={cause:e.damageSource?.cause??'entityAttack'};if(e.damageSource?.damagingEntity)opt.damagingEntity=e.damageSource.damagingEntity;target.applyDamage(remain,opt)}catch{DRAGON_REPLAY.delete(target.id)}});
   return;
  }
 }
 const hm=fxGet(target,'heavy_metal'),hp=target.getComponent?.('minecraft:health');if(hm&&!fxGet(target,'heavy_metal_poisoning')&&hp&&e.damage>=hp.currentValue){e.cancel=true;system.run(()=>{fxClear(target,'heavy_metal');fxSet(target,'heavy_metal_poisoning',12000);try{hp.setCurrentValue(1);target.dimension.playSound('random.totem',target.location)}catch{}})}"""
 s=replace_once(s,old,new,'dragon hurt pool')
 # Storage sorter interception before grill/bottle handling.
 old="world.beforeEvents.playerInteractWithBlock.subscribe(e=>{if(e.block.typeId!==GRILL_ID&&!isSeasoningBlock(e.block.typeId))return;e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const block=dim.getBlock(loc);if(block?.typeId===GRILL_ID)handleGrill(block,p);else if(block&&isSeasoningBlock(block.typeId))handleSeasoningBlock(block,p)})});"
 new="""world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 if(e.player.isSneaking&&!e.itemStack&&STORAGE_SORT_BLOCKS.has(e.block.typeId)){
  e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;
  system.run(()=>{const b=dim.getBlock(loc),c=b?.getComponent('minecraft:inventory')?.container;if(!c)return;const r=compactSkewerContainer(c,false);message(p,r.changed?'§b已整理串類：熱度差≤5分鐘的熱串按數量加權合併':'§7沒有可整理的串類')});return;
 }
 if(e.block.typeId!==GRILL_ID&&!isSeasoningBlock(e.block.typeId))return;e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension;system.run(()=>{const block=dim.getBlock(loc);if(block?.typeId===GRILL_ID)handleGrill(block,p);else if(block&&isSeasoningBlock(block.typeId))handleSeasoningBlock(block,p)});
});"""
 s=replace_once(s,old,new,'storage sorter')
 # Replace generic repel with closer Java semantics.
 old="function repel(player,type,radius){try{for(const e of player.dimension.getEntities({type,location:player.location,maxDistance:radius})){const dx=e.location.x-player.location.x,dz=e.location.z-player.location.z,len=Math.max(.001,Math.hypot(dx,dz));e.applyKnockback({x:dx/len*.18,z:dz/len*.18},.04)}}catch{}}"
 new="""function fleeCreepers(player){
 try{for(const e of player.dimension.getEntities({type:'minecraft:creeper',location:player.location,maxDistance:6})){const dx=e.location.x-player.location.x,dz=e.location.z-player.location.z,len=Math.max(.001,Math.hypot(dx,dz));e.applyKnockback({x:dx/len*.12,z:dz/len*.12},.02)}}catch{}
}
function repelPhantoms(player){
 try{for(const e of player.dimension.getEntities({type:'minecraft:phantom',location:player.location,maxDistance:18})){const dx=e.location.x-player.location.x,dy=e.location.y-player.location.y,dz=e.location.z-player.location.z;if(Math.abs(dx)>8||Math.abs(dz)>8||Math.abs(dy)>16)continue;const len=Math.max(.001,Math.hypot(dx,dz));e.applyKnockback({x:dx/len*.16,z:dz/len*.16},.06)}}catch{}
}
function tundraFactor(id){if(id==='minecraft:blue_ice')return 1.1055;if(['minecraft:ice','minecraft:packed_ice','minecraft:frosted_ice'].includes(id))return 1.11;return 1.3}"""
 s=replace_once(s,old,new,'effect helpers')
 old="  if(system.currentTick%5===0){if(fxGet(p,'mustard'))repel(p,'minecraft:creeper',6);if(fxGet(p,'sulfur'))repel(p,'minecraft:phantom',16)}"
 new="  if(system.currentTick%5===0){if(fxGet(p,'mustard'))fleeCreepers(p);if(fxGet(p,'sulfur'))repelPhantoms(p)}"
 s=replace_once(s,old,new,'mustard sulfur')
 old="  if(system.currentTick%10===0&&fxGet(p,'tundra_strider')){try{const b=p.getBlockStandingOn();if(b&&TUNDRA_BLOCKS.has(b.typeId)){p.addEffect('speed',12,{amplifier:0,showParticles:false});if(b.typeId==='minecraft:powder_snow')p.applyImpulse({x:0,y:.035,z:0})}}catch{}}"
 new="""  if(fxGet(p,'tundra_strider')){try{const b=p.getBlockStandingOn();if(b&&TUNDRA_BLOCKS.has(b.typeId)){const v=p.getVelocity(),factor=tundraFactor(b.typeId);p.applyImpulse({x:v.x*(factor-1),y:0,z:v.z*(factor-1)});if(b.typeId==='minecraft:powder_snow'&&v.y<.02)p.applyImpulse({x:0,y:Math.min(.16,Math.max(.04,-v.y+.04)),z:0})}}catch{}}"""
 s=replace_once(s,old,new,'tundra factor')
 old="  if(system.currentTick%20===0){const db=fxGet(p,'dragon_blood');if(db)try{p.addEffect('health_boost',25,{amplifier:db.amp>0?1:0,showParticles:false})}catch{}}"
 new="  if(system.currentTick%20===0){const db=fxGet(p,'dragon_blood');if(db){try{p.addEffect('health_boost',25,{amplifier:db.amp>0?1:0,showParticles:false})}catch{};if(dragonPool(p)<=0&&p.getDynamicProperty(DRAGON_POOL_KEY)===undefined)setDragonPool(p,2)}else setDragonPool(p,0)}"
 s=replace_once(s,old,new,'dragon refresh')
 path.write_text(s,encoding='utf-8')

def grill_block():
 terrain=load(RP/'textures/terrain_texture.json')
 terrain['texture_data']['kg_a23_grill_unlit']={'textures':'textures/blocks/grill_unlit'}
 terrain['texture_data']['kg_a23_grill_lit']={'textures':'textures/blocks/grill_lit'}
 write(RP/'textures/terrain_texture.json',terrain)
 (RP/'textures/blocks').mkdir(parents=True,exist_ok=True)
 shutil.copyfile(SRC/'resource_pack/textures/kg_a1/grill_unlit.png',RP/'textures/blocks/grill_unlit.png')
 shutil.copyfile(SRC/'resource_pack/textures/kg_a1/grill_lit.png',RP/'textures/blocks/grill_lit.png')
 variants=['grill_flat','grill_flat_lit','grill_legged','grill_legged_lit']
 for v in variants:
  doc=load(SRC/f'resource_pack/models/entity/kg_a1/{v}.geo.json');doc['minecraft:geometry'][0]['description']['identifier']='geometry.kg_a23.'+v;write(RP/f'models/blocks/{v}.geo.json',doc)
 desc={
  'identifier':'kaleidoscope_grilling:grill','menu_category':{'category':'items'},
  'states':{'kaleidoscope_grilling:legged':[False,True],'kaleidoscope_grilling:lit':[False,True]},
  'traits':{'minecraft:placement_direction':{'enabled_states':['minecraft:cardinal_direction'],'y_rotation_offset':180.0}}
 }
 base={'minecraft:display_name':'tile.kaleidoscope_grilling:grill.name','minecraft:block_entity':{'container':{'slot_count':3}},
       'minecraft:geometry':'geometry.kg_a23.grill_flat','minecraft:material_instances':{'*':{'texture':'kg_a23_grill_unlit','render_method':'alpha_test','ambient_occlusion':1.0,'face_dimming':True}},
       'minecraft:light_emission':0,'minecraft:collision_box':{'origin':[-8,0,-6],'size':[16,6,12]},'minecraft:selection_box':{'origin':[-8,0,-6],'size':[16,8,12]},
       'minecraft:destructible_by_mining':{'seconds_to_destroy':3},'minecraft:destructible_by_explosion':{'explosion_resistance':6}}
 perms=[]
 for leg in (False,True):
  for lit in (False,True):
   name='grill_'+('legged' if leg else 'flat')+('_lit' if lit else '')
   comp={'minecraft:geometry':'geometry.kg_a23.'+name,'minecraft:material_instances':{'*':{'texture':'kg_a23_grill_lit' if lit else 'kg_a23_grill_unlit','render_method':'alpha_test','ambient_occlusion':0.0 if lit else 1.0,'face_dimming':False if lit else True}},'minecraft:light_emission':13 if lit else 0}
   perms.append({'condition':f"q.block_state('kaleidoscope_grilling:legged') == {'true' if leg else 'false'} && q.block_state('kaleidoscope_grilling:lit') == {'true' if lit else 'false'}",'components':comp})
 for face,rot in [('north',0),('south',180),('west',90),('east',270)]:
  perms.append({'condition':f"q.block_state('minecraft:cardinal_direction') == '{face}'",'components':{'minecraft:transformation':{'rotation':[0,rot,0]}}})
 write(BP/'blocks/grill.json',{'format_version':'1.26.50','minecraft:block':{'description':desc,'components':base,'permutations':perms}})

def oil_resources():
 terrain=load(RP/'textures/terrain_texture.json');items=load(RP/'textures/item_texture.json')
 # shared level geometries
 geos=[]
 for level in range(8):
  h=16-level*2
  geos.append({'description':{'identifier':f'geometry.kg_a23.oil_level_{level}','texture_width':16,'texture_height':16,'visible_bounds_width':2,'visible_bounds_height':2,'visible_bounds_offset':[0,.5,0]},'bones':[{'name':'root','pivot':[0,0,0],'cubes':[{'origin':[-8,0,-8],'size':[16,h,16],'uv':[0,0]}]}]})
 write(RP/'models/blocks/a23_oil_levels.geo.json',{'format_version':'1.21.0','minecraft:geometry':geos})
 for typ,meta in OILS.items():
  png(RP/f'textures/blocks/{typ}_oil.png',meta['tint']);terrain['texture_data'][f'kg_a23_{typ}_oil']={'textures':f'textures/blocks/{typ}_oil'}
  perms=[]
  for level in range(8):
   h=16-level*2;perms.append({'condition':f"q.block_state('kaleidoscope_grilling:level') == {level}",'components':{'minecraft:geometry':f'geometry.kg_a23.oil_level_{level}','minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,h,16]}}})
  write(BP/f'blocks/{typ}_oil.json',{'format_version':'1.26.50','minecraft:block':{'description':{'identifier':f'kaleidoscope_grilling:{typ}_oil','states':{'kaleidoscope_grilling:level':list(range(8))}},'components':{
    'minecraft:display_name':f'tile.kaleidoscope_grilling:{typ}_oil.name','minecraft:geometry':'geometry.kg_a23.oil_level_0','minecraft:material_instances':{'*':{'texture':f'kg_a23_{typ}_oil','render_method':'blend','ambient_occlusion':0.0,'face_dimming':False}},
    'minecraft:collision_box':False,'minecraft:selection_box':{'origin':[-8,0,-8],'size':[16,16,16]},'minecraft:replaceable':{},'minecraft:light_emission':meta['light'],'minecraft:destructible_by_mining':{'seconds_to_destroy':100}
   },'permutations':perms}})
 write(RP/'textures/terrain_texture.json',terrain)
 for item,(sha,zh,en) in BUCKETS.items():
  raw=fetch(f'common/src/main/resources/assets/kaleidoscope_grilling/textures/item/{item}.png',sha);(RP/f'textures/items/{item}.png').write_bytes(raw);items['texture_data'][item]={'textures':f'textures/items/{item}'}
  write(BP/f'items/{item}.json',{'format_version':'1.26.30','minecraft:item':{'description':{'identifier':f'kaleidoscope_grilling:{item}','menu_category':{'category':'items'}},'components':{'minecraft:display_name':{'value':f'item.kaleidoscope_grilling:{item}.name'},'minecraft:icon':{'textures':{'default':item}},'minecraft:max_stack_size':1,'minecraft:hand_equipped':True}}})
 write(RP/'textures/item_texture.json',items)
 for lang in ('zh_TW','zh_CN','en_US'):
  p=RP/f'texts/{lang}.lang';t=p.read_text()
  for typ,meta in OILS.items():t+=f'\ntile.kaleidoscope_grilling:{typ}_oil.name='+(meta['en'] if lang=='en_US' else meta['label'])
  for item,(_,zh,en) in BUCKETS.items():t+=f'\nitem.kaleidoscope_grilling:{item}.name='+(en if lang=='en_US' else zh)
  p.write_text(t+'\n',encoding='utf-8')

def main():
 report=load(P/'reports/build.json')
 if report.get('version')!='A2.2.0':raise RuntimeError('expected A2.2 baseline')
 # versions
 bm=load(BP/'manifest.json');rm=load(RP/'manifest.json');bm['header']['version']=VERSION;rm['header']['version']=VERSION;bm['header']['name']='Kaleidoscope Grilling A2.3 Gameplay BP';rm['header']['name']='Kaleidoscope Grilling A2.3 Gameplay RP'
 for m in bm['modules']:m['version']=VERSION
 for m in rm['modules']:m['version']=VERSION
 for d in bm['dependencies']:
  if d.get('uuid')==rm['header']['uuid']:d['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.3 Gameplay';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_3';write(P/'config.json',cfg)
 # restore normal stack size for all formal foods
 count=0
 for p in (BP/'items').glob('*.json'):
  doc=load(p);comp=doc['minecraft:item']['components']
  if 'minecraft:food' in comp:comp['minecraft:max_stack_size']=64;write(p,doc);count+=1
 if count!=41:raise RuntimeError(f'expected 41 foods, got {count}')
 # modules
 for name in ('a23_hot_merge.js','a23_hot_runtime.js','a23_oil_world.js'):shutil.copyfile(Path(__file__).parent/name,BP/'scripts'/name)
 grill_block();oil_resources();patch_runtime()
 report.update({
  'version':'A2.3.0','formal_food_max_stack':64,'hot_merge_weighted_remaining':True,'normal_storage_heat_window_ticks':6000,
  'bedrock_storage_sort_blocks':['minecraft:chest','minecraft:trapped_chest','minecraft:barrel'],'order_to_cook_full_sort_algorithm_available':True,'order_to_cook_mod_present':False,
  'grill_visual_states':['flat_unlit','flat_lit','legged_unlit','legged_lit'],'grill_support_rule':'legged = !below.isSolid (stable Bedrock approximation of Java top-face-sturdy)','grill_lit_light_emission':13,'grill_light_note':'Bedrock presentation enhancement; Java GrillBlock itself does not emit block light',
  'dragon_blood_effective_bonus_hp':[6,10],'dragon_blood_native_visible_bonus_hp':[4,8],'dragon_blood_virtual_pool_hp':2,
  'tundra_strider_speed_factors':{'snow_like':1.3,'ice_like':1.11,'blue_ice':1.1055},
  'mustard_semantics':'6-block flee-like scripted knockback; writable AI AvoidEntityGoal unavailable in stable API',
  'sulfur_semantics':'AABB 8x16 flee-like push; writable phantom target clear unavailable in stable API',
  'numb_crosshair':'not implemented: no safe stable per-player HUD crosshair-offset API; global hud override intentionally avoided',
  'world_oil_simulation':True,'world_oil_levels':8,'world_oil_types':['canola','secret_chili','premium_chili'],'true_engine_liquid_type':False,
  'world_oil_note':'scripted stable custom-block fluid simulation with gravity/horizontal spread, bucket and Cookery oil-pot transfer; not Forge/Bedrock engine LiquidType'
 })
 write(P/'reports/build.json',report)
 write(P/'reports/a23-build.json',{k:report[k] for k in ['version','formal_food_max_stack','hot_merge_weighted_remaining','normal_storage_heat_window_ticks','bedrock_storage_sort_blocks','grill_visual_states','grill_support_rule','grill_lit_light_emission','dragon_blood_effective_bonus_hp','dragon_blood_native_visible_bonus_hp','dragon_blood_virtual_pool_hp','tundra_strider_speed_factors','mustard_semantics','sulfur_semantics','numb_crosshair','world_oil_simulation','world_oil_levels','world_oil_types','true_engine_liquid_type','world_oil_note']})
 write(P/'README.zh-TW.md','# A2.3 Gameplay Core\n\nA2.3 補上 Hot Food 手動安全堆疊／儲物整理、烤爐 flat/legged + lit/unlit 四態、Dragon Blood 精確總有效+6/+10生命、Tundra/Mustard/Sulfur 更貼近 Java 的腳本語義，以及三種8級世界油流動模擬。Numb 準星仍因26.51 stable無安全per-player HUD offset而不做全局UI覆寫。\n')
 print(json.dumps(load(P/'reports/a23-build.json'),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
