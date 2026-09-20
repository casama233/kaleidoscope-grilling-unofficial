from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'projects/grilling'
P=SRC/'gameplay_core'
BP=P/'behavior_pack'
RP=P/'resource_pack'
DEV=Path(__file__).parent
VERSION=[2,4,0]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
SECRET_TEXTURE=('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/secret_skewer_stick.png','77321e269c440f5844cc48fe6456f92e0544d8ab')

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+b'\\0'+v).hexdigest()
def fetch(path,sha):
    req=urllib.request.Request(UP+path,headers={'User-Agent':'Grilling-A2.4/1'})
    with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
    if blob(v)!=sha:raise RuntimeError('pinned upstream mismatch '+path)
    return v

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(data,(dict,list)):
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:
        path.write_text(data,encoding='utf-8')

def replace_once(text,old,new,label):
    if old not in text:
        raise RuntimeError('A2.4 patch anchor missing: '+label)
    return text.replace(old,new,1)

def patch_manifest():
    bm=load(BP/'manifest.json');rm=load(RP/'manifest.json')
    for doc,name in ((bm,'Kaleidoscope Grilling A2.4 Gameplay BP'),(rm,'Kaleidoscope Grilling A2.4 Gameplay RP')):
        doc['header']['version']=VERSION
        doc['header']['name']=name
        for module in doc.get('modules',[]): module['version']=VERSION
    for dep in bm.get('dependencies',[]):
        if dep.get('uuid')==rm['header']['uuid']: dep['version']=VERSION
    write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
    cfg=load(P/'config.json')
    cfg['name']='Kaleidoscope Grilling A2.4 Gameplay'
    cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_4'
    write(P/'config.json',cfg)

def patch_items_and_assets():
    # Java HotFoodConfig.ALLOW_SKEWERS_AT_FULL_HUNGER defaults true.
    foods=0
    for path in (BP/'items').glob('*.json'):
        doc=load(path);comp=doc.get('minecraft:item',{}).get('components',{})
        food=comp.get('minecraft:food')
        if isinstance(food,dict):
            food['can_always_eat']=True
            write(path,doc);foods+=1
    if foods!=41:
        raise RuntimeError(f'expected A2.3 41 formal foods, got {foods}')

    base_components={
        'minecraft:display_name':{'value':'item.kaleidoscope_grilling:unfinished_skewer.name'},
        'minecraft:icon':{'textures':{'default':'unfinished_skewer'}},
        'minecraft:max_stack_size':64,
        'minecraft:allow_off_hand':True,
        'minecraft:hand_equipped':True
    }
    write(BP/'items/unfinished_skewer.json',{
        'format_version':'1.26.30','minecraft:item':{
            'description':{'identifier':'kaleidoscope_grilling:unfinished_skewer','menu_category':{'category':'items'}},
            'components':base_components
        }
    })
    secret_components={
        'minecraft:display_name':{'value':'item.kaleidoscope_grilling:secret_skewer.name'},
        'minecraft:icon':{'textures':{'default':'secret_skewer'}},
        'minecraft:max_stack_size':64,
        'minecraft:allow_off_hand':True,
        'minecraft:hand_equipped':True,
        'minecraft:use_modifiers':{'start_using':'always','use_duration':4.5,'movement_modifier':0.35},
        # Runtime applies the Java dynamic nutrition formula. Keep native contribution at zero.
        'minecraft:food':{'can_always_eat':True,'nutrition':0,'saturation_modifier':0.0},
        'minecraft:use_animation':{'value':'eat'},
        'minecraft:tags':{'tags':['minecraft:is_food']}
    }
    write(BP/'items/secret_skewer.json',{
        'format_version':'1.26.30','minecraft:item':{
            'description':{'identifier':'kaleidoscope_grilling:secret_skewer','menu_category':{'category':'items'}},
            'components':secret_components
        }
    })

    tex=load(RP/'textures/item_texture.json')
    tex['texture_data']['unfinished_skewer']={'textures':'textures/items/unfinished_skewer'}
    tex['texture_data']['secret_skewer']={'textures':'textures/items/secret_skewer'}
    write(RP/'textures/item_texture.json',tex)
    texture_path,texture_sha=SECRET_TEXTURE;raw=fetch(texture_path,texture_sha)
    for name in ('unfinished_skewer','secret_skewer'):
        (RP/f'textures/items/{name}.png').write_bytes(raw)

    labels={
        'zh_TW':('未完成烤串','秘制串'),
        'zh_CN':('未完成烤串','秘制串'),
        'en_US':('Unfinished Skewer','Secret Skewer')
    }
    for lang,(unfinished,secret) in labels.items():
        path=RP/f'texts/{lang}.lang'
        text=path.read_text(encoding='utf-8')
        for key,value in (
            ('item.kaleidoscope_grilling:unfinished_skewer.name',unfinished),
            ('item.kaleidoscope_grilling:secret_skewer.name',secret)
        ):
            if key+'=' not in text: text+='\n'+key+'='+value
        path.write_text(text.rstrip()+'\n',encoding='utf-8')

def patch_hot_runtime():
    path=BP/'scripts/a23_hot_runtime.js'
    text=path.read_text(encoding='utf-8')
    old="""function setHot(stack,remaining,t=now()){
 try{
  if(remaining>0)stack.setDynamicProperty(HOT,bucket(t+remaining));
  else stack.setDynamicProperty(HOT,undefined);
  const lore=baseLore(stack);
  if(remaining>0){const sec=Math.max(1,Math.ceil(remaining/20)),m=Math.floor(sec/60),s=String(sec%60).padStart(2,'0');lore.push('§c🔥 煙火氣 '+m+':'+s)}
  stack.setLore(lore);
 }catch{}
 return stack;
}"""
    new="""function setHot(stack,remaining,t=now()){
 try{
  const lore=baseLore(stack);
  if(remaining>0){const sec=Math.max(1,Math.ceil(remaining/20)),m=Math.floor(sec/60),s=String(sec%60).padStart(2,'0');lore.push('§c🔥 煙火氣 '+m+':'+s)}
  // Stable 2.9 ItemStack dynamic properties require a non-stackable/custom-data stack.
  // Give the stack custom lore first, then persist HotUntil.
  stack.setLore(lore);
  if(remaining>0)stack.setDynamicProperty(HOT,bucket(t+remaining));
  else stack.setDynamicProperty(HOT,undefined);
 }catch{}
 return stack;
}"""
    text=replace_once(text,old,new,'A2.3 hot runtime property ordering')
    path.write_text(text,encoding='utf-8')

def patch_oil_world():
    path=BP/'scripts/a23_oil_world.js';text=path.read_text(encoding='utf-8')
    text=replace_once(text,
        "import {world,system,ItemStack,EquipmentSlot,GameMode,BlockPermutation} from '@minecraft/server';",
        "import {world,system,ItemStack,EquipmentSlot,GameMode,BlockPermutation} from '@minecraft/server';\nimport {FLUID_CAPACITY,OIL_BUCKET_POINTS} from './a24_skewering_core.js';",
        'oil world import')
    old="""function takeSource(player,block,type,hand,toCookery=false){
 if(level(block)!==0)return false;
 const rows=readReg(),k=posKey(block.dimension.id,block.x,block.y,block.z),row=rows.find(r=>r.k===k);
 try{block.setType('minecraft:air')}catch{return false}
 if(row){clearCells(row,rows);saveReg(rows.filter(r=>r!==row))}
 if(toCookery){
  const pot=new ItemStack(COOKERY_FILLED,1);try{pot.setDynamicProperty('kc_oil_count',256);pot.setDynamicProperty('kaleidoscope_grilling:oil_type',type);pot.setLore(['§7Oil: 256/256'])}catch{};setHand(player,hand,pot);
 }else setHand(player,hand,new ItemStack(OIL_TYPES[type].bucket,1));
 return true;
}"""
    new="""function cookeryType(stack){try{return String(stack?.getDynamicProperty('kaleidoscope_grilling:oil_type')??'')}catch{return ''}}
function cookeryCount(stack){try{return Math.max(0,Math.min(FLUID_CAPACITY,Number(stack?.getDynamicProperty('kc_oil_count')??0)|0))}catch{return 0}}
function takeSource(player,block,type,hand,toCookery=false){
 if(level(block)!==0)return false;
 const held=hand==='off'?off(player):main(player);
 let nextPot;
 if(toCookery){
  const currentType=held?.typeId===COOKERY_FILLED?cookeryType(held):'',current=held?.typeId===COOKERY_FILLED?cookeryCount(held):0;
  if((currentType&&currentType!==type)||current+OIL_BUCKET_POINTS>FLUID_CAPACITY)return false;
  nextPot=new ItemStack(COOKERY_FILLED,1);
  try{
   const next=current+OIL_BUCKET_POINTS;
   nextPot.setLore(['§7Oil: '+next+'/'+FLUID_CAPACITY]);
   nextPot.setDynamicProperty('kc_oil_count',next);
   nextPot.setDynamicProperty('kaleidoscope_grilling:oil_type',type);
  }catch{}
 }
 const rows=readReg(),k=posKey(block.dimension.id,block.x,block.y,block.z),row=rows.find(r=>r.k===k);
 try{block.setType('minecraft:air')}catch{return false}
 if(row){clearCells(row,rows);saveReg(rows.filter(r=>r!==row))}
 if(toCookery)setHand(player,hand,nextPot);else setHand(player,hand,new ItemStack(OIL_TYPES[type].bucket,1));
 return true;
}"""
    text=replace_once(text,old,new,'oil source to pot transaction')
    old=""" if(typeFromBlock&&(item?.typeId==='minecraft:bucket'||item?.typeId===COOKERY_EMPTY)){
  e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension,hand=findHand(p,item.typeId);
  system.run(()=>{const b=dim.getBlock(loc);if(b&&hand)takeSource(p,b,typeFromBlock,hand,item.typeId===COOKERY_EMPTY)});return;
 }"""
    new=""" if(typeFromBlock&&(item?.typeId==='minecraft:bucket'||item?.typeId===COOKERY_EMPTY||item?.typeId===COOKERY_FILLED)){
  e.cancel=true;const p=e.player,loc={...e.block.location},dim=e.block.dimension,hand=findHand(p,item.typeId);
  system.run(()=>{const b=dim.getBlock(loc);if(b&&hand)takeSource(p,b,typeFromBlock,hand,item.typeId!== 'minecraft:bucket')});return;
 }"""
    text=replace_once(text,old,new,'oil source interaction')
    path.write_text(text,encoding='utf-8')

def patch_main_runtime():
    path=BP/'scripts/main.js';s=path.read_text(encoding='utf-8')
    s=replace_once(s,
        "import './a23_oil_world.js';",
        """import './a23_oil_world.js';
import {UNFINISHED_ID,SECRET_ID,SKEWER_INGREDIENTS_KEY,SECRET_COOKED_KEY,SECRET_COOKED_INGREDIENTS_KEY,SECRET_CREATOR_KEY,FLUID_CAPACITY,appendOutcome,secretFood,isDisassemblableRaw} from './a24_skewering_core.js';""",
        'A2.4 imports')
    s=replace_once(s,
        "const ACTIVE_EATS=new Map(),SETTLED=new Map(),VIGOR_LAST=new Map(),SNEAK_LAST=new Map(),SEASON_PLACE_CACHE=new Map();",
        "const ACTIVE_EATS=new Map(),SETTLED=new Map(),VIGOR_LAST=new Map(),SNEAK_LAST=new Map(),SEASON_PLACE_CACHE=new Map(),THREAD_LAST=new Map();",
        'thread guard')

    old="function copyOne(stack){return new ItemStack(stack.typeId,1)}"
    new="""function copyOne(stack){const out=stack.clone();out.amount=1;return out}
function copyCustomData(from,to){
 try{if(from.nameTag)to.nameTag=from.nameTag}catch{}
 let lore=[];try{lore=from.getLore()}catch{}
 let ids=[];try{ids=from.getDynamicPropertyIds()}catch{}
 try{if(lore.length)to.setLore(lore);else if(ids.length)to.setLore(['§r'])}catch{}
 for(const id of ids)try{to.setDynamicProperty(id,from.getDynamicProperty(id))}catch{}
 return to;
}
function primitiveProps(stack){
 const out={};let ids=[];try{ids=stack.getDynamicPropertyIds()}catch{}
 for(const id of ids)try{const value=stack.getDynamicProperty(id);if(['string','number','boolean'].includes(typeof value))out[id]=value;else if(value&&typeof value==='object'&&Number.isFinite(value.x)&&Number.isFinite(value.y)&&Number.isFinite(value.z))out[id]={x:value.x,y:value.y,z:value.z}}catch{}
 return out;
}
function ingredientSnapshot(stack){
 let nutrition=0,saturation=0,convertTo='';
 try{const food=stack.getComponent('minecraft:food');if(food){nutrition=Number(food.nutrition)||0;saturation=Number(food.saturationModifier)||0;convertTo=String(food.usingConvertsTo??'')}}catch{}
 let lore=[];try{lore=stack.getLore()}catch{}
 let name='';try{name=stack.nameTag??''}catch{}
 const props=primitiveProps(stack),signature=JSON.stringify({id:stack.typeId,name,lore,props});
 return {id:stack.typeId,nutrition,saturation,convertTo,name,lore,props,signature};
}
function restoreIngredient(row){
 let out;try{out=new ItemStack(row.id,1)}catch{return undefined}
 try{if(row.name)out.nameTag=row.name}catch{}
 const props=row.props&&typeof row.props==='object'?row.props:{},keys=Object.keys(props);
 try{if(Array.isArray(row.lore)&&row.lore.length)out.setLore(row.lore);else if(keys.length)out.setLore(['§r'])}catch{}
 for(const id of keys)try{out.setDynamicProperty(id,props[id])}catch{}
 return out;
}
function readRowsFromKey(stack,key){
 try{const raw=stack?.getDynamicProperty(key);if(typeof raw!=='string')return [];const rows=JSON.parse(raw);return Array.isArray(rows)?rows.filter(x=>x&&typeof x.id==='string').slice(0,3):[]}catch{return []}
}
function readSkewerRows(stack){return readRowsFromKey(stack,SKEWER_INGREDIENTS_KEY)}
function isSecretCooked(stack){try{return stack?.typeId===SECRET_ID&&stack.getDynamicProperty(SECRET_COOKED_KEY)===true}catch{return false}}
function readEffectiveSkewerRows(stack){if(isSecretCooked(stack)){const cooked=readRowsFromKey(stack,SECRET_COOKED_INGREDIENTS_KEY);if(cooked.length)return cooked}return readSkewerRows(stack)}
function rowLabel(row){return String(row.id??'').replace(/^.*:/,'').replaceAll('_',' ')}
function writeSkewerRows(stack,rows){
 const clean=(rows??[]).filter(x=>x&&typeof x.id==='string').slice(0,3);
 try{
  stack.setLore(['§8手工穿串 '+clean.length+'/3',...clean.map(x=>'§7- '+rowLabel(x))]);
  stack.setDynamicProperty(SKEWER_INGREDIENTS_KEY,JSON.stringify(clean));
 }catch{}
 return stack;
}
function setSecretCreator(stack,player){
 try{const creator={name:player.name,id:player.id};stack.setDynamicProperty(SECRET_CREATOR_KEY,JSON.stringify(creator));const lore=stack.getLore();lore.push('§7製作者: '+player.name);stack.setLore(lore)}catch{}
 return stack;
}
const VANILLA_SMOKED=Object.freeze({
 'minecraft:beef':'minecraft:cooked_beef','minecraft:porkchop':'minecraft:cooked_porkchop','minecraft:chicken':'minecraft:cooked_chicken',
 'minecraft:mutton':'minecraft:cooked_mutton','minecraft:rabbit':'minecraft:cooked_rabbit','minecraft:cod':'minecraft:cooked_cod',
 'minecraft:salmon':'minecraft:cooked_salmon','minecraft:potato':'minecraft:baked_potato','minecraft:kelp':'minecraft:dried_kelp'
});
function cookedIngredientRows(rows){
 return (rows??[]).map(row=>{const id=VANILLA_SMOKED[row.id];if(!id)return row;try{return ingredientSnapshot(new ItemStack(id,1))}catch{return row}});
}
function setCookedIngredientRows(stack,rows){try{stack.setDynamicProperty(SECRET_COOKED_INGREDIENTS_KEY,JSON.stringify(cookedIngredientRows(rows)))}catch{}return stack}
function dynamicFood(stack){return stack?.typeId===SECRET_ID?secretFood(readEffectiveSkewerRows(stack),isSecretCooked(stack)):FOOD_DATA[stack?.typeId]}
function isEdible(stack){try{return !!stack?.getComponent('minecraft:food')}catch{return false}}
function threadOutcome(player){
 const food=heldMain(player),off=heldOff(player);if(!food||!off||player.isSneaking)return null;
 if(off.typeId!=='minecraft:stick'&&off.typeId!==UNFINISHED_ID&&!(off.typeId===SECRET_ID&&!isSecretCooked(off)))return null;
 const rows=off.typeId==='minecraft:stick'?[]:readSkewerRows(off);
 return appendOutcome(rows,food.typeId,isEdible(food),false);
}
function canDisassembleOff(player){const off=heldOff(player);return !!off&&isDisassemblableRaw(off.typeId,isSecretCooked(off))&&readSkewerRows(off).length>0}
function threadCurrent(player){
 const food=heldMain(player),off=heldOff(player),outcome=threadOutcome(player);if(!food||!off||!outcome?.ok)return false;
 const rows=off.typeId==='minecraft:stick'?[]:readSkewerRows(off),nextRows=[...rows,ingredientSnapshot(food)],next=new ItemStack(outcome.id,1);
 writeSkewerRows(next,nextRows);if(outcome.kind==='secret')setSecretCreator(next,player);
 if(!creative(player)&&!decrementMain(player))return false;
 if(off.typeId==='minecraft:stick'){
  const keep=off.amount-(creative(player)?0:1);setOff(player,next);if(keep>0)give(player,new ItemStack('minecraft:stick',keep));
 }else setOff(player,next);
 try{player.playSound('random.pop',{volume:.7,pitch:1.2})}catch{}
 message(player,outcome.kind==='fixed'?'§a固定配方完成':outcome.kind==='secret'?'§d秘制串完成':'§e已穿入 '+nextRows.length+'/3');
 return true;
}
function disassembleOff(player){
 const off=heldOff(player);if(!off||!canDisassembleOff(player))return false;const rows=readSkewerRows(off);
 if(off.amount<=1)setOff(player,undefined);else{off.amount-=1;setOff(player,off)}
 for(const row of rows){const item=restoreIngredient(row);if(item)give(player,item)}
 give(player,new ItemStack('minecraft:stick',1));try{player.playSound('random.pop',{volume:.8,pitch:.8})}catch{};message(player,'§a已拆解烤串並返還材料');return true;
}
function scheduleSkewerAction(player,action){
 const old=THREAD_LAST.get(player.id);if(old?.tick===system.currentTick)return true;THREAD_LAST.set(player.id,{tick:system.currentTick,action});
 system.run(()=>{if(action==='disassemble')disassembleOff(player);else threadCurrent(player)});return true;
}
function skewerAction(player,itemStack){
 if(player.isSneaking&&canDisassembleOff(player))return 'disassemble';
 const main=heldMain(player);if(!main||!itemStack||itemStack.typeId!==main.typeId)return null;
 return threadOutcome(player)?.ok?'thread':null;
}
function secretRemainders(player,stack){
 for(const row of readEffectiveSkewerRows(stack)){const id=String(row.convertTo??'');if(!id)continue;try{give(player,new ItemStack(id,1))}catch{}}
}
function addSecretNutrition(player,stack,meta){
 const d=dynamicFood(stack),h=player.getComponent('minecraft:player.hunger'),sat=player.getComponent('minecraft:player.saturation');if(!d||!h||!sat)return;
 const hunger=Math.min(h.effectiveMax,h.currentValue+d.nutrition);h.setCurrentValue(hunger);
 const gain=d.nutrition*d.saturation*2*(meta?.hot?1.25:1);sat.setCurrentValue(Math.min(hunger,sat.currentValue+gain));
}"""
    s=replace_once(s,old,new,'skewer helpers')

    old="function setHot(stack,ticks){if(ticks<=0)return stack;try{stack.setDynamicProperty(HOT_UNTIL_KEY,bucketHot(now()+ticks))}catch{}return stack}"
    new="""function setHot(stack,ticks){
 if(ticks<=0)return stack;
 try{
  const until=bucketHot(now()+ticks),left=Math.max(1,until-now()),sec=Math.max(1,Math.ceil(left/20)),m=Math.floor(sec/60),ss=String(sec%60).padStart(2,'0');
  const lore=stack.getLore().filter(x=>!String(x).startsWith('§c🔥'));lore.push('§c🔥 煙火氣 '+m+':'+ss);
  // Make the max-64 stack custom/non-stackable before the stable API dynamic-property write.
  stack.setLore(lore);stack.setDynamicProperty(HOT_UNTIL_KEY,until);
 }catch{}
 return stack;
}"""
    s=replace_once(s,old,new,'hot property order')

    old="""function refreshHotLore(stack){
 if(!stack)return stack;const until=hotUntil(stack);
 try{
  if(until<=0)return stack;const left=Math.max(0,until-now());
  if(left<=0){stack.setDynamicProperty(HOT_UNTIL_KEY,undefined);stack.setLore([]);return stack}
  const sec=Math.max(1,Math.ceil(left/20)),m=Math.floor(sec/60),s=String(sec%60).padStart(2,'0');
  stack.setLore(['§c🔥 煙火氣 '+m+':'+s]);
 }catch{}return stack;
}"""
    new="""function refreshHotLore(stack){
 if(!stack)return stack;const until=hotUntil(stack);
 try{
  const base=stack.getLore().filter(x=>!String(x).startsWith('§c🔥'));if(until<=0)return stack;const left=Math.max(0,until-now());
  if(left<=0){stack.setDynamicProperty(HOT_UNTIL_KEY,undefined);stack.setLore(base);return stack}
  const sec=Math.max(1,Math.ceil(left/20)),m=Math.floor(sec/60),s=String(sec%60).padStart(2,'0');
  base.push('§c🔥 煙火氣 '+m+':'+s);stack.setLore(base);
 }catch{}return stack;
}"""
    s=replace_once(s,old,new,'preserve stateful lore')

    old="""function cookedStack(raw,state){
 const out=RAW_TO_COOKED[raw.typeId];if(!out)return new ItemStack(MYSTERIOUS_ID,1);
 const stack=new ItemStack(out,1);setHot(stack,state.heatTicks);setSeasonings(stack,state.seasonings??[]);
 try{stack.setDynamicProperty('kaleidoscope_grilling:seasoned',state.seasoned)}catch{}
 return refreshHotLore(stack);
}
function outputFor(raw,state,kind){if(kind==='raw')return copyOne(raw);if(kind==='dark')return new ItemStack(DARK_ID,1);if(kind==='mysterious')return new ItemStack(MYSTERIOUS_ID,1);return cookedStack(raw,state)}"""
    new="""function cookedStack(raw,state){
 let stack;
 if(raw.typeId===SECRET_ID){
  stack=copyOne(raw);setCookedIngredientRows(stack,readSkewerRows(raw));try{stack.setDynamicProperty(SECRET_COOKED_KEY,true)}catch{}
 }else{
  const out=RAW_TO_COOKED[raw.typeId];if(!out)return new ItemStack(MYSTERIOUS_ID,1);
  stack=new ItemStack(out,1);copyCustomData(raw,stack);
 }
 setHot(stack,state.heatTicks);setSeasonings(stack,state.seasonings??[]);
 try{stack.setDynamicProperty('kaleidoscope_grilling:seasoned',state.seasoned)}catch{}
 return refreshHotLore(stack);
}
function failedStack(raw,id){const stack=new ItemStack(id,1);return copyCustomData(raw,stack)}
function outputFor(raw,state,kind){if(kind==='raw')return copyOne(raw);if(kind==='dark')return failedStack(raw,DARK_ID);if(kind==='mysterious')return failedStack(raw,MYSTERIOUS_ID);return cookedStack(raw,state)}"""
    s=replace_once(s,old,new,'secret/fixed cooked metadata')

    old="function cookeryOilCount(stack){if(stack?.typeId!==COOKERY_FILLED)return 0;try{const raw=stack.getDynamicProperty(COOKERY_OIL_KEY);return raw===undefined?256:Math.max(0,Math.min(256,Number(raw)|0))}catch{return 256}}\nfunction cookeryOilType(stack){try{const type=String(stack?.getDynamicProperty('kaleidoscope_grilling:oil_type')??'canola');return Object.hasOwn(OIL_TYPES,type)?type:'canola'}catch{return 'canola'}}"
    new="""function cookeryOilType(stack){try{const type=String(stack?.getDynamicProperty('kaleidoscope_grilling:oil_type')??'');return Object.hasOwn(OIL_TYPES,type)?type:''}catch{return ''}}
function cookeryOilCount(stack){
 if(stack?.typeId!==COOKERY_FILLED)return 0;const type=cookeryOilType(stack),cap=type?FLUID_CAPACITY:256;
 try{const raw=stack.getDynamicProperty(COOKERY_OIL_KEY);return raw===undefined?cap:Math.max(0,Math.min(cap,Number(raw)|0))}catch{return cap}
}"""
    s=replace_once(s,old,new,'Cookery 256/64 capacity')

    old=""" const remaining=count-needed,next=new ItemStack(remaining>0?COOKERY_FILLED:COOKERY_POT,1);
 if(remaining>0){try{next.setDynamicProperty(COOKERY_OIL_KEY,remaining);if(type!=='canola')next.setDynamicProperty('kaleidoscope_grilling:oil_type',type);next.setLore(['§7Oil: '+remaining+'/256'])}catch{}}
 setMain(player,next);return {ok:true,heat:heatForOil(type),remaining};"""
    new=""" const remaining=count-needed,next=new ItemStack(remaining>0?COOKERY_FILLED:COOKERY_POT,1),cap=type?FLUID_CAPACITY:256;
 if(remaining>0){try{next.setLore(['§7Oil: '+remaining+'/'+cap]);next.setDynamicProperty(COOKERY_OIL_KEY,remaining);if(type)next.setDynamicProperty('kaleidoscope_grilling:oil_type',type)}catch{}}
 setMain(player,next);return {ok:true,heat:heatForOil(type),remaining};"""
    s=replace_once(s,old,new,'Cookery oil consume lore')

    old=" if(id&&Object.hasOwn(RAW_TO_COOKED,id)){if(!state.lit){message(player,'§c需要先點火');return}if(!canInsert(state,n)){message(player,'§7烤爐現在不能再放入生串');return}const c=inv(block),slot=[0,1,2].find(i=>!c.getItem(i));if(slot===undefined)return;c.setItem(slot,new ItemStack(id,1));decrementMain(player);message(player,'§a已放入烤串 '+(slot+1)+'/3');return}"
    new=""" if(id&&(Object.hasOwn(RAW_TO_COOKED,id)||(id===SECRET_ID&&!isSecretCooked(held)&&readSkewerRows(held).length===3))){
  if(!state.lit){message(player,'§c需要先點火');return}if(!canInsert(state,n)){message(player,'§7烤爐現在不能再放入生串');return}
  const c=inv(block),slot=[0,1,2].find(i=>!c.getItem(i));if(slot===undefined)return;c.setItem(slot,copyOne(held));decrementMain(player);message(player,'§a已放入烤串 '+(slot+1)+'/3');return
 }"""
    s=replace_once(s,old,new,'secret grill insert')

    old="function hungerSettle(player,id,active){\n const d=FOOD_DATA[id];if(!d)return false;"
    new="function hungerSettle(player,id,active){\n const current=active.hand==='off'?heldOff(player):heldMain(player),d=id===SECRET_ID?dynamicFood(current):FOOD_DATA[id];if(!d)return false;"
    s=replace_once(s,old,new,'dynamic secret hunger')
    old=""" let stack=active.hand==='off'?heldOff(player):heldMain(player);if(!stack||stack.typeId!==id)return false;if(stack.amount<=1)setHand(player,active.hand,undefined);else{stack.amount-=1;setHand(player,active.hand,stack)}
 if(RAW_NAUSEA[id])try{player.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{player.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{player.addEffect('blindness',200,{showParticles:true})}catch{}
 afterCommitted(player,id,active.meta,active,false);return true;"""
    new=""" let stack=current;if(!stack||stack.typeId!==id)return false;const consumed=copyOne(stack);if(stack.amount<=1)setHand(player,active.hand,undefined);else{stack.amount-=1;setHand(player,active.hand,stack)}
 if(id===SECRET_ID)secretRemainders(player,consumed);
 if(RAW_NAUSEA[id])try{player.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{player.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{player.addEffect('blindness',200,{showParticles:true})}catch{}
 afterCommitted(player,id,active.meta,active,false);return true;"""
    s=replace_once(s,old,new,'secret partial consume remainder')

    old=""" if(!FOOD_DATA[id])return;
 const requested=PROFILE_BY_ITEM[id]??'THREE',hand=handFor(e.source,id)?.name??'main',profile=resolvedProfile(requested),meta=stackMeta(e.itemStack),sat=e.source.getComponent('minecraft:player.saturation');"""
    new=""" if(!FOOD_DATA[id]&&id!==SECRET_ID)return;
 const requested=PROFILE_BY_ITEM[id]??'THREE_RANDOM',hand=handFor(e.source,id)?.name??'main',profile=resolvedProfile(requested),meta=stackMeta(e.itemStack),sat=e.source.getComponent('minecraft:player.saturation');"""
    s=replace_once(s,old,new,'secret itemStartUse')

    old=""" dangerousPreservation(e.source,id);if(!FOOD_DATA[id])return;
 const a=ACTIVE_EATS.get(e.source.id)??{id,profile:PROFILE_BY_ITEM[id]??'THREE',meta:stackMeta(e.itemStack),nativeBefore:{},fxBefore:{},saturationBefore:undefined};stopEatSound(e.source,a.profile);SETTLED.set(e.source.id,system.currentTick);ACTIVE_EATS.delete(e.source.id);
 if(RAW_NAUSEA[id])try{e.source.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{e.source.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{e.source.addEffect('blindness',200,{showParticles:true})}catch{}
 afterCommitted(e.source,id,a.meta,a,true);"""
    new=""" dangerousPreservation(e.source,id);if(!FOOD_DATA[id]&&id!==SECRET_ID)return;
 const a=ACTIVE_EATS.get(e.source.id)??{id,profile:PROFILE_BY_ITEM[id]??'THREE_RANDOM',meta:stackMeta(e.itemStack),nativeBefore:{},fxBefore:{},saturationBefore:undefined};stopEatSound(e.source,a.profile);SETTLED.set(e.source.id,system.currentTick);ACTIVE_EATS.delete(e.source.id);
 if(id===SECRET_ID){addSecretNutrition(e.source,e.itemStack,a.meta);secretRemainders(e.source,e.itemStack)}
 if(RAW_NAUSEA[id])try{e.source.addEffect('nausea',60,{showParticles:true})}catch{};if(id===MYSTERIOUS_ID)try{e.source.addEffect('nausea',100,{showParticles:true})}catch{};if(id===DARK_ID)try{e.source.addEffect('blindness',200,{showParticles:true})}catch{}
 afterCommitted(e.source,id,a.meta,a,true);"""
    s=replace_once(s,old,new,'secret itemCompleteUse')

    anchor="world.beforeEvents.playerPlaceBlock.subscribe(e=>{try{if(e.permutationToPlace?.type?.id!==SEASONING_BLOCK)return;"
    injected="""world.beforeEvents.itemUse.subscribe(e=>{
 try{const action=skewerAction(e.source,e.itemStack);if(!action)return;e.cancel=true;scheduleSkewerAction(e.source,action)}catch{}
});
world.beforeEvents.playerInteractWithEntity.subscribe(e=>{
 try{const action=skewerAction(e.player,e.itemStack??heldMain(e.player));if(!action)return;e.cancel=true;scheduleSkewerAction(e.player,action)}catch{}
});
"""+anchor
    s=replace_once(s,anchor,injected,'air/entity skewer input')

    old="""world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 if(e.player.isSneaking&&!e.itemStack&&STORAGE_SORT_BLOCKS.has(e.block.typeId)){"""
    new="""world.beforeEvents.playerInteractWithBlock.subscribe(e=>{
 const skewerInput=skewerAction(e.player,e.itemStack??heldMain(e.player));if(skewerInput){e.cancel=true;scheduleSkewerAction(e.player,skewerInput);return}
 if(e.player.isSneaking&&!e.itemStack&&STORAGE_SORT_BLOCKS.has(e.block.typeId)){"""
    s=replace_once(s,old,new,'block skewer input')
    path.write_text(s,encoding='utf-8')

def main():
    report=load(P/'reports/build.json')
    if report.get('version')!='A2.3.0': raise RuntimeError('expected A2.3 baseline')
    patch_manifest()
    shutil.copyfile(DEV/'a24_skewering_core.js',BP/'scripts/a24_skewering_core.js')
    patch_items_and_assets()
    patch_hot_runtime()
    patch_oil_world()
    patch_main_runtime()
    report.update({
        'version':'A2.4.0',
        'java_reference':'breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c',
        'configured_skewer_recipes':20,
        'hand_threading':True,
        'unfinished_skewer':True,
        'secret_skewer':True,
        'secret_creator_metadata':True,
        'raw_skewer_disassembly':True,
        'secret_food_formula':'Java 0.6 coefficient; duplicate ingredient x0.8; raw nutrition/saturation x0.5',
        'secret_cooked_ingredient_resolution':'vanilla smoking map implemented; arbitrary modded smoking recipe lookup unavailable in stable Script API',
        'secret_finish_using_item':'using_converts_to remainders emulated; arbitrary ingredient finishUsingItem callbacks unavailable',
        'typed_oil_pot_capacity':64,
        'cookery_fat_capacity':256,
        'typed_oil_bucket_points':8,
        'allow_skewers_at_full_hunger':True,
        'stateful_stack_property_order':'custom lore first, dynamic property second, to satisfy stable ItemStack stateful-stack restriction',
        'plain_nonusable_air_threading':'stable Script API exposes successful itemUse/block/entity interaction, not a generic use-button event; non-usable ingredients can be threaded while targeting a block/entity'
    })
    write(P/'reports/build.json',report)
    write(P/'reports/a24-build.json',{
        k:report[k] for k in [
            'version','java_reference','configured_skewer_recipes','hand_threading','unfinished_skewer','secret_skewer',
            'secret_creator_metadata','raw_skewer_disassembly','secret_food_formula','secret_cooked_ingredient_resolution',
            'secret_finish_using_item','typed_oil_pot_capacity','cookery_fat_capacity','typed_oil_bucket_points',
            'allow_skewers_at_full_hunger','stateful_stack_property_order','plain_nonusable_air_threading'
        ]
    })
    write(P/'README.zh-TW.md',
"""# A2.4 Gameplay Core

A2.4 在 A2.3 上補回 Java 1.1.1 的手工穿串主鏈：副手木棍／未完成串 + 主手食材、20 條固定配方、三料秘制串、製作者資料、潛行拆解返還材料，以及秘制串動態營養公式。Cookery 油壺同步修正為普通脂肪 256 點、Grilling 三種流體油 64 點，每桶 8 點；固定串預設可滿飽食度進食。

Bedrock stable 2.9 沒有任意 smoking recipe manager 查詢，也沒有通用「使用鍵」事件；因此秘制串烹熟食材目前完整處理原版 smoking 映射，模組食材回退原始營養；不可原生使用的食材若對空氣按使用鍵無事件，需對著方塊或實體完成穿串。這兩項列為平台差異，不冒充 Java 原生能力。
""")
    print(json.dumps(load(P/'reports/a24-build.json'),ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
