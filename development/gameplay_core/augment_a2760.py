from __future__ import annotations
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,60]
NEW=('a2760_advancement_inventory_core.js','a2760_advancement_inventory_runtime.js')
LANG={
'en_US.lang':[
'advancement.kaleidoscope_grilling.human_fireworks.title=Human Fireworks',
'advancement.kaleidoscope_grilling.human_fireworks.description=Obtain a grill and begin your fireside cooking journey.',
'advancement.kaleidoscope_grilling.better_write_it_down.title=Better Write It Down',
'advancement.kaleidoscope_grilling.better_write_it_down.description=Obtain your first skewer recipe.',
'advancement.kaleidoscope_grilling.a_handful_of_canola.title=A Handful of Canola',
'advancement.kaleidoscope_grilling.a_handful_of_canola.description=Obtain canola seeds.',
'advancement.kaleidoscope_grilling.strength_makes_oil.title=Strength Makes Oil',
'advancement.kaleidoscope_grilling.strength_makes_oil.description=Complete pressing and collect the residue.',
'advancement.kaleidoscope_grilling.sweet_potato.title=Sweet Potato',
'advancement.kaleidoscope_grilling.sweet_potato.description=Harvest a sweet potato.',
'advancement.kaleidoscope_grilling.nether_taste.title=Nether Taste',
'advancement.kaleidoscope_grilling.nether_taste.description=Carry houttuynia in the Nether.',
],
'zh_CN.lang':[
'advancement.kaleidoscope_grilling.human_fireworks.title=人间烟火',
'advancement.kaleidoscope_grilling.human_fireworks.description=获得一座烧烤架，烟火就从这里开始。',
'advancement.kaleidoscope_grilling.better_write_it_down.title=好记性不如烂笔头',
'advancement.kaleidoscope_grilling.better_write_it_down.description=获得第一张签谱。',
'advancement.kaleidoscope_grilling.a_handful_of_canola.title=一把油菜籽',
'advancement.kaleidoscope_grilling.a_handful_of_canola.description=获得油菜籽。',
'advancement.kaleidoscope_grilling.strength_makes_oil.title=力大出油',
'advancement.kaleidoscope_grilling.strength_makes_oil.description=完成压榨并取得产出的油渣。',
'advancement.kaleidoscope_grilling.sweet_potato.title=红苕',
'advancement.kaleidoscope_grilling.sweet_potato.description=收获红薯。',
'advancement.kaleidoscope_grilling.nether_taste.title=地狱口味',
'advancement.kaleidoscope_grilling.nether_taste.description=在下界携带折耳根。',
],
'zh_TW.lang':[
'advancement.kaleidoscope_grilling.human_fireworks.title=人間煙火',
'advancement.kaleidoscope_grilling.human_fireworks.description=獲得一座燒烤架，煙火就從這裡開始。',
'advancement.kaleidoscope_grilling.better_write_it_down.title=好記性不如爛筆頭',
'advancement.kaleidoscope_grilling.better_write_it_down.description=獲得第一張籤譜。',
'advancement.kaleidoscope_grilling.a_handful_of_canola.title=一把油菜籽',
'advancement.kaleidoscope_grilling.a_handful_of_canola.description=獲得油菜籽。',
'advancement.kaleidoscope_grilling.strength_makes_oil.title=力大出油',
'advancement.kaleidoscope_grilling.strength_makes_oil.description=完成壓榨並取得產出的油渣。',
'advancement.kaleidoscope_grilling.sweet_potato.title=紅苕',
'advancement.kaleidoscope_grilling.sweet_potato.description=收穫紅薯。',
'advancement.kaleidoscope_grilling.nether_taste.title=地獄口味',
'advancement.kaleidoscope_grilling.nether_taste.description=在下界攜帶折耳根。',
]}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.60 Inventory Advancement Parity BP'),(rm,'Kaleidoscope Grilling A2.7.60 Inventory Advancement Parity RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.60 Inventory Advancement Parity';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_60_Inventory_Advancement_Parity';write(P/'config.json',cfg)

def scripts():
 d=BP/'scripts'
 for name in NEW:shutil.copy2(DEV/name,d/name)
 p=d/'main.js';s=p.read_text(encoding='utf-8')
 anchor="import {awardSeasoningFinishedChallenges,awardMentalPreparationFailed,awardMetalToleranceFailed,awardOrdinaryChallenge,ordinaryChallengeOutcome} from './a2758_advancement_challenge_runtime.js';\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.60 import anchor drift')
 s=s.replace(anchor,anchor+"import {awardInventoryAdvancements} from './a2760_advancement_inventory_runtime.js';\n",1)
 anchor=" for(const p of world.getAllPlayers()){try{\n"
 if s.count(anchor)!=1:raise RuntimeError('A2.7.60 player loop anchor drift')
 s=s.replace(anchor,anchor+"  if(system.currentTick%20===0)awardInventoryAdvancements(p);\n",1)
 p.write_text(s,encoding='utf-8')

def lang():
 for name,vals in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in vals:
   key=line.split('=',1)[0]
   if any(x.startswith(key+'=') for x in rows):raise RuntimeError(f'{name}: duplicate {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(vals)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2760-inventory-advancement-parity.json',{
 'version':'A2.7.60','new_advancements':['human_fireworks','better_write_it_down','a_handful_of_canola','strength_makes_oil','sweet_potato','nether_taste'],
 'java_fallback_preserved':'looking_the_part',
 'reuse':{'one_shot_adapter':'a2753_advancement_runtime.js','raw_skewer_source':'Object.keys(RAW_TO_COOKED)','player_loop':'existing main.js system.runInterval','new_interval_count':0,'new_listener_count':0,'offhand_io':'a2735_player_io.getOffHand'},
 'cadence_ticks':20,'minecraft_tested':False,'bds_tested':False})

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,59]:raise RuntimeError('A2.7.60 must augment published A2.7.59')
 scripts();lang();versions();report();print('A2.7.60 inventory advancement parity complete')
if __name__=='__main__':main()
