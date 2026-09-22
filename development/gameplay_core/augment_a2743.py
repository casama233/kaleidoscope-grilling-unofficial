from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,43]
NEW_FILES=(
 'a2743_seasoning_contract_core.js',
 'a2743_seasoning_block_adapter.js',
 'a2743_seasoning_hud_core.js',
 'a2743_seasoning_hud_provider.js',
)
LANG={
 'en_US.lang':[
  'hud.kaleidoscope_grilling.seasoning.title=Seasoning Bottle · Mixing',
  'hud.kaleidoscope_grilling.seasoning.capacity=Capacity %1$s/%2$s · %3$s remaining',
  'hud.kaleidoscope_grilling.seasoning.effects=Effect Preview',
  'hud.kaleidoscope_grilling.seasoning.no_effect=Basic seasoning only',
  'hud.kaleidoscope_grilling.seasoning.base.green_chili=Green Chili Powder ×%s',
  'hud.kaleidoscope_grilling.seasoning.base.sichuan_pepper=Sichuan Pepper ×%s',
  'hud.kaleidoscope_grilling.seasoning.base.onion=Onion Powder ×%s',
  'hud.kaleidoscope_grilling.seasoning.speed=Speed · Redstone ×%s',
  'hud.kaleidoscope_grilling.seasoning.strength=Strength · Gunpowder ×%s',
  'hud.kaleidoscope_grilling.seasoning.duration=Extended duration · Houttuynia Powder ×%s',
  'hud.kaleidoscope_grilling.seasoning.totem=Death protection · Totem Powder ×%s',
  'hud.kaleidoscope_grilling.seasoning.vitality=Maximum health · Dragon Egg Powder ×%s',
  'hud.kaleidoscope_grilling.seasoning.numbness=Numb · Sichuan Pepper ×%s (requires at least 4)',
  'hud.kaleidoscope_grilling.seasoning.numbness_pending=Numb (inactive) · Sichuan Pepper ×%s/4',
  'jade.kaleidoscope_grilling.seasoning.capacity=Seasoning capacity: %1$s/%2$s',
  'jade.kaleidoscope_grilling.seasoning.uses=Uses remaining: %s',
 ],
 'zh_CN.lang':[
  'hud.kaleidoscope_grilling.seasoning.title=调料瓶 · 调制中',
  'hud.kaleidoscope_grilling.seasoning.capacity=容量 %1$s/%2$s · 还能加入 %3$s 份',
  'hud.kaleidoscope_grilling.seasoning.effects=当前效果预览',
  'hud.kaleidoscope_grilling.seasoning.no_effect=仅提供基础调味',
  'hud.kaleidoscope_grilling.seasoning.base.green_chili=绿辣椒粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.base.sichuan_pepper=花椒 ×%s',
  'hud.kaleidoscope_grilling.seasoning.base.onion=洋葱粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.speed=迅捷 · 红石粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.strength=力量 · 火药粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.duration=效果延长 · 折耳根粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.totem=一次保命 · 不死图腾粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.vitality=生命上限 · 龙蛋粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.numbness=麻了 · 花椒 ×%s（至少需要 4 份）',
  'hud.kaleidoscope_grilling.seasoning.numbness_pending=麻了（未触发） · 花椒 ×%s/4',
  'jade.kaleidoscope_grilling.seasoning.capacity=调料容量：%1$s/%2$s',
  'jade.kaleidoscope_grilling.seasoning.uses=剩余使用次数：%s',
 ],
 'zh_TW.lang':[
  'hud.kaleidoscope_grilling.seasoning.title=調料瓶 · 調製中',
  'hud.kaleidoscope_grilling.seasoning.capacity=容量 %1$s/%2$s · 還能加入 %3$s 份',
  'hud.kaleidoscope_grilling.seasoning.effects=目前效果預覽',
  'hud.kaleidoscope_grilling.seasoning.no_effect=僅提供基礎調味',
  'hud.kaleidoscope_grilling.seasoning.base.green_chili=綠辣椒粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.base.sichuan_pepper=花椒 ×%s',
  'hud.kaleidoscope_grilling.seasoning.base.onion=洋蔥粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.speed=迅捷 · 紅石粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.strength=力量 · 火藥粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.duration=效果延長 · 折耳根粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.totem=一次保命 · 不死圖騰粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.vitality=生命上限 · 龍蛋粉 ×%s',
  'hud.kaleidoscope_grilling.seasoning.numbness=麻了 · 花椒 ×%s（至少需要 4 份）',
  'hud.kaleidoscope_grilling.seasoning.numbness_pending=麻了（未觸發） · 花椒 ×%s/4',
  'jade.kaleidoscope_grilling.seasoning.capacity=調料容量：%1$s/%2$s',
  'jade.kaleidoscope_grilling.seasoning.uses=剩餘使用次數：%s',
 ],
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def replace_once(s,old,new,label):
 n=s.count(old)
 if n!=1:raise RuntimeError(f'{label} drift: expected 1, got {n}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.43 Seasoning Bottle HUD BP'),(rm,'Kaleidoscope Grilling A2.7.43 Seasoning Bottle HUD RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.43 Seasoning Bottle HUD'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_43_Seasoning_Bottle_HUD'
 write(P/'config.json',cfg)

def patch_main():
 p=BP/'scripts/main.js';s=p.read_text(encoding='utf-8')
 anchor="import {playerInventory as mainContainer,getMainHand as heldMain,setMainHand as setMain,getOffHand as heldOff,setOffHand as setOff,getHand as heldByHand,findHandEntry as handFor,setHand,isCreative as creative} from './a2735_player_io.js';\n"
 imports="""import {
 SEASONING_CAPACITY,SEASONING_MAX_BOTTLES,SEASONING_MAX_USES,SEASONING_VARIANT_MAX,
 PENDING_SEASONING_ID as PENDING_SEASONING,SEASONING_PLACE_BLOCK_ID as SEASONING_BLOCK,
 SEASONING_LIST_KEY as SEASON_LIST_KEY,SEASONING_USES_KEY as SEASON_USES_KEY,
 SEASONING_VARIANT_KEY as SEASON_VARIANT_KEY,SEASONING_KINDS,
 normalizeSeasoningList,hasSeasoningBase,isSeasoningBlockId as isSeasoningBlock
} from './a2743_seasoning_contract_core.js';
import {
 readPlacedSeasoningStack as readBottleStack,writePlacedSeasoningStack as writeBottleStack
} from './a2743_seasoning_block_adapter.js';
"""
 if imports in s:raise RuntimeError('A2.7.43 seasoning imports already present')
 s=replace_once(s,anchor,anchor+imports,'player IO import anchor')

 start=s.index("const PENDING_SEASONING='")
 end=s.index("const HEAT_BLOCKS=",start)
 middle=s[start:end]
 hot=[line for line in middle.splitlines() if line.startswith("const HOT_UNTIL_KEY=")]
 if len(hot)!=1:raise RuntimeError('HOT/FX line drift')
 s=s[:start]+hot[0]+'\n'+s[end:]

 s=replace_once(s,"function isSeasoningBlock(id){return SEASONING_BLOCKS.has(id)}\n",'','local seasoning block helper')
 s=replace_once(s,"function enc(n){return n<0?'m'+Math.abs(n):'p'+n}\n",'','local coordinate encoder')
 old_key="function seasoningBlockKey(block){return 'kaleidoscope_grilling:sb_'+block.dimension.id.replace(/[^a-z0-9]/gi,'_')+'_'+enc(block.x)+'_'+enc(block.y)+'_'+enc(block.z)}\n"
 s=replace_once(s,old_key,'','local seasoning block key')

 h0=s.index('function parseList(raw)')
 h1=s.index('function bucketHot(until)',h0)
 helpers="""function readSeasonings(stack){try{const raw=stack?.getDynamicProperty(SEASON_LIST_KEY);return typeof raw==='string'?normalizeSeasoningList(JSON.parse(raw)):[]}catch{return []}}
function setSeasonings(stack,list){try{stack.setDynamicProperty(SEASON_LIST_KEY,JSON.stringify(normalizeSeasoningList(list)))}catch{}return stack}
function getUses(stack){try{return Math.max(0,Math.min(SEASONING_MAX_USES,Number(stack?.getDynamicProperty(SEASON_USES_KEY)??0)|0))}catch{return 0}}
function setUses(stack,n){try{stack.setDynamicProperty(SEASON_USES_KEY,Math.max(0,Math.min(SEASONING_MAX_USES,n|0)))}catch{}return stack}
"""
 s=s[:h0]+helpers+s[h1:]

 b0=s.index('function readBottleStack(block)')
 b1=s.index('function bottleDataFromItem(stack)',b0)
 s=s[:b0]+s[b1:]

 s=replace_once(s,
  "variant:kind==='special'?Math.max(0,Math.min(7,Number(stack.getDynamicProperty(SEASON_VARIANT_KEY)??0)|0)):0",
  "variant:kind==='special'?Math.max(0,Math.min(SEASONING_VARIANT_MAX,Number(stack.getDynamicProperty(SEASON_VARIANT_KEY)??0)|0)):0",
  'item variant clamp')
 s=replace_once(s,
  "stack.setLore(['§7Uses: '+(16-(data.uses??0))+'/16','§7Ingredients: '+(data.ingredients?.length??0)+'/8'])",
  "stack.setLore(['§7Uses: '+(SEASONING_MAX_USES-(data.uses??0))+'/'+SEASONING_MAX_USES,'§7Ingredients: '+(data.ingredients?.length??0)+'/'+SEASONING_CAPACITY])",
  'finished bottle lore')
 s=replace_once(s,
  "stack.setLore(['§7Ingredients: '+data.ingredients.length+'/8',data.kind==='pending'?'§eReady to shake':'§7Missing base seasoning'])",
  "stack.setLore(['§7Ingredients: '+data.ingredients.length+'/'+SEASONING_CAPACITY,data.kind==='pending'?'§eReady to shake':'§7Missing base seasoning'])",
  'unfinished bottle lore')
 s=replace_once(s,
  "Math.max(1,Math.min(4,count))",
  "Math.max(1,Math.min(SEASONING_MAX_BOTTLES,count))",
  'bottle visual count')
 s=replace_once(s,"stack.length>=4","stack.length>=SEASONING_MAX_BOTTLES",'stack capacity check')
 s=replace_once(s,"message(player,'§c最多只能堆4瓶')","message(player,'§c最多只能堆'+SEASONING_MAX_BOTTLES+'瓶')",'stack capacity message')
 s=s.replace("stack.length+'/4'","stack.length+'/'+SEASONING_MAX_BOTTLES")
 s=replace_once(s,"top.ingredients.length>=8","top.ingredients.length>=SEASONING_CAPACITY",'ingredient capacity check')
 s=replace_once(s,"message(player,'§c最上層調料瓶已滿 8/8')","message(player,'§c最上層調料瓶已滿 '+SEASONING_CAPACITY+'/'+SEASONING_CAPACITY)",'ingredient full message')
 s=s.replace("top.ingredients.length+'/8","top.ingredients.length+'/'+SEASONING_CAPACITY")
 s=replace_once(s,"Math.floor(Math.random()*8)","Math.floor(Math.random()*(SEASONING_VARIANT_MAX+1))",'variant random range')
 s=replace_once(s,
  "out.setLore(['§7Uses: 16/16','§7Ingredients: '+list.length+'/8'])",
  "out.setLore(['§7Uses: '+SEASONING_MAX_USES+'/'+SEASONING_MAX_USES,'§7Ingredients: '+list.length+'/'+SEASONING_CAPACITY])",
  'completed bottle lore')

 hud_anchor="import './a2742_big_vat_hud_provider.js';\n"
 s=replace_once(s,hud_anchor,hud_anchor+"import './a2743_seasoning_hud_provider.js';\n",'HUD provider anchor')
 p.write_text(s,encoding='utf-8')

def patch_scripts():
 scripts=BP/'scripts'
 for name in NEW_FILES:shutil.copy2(DEV/name,scripts/name)
 patch_main()

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate localization key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2743-seasoning-hud.json',{
  'version':'A2.7.43',
  'scope':'Seasoning Bottle provider + shared seasoning contract and placed-state adapter',
  'java_contract':{
   'capacity':8,'max_bottles':4,'max_uses':16,'variant_range':[0,7],
   'base':['green_chili_powder','sichuan_pepper','onion_powder'],
   'effects':['speed','strength','duration','totem','vitality','numbness'],
   'numbness_threshold':4
  },
  'reuse':{
   'shared_crosshair_runtime':'a2739_crosshair_hud_runtime.js',
   'shared_contract':'a2743_seasoning_contract_core.js',
   'shared_block_adapter':'a2743_seasoning_block_adapter.js',
   'main_reuses_contract':True,'main_reuses_block_adapter':True,
   'provider_direct_dynamic_property_access':False,'single_poll_loop':True
  },
  'hud':{
   'top_bottle_semantics':True,'capacity':True,'remaining_uses':True,
   'required_base_counts':True,'effect_preview':True,'variant_in_signature':True,
   'variant_displayed':False
  },
  'minecraft_tested':False,'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,42]:raise RuntimeError('A2.7.43 must augment published A2.7.42')
 patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.43 Seasoning Bottle HUD complete')

if __name__=='__main__':main()
