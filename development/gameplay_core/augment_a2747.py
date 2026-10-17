from __future__ import annotations
import hashlib,json,shutil,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,47]
ITEM_ID='kaleidoscope_grilling:wedding_candy'
TEXTURE_URL='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/common/src/main/resources/assets/kaleidoscope_grilling/textures/item/wedding_candy.png'
TEXTURE_BLOB='d7ca9f5dfa61d6658372d8e181283fb5bf756d78'
LANG={
 'en_US.lang':[
  'item.kaleidoscope_grilling:wedding_candy.name=Wedding Candy',
  'tooltip.kaleidoscope_grilling.wedding_candy.1=A wedding candy from Breezeth.',
  'tooltip.kaleidoscope_grilling.wedding_candy.2=He would like to share this sweetness with you.',
  "message.kaleidoscope_grilling.wedding_candy.received=Today's wedding candy has arrived: %1$s pieces. May some of the happiness find you too!",
 ],
 'zh_CN.lang':[
  'item.kaleidoscope_grilling:wedding_candy.name=喜糖',
  'tooltip.kaleidoscope_grilling.wedding_candy.1=一颗来自微风 Breezeth 的喜糖。',
  'tooltip.kaleidoscope_grilling.wedding_candy.2=这份甜蜜，也想与你一同分享。',
  'message.kaleidoscope_grilling.wedding_candy.received=今日的喜糖已送达：共 %1$s 颗，愿你也沾沾喜气！',
 ],
 'zh_TW.lang':[
  'item.kaleidoscope_grilling:wedding_candy.name=喜糖',
  'tooltip.kaleidoscope_grilling.wedding_candy.1=一顆來自微風 Breezeth 的喜糖。',
  'tooltip.kaleidoscope_grilling.wedding_candy.2=這份甜蜜，也想與你一同分享。',
  'message.kaleidoscope_grilling.wedding_candy.received=今日的喜糖已送達：共 %1$s 顆，願你也沾沾喜氣！',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def replace_once(s,old,new,label):
 if s.count(old)!=1:raise RuntimeError(f'A2.7.47 patch anchor drift ({label}): {s.count(old)}')
 return s.replace(old,new,1)
def git_blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.47 Wedding Candy BP'),(rm,'Kaleidoscope Grilling A2.7.47 Wedding Candy RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.47 Wedding Candy'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_47_Wedding_Candy'
 write(P/'config.json',cfg)

def add_item():
 write(BP/'items/wedding_candy.json',{
  'format_version':'1.26.30','minecraft:item':{
   'description':{'identifier':ITEM_ID,'menu_category':{'category':'items'}},
   'components':{
    'minecraft:display_name':{'value':'item.kaleidoscope_grilling:wedding_candy.name'},
    'minecraft:icon':{'textures':{'default':'wedding_candy'}},
    'minecraft:max_stack_size':64,'minecraft:allow_off_hand':True,
    'minecraft:use_modifiers':{'start_using':'always','use_duration':1.6,'movement_modifier':0.35},
    'minecraft:food':{'can_always_eat':True,'nutrition':20,'saturation_modifier':0.5},
    'minecraft:use_animation':{'value':'eat'},
    'minecraft:tags':{'tags':['minecraft:is_food']}
   }
  }
 })

def add_texture():
 req=urllib.request.Request(TEXTURE_URL,headers={'User-Agent':'Grilling-A2.7.47/1'})
 with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
 actual=git_blob(data)
 if actual!=TEXTURE_BLOB:raise RuntimeError(f'wedding candy texture drift: {actual}')
 out=RP/'textures/items/wedding_candy.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 atlas=load(RP/'textures/item_texture.json');td=atlas.setdefault('texture_data',{})
 if 'wedding_candy' in td:raise RuntimeError('wedding_candy texture key already exists')
 td['wedding_candy']={'textures':'textures/items/wedding_candy'};write(RP/'textures/item_texture.json',atlas)

def patch_catalog():
 p=BP/'item_catalog/crafting_item_catalog.json';doc=load(p)
 groups=doc['minecraft:crafting_items_catalog']['categories'][0]['groups']
 group=next((x for x in groups if x.get('group_identifier',{}).get('name')=='kaleidoscope_grilling:itemGroup.main'),None)
 if group is None:raise RuntimeError('main item catalog group missing')
 items=group.setdefault('items',[])
 if ITEM_ID in items:raise RuntimeError('wedding candy already in item catalog')
 items.append(ITEM_ID);write(p,doc)

def patch_effect_registry():
 p=BP/'scripts/a2732_standalone_food_effect_core.js';s=p.read_text(encoding='utf-8')
 import_anchor="""import {
 COLD_ID,FIRE_RESISTANCE_TICKS
} from './a2722_cold_houttuynia_core.js';
"""
 import_add=import_anchor+"""import {
 WEDDING_CANDY_ID,WEDDING_CANDY_EFFECT,WEDDING_CANDY_EFFECT_TICKS
} from './a2747_wedding_candy_core.js';
"""
 s=replace_once(s,import_anchor,import_add,'standalone effect wedding import')
 cold_tail=""" Object.freeze({
  itemId:COLD_ID,
  effects:Object.freeze([
   Object.freeze({
    kind:'native',
    effect:'fire_resistance',
    ticks:FIRE_RESISTANCE_TICKS,
    options:Object.freeze({showParticles:true})
   })
  ])
 })
]);
"""
 wedding_tail=""" Object.freeze({
  itemId:COLD_ID,
  effects:Object.freeze([
   Object.freeze({
    kind:'native',
    effect:'fire_resistance',
    ticks:FIRE_RESISTANCE_TICKS,
    options:Object.freeze({showParticles:true})
   })
  ])
 }),
 Object.freeze({
  itemId:WEDDING_CANDY_ID,
  effects:Object.freeze([
   Object.freeze({
    kind:'persistent_fx',
    effect:WEDDING_CANDY_EFFECT,
    ticks:WEDDING_CANDY_EFFECT_TICKS,
    amplifier:0,
    stacking:'max_until'
   })
  ])
 })
]);
"""
 p.write_text(replace_once(s,cold_tail,wedding_tail,'standalone effect wedding row'),encoding='utf-8')

def patch_scripts():
 scripts=BP/'scripts'
 for name in ('a2747_wedding_candy_core.js','a2747_wedding_candy_runtime.js'):
  shutil.copy2(DEV/name,scripts/name)
 main=scripts/'main.js';s=main.read_text(encoding='utf-8')
 anchor="import './a2732_standalone_food_effect_runtime.js';\n"
 add=anchor+"import './a2747_wedding_candy_runtime.js';\n"
 if 'a2747_wedding_candy_runtime.js' in s:raise RuntimeError('A2.7.47 wedding runtime already active')
 main.write_text(replace_once(s,anchor,add,'main wedding runtime import'),encoding='utf-8')

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate localization key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2747-wedding-candy.json',{
  'version':'A2.7.47','scope':'port Java Wedding Candy item, Invincible food effect, and September 2026 acquisition event',
  'java_contract':{
   'nutrition':20,'saturation_modifier':0.5,'always_edible':True,
   'effect':'kaleidoscope_grilling:invincible','effect_ticks':300,
   'event_timezone':'Asia/Shanghai','event_dates':'2026-09-01..2026-09-12',
   'required_online_seconds':'day_of_month * 60','reward_count':'day_of_month','advancement_xp_reward':50
  },
  'reuse':{
   'standalone_food_effect_runtime':'a2732_standalone_food_effect_runtime.js',
   'existing_item_complete_use_listener':True,'new_item_complete_use_listener':False,
   'existing_invincible_damage_guard':'main.js FX_KEY / beforeEvents.entityHurt'
  },
  'bedrock_adaptation':{
   'advancement_ui':False,'xp_reward_preserved':True,
   'intrinsic_java_hover_tooltip':False,'translation_keys_preserved':True,
   'event_state':'player dynamic property JSON'
  },
  'texture':{'upstream_git_blob':TEXTURE_BLOB},
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,46]:raise RuntimeError('A2.7.47 must augment published A2.7.46')
 add_item();add_texture();patch_catalog();patch_scripts();patch_effect_registry();patch_lang();patch_versions();report()
 print('A2.7.47 Wedding Candy complete')

if __name__=='__main__':main()
