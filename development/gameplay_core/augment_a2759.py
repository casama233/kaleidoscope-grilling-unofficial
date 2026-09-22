from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,59]

LANG={
 'en_US.lang':(
  'advancement.kaleidoscope_grilling.fireworks_feast.title=Fireworks Feast',
  'advancement.kaleidoscope_grilling.fireworks_feast.description=Eat every fixed cooked skewer, cold dish, and linked meal.',
 ),
 'zh_CN.lang':(
  'advancement.kaleidoscope_grilling.fireworks_feast.title=烟火全席',
  'advancement.kaleidoscope_grilling.fireworks_feast.description=吃过全部固定熟烤串、凉菜与联动料理。',
 ),
 'zh_TW.lang':(
  'advancement.kaleidoscope_grilling.fireworks_feast.title=煙火全席',
  'advancement.kaleidoscope_grilling.fireworks_feast.description=吃過全部固定熟烤串、涼菜與聯動料理。',
 ),
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.59 Fireworks Feast Parity BP'),
  (rm,'Kaleidoscope Grilling A2.7.59 Fireworks Feast Parity RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.59 Fireworks Feast Parity'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_59_Fireworks_Feast_Parity'
 write(P/'config.json',cfg)

def patch_scripts():
 for name in ('a2759_fireworks_feast_core.js','a2759_fireworks_feast_runtime.js'):
  shutil.copy2(DEV/name,BP/'scripts'/name)

 p=BP/'scripts/main.js';s=p.read_text(encoding='utf-8')
 old="import {awardSeasoningFinishedChallenges,awardMentalPreparationFailed,awardMetalToleranceFailed,awardOrdinaryChallenge,ordinaryChallengeOutcome} from './a2758_advancement_challenge_runtime.js';"
 new=old+"\nimport {recordFireworksFeastFood} from './a2759_fireworks_feast_runtime.js';"
 if s.count(old)!=1:raise RuntimeError('A2.7.59 import anchor drift')
 s=s.replace(old,new,1)

 old=" awardMentalPreparationFailed(player,id);\n"
 new=" awardMentalPreparationFailed(player,id);\n recordFireworksFeastFood(player,id);\n"
 if s.count(old)!=1:raise RuntimeError('A2.7.59 food-finished anchor drift')
 s=s.replace(old,new,1)
 p.write_text(s,encoding='utf-8')

def patch_lang():
 for name,lines in LANG.items():
  p=RP/'texts'/name;s=p.read_text(encoding='utf-8');rows=s.splitlines()
  for line in lines:
   key=line.split('=',1)[0]
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{name}: duplicate key {key}')
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(lines)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2759-fireworks-feast-parity.json',{
  'version':'A2.7.59',
  'advancement':'fireworks_feast',
  'java_contract':{
   'food_count':29,
   'parent':'eat_it_hot',
   'frame':'challenge',
   'experience':100,
   'progress_key':'kaleidoscope_grilling:advancement_foods',
   'records_only_finished_food':True
  },
  'reuse':{
   'one_shot_adapter':'a2753_advancement_runtime.js',
   'existing_after_committed_path':True,
   'new_listener_count':0,
   'new_interval_count':0,
   'duplicate_progression_store':False
  },
  'official_reference':{
   'repository':'microsoft/minecraft-scripting-samples',
   'commit':'73a171fc8393a1052b4ca0669dc82231f775d8b1',
   'path':'editor-multi/scripts/goto-mark.ts',
   'git_blob':'833e034c9e04dd920680f4287a66efb008a81449',
   'pattern':'player.setDynamicProperty(key, JSON.stringify(structuredState))'
  },
  'native_java_advancement_tree':False,
  'native_java_toast':False,
  'minecraft_tested':False,
  'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,58]:
  raise RuntimeError('A2.7.59 must augment published A2.7.58')
 patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.59 Fireworks Feast parity complete')

if __name__=='__main__':main()
