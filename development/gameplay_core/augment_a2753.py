from __future__ import annotations
import json,shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack';DEV=Path(__file__).parent
VERSION=[2,7,53]
LANG={
 'en_US.lang':{
  'advancement.kaleidoscope_grilling.mountain_fragrance.title':'Mountain Fragrance',
  'advancement.kaleidoscope_grilling.mountain_fragrance.description':'Pick Sichuan pepper from a pepper tree.',
  'message.kaleidoscope_grilling.advancement.goal_announce':' completed the goal: ',
  'message.kaleidoscope_grilling.advancement.goal_self':'§6Goal complete: §r',
 },
 'zh_CN.lang':{
  'advancement.kaleidoscope_grilling.mountain_fragrance.title':'山野麻香',
  'advancement.kaleidoscope_grilling.mountain_fragrance.description':'从花椒树上摘得花椒。',
  'message.kaleidoscope_grilling.advancement.goal_announce':' 完成目标：',
  'message.kaleidoscope_grilling.advancement.goal_self':'§6目标达成：§r',
 },
 'zh_TW.lang':{
  'advancement.kaleidoscope_grilling.mountain_fragrance.title':'山野麻香',
  'advancement.kaleidoscope_grilling.mountain_fragrance.description':'從花椒樹上摘得花椒。',
  'message.kaleidoscope_grilling.advancement.goal_announce':' 完成目標：',
  'message.kaleidoscope_grilling.advancement.goal_self':'§6目標達成：§r',
 },
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def replace_once(s,old,new,label):
 n=s.count(old)
 if n!=1:raise RuntimeError(f'A2.7.53 patch anchor drift ({label}): {n}')
 return s.replace(old,new,1)

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in (
  (bm,'Kaleidoscope Grilling A2.7.53 Mountain Fragrance Advancement BP'),
  (rm,'Kaleidoscope Grilling A2.7.53 Mountain Fragrance Advancement RP'),
 ):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for module in doc.get('modules',[]):module['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json')
 cfg['name']='Kaleidoscope Grilling A2.7.53 Mountain Fragrance Advancement'
 cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_53_Mountain_Fragrance_Advancement'
 write(P/'config.json',cfg)

def patch_scripts():
 scripts=BP/'scripts'
 for name in ('a2753_advancement_core.js','a2753_advancement_runtime.js'):
  shutil.copy2(DEV/name,scripts/name)

 p=scripts/'a2748_pepper_tree_runtime.js';s=p.read_text(encoding='utf-8')
 anchor="""} from './a2748_pepper_tree_core.js';
"""
 s=replace_once(
  s,anchor,
  anchor+"import {awardMountainFragrance} from './a2753_advancement_runtime.js';\n",
  'pepper advancement import'
 )
 harvest="""    drop(block,SICHUAN_PEPPER_ID,harvestedPepperCount(Math.random()));
    setState(block,HAS_PEPPER_STATE,false);
"""
 s=replace_once(
  s,harvest,
  """    drop(block,SICHUAN_PEPPER_ID,harvestedPepperCount(Math.random()));
    awardMountainFragrance(player);
    setState(block,HAS_PEPPER_STATE,false);
""",
  'pepper harvest award'
 )
 p.write_text(s,encoding='utf-8')

def patch_lang():
 for lang,entries in LANG.items():
  p=RP/'texts'/lang;s=p.read_text(encoding='utf-8');rows=s.splitlines();add=[]
  for key,value in entries.items():
   if any(row.startswith(key+'=') for row in rows):raise RuntimeError(f'{lang}: duplicate {key}')
   add.append(key+'='+value)
  if s and not s.endswith('\n'):s+='\n'
  p.write_text(s+'\n'.join(add)+'\n',encoding='utf-8')

def report():
 write(P/'reports/a2753-mountain-fragrance-advancement.json',{
  'version':'A2.7.53',
  'java_advancement':'mountain_fragrance',
  'trigger':'empty-hand harvest of fruiting Pepper Leaves',
  'xp_reward':25,
  'once_per_player':True,
  'announce_to_chat':True,
  'frame':'goal',
  'shared_advancement_adapter':True,
  'dynamic_property_key':'kaleidoscope_grilling:adv_mountain_fragrance',
  'new_poll_loop':False,
  'new_world_event_listener':False,
  'native_java_advancement_tree':False,
  'native_java_toast':False,
  'bedrock_chat_goal_message':True,
  'minecraft_tested':False,
  'bds_tested':False
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,52]:
  raise RuntimeError('A2.7.53 must augment published A2.7.52')
 patch_scripts();patch_lang();patch_versions();report()
 print('A2.7.53 Mountain Fragrance Advancement complete')

if __name__=='__main__':main()
